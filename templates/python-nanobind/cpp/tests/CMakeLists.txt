include(${PROJECT_SOURCE_DIR}/cmake/CPM.cmake)
CPMAddPackage("gh:catchorg/Catch2@3.16.1")
list(APPEND CMAKE_MODULE_PATH ${Catch2_SOURCE_DIR}/extras)
include(Catch)

# Every *.test.cpp in this directory is compiled into the test runner.
file(GLOB test_sources CONFIGURE_DEPENDS *.test.cpp)
add_executable(core_tests ${test_sources})
target_link_libraries(core_tests PRIVATE core project_warnings Catch2::Catch2WithMain)
catch_discover_tests(core_tests)
