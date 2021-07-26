cmake_minimum_required(VERSION 3.17)
project(cpp_pyqubo)

include(CheckLanguage)
check_language(C)
check_language(CXX)

if(APPLE)
    set(CMAKE_MACOSX_RPATH TRUE)
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-unused-command-line-argument")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}  -Wno-unused-command-line-argument")
    find_package(BLAS)
    find_package(LAPACK)
endif()

set(CXX_STANDARD_REQUIRED TRUE)
set(CMAKE_VERBOSE_MAKEFILE TRUE)
set(CMAKE_CXX_STANDARD 14)


##### Set default behavior #####
set(DEFAULT_USE_TEST No)
option(USE_TEST "Use test code" No)

if(NOT DEFINED USE_TEST)
    set(USE_TEST ${DEFAULT_USE_TEST})
endif()

message(STATUS "USE_TEST = ${USE_TEST}")

if(USE_TEST)
       include(external/googletest.cmake)          
else()
	message(STATUS "Skip downloding googletest")
endif()


include(external/pybind11.cmake)
#include(external/cimod.cmake)
#include(external/eigen.cmake)
find_package(Python COMPONENTS Development.Module)

add_subdirectory(cpp_dimod)
add_subdirectory(include)
add_subdirectory(src)

if(USE_TEST)
    add_subdirectory(tests)
endif()
