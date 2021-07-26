include(FetchContent)

#### Google test ####
FetchContent_Declare(
    googletest
    GIT_REPOSITORY  https://github.com/google/googletest
    GIT_TAG         release-1.11.0
)

FetchContent_MakeAvailable(googletest)
