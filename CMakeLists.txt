cmake_minimum_required(VERSION 3.20)

project(cpp_pyqubo)

include(CheckLanguage)

check_language(C)
check_language(CXX)

if(CMAKE_C_COMPILER)
  enable_language(C)
endif() 
if(CMAKE_CXX_COMPILER)
  enable_language(CXX)
endif() 

#set(Python3_FIND_VIRTUALENV FIRST)
#set(Python3_EXECUTABLE "${PYTHON_EXECUTABLE}")
#find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
#set(pybind11_DIR ${Python3_SITELIB}/pybind11/share/cmake/pybind11)
#find_package(pybind11 REQUIRED CONFIG)
#if(NOT TARGET pybind11::pybind11)
#  include(external/pybind11.cmake)
#endif() 

include(external/boost_assert.cmake)
include(external/boost_config.cmake)
include(external/boost_container.cmake)
include(external/boost_container_hash.cmake)
include(external/boost_core.cmake)
include(external/boost_detail.cmake)
include(external/boost_integer.cmake)
include(external/boost_intrusive.cmake)
include(external/boost_move.cmake)
include(external/boost_static_assert.cmake)
include(external/boost_type_traits.cmake)
include(external/cimod.cmake)
include(external/robin_hood.cmake)
include(external/pybind11.cmake)
include(external/eigen.cmake)

pybind11_add_module(cpp_pyqubo src/main.cpp)

target_compile_definitions(cpp_pyqubo PRIVATE VERSION_INFO=${PYQUBO_VERSION_INFO})
target_compile_features(cpp_pyqubo PRIVATE cxx_std_17)
target_compile_options(cpp_pyqubo PRIVATE
    $<$<CXX_COMPILER_ID:GNU>: -Ofast -Wall -Wno-terminate>
    $<$<CXX_COMPILER_ID:AppleClang>: -Ofast -Wno-exceptions>
    $<$<CXX_COMPILER_ID:MSVC>: /O2 /wd4297>
)
target_include_directories(cpp_pyqubo PRIVATE ${Boost_INCLUDE_DIRS})
