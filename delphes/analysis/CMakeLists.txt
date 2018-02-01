include_directories(
  ${CMAKE_SOURCE_DIR}
  ${ROOT_INCLUDE_DIRS}
  ${DelphesExternals_INCLUDE_DIR} 
)

#file(GLOB sources basicTrackReconstructon.cpp)


add_executable(basicTrackReconstruction basicTrackReconstructon.cpp)
target_link_libraries(basicTrackReconstruction Delphes)


# install pcms if they are created
if (NOT ${ROOT_VERSION} VERSION_LESS "6.0.0")
  install(FILES
      ${PROJECT_BINARY_DIR}/classes/libClassesDict_rdict.pcm
      DESTINATION lib)
endif()
