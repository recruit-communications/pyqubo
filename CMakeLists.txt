cmake_minimum_required(VERSION 3.11)

project(cpp_pyqubo)

set(CMAKE_INTERPROCEDURAL_OPTIMIZATION True)

set(CXX_STANDARD_REQUIRED TRUE)
set(CMAKE_VERBOSE_MAKEFILE TRUE)

set(CMAKE_CXX_STANDARD 14)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated-declarations")
set(CMAKE_C_FLAGS "-Ofast -pipe" )
set(CMAKE_CXX_FLAGS "-Ofast -pipe")
set(CMAKE_C_FLAGS_RELEASE "-Ofast -pipe")
set(CMAKE_CXX_FLAGS_RELEASE "-Ofast -pipe")

include(external/pybind11.cmake)
include_directories(cpp_dimod)
add_subdirectory(src)



include(external/googletest.cmake)
add_subdirectory(tests)
