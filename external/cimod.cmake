include(FetchContent)

FetchContent_Declare(
    cimod
    GIT_REPOSITORY https://github.com/OpenJij/cimod
    GIT_TAG        v1.2.3
)

FetchContent_GetProperties(cimod)

if(NOT cimod_POPULATED)
    message(STATUS "Fetch cimod")
    FetchContent_Populate(cimod)
    include_directories(${cimod_SOURCE_DIR}/src)
endif()
