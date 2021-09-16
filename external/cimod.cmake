include(FetchContent)

FetchContent_Declare(
    cimod
    GIT_REPOSITORY https://github.com/OpenJij/cimod
    GIT_TAG        v1.2.3
)

FetchContent_MakeAvailable(cimod)
