include(FetchContent)

#### Google test ####
FetchContent_Declare(
    googletest
    GIT_REPOSITORY  https://github.com/google/googletest.git
    GIT_TAG         release-1.8.1
)

FetchContent_GetProperties(googletest)
if(NOT googletest_POPULATED)
    message(STATUS "Fetch googletest for C++ testing")
    FetchContent_Populate(googletest)
    add_subdirectory(${googletest_SOURCE_DIR} ${googletest_SOURCE_DIR}/googlemock)
endif()
