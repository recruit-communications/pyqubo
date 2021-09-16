include(FetchContent)

FetchContent_Declare(
    boost_detail
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/detail
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

