set(DRIVER_NAME ssd1680)
add_library(${DRIVER_NAME} INTERFACE)

target_sources(ssd1680 INTERFACE
  ${CMAKE_CURRENT_LIST_DIR}/ssd1680_bindings.c
  ${CMAKE_CURRENT_LIST_DIR}/ssd1680_bindings.cpp
  ${CMAKE_CURRENT_LIST_DIR}/ssd1680.cpp
)

target_include_directories(ssd1680 INTERFACE ${CMAKE_CURRENT_LIST_DIR})

# Pull in pico libraries that we need
target_link_libraries(ssd1680 INTERFACE pico_stdlib hardware_pwm hardware_pio hardware_dma)

target_link_libraries(usermod INTERFACE ssd1680)
