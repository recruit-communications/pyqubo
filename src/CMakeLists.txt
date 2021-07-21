add_library(cpp_pyqubo MODULE 
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
    VISIBLITY_INLINES_HIDDEN ON
    INTERPROCEDURAL_OPTIMIZATION TRUE
    POSITION_INDEPENDENT_CODE ON
    PREFIX "${PYTHON_MODULE_PREFIX}"
    SUFFIX "${PYTHON_MODULE_EXTENSION}"
)

target_link_libraries(cpp_pyqubo PRIVATE 
  pybind11::module
  pybind11::thin_lto
  cpp_pyqubo_header_only
  cpp_dimod
)

add_library(cpp_pyqubo_body SHARED
    express.cpp
    coeff.cpp
    encoder.cpp
    placeholderpoly.cpp
    expanded.cpp
    poly.cpp
)

target_link_libraries(cpp_pyqubo_body PRIVATE 
  pybind11::module
  pybind11::thin_lto
  cpp_pyqubo_header_only
  cpp_dimod
)

add_custom_target(python
    DEPENDS cpp_pyqubo
)
