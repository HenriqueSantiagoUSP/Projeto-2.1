#ifndef REEDSWITCH_H
#define REEDSWITCH_H

#include "gpio_sensor.h"

/**
 * @brief Wrapper para o sensor Reed Switch.
 *
 * Internamente usa o módulo genérico gpio_sensor.
 * Reed switches têm bounce mecânico, então o debounce
 * por software é essencial (200ms padrão).
 */
typedef gpio_sensor_t          reed_switch_t;
typedef gpio_sensor_callback_t reed_switch_callback_t;

/**
 * @brief Inicializa o sensor Reed Switch.
 *
 * @param sensor    Ponteiro para a struct (deve ser persistente).
 * @param gpio_num  Pino GPIO conectado ao Reed Switch.
 * @param callback  Função chamada quando o switch é acionado.
 * @param ctx       Contexto passado ao callback (pode ser NULL).
 * @return ESP_OK ou código de erro.
 */
static inline esp_err_t reed_switch_init(reed_switch_t *sensor, gpio_num_t gpio_num,
                                         reed_switch_callback_t callback, void *ctx)
{
    return gpio_sensor_init(sensor, gpio_num,
                            GPIO_INTR_POSEDGE,
                            GPIO_PULLUP_DISABLE,
                            GPIO_PULLDOWN_ENABLE,
                            callback, ctx,
                            200,  // debounce 200ms — essencial para reed switch
                            "reed_task");
}

/**
 * @brief Deinicializa o sensor Reed Switch.
 */
static inline void reed_switch_deinit(reed_switch_t *sensor) {
    gpio_sensor_deinit(sensor);
}

#endif /* REEDSWITCH_H */