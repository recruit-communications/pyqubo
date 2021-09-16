include(FetchContent)

FetchContent_Declare(
    boost_container_hash
    GIT_REPOSITORY https://github.com/boostorg/container_hash
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_container_hash)
