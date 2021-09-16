include(FetchContent)

FetchContent_Declare(
    boost_intrusive
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/intrusive
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

