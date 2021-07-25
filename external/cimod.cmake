include(FetchContent)

#### cimod ####
FetchContent_Declare(
    cimod
    GIT_REPOSITORY  https://github.com/OpenJij/cimod
    GIT_TAG  v1.3.0
)

FetchContent_MakeAvailable(cimod)

add_library(cxxcimod_header_only INTERFACE)
target_include_directories(cxxcimod_header_only INTERFACE ${cimod_SOURCE_DIR})
target_link_libraries(cxxcimod_header_only INTERFACE 
  $<IF:$<TARGET_EXISTS:Eigen3::Eigen>,Eigen3::Eigen,eigen_lib>
  $<$<TARGET_EXISTS:OpenMP::OpenMP_CXX>:OpenMP::OpenMP_CXX>
)
