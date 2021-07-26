#### Eigen ####
FetchContent_Declare(
    eigen
    GIT_REPOSITORY  https://gitlab.com/libeigen/eigen
    GIT_TAG         3.3.9
    CMAKE_ARGS -DEIGEN_MPL2_ONLY
    )
set(EIGEN_MPL2_ONLY ON)
FetchContent_MakeAvailable(eigen)
