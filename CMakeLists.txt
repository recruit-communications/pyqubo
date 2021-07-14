cmake_minimum_required(VERSION 3.11)

project(cpp_pyqubo)

option(PYQUBO_BUILD_SHARED_LIBS "build mylib as a shared library" OFF)

set(CMAKE_INTERPROCEDURAL_OPTIMIZATION True)

set(CXX_STANDARD_REQUIRED TRUE)
set(CMAKE_VERBOSE_MAKEFILE TRUE)

set(CMAKE_CXX_STANDARD 14)

set(DEFAULT_USE_OMP Yes)
message(STATUS "USE_OMP = ${USE_OMP}")

if(USE_OMP)
    find_package(OpenMP REQUIRED)
    if(OpenMP_FOUND)
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
        add_definitions(-DUSE_OMP)
    endif()
endif()

if (APPLE)
    find_package(BLAS)
endif()

include(external/pybind11.cmake)
include_directories(cpp_dimod)
add_subdirectory(src)



include(external/googletest.cmake)
add_subdirectory(tests)
