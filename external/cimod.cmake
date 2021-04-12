include(FetchContent)

#### cimod ####
FetchContent_Declare(
    cimod
    GIT_REPOSITORY  https://github.com/kotarotanahashi/cimod.git
    GIT_TAG v1.0.0
)

FetchContent_GetProperties(cimod)
if(NOT cimod_POPULATED)
    message(STATUS "Fetch cimod")
    FetchContent_Populate(cimod)
    include_directories(${cimod_SOURCE_DIR}/src)
endif()

