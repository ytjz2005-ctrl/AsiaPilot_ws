#!/bin/bash
# Exit Anaconda environment
conda deactivate
conda deactivate

sudo apt update

sudo apt install -y \
    ros-${ROS_DISTRO}-moveit-msgs \
    ros-${ROS_DISTRO}-object-recognition-msgs \
    ros-${ROS_DISTRO}-camera-info-manager  \
    ros-${ROS_DISTRO}-control-toolbox \
    ros-${ROS_DISTRO}-polled-camera \
    ros-${ROS_DISTRO}-controller-manager \
    ros-${ROS_DISTRO}-transmission-interface \
    ros-${ROS_DISTRO}-joint-limits-interface
sudo apt install -y gazebo11 libgazebo11-dev
sudo apt install -y ros-${ROS_DISTRO}-gazebo-ros
