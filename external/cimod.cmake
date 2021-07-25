include(FetchContent)

#### cimod ####
FetchContent_Declare(
    cimod
    GIT_REPOSITORY  https://github.com/OpenJij/cimod
    GIT_TAG  v1.3.0
)

FetchContent_MakeAvailable(cimod)
target_include_directories(cxxcimod_header_only INTERFACE ${cimod_SOURCE_DIR})

target_include_directories(cxxcimod_header_only INTERFACE 
  ${cimod_SOURCE_DIR})
  $<IF:$<TARGET_EXISTS:Eigen3::Eigen>, ${EIGEN3_INCLUDE_DIR}, ${eigen_SOURCE_DIR}> 
)

if(OpenMP_FOUND)
  target_link_libraries(cxxcimod_header_only INTERFACE OpenMP::OpenMP_CXX)
endif()
