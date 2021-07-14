if (PYQUBO_BUILD_SHARED_LIBS)
  pybind11_add_module(cpp_pyqubo SHARED
    ${PROJECT_SOURCE_DIR}/pybind_mapping.cpp
    ${PROJECT_SOURCE_DIR}/express.cpp
    ${PROJECT_SOURCE_DIR}/coeff.cpp
    ${PROJECT_SOURCE_DIR}/encoder.cpp
    ${PROJECT_SOURCE_DIR}/placeholderpoly.cpp
    ${PROJECT_SOURCE_DIR}/expanded.cpp
    ${PROJECT_SOURCE_DIR}/poly.cpp
  )
else()
  pybind11_add_module(cpp_pyqubo MODULE
    ${PROJECT_SOURCE_DIR}/pybind_mapping.cpp
    ${PROJECT_SOURCE_DIR}/express.cpp
    ${PROJECT_SOURCE_DIR}/coeff.cpp
    ${PROJECT_SOURCE_DIR}/encoder.cpp
    ${PROJECT_SOURCE_DIR}/placeholderpoly.cpp
    ${PROJECT_SOURCE_DIR}/expanded.cpp
    ${PROJECT_SOURCE_DIR}/poly.cpp
  )
endif()

set_target_properties(cpp_pyqubo PROPERTIES
    CXX_VISIBILITY_PRESET "hidden"
    INTERPROCEDURAL_OPTIMIZATION TRUE
    PREFIX "${PYTHON_MODULE_PREFIX}"
    SUFFIX "${PYTHON_MODULE_EXTENSION}"
)

if (PYQUBO_BUILD_SHARED_LIBS)
  add_library(cpp_pyqubo_body SHARED
    ${PROJECT_SOURCE_DIR}/src/express.cpp
    ${PROJECT_SOURCE_DIR}/src/coeff.cpp
    ${PROJECT_SOURCE_DIR}/src/encoder.cpp
    ${PROJECT_SOURCE_DIR}/src/placeholderpoly.cpp
    ${PROJECT_SOURCE_DIR}/src/expanded.cpp
    ${PROJECT_SOURCE_DIR}/src/poly.cpp
  )
else()
  add_library(cpp_pyqubo_body STATIC
    ${PROJECT_SOURCE_DIR}/src/express.cpp
    ${PROJECT_SOURCE_DIR}/src/coeff.cpp
    ${PROJECT_SOURCE_DIR}/src/encoder.cpp
    ${PROJECT_SOURCE_DIR}/src/placeholderpoly.cpp
    ${PROJECT_SOURCE_DIR}/src/expanded.cpp
    ${PROJECT_SOURCE_DIR}/src/poly.cpp
  )
endif()
target_include_directories(cpp_pyqubo PUBLIC ${PROJECT_SOURCE_DIR}/include)
