include(FetchContent)

FetchContent_Declare(
    boost_container_hash
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/container_hash
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

