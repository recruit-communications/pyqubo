include(FetchContent)

FetchContent_Declare(
    boost_config
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/config
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

