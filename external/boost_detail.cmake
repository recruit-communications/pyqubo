include(FetchContent)

FetchContent_Declare(
    boost_detail
    GIT_REPOSITORY https://github.com/boostorg/detail
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_detail)
