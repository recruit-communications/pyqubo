
add_executable(pyqubo_test
    EXCLUDE_FROM_ALL
    pyqubotest.cpp
)

target_link_libraries(pyqubo_test PRIVATE
    cpp_pyqubo_body
    gtest_main
    gtest
    pthread
    pybind11::module
)
