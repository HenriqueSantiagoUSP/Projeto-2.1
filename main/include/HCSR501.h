#ifndef HCSR501_H
#define HCSR501_H

#include "gpio_sensor.h"

/**
 * @brief Wrapper para o sensor de presença HCSR501.
 *
 * Internamente usa o módulo genérico gpio_sensor.
 * O HCSR501 tem debounce por hardware (retrigger time),
 * então o debounce por software é mínimo (50ms de segurança).
 */
typedef gpio_sensor_t       hcsr501_t;
typedef gpio_sensor_callback_t  hcsr501_callback_t;

/**
 * @brief Inicializa o sensor de presença HCSR501.
 *
 * @param sensor    Ponteiro para a struct (deve ser persistente).
 * @param gpio_num  Pino GPIO conectado ao OUT do HCSR501.
 * @param callback  Função chamada quando detectar presença.
 * @param ctx       Contexto passado ao callback (pode ser NULL).
 * @return ESP_OK ou código de erro.
 */
static inline esp_err_t hcsr501_init(hcsr501_t *sensor, gpio_num_t gpio_num,
                                     hcsr501_callback_t callback, void *ctx)
{
    return gpio_sensor_init(sensor, gpio_num,
                            GPIO_INTR_POSEDGE,
                            GPIO_PULLUP_DISABLE,
                            GPIO_PULLDOWN_ENABLE,
                            callback, ctx,
                            50,  // debounce 50ms (HCSR501 já tem retrigger interno)
                            "pir_task");
}

/**
 * @brief Deinicializa o sensor HCSR501.
 */
static inline void hcsr501_deinit(hcsr501_t *sensor) {
    gpio_sensor_deinit(sensor);
}

#endif /* HCSR501_H */