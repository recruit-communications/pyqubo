cmake_minimum_required(VERSION 3.11)

project(cpp_pyqubo)
set(CMAKE_CXX_STANDARD 14)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated-declarations")
set(CMAKE_CXX_FLAGS "-std=c++11 -msse4.1 -O3")

include(external/pybind11.cmake)
include_directories(cpp_dimod)
#add_subdirectory(include)
add_subdirectory(src)



include(external/googletest.cmake)
add_subdirectory(tests)
