cmake_minimum_required(VERSION 3.12)

project(motoman_gp12_dual_cell_support)

find_package(ament_cmake REQUIRED)
ament_package()

install(DIRECTORY launch urdf
  DESTINATION share/${PROJECT_NAME})
