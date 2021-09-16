include(FetchContent)

FetchContent_Declare(
    boost_assert
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/assert
    GIT_TAG        ${PREFIX_BOOST_TAG}
)
