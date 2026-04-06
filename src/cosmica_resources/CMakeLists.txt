cmake_minimum_required(VERSION 3.12)

project(cosmica_resources)

find_package(ament_cmake REQUIRED)
ament_package()

install(DIRECTORY meshes urdf
  DESTINATION share/${PROJECT_NAME})
