cmake_minimum_required(VERSION 3.8)

project(robot_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    urdf
    worlds
    launch
  DESTINATION
    share/${PROJECT_NAME}/
)

install(
  PROGRAMS
    scripts/lift_control.py
    scripts/remote_control.py
    scripts/pallet_mission.py
  DESTINATION
    lib/${PROJECT_NAME}
)

ament_package()
