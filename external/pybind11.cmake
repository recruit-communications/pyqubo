include(FetchContent)

#### pybind11 ####
FetchContent_Declare(
    pybind11
    GIT_REPOSITORY  https://github.com/pybind/pybind11
    GIT_TAG         v2.5.0
)

FetchContent_GetProperties(pybind11)
if(NOT pybind11_fetch_POPULATED)
    message(STATUS "Fetch pybind11 for python-binding")
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR})
endif()

#set(PYBIND11_CPP_STANDARD -std=c++11)
