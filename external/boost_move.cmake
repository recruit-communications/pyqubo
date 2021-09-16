include(FetchContent)

FetchContent_Declare(
    boost_move
    GIT_REPOSITORY https://github.com/boostorg/move
    GIT_TAG        boost-1.76.0
)

FetchContent_GetProperties(boost_move)

if(NOT boost_move_POPULATED)
    message(STATUS "Fetch boost move")
    FetchContent_Populate(boost_move)
    include_directories(${boost_move_SOURCE_DIR}/include)
endif()
