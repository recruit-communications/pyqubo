include(FetchContent)

FetchContent_Declare(
    boost_container
    GIT_REPOSITORY https://github.com/boostorg/container
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_container)

if(NOT boost_container_POPULATED)
    message(STATUS "Fetch boost container")
    FetchContent_Populate(boost_container)
    include_directories(${boost_container_SOURCE_DIR}/include)
endif()
