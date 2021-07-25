
add_executable(pyqubo_test
    EXCLUDE_FROM_ALL
    pyqubotest.cpp
)

set_target_properties(pyqubo_test PROPERTIES
        CXX_VISIBILITY_PRESET "hidden"
        INTERPROCEDURAL_OPTIMIZATION TRUE
 )
target_link_libraries(pyqubo_test PRIVATE
    cpp_pyqubo_header_only
    cpp_dimod
    cpp_pyqubo_body
    cxxcimod_header_only
    $<IF:$<TARGET_EXISTS:Eigen3::Eigen>,Eigen3::Eigen,eigen-lib-headder>
    gmock
    gtest_main
    gtest
    pthread
)
