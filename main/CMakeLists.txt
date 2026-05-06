idf_component_register(
    SRCS "main.c" "gpio_sensor.c" "MPU6050.c"
    INCLUDE_DIRS "." "include/"
    REQUIRES led_strip esp_driver_gpio esp_driver_i2c
)