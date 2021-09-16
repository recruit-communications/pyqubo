include(FetchContent)

FetchContent_Declare(
    robin_hood
    GIT_REPOSITORY https://github.com/martinus/robin-hood-hashing
    GIT_TAG        3.11.2
)

FetchContent_MakeAvailable(robin_hood)
