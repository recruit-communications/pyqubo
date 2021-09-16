include(FetchContent)

FetchContent_Declare(
    boost_container
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/container
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

