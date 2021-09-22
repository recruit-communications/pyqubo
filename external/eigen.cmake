include(FetchContent)

FetchContent_Declare(
    eigen
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen
    GIT_TAG        3.3.7
)

FetchContent_GetProperties(eigen)

if(NOT eigen_POPULATED)
    message(STATUS "Fetch eigen")
    FetchContent_Populate(eigen)
    include_directories(${eigen_SOURCE_DIR})
endif()
