# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.1.5 - 2025-03-24
- update `coordinate_frame` & `setpoint_type` for `Offboard` command

## v1.1.4 - 2024.08.25
- [new feature]: `Return`, `Stabilized`, `Acro`, `Rattitude`, `Altitude`, `Position`

## [v1.1.3] - 2024-08-08
- [CRUCIAL, new feature]: position command via `quadrotor_msgs::PositionCommand`
- [remove feature]: `AttitudeReference`, `ControlOutput`, `DroneState`, `PositionReference`

## [v1.1.2] - 2024-08-06
- [new feature]: `Manual`
- [deprecated] easondrone_msgs::ControlCommand::Idle
- separate `Offboard` and `Arm`

## [v1.1.1]
- [deprecated] `source` and check for `Command_ID` from `ControlCommand`
- [deprecated] `time_from_start`
- [deprecated] OFFBOARD & arm with `easondrone_msgs::ControlCommand::OFFBOARD_ARM`
- [remove feature]: useless msgs

## [v1.1.0]
- [new feature]: `POS_VEL_ACC` control
