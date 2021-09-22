include(FetchContent)

FetchContent_Declare(
    boost_container_hash
    GIT_REPOSITORY https://github.com/boostorg/container_hash
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_container_hash)

if(NOT boost_container_hash_POPULATED)
    message(STATUS "Fetch boost container_hash")
    FetchContent_Populate(boost_container_hash)
    include_directories(${boost_container_hash_SOURCE_DIR}/include)
endif()
