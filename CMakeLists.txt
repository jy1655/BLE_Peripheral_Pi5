cmake_minimum_required(VERSION 3.16)
project(BLE_Peripheral_Pi5)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)
pkg_check_modules(DBUS REQUIRED dbus-1)
pkg_check_modules(GIO REQUIRED gio-2.0)
pkg_check_modules(GLIB REQUIRED glib-2.0)

# Include directories
include_directories(include)
include_directories(${DBUS_INCLUDE_DIRS})
include_directories(${GIO_INCLUDE_DIRS})
include_directories(${GLIB_INCLUDE_DIRS})

# Source files
set(SOURCES
    src/main.cpp
    src/BLEPeripheral.cpp
    src/BLEService.cpp
    src/BLECharacteristic.cpp
    src/BLEAdvertisement.cpp
)

# Create executable
add_executable(${PROJECT_NAME} ${SOURCES})

# Link libraries
target_link_libraries(${PROJECT_NAME} 
    ${DBUS_LIBRARIES}
    ${GIO_LIBRARIES}
    ${GLIB_LIBRARIES}
)

# Compiler flags
target_compile_options(${PROJECT_NAME} PRIVATE
    ${DBUS_CFLAGS_OTHER}
    ${GIO_CFLAGS_OTHER}
    ${GLIB_CFLAGS_OTHER}
)