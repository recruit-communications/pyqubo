include(FetchContent)

FetchContent_Declare(
    boost_integer
    GIT_REPOSITORY https://github.com/boostorg/integer
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_integer)

if(NOT boost_integer_POPULATED)
    message(STATUS "Fetch boost integer")
    FetchContent_Populate(boost_integer)
    include_directories(${boost_integer_SOURCE_DIR}/include)
endif()
