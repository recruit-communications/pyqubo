include(FetchContent)

#### cimod ####
FetchContent_Declare(
    cimod
    GIT_REPOSITORY  https://github.com/OpenJij/cimod
    GIT_TAG  v1.3.0
)
set(USE_OMP Off) 
FetchContent_MakeAvailable(cimod)
