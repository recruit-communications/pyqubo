include_directories(../include)

add_library(cpp_pyqubo STATIC
pybind_mapping.cpp
express.cpp
coeff.cpp
encoder.cpp
placeholderpoly.cpp
expanded.cpp
poly.cpp
)

set_target_properties(cpp_pyqubo PROPERTIES
    CXX_VISIBILITY_PRESET "hidden"
    INTERPROCEDURAL_OPTIMIZATION TRUE
    PREFIX "${PYTHON_MODULE_PREFIX}"
    SUFFIX "${PYTHON_MODULE_EXTENSION}"
)


target_link_libraries(cpp_pyqubo
    pybind11::module
)

add_custom_target(python
    DEPENDS cpp_pyqubo
)