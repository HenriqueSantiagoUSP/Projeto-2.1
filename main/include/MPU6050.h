#ifndef MPU6050_H
#define MPU6050_H

#include "driver/i2c_master.h"
#include "esp_err.h"
#include <stdint.h>

/** @brief Endereço I2C padrão do MPU6050 (AD0 = LOW). */
#define MPU6050_ADDR_DEFAULT  0x68

/** @brief Endereço I2C alternativo do MPU6050 (AD0 = HIGH). */
#define MPU6050_ADDR_ALT      0x69

/**
 * @brief Dados convertidos do acelerômetro e giroscópio.
 */
typedef struct {
    float ax, ay, az;  // aceleração em g
    float gx, gy, gz;  // velocidade angular em °/s
} mpu6050_data_t;

/**
 * @brief Handle do dispositivo MPU6050.
 *
 * Encapsula o handle I2C e as sensitividades configuradas.
 * Permite múltiplas instâncias no mesmo barramento ou em barramentos diferentes.
 */
typedef struct {
    i2c_master_dev_handle_t dev_handle;
    float accel_sensitivity;
    float gyro_sensitivity;
} mpu6050_t;

/**
 * @brief Inicializa o MPU6050 em um barramento I2C existente.
 *
 * @note O barramento I2C deve ser criado ANTES com `i2c_new_master_bus()`.
 *
 * @param dev           Ponteiro para a struct do device (deve ser persistente).
 * @param bus_handle    Handle do barramento I2C já inicializado.
 * @param addr          Endereço I2C (MPU6050_ADDR_DEFAULT ou MPU6050_ADDR_ALT).
 * @param scl_speed_hz  Velocidade do clock SCL (ex: 400000 para 400kHz).
 * @return ESP_OK ou código de erro.
 */
esp_err_t mpu6050_init(mpu6050_t *dev, i2c_master_bus_handle_t bus_handle,
                       uint8_t addr, uint32_t scl_speed_hz);

/**
 * @brief Acorda o MPU6050 (limpa o bit SLEEP no registrador PWR_MGMT_1).
 *
 * @param dev  Ponteiro para o device.
 * @return ESP_OK ou código de erro.
 */
esp_err_t mpu6050_wake(mpu6050_t *dev);

/**
 * @brief Lê os valores brutos (raw) do acelerômetro e giroscópio.
 *
 * @param dev  Ponteiro para o device.
 * @param ax,ay,az  Aceleração bruta (LSB).
 * @param gx,gy,gz  Velocidade angular bruta (LSB).
 * @return ESP_OK ou código de erro.
 */
esp_err_t mpu6050_read_raw(mpu6050_t *dev,
                           int16_t *ax, int16_t *ay, int16_t *az,
                           int16_t *gx, int16_t *gy, int16_t *gz);

/**
 * @brief Lê e converte os dados do MPU6050 para unidades físicas.
 *
 * @param dev   Ponteiro para o device.
 * @param data  Struct de saída com aceleração (g) e velocidade angular (°/s).
 * @return ESP_OK ou código de erro.
 */
esp_err_t mpu6050_read(mpu6050_t *dev, mpu6050_data_t *data);

/**
 * @brief Deinicializa o MPU6050, removendo-o do barramento I2C.
 *
 * @note Não libera o barramento I2C — isso é responsabilidade do chamador.
 *
 * @param dev  Ponteiro para o device.
 * @return ESP_OK ou código de erro.
 */
esp_err_t mpu6050_deinit(mpu6050_t *dev);

#endif /* MPU6050_H */