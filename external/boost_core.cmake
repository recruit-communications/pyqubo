include(FetchContent)

FetchContent_Declare(
    boost_core
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/core
    GIT_TAG        ${PREFIX_BOOST_TAG}
)
