include(FetchContent)

FetchContent_Declare(
    boost_type_traits
    GIT_REPOSITORY https://github.com/boostorg/type_traits
    GIT_TAG        boost-1.76.0
)

FetchContent_MakeAvailable(boost_type_traits)
