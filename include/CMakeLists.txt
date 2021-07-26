add_library(cpp_pyqubo_header_only INTERFACE)

target_include_directories(cpp_pyqubo_header_only INTERFACE 
  ${CMAKE_CURRENT_SOURCE_DIR} 
)
target_link_libraries(cpp_pyqubo_header_only INTERFACE cpp_dimod)
