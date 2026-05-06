#include "MPU6050.h"
#include "esp_log.h"

static const char *TAG = "MPU6050";

// sensitividades padrão (full-scale range default: ±2g, ±250°/s)
#define ACCEL_SENSITIVITY_DEFAULT   16384.0f  // LSB/g
#define GYRO_SENSITIVITY_DEFAULT    131.0f    // LSB/(°/s)

// registradores
#define REG_PWR_MGMT_1   0x6B
#define REG_ACCEL_XOUT_H 0x3B

esp_err_t mpu6050_init(mpu6050_t *dev, i2c_master_bus_handle_t bus_handle,
                       uint8_t addr, uint32_t scl_speed_hz)
{
    if (dev == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    dev->accel_sensitivity = ACCEL_SENSITIVITY_DEFAULT;
    dev->gyro_sensitivity  = GYRO_SENSITIVITY_DEFAULT;

    i2c_device_config_t dev_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address  = addr,
        .scl_speed_hz    = scl_speed_hz,
    };

    esp_err_t ret = i2c_master_bus_add_device(bus_handle, &dev_config, &dev->dev_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "falha ao adicionar device 0x%02X: %s", addr, esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(TAG, "dispositivo 0x%02X adicionado ao barramento I2C", addr);
    return ESP_OK;
}

esp_err_t mpu6050_wake(mpu6050_t *dev)
{
    if (dev == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    // registrador PWR_MGMT_1 com valor 0x00 = acorda o sensor
    uint8_t data[] = {REG_PWR_MGMT_1, 0x00};
    esp_err_t ret = i2c_master_transmit(dev->dev_handle, data, sizeof(data), 100);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "falha ao acordar MPU6050: %s", esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(TAG, "MPU6050 acordado");
    return ESP_OK;
}

// registradores a partir de 0x3B:
// 0x3B-0x3C: ACCEL_X
// 0x3D-0x3E: ACCEL_Y
// 0x3F-0x40: ACCEL_Z
// 0x41-0x42: TEMP
// 0x43-0x44: GYRO_X
// 0x45-0x46: GYRO_Y
// 0x47-0x48: GYRO_Z

esp_err_t mpu6050_read_raw(mpu6050_t *dev,
                           int16_t *ax, int16_t *ay, int16_t *az,
                           int16_t *gx, int16_t *gy, int16_t *gz)
{
    if (dev == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    uint8_t reg = REG_ACCEL_XOUT_H;
    uint8_t buffer[14];

    // escreve o registrador de início, depois lê 14 bytes
    esp_err_t ret = i2c_master_transmit_receive(dev->dev_handle, &reg, 1, buffer, 14, 100);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "falha ao ler dados: %s", esp_err_to_name(ret));
        return ret;
    }

    // cada valor é 16 bits, big-endian (byte alto primeiro)
    *ax = (int16_t)((uint16_t)buffer[0]  << 8 | buffer[1]);
    *ay = (int16_t)((uint16_t)buffer[2]  << 8 | buffer[3]);
    *az = (int16_t)((uint16_t)buffer[4]  << 8 | buffer[5]);
    // buffer[6] e [7] são temperatura, pulamos
    *gx = (int16_t)((uint16_t)buffer[8]  << 8 | buffer[9]);
    *gy = (int16_t)((uint16_t)buffer[10] << 8 | buffer[11]);
    *gz = (int16_t)((uint16_t)buffer[12] << 8 | buffer[13]);

    return ESP_OK;
}

esp_err_t mpu6050_read(mpu6050_t *dev, mpu6050_data_t *data)
{
    if (dev == NULL || data == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    int16_t ax, ay, az, gx, gy, gz;
    esp_err_t ret = mpu6050_read_raw(dev, &ax, &ay, &az, &gx, &gy, &gz);
    if (ret != ESP_OK) {
        return ret;
    }

    data->ax = ax / dev->accel_sensitivity;
    data->ay = ay / dev->accel_sensitivity;
    data->az = az / dev->accel_sensitivity;
    data->gx = gx / dev->gyro_sensitivity;
    data->gy = gy / dev->gyro_sensitivity;
    data->gz = gz / dev->gyro_sensitivity;

    return ESP_OK;
}

esp_err_t mpu6050_deinit(mpu6050_t *dev)
{
    if (dev == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    esp_err_t ret = i2c_master_bus_rm_device(dev->dev_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "falha ao remover device: %s", esp_err_to_name(ret));
        return ret;
    }

    dev->dev_handle = NULL;
    ESP_LOGI(TAG, "MPU6050 deinicializado");
    return ESP_OK;
}