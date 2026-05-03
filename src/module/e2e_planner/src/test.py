#!/usr/bin/env python3
"""Test node: commands the drone to fly to a specified target"""

import rospy
import math
from std_msgs.msg import Float32
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
from mavros_msgs.msg import AttitudeTarget, State
from mavros_msgs.srv import SetMode, CommandBool

# ========== Global Variables ==========
current_state = State()    # Flight controller state
current_odom = Odometry()  # Odometry data

# Current desired attitude and throttle (timer will continuously send these values)
# Default hover throttle (e.g., around 0.7~0.8 in simulation, adjust according to your drone) to prevent falling upon mode switch
target_throttle = 0.79  
target_roll = 0.0
target_pitch = 0.0
target_yaw = 0.0

def state_cb(msg):
    global current_state
    current_state = msg

def odom_cb(msg):
    global current_odom
    current_odom = msg

def euler_to_quaternion(roll, pitch, yaw):
    """Correct Euler angle to quaternion conversion function"""
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    q = Quaternion()
    q.w = cr * cp * cy + sr * sp * sy
    q.x = sr * cp * cy - cr * sp * sy
    q.y = cr * sp * cy + sr * cp * sy
    q.z = cr * cp * sy - sr * sp * cy
    return q

def publish_attitude_timer_cb(event):
    """Timer callback: continuously send attitude commands (30Hz) in the background"""
    # Only publish when connected to the flight controller
    if not current_state.connected:
        return
        
    att = AttitudeTarget()
    att.header.stamp = rospy.Time.now()
    att.type_mask = AttitudeTarget.IGNORE_ROLL_RATE \
                  | AttitudeTarget.IGNORE_PITCH_RATE \
                  | AttitudeTarget.IGNORE_YAW_RATE
                  
    # Correctly convert Euler angles to quaternion
    att.orientation = euler_to_quaternion(target_roll, target_pitch, target_yaw)
    att.thrust = target_throttle
    
    attitude_pub.publish(att)

def main():
    global attitude_pub
    global target_throttle, target_roll, target_pitch, target_yaw

    rospy.init_node("test")
    rate = rospy.Rate(10) # Main loop frequency doesn't need to be high, as the timer handles control stream

    # ========== Subscribers and Publishers ==========
    rospy.Subscriber("/mavros/state", State, state_cb)
    rospy.Subscriber("/mavros/local_position/odom", Odometry, odom_cb)
    attitude_pub = rospy.Publisher("/mavros/setpoint_raw/attitude", AttitudeTarget, queue_size=1)

    # ========== Wait for MAVROS Connection ==========
    while not rospy.is_shutdown() and not current_state.connected:
        rospy.loginfo("Waiting for PX4 connection...")
        rate.sleep()
    rospy.loginfo("Flight controller connected!")

    # ========== Start background timer for sending commands (30Hz) ==========
    # This replaces the original "warm-up" and the issue of stream interruption during blocking
    rospy.Timer(rospy.Duration(1.0 / 30.0), publish_attitude_timer_cb)
    rospy.loginfo("Setpoint sending thread started (30Hz)")

    # Wait a moment for the timer to send a few packets to complete warm-up
    rospy.sleep(1.0) 

    # ========== User Operation Instructions ==========
    rospy.loginfo("\n=== Operation Instructions ===")
    rospy.loginfo("1. Manually arm and take off to a certain altitude in QGC.")
    rospy.loginfo("2. Switch to OFFBOARD mode in QGC.")
    rospy.loginfo("3. The drone will now maintain target_throttle=0.6.")
    rospy.loginfo("4. Enter in terminal: throttle roll pitch yaw to control the drone")
    rospy.loginfo("Example: 0.6 0.0 0.0 0.0  (60%% throttle, level forward flight)\n")

    # ========== Main Loop: only handles terminal input ==========
    while not rospy.is_shutdown():
        if current_state.mode != "OFFBOARD":
            rospy.loginfo_throttle(2, "Waiting to switch to OFFBOARD mode in QGC...")
            rate.sleep()
            continue

        # Read user input (blocking here is fine, because the Timer is still sending packets in the background)
        try:
            cmd = input(">>> ")
            if not cmd.strip():
                continue
                
            parts = cmd.strip().split()
            
            # Update global desired variables, Timer callback will automatically use these new values
            target_throttle = float(parts[0])
            target_roll     = float(parts[1]) if len(parts) > 1 else 0.0
            target_pitch    = float(parts[2]) if len(parts) > 2 else 0.0
            target_yaw      = float(parts[3]) if len(parts) > 3 else 0.0

            rospy.loginfo(f"Command updated: Throttle={target_throttle:.2f}, Attitude=({target_roll:.2f}, {target_pitch:.2f}, {target_yaw:.2f})")

        except ValueError:
            rospy.logwarn("Format error, please use numbers: throttle [roll pitch yaw]")
        except KeyboardInterrupt:
            rospy.loginfo("User interrupted")
            break
        except EOFError:
            break

if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass