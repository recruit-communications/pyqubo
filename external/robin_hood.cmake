include(FetchContent)

FetchContent_Declare(
    robin_hood
    GIT_REPOSITORY https://github.com/martinus/robin-hood-hashing
    GIT_TAG        3.11.2
)

FetchContent_GetProperties(robin_hood)

if(NOT robin_hood_POPULATED)
    message(STATUS "Fetch robin_hood")
    FetchContent_Populate(robin_hood)
    include_directories(${robin_hood_SOURCE_DIR}/src/include)
endif()
