cmake_minimum_required(VERSION 2.8.3)
project(easondrone_msgs)

find_package(catkin REQUIRED COMPONENTS
  message_generation  
  roscpp
  geometry_msgs
  actionlib_msgs
  sensor_msgs
  nav_msgs
  std_msgs
        quadrotor_msgs
)
find_package(Boost REQUIRED COMPONENTS system)

add_message_files(
  DIRECTORY msg
  FILES
  ControlCommand.msg
)

generate_messages(
  DEPENDENCIES
  actionlib_msgs
  geometry_msgs 
  sensor_msgs
  std_msgs
        quadrotor_msgs
)

catkin_package(
  CATKIN_DEPENDS
  message_runtime
  actionlib_msgs
  geometry_msgs
  sensor_msgs
  std_msgs
        quadrotor_msgs
)
