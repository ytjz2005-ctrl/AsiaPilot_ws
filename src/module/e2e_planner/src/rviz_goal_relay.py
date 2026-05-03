#!/usr/bin/env python3
"""
Receives 2D target point coordinates published by '2D Nav Goal' in RViz,
adds the desired flight altitude, and publishes to mavros_nn_planner
"""

import rospy
from geometry_msgs.msg import PoseStamped, Point

class RvizGoalRelay:
    def __init__(self):
        rospy.init_node("rviz_goal_relay")
        
        # Desired flight altitude (default 1.5 meters)
        self.flight_height = rospy.get_param("~flight_height", 1.5)
        
        # Subscribe to the default topic published by RViz's 2D Nav Goal tool
        self.goal_sub = rospy.Subscriber("/planning/direct_goal", PoseStamped, self.goal_cb)
        
        # Publish 3D target point to the neural network planner
        self.target_pub = rospy.Publisher("/e2e_network/target_position", Point, queue_size=1)
        
        rospy.loginfo(f"RViz goal relay node started, current flight altitude set to: {self.flight_height} m")
        rospy.loginfo("Please use the '2D Nav Goal' tool in RViz to click a target point...")

    def goal_cb(self, msg):
        target_point = Point()
        target_point.x = msg.pose.position.x
        target_point.y = msg.pose.position.y
        target_point.z = self.flight_height  # Force assign flight altitude
        
        self.target_pub.publish(target_point)
        rospy.loginfo(f"Received new target and forwarded: x={target_point.x:.2f}, y={target_point.y:.2f}, z={target_point.z:.2f}")

if __name__ == "__main__":
    try:
        relay = RvizGoalRelay()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass