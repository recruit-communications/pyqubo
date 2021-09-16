include(FetchContent)

FetchContent_Declare(
    boost_core
    GIT_REPOSITORY https://github.com/boostorg/core
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_core)
