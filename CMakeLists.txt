cmake_minimum_required(VERSION 3.11)

project(cpp_pyqubo)

set(CMAKE_VERBOSE_MAKEFILE TRUE)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE )
find_program(CMAKE_MAKE_PROGRAM NAMES Ninja Ninja.exe)


set(CMAKE_CXX_STANDARD 14)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated-declarations")
set(CMAKE_C_FLAGS "-std=c++11 -Ofast -pipe -mtune=native -march=native" )
set(CMAKE_CXX_FLAGS "-std=c++11 -Ofast -pipe -mtune=native -march=native")


include(external/pybind11.cmake)
include_directories(cpp_dimod)
add_subdirectory(src)



include(external/googletest.cmake)
add_subdirectory(tests)
