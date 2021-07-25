#### Eigen ####
FetchContent_Declare(
    eigen
    GIT_REPOSITORY  https://gitlab.com/libeigen/eigen
    GIT_TAG         3.3.9
    )
    
FetchContent_MakeAvailable(eigen)
set(EIGEN_CPP_STANDARD -std=c++11)
add_library(eigen-lib-headder INTERFACE)
target_include_directories(eigen-lib-headder INTERFACE ${eigen_SOURCE_DIR})
target_compile_definitions(eigen-lib-headder INTERFACE EIGEN_MPL2_ONLY)
if (APPLE)
    if(BLAS_FOUND AND LAPACK_FOUND) 
      target_compile_definitions(eigen-lib-headder INTERFACE EIGEN_USE_BLAS=ON)
      target_compile_definitions(eigen-lib-headder- INTERFACE EIGEN_USE_LAPACKE=ON)
    endif()
endif()
