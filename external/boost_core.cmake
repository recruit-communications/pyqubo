include(FetchContent)

FetchContent_Declare(
    boost_core
    GIT_REPOSITORY https://github.com/boostorg/core
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_core)

if(NOT boost_core_POPULATED)
    message(STATUS "Fetch boost core")
    FetchContent_Populate(boost_core)
    include_directories(${boost_core_SOURCE_DIR}/include)
endif()
