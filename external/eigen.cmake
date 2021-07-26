#### Eigen ####
FetchContent_Declare(
    pyqubo-eigen
    GIT_REPOSITORY  https://gitlab.com/libeigen/eigen
    GIT_TAG         3.3.9
    CMAKE_ARGS -DEIGEN_MPL2_ONLY
    )
set(EIGEN_MPL2_ONLY ON)
set(EIGEN_CPP_STANDARD 11)
FetchContent_MakeAvailable(pyqubo-eigen)
