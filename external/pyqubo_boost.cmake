include(FetchContent)

set(PREFIX_BOOST_URL "https://github.com/boostorg") 
set(PREFIX_BOOST_TAG "boost-1.76.0")

FetchContent_Declare(
    boost_assert
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/assert
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_config
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/config
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_container
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/container
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_core
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/core
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_detail
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/detail
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_integer
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/integer
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_intrusive
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/intrusive
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_move
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/move
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_static_assert
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/static_assert
    GIT_TAG        ${PREFIX_BOOST_TAG}
)

FetchContent_Declare(
    boost_type_traits
    GIT_REPOSITORY ${PREFIX_BOOST_URL}/type_traits
    GIT_TAG        ${PREFIX_BOOST_TAG}
)
