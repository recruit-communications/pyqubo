cmake_minimum_required(VERSION 3.11)


add_executable(pyqubo_test
    EXCLUDE_FROM_ALL
    pyqubotest.cpp
)

include_directories(../include)
include_directories(../cpp_dimod)


target_link_libraries(pyqubo_test PRIVATE
    cpp_pyqubo_body
    gtest_main
    gtest
    pthread
    pybind11::module
)
