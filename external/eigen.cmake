#### Eigen ####
FetchContent_Declare(
    eigen
    GIT_REPOSITORY  https://gitlab.com/libeigen/eigen
    GIT_TAG         3.3.9
    )
    
FetchContent_MakeAvailable(eigen)
set(EIGEN_CPP_STANDARD -std=c++11)
