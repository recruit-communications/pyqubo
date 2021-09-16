include(FetchContent)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG        v2.6.2
)

FetchContent_GetProperties(pybind11)
if(NOT pybind11_POPULATED)
    message(STATUS "Fetch pybind11")
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR})
endif()
