# easondrone_msgs

![HitCount](https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FHuaYuXiao%2FEasonDrone_Msgs.json%3Fcolor%3Dpink)
![Static Badge](https://img.shields.io/badge/ROS-noetic-22314E?logo=ros)
![Static Badge](https://img.shields.io/badge/C%2B%2B-14-00599C?logo=cplusplus)
![Static Badge](https://img.shields.io/badge/Ubuntu-20.04.6-E95420?logo=ubuntu)

The easondrone_msgs package. Implement an interface to control the drone.

```
uint16 Arm = 0
uint16 Disarm = 1
uint16 Takeoff = 2
uint16 Land = 3
uint16 Return = 4
uint16 Manual = 5
uint16 Stabilized = 6
uint16 Acro = 7
uint16 Rattitude = 8
uint16 Altitude = 9
uint16 Offboard = 10
uint16 Position = 11
uint16 Hold = 12
uint16 Move = 13
```

![image](doc/Snipaste_2024-08-25_10-22-31.png)

## Installation

```shell
git clone https://github.com/HuaYuXiao/easondrone_msgs.git ~/easondrone_ws/module/easondrone_msgs
cd ~/easondrone_ws && catkin_make --source module/easondrone_msgs --build module/easondrone_msgs/build
```
