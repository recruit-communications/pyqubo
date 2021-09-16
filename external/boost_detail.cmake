include(FetchContent)

FetchContent_Declare(
    boost_detail
    GIT_REPOSITORY https://github.com/boostorg/detail
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_detail)

if(NOT boost_detail_POPULATED)
    message(STATUS "Fetch boost detail")
    FetchContent_Populate(boost_detail)
    include_directories(${boost_detail_SOURCE_DIR}/include)
endif()
