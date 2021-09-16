include(FetchContent)

FetchContent_Declare(
    boost_static_assert
    GIT_REPOSITORY https://github.com/boostorg/static_assert
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_static_assert)
