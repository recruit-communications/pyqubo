include(FetchContent)

FetchContent_Declare(
    boost_move
    GIT_REPOSITORY https://github.com/boostorg/move
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_move)
