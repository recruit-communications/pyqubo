include(FetchContent)

#### cimod ####
FetchContent_Declare(
    cimod
    GIT_REPOSITORY  https://github.com/OpenJij/cimod.git
    GIT_TAG  v1.2.3
)

FetchContent_MakeAvailable(cimod)
