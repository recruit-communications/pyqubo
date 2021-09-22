include(FetchContent)

FetchContent_Declare(
    boost_assert
    GIT_REPOSITORY https://github.com/boostorg/assert
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_assert)

if(NOT boost_assert_POPULATED)
    message(STATUS "Fetch boost assert")
    FetchContent_Populate(boost_assert)
    include_directories(${boost_assert_SOURCE_DIR}/include)
endif()
