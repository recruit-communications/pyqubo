include(FetchContent)

FetchContent_Declare(
    boost_type_traits
    GIT_REPOSITORY https://github.com/boostorg/type_traits
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_type_traits)

if(NOT boost_type_traits_POPULATED)
    message(STATUS "Fetch boost type_traits")
    FetchContent_Populate(boost_type_traits)
    include_directories(${boost_type_traits_SOURCE_DIR}/include)
endif()
