# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.2.3 - 2025-03-07
- update `export gazebo_ros` within `package.xml`
- remove some useless models

## v1.2.2 - 2024-12-28
- [new feature] drone swarm
- remove some useless models

## v1.2.1 - 2024-12-23
- [new model:sensor] `livox_mid360`
- [new model:drone] `iris_d435i_mid360`
- [upgrade] upgrade `tf` to `tf2_ros`
- [remove model:sensor] `livox_mid40`
- remove all scripts

## v1.2.0 - 2024-08-24
- [new model] `iris_d435i_vlp16`, with `Velodyne VLP 16`, `Intel RealSense D435i` and `monocular camera`'
- remove some useless models
- remove useless config files

## [v1.1.4] - 2024-08-13
- [new model] `round_bucket`
- [new model] `basketball_court`
- [new world] `cuadc.world`, with `basketball_court`, `round_bucket`, `landing_pad`
- update parameters of `monocular_camera`
- modify lisence from `Apache` to `GPLv3`

## [v1.1.3] - 2024-08-05
- update `Eason_indoor.world`, add more features
- [new feature]: output odometry of drone via `libgazebo_ros_p3d`
- [new model] add model `landmark`, for camera calibration
- update model `Intel RealSense D435i`

## [v1.1.2] - 2024-08-04
- [new model] `Intel RealSense R200`
- update model `Intel RealSense D435i`
- remove some models of `iris`, `typhoon_h480`

## [v1.1.1]
- update model `Intel RealSense D435i`
- remove imu from model `Velodyne VLP 16`

## [v1.1.0]
- [new model] `iris`, with Livox LiDAR & D435i RGB-D Camera
- [new model] `typhoon_h480`

## [v1.0.8]
- add some worlds

## [v1.0.7]
- [new feature]: add `imu` to model `Intel RealSense D435i`
- update model `Intel RealSense D435i`

## [v1.0.6]
- add support for `launch`

## [v1.0.5]
- [new feature]: import `gazebo_ros_p3d` to get Odometry of camera (removed in [v1.1.1])

## [v1.0.4]
- [new feature]: add `imu` to `Velodyne VLP 16` (removed in [v1.1.1])
