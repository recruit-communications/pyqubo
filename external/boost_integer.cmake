include(FetchContent)

FetchContent_Declare(
    boost_integer
    GIT_REPOSITORY https://github.com/boostorg/integer
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_integer)
