cmake_minimum_required(VERSION 3.0.2)
project(easondrone_gazebo)

find_package(catkin REQUIRED COMPONENTS
  gazebo_dev
  gazebo_msgs
  gazebo_ros    
)

catkin_package()

catkin_install_python(PROGRAMS scripts/csrt.py
        DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
