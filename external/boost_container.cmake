include(FetchContent)

FetchContent_Declare(
    boost_container
    GIT_REPOSITORY https://github.com/boostorg/container
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_container)
