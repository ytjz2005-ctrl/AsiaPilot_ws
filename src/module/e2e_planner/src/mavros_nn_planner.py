#!/usr/bin/env python3
"""
End-to-End High-Speed Obstacle Avoidance for Drones Based on Differentiable Physics
"""

import rospy
import time
import numpy as np
import cv2
import torch
import torch.nn.functional as F
from cv_bridge import CvBridge

from std_msgs.msg import Float32
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion, Point, PoseStamped
from sensor_msgs.msg import Image
from mavros_msgs.msg import AttitudeTarget, State

# Import network model and rotation matrix conversion
from model import Model
from rotation import matrix_to_quaternion, quaternion_to_matrix

torch.set_grad_enabled(False)

class E2EMavrosPlanner:
    def __init__(self):
        rospy.init_node("e2e_mavros_planner")
        
        # ========== Parameter Configuration ==========
        self.net_weight_path = rospy.get_param("~weight", "your_model_weight.pth")
        self.target_speed = rospy.get_param("~target_speed", 2.0)
        self.margin = rospy.get_param("~margin", 0.5)
        # Hover throttle: MAVROS throttle (0~1) corresponding to physical acceleration of 9.81 m/s^2
        # Typically between 0.5-0.8 in simulation, adjust according to your actual drone!
        self.hover_throttle = rospy.get_param("~hover_throttle", 0.79) 
        
        # ========== State Variables ==========
        self.current_state = State()
        self.current_odom = None
        
        # Control commands (updated by depth callback, continuously published by Timer)
        self.target_throttle = self.hover_throttle
        self.target_quat = Quaternion(0.0, 0.0, 0.0, 1.0) # Initially level
        
        # Network state variables
        self.h_state = None     # GRU hidden state
        self.forward = None     # Record forward vector
        self.p_target = torch.tensor([0.0, 0.0, 1.5], dtype=torch.float32)
        
        self.bridge = CvBridge()

        self.hover_radius = 1.5  # Switching radius: switch to PID hover when distance < 1.5 meters
        self.use_nn_control = True # State machine flag
        
        # ========== Initialize Network ==========
        rospy.loginfo(f"Loading network model: {self.net_weight_path}")
        self.model = Model(7 + 3, 6).eval()
        try:
            state_dict = torch.load(self.net_weight_path, map_location='cpu')
            self.model.load_state_dict(state_dict, strict=True)
            # Warm up the network
            self.model(torch.zeros(1, 1, 12, 16), torch.zeros(1, self.model.dim_obs))
            rospy.loginfo("Neural network initialized and warmed up!")
        except Exception as e:
            rospy.logerr(f"Model loading failed: {e}")
            
        # ========== Subscribers and Publishers ==========
        self.state_sub = rospy.Subscriber("/mavros/state", State, self.state_cb)
        self.odom_sub = rospy.Subscriber("/mavros/local_position/odom", Odometry, self.odom_cb)
        self.depth_sub = rospy.Subscriber("/camera/depth/image_rect_raw", Image, self.depth_cb, queue_size=1) # Replace with your depth topic
        self.target_sub = rospy.Subscriber("/e2e_network/target_position", Point, self.target_cb)

        self.pos_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=1)
        self.attitude_pub = rospy.Publisher("/mavros/setpoint_raw/attitude", AttitudeTarget, queue_size=1)
        
        # Start 30Hz timer for sending control stream
        self.control_timer = rospy.Timer(rospy.Duration(1.0 / 30.0), self.control_timer_cb)
        
    def state_cb(self, msg):
        self.current_state = msg

    def odom_cb(self, msg):
        self.current_odom = msg

    def target_cb(self, msg):
        self.p_target = torch.tensor([msg.x, msg.y, msg.z], dtype=torch.float32)
        rospy.loginfo(f"Received new flight target point: [{msg.x:.2f}, {msg.y:.2f}, {msg.z:.2f}]")

    def control_timer_cb(self, event):
        """Timer callback: continuously send control commands (30Hz) to maintain OFFBOARD mode"""
        if not self.current_state.connected:
            return
            
        if self.use_nn_control:
            # ----------------------------------------------------
            # State A: Far from target, send attitude+thrust computed by neural network
            # ----------------------------------------------------
            att = AttitudeTarget()
            att.header.stamp = rospy.Time.now()
            att.type_mask = AttitudeTarget.IGNORE_ROLL_RATE \
                        | AttitudeTarget.IGNORE_PITCH_RATE \
                        | AttitudeTarget.IGNORE_YAW_RATE
            
            att.orientation = self.target_quat
            att.thrust = self.target_throttle
            self.attitude_pub.publish(att)
            
        else:
            # ----------------------------------------------------
            # State B: Near target, send target position point, let PX4's PID control hover
            # ----------------------------------------------------
            pose = PoseStamped()
            pose.header.stamp = rospy.Time.now()
            # Coordinate frame set to local reference frame
            pose.header.frame_id = "map"  
            
            # Assign target point coordinates
            pose.pose.position.x = self.p_target[0].item()
            pose.pose.position.y = self.p_target[1].item()
            pose.pose.position.z = self.p_target[2].item()
            
            # Maintain the last orientation output by the network to prevent heading drift during mode switch
            pose.pose.orientation = self.target_quat 
            
            self.pos_pub.publish(pose)

    @torch.no_grad()
    def depth_cb(self, data):
        """Depth image callback: core inference logic"""
        if self.current_state.mode != "OFFBOARD":
            # Only update commands in OFFBOARD mode, otherwise maintain level hover state
            self.target_throttle = self.hover_throttle
            self.target_quat = Quaternion(0.0, 0.0, 0.0, 1.0)
            self.h_state = None # Reset network hidden state
            self.forward = None
            return

        if self.current_odom is None:
            rospy.logwarn_throttle(2.0, "Waiting for odometry data...")
            return

        t0 = time.time()
        
        # 1. Extract current pose and velocity
        p = self.current_odom.pose.pose.position
        q_odom = self.current_odom.pose.pose.orientation
        v = self.current_odom.twist.twist.linear
        
        pos = (p.x, p.y, p.z)
        quat = (q_odom.w, q_odom.x, q_odom.y, q_odom.z) # Note: w first
        vel = (v.x, v.y, v.z)

        # 2. Depth image preprocessing
        # depth = self.bridge.imgmsg_to_cv2(data)
        # depth = np.float32(depth) / 1000.0
        # depth[depth == 0] = 24.  # 24 meter barrier for uncertain pixels
        depth = self.bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")
        depth = np.array(depth, dtype=np.float32)
        depth[np.isnan(depth)] = 24.0
        depth[np.isinf(depth)] = 24.0
        depth[depth <= 0.0] = 24.0
        
        depth = 3 / np.clip(depth, 0.3, 24) - 0.6
        h, w = depth.shape
        _h = round((h - h * 0.82) / 2)
        _w = round((w - w * 0.82) / 2)
        depth_tensor = torch.as_tensor(depth[_h:-_h, _w:-_w])[None, None]
        depth_tensor = F.interpolate(depth_tensor, (36, 48), mode='nearest')
        depth_tensor = F.max_pool2d(depth_tensor, (3, 3))

        # 3. State preprocessing
        pos_t, quat_t, vel_t = map(torch.as_tensor, (pos, quat, vel))
        
        R = quaternion_to_matrix(quat_t)
        env_R = R.clone()
        
        fwd = R[:, 0].clone()
        up = torch.zeros_like(fwd)
        fwd[2] = 0
        up[2] = 1
        fwd = fwd / torch.norm(fwd, 2, -1, keepdim=True)
        R = torch.stack([fwd, torch.cross(up, fwd), up], -1)

        if self.forward is None:
            self.forward = R[:, 0]

        # Set target velocity vector
        raw_diff = self.p_target - pos_t
        target_v_norm = torch.norm(raw_diff, 2, -1, keepdim=True)
        if target_v_norm.item() < self.hover_radius:
            # [Switch to PID hover mode]
            self.use_nn_control = False
            # Reset network hidden state to prevent accumulating useless features during hover
            self.h_state = None  
            rospy.loginfo_throttle(1.0, f"Distance to target {target_v_norm.item():.2f}m < {self.hover_radius}m, switched to PID precision hover.")
            return
        else:
            self.use_nn_control = True
            target_v = raw_diff / target_v_norm * target_v_norm.clamp_max(self.target_speed)

        margin_t = torch.tensor([self.margin])

        # Concatenate state vector [global_v in body frame, target_v in body frame, gravity direction in body frame, margin]
        global_v = vel_t @ env_R.T
        state = [global_v[None] @ R, target_v[None] @ R, env_R[None, 2], margin_t[None]]
        state = torch.cat(state, -1)

        # 4. Network forward inference
        act, _, self.h_state = self.model(depth_tensor, state, self.h_state)
        
        # 5. Post-processing to compute desired thrust and attitude
        a_pred, v_pred, *_ = (R @ act.reshape(3, -1)).unbind(-1)
        a_pred = a_pred - v_pred
        a_pred[2] += 9.81 # Add gravity compensation

        # Physical thrust magnitude (m/s^2)
        phys_thrust = torch.norm(a_pred)
        up_vec = a_pred / phys_thrust
        
        self.forward = self.forward * 5 + target_v
        self.forward[2] = (self.forward[0] * up_vec[0] + self.forward[1] * up_vec[1]) / -up_vec[2]
        self.forward /= torch.norm(self.forward, 2, -1, True)
        left_vec = torch.cross(up_vec, self.forward)
        
        # Convert to desired quaternion attitude (w, x, y, z)
        qw, qx, qy, qz = matrix_to_quaternion(torch.stack([
            self.forward, left_vec, up_vec
        ], 1)).tolist()

        # ========== 6. Convert to MAVROS Commands ==========
        # MAVROS attitude setpoint requires thrust value in [0.0, 1.0] range
        # Assume 9.81 m/s^2 corresponds to MAVROS Throttle of self.hover_throttle
        throttle = (phys_thrust.item() / 9.81) * self.hover_throttle
        throttle_clipped = np.clip(throttle, 0.0, 1.0) # Clamp for safety
        
        # Update global control commands (Timer will automatically send)
        self.target_quat = Quaternion(qx, qy, qz, qw) # ROS Quaternion order is x,y,z,w
        self.target_throttle = throttle_clipped

        # Print debug info
        rospy.loginfo_throttle(0.5, f"Net Output: Thrust: {phys_thrust.item():.2f}m/s^2 -> Throttle: {self.target_throttle:.2f}")

    def run(self):
        rate = rospy.Rate(10)
        
        # Wait for MAVROS connection
        while not rospy.is_shutdown() and not self.current_state.connected:
            rospy.loginfo("Waiting for PX4 connection...")
            rate.sleep()
        rospy.loginfo("Flight controller connected!")

        rospy.loginfo("\n=== Operation Instructions ===")
        rospy.loginfo("1. Ensure the depth image topic (/camera/depth/image_raw) is correct.")
        rospy.loginfo("2. Manually arm and take off to a certain altitude in QGC.")
        rospy.loginfo("3. After switching to OFFBOARD mode, network inference results will automatically take over control.\n")
        rospy.loginfo("4. Use '2D Nav Goal' in RViz to specify a target; the drone will fly there and automatically decelerate to hover upon arrival.\n")

        # Main loop
        while not rospy.is_shutdown():
            if self.current_state.mode != "OFFBOARD":
                rospy.loginfo_throttle(2, "Waiting to switch to OFFBOARD mode in QGC...")
            rate.sleep()

if __name__ == "__main__":
    try:
        planner = E2EMavrosPlanner()
        planner.run()
    except rospy.ROSInterruptException:
        pass