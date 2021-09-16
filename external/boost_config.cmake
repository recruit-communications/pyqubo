include(FetchContent)

FetchContent_Declare(
    boost_config
    GIT_REPOSITORY https://github.com/boostorg/config
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_config)

if(NOT boost_config_POPULATED)
    message(STATUS "Fetch boost config")
    FetchContent_Populate(boost_config)
    include_directories(${boost_config_SOURCE_DIR}/include)
endif()
