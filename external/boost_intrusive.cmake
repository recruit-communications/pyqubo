include(FetchContent)

FetchContent_Declare(
    boost_intrusive
    GIT_REPOSITORY https://github.com/boostorg/intrusive
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_intrusive)

if(NOT boost_intrusive_POPULATED)
    message(STATUS "Fetch boost intrusive")
    FetchContent_Populate(boost_intrusive)
    include_directories(${boost_intrusive_SOURCE_DIR}/include)
endif()
