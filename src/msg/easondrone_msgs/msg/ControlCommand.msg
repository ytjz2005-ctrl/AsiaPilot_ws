std_msgs/Header header

# 控制模式枚举
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

# 控制命令的模式
uint16 mode

uint8 SETPOINT_TYPE_POSITION=0 # position setpoint
uint8 SETPOINT_TYPE_VELOCITY=1 # velocity setpoint

uint8 setpoint_type # setpoint type to adjust behavior of position controller

uint8 FRAME_LOCAL_NED = 1
uint8 FRAME_LOCAL_OFFSET_NED = 7
uint8 FRAME_BODY_NED = 8
uint8 FRAME_BODY_OFFSET_NED = 9

uint8 coordinate_frame

# 位置参考量：位置、速度、加速度、加加速度、加加加速度
quadrotor_msgs/PositionCommand poscmd
