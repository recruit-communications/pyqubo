include(FetchContent)

#### cimod ####
FetchContent_Declare(
    cimod
    GIT_REPOSITORY  https://github.com/OpenJij/cimod
    GIT_TAG  v1.3.0
)

FetchContent_MakeAvailable(cimod eigen)
add_library(cxxcimod_header_only INTERFACE)

target_include_directories(cxxcimod_header_only INTERFACE 
  $<IF:$<TARGET_EXISTS:Eigen3::Eigen>, ${EIGEN3_INCLUDE_DIR}, ${eigen_SOURCE_DIR}> 
)
