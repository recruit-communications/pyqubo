include(FetchContent)

FetchContent_Declare(
    boost_integer
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/integer
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_MakeAvailable(boost_integer)
