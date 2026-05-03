# easondrone_gazebo

![HitCount](https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FHuaYuXiao%2Feasondrone_gazebo.json%3Fcolor%3Dpink)
![Static Badge](https://img.shields.io/badge/ROS-noetic-22314E?logo=ros)
![Static Badge](https://img.shields.io/badge/Ubuntu-20.04.6-E95420?logo=ubuntu)

The easondrone_gazebo package.

## Launch

### Single drone

```sh
roslaunch easondrone_gazebo simulation.launch
```

### Swarm drone

```sh
roslaunch easondrone_gazebo multi_uav_mavros_sitl.launch
```

## Acknowledgement

Support of `livox_mid360` are based on:

- [livox_laser_simulation](https://github.com/Livox-SDK/livox_laser_simulation) package
- 3D model of `livox_mid360` from [Livox Technology Company Limited](https://terra-1-g.djicdn.com/65c028cd298f4669a7f0e40e50ba1131/Mid360/mid-360-asm.stp)
- `.dae` file from [Shaochang Tang](https://github.com/petertheprocess)
- Technique support from [Yunfei Zhu](https://github.com/zyf0205)

Many thanks for some models and worlds provided by [prometheus_gazebo](https://github.com/amov-lab/Prometheus/Simulator/gazebo_simulator) package.
