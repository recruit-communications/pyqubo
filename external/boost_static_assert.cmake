include(FetchContent)

FetchContent_Declare(
    boost_static_assert
    GIT_REPOSITORY https://github.com/boostorg/static_assert
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_static_assert)

if(NOT boost_static_assert_POPULATED)
    message(STATUS "Fetch boost static_assert")
    FetchContent_Populate(boost_static_assert)
    include_directories(${boost_static_assert_SOURCE_DIR}/include)
endif()
