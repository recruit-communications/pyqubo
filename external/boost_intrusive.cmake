include(FetchContent)

FetchContent_Declare(
    boost_intrusive
    GIT_REPOSITORY https://github.com/boostorg/intrusive
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_intrusive)
