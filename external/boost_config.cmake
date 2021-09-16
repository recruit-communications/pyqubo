include(FetchContent)

FetchContent_Declare(
    boost_config
    GIT_REPOSITORY https://github.com/boostorg/config
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_config)
