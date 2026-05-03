#!/bin/bash
# Exit Anaconda environment
conda deactivate
conda deactivate

sudo apt update

sudo apt install -y ros-${ROS_DISTRO}-mavros*

sudo rm -rf /usr/share/GeographicLib/

sudo cp -r ./3rdparty/GeographicLib/ /usr/share/
