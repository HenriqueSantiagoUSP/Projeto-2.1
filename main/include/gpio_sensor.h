#ifndef GPIO_SENSOR_H
#define GPIO_SENSOR_H

#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_err.h"

/**
 * @brief Callback chamado quando o sensor GPIO dispara.
 * @param ctx  Ponteiro de contexto definido pelo usuário (pode ser NULL).
 */
typedef void (*gpio_sensor_callback_t)(void *ctx);

/**
 * @brief Estrutura que encapsula um sensor baseado em interrupção GPIO.
 *
 * Usado como base para HCSR501, ReedSwitch, e qualquer sensor digital
 * que funcione por nível/borda GPIO.
 */
typedef struct {
    gpio_num_t              gpio_num;
    TaskHandle_t            task_handle;
    gpio_sensor_callback_t  callback;
    void                   *callback_ctx;
    TickType_t              debounce_ticks;
    TickType_t              last_trigger;
} gpio_sensor_t;

/**
 * @brief Inicializa um sensor GPIO genérico.
 *
 * Configura o pino, cria uma task interna para processar eventos e
 * registra o ISR handler.
 *
 * @note `gpio_install_isr_service()` deve ser chamado ANTES desta função.
 *
 * @param sensor         Ponteiro para a struct do sensor (deve ser persistente).
 * @param gpio_num       Número do pino GPIO.
 * @param intr_type      Tipo de interrupção (POSEDGE, NEGEDGE, ANYEDGE).
 * @param pull_up        Habilitar pull-up interno.
 * @param pull_down      Habilitar pull-down interno.
 * @param callback       Função chamada quando o sensor dispara.
 * @param callback_ctx   Contexto passado ao callback (pode ser NULL).
 * @param debounce_ms    Tempo mínimo entre triggers (0 para desabilitar debounce).
 * @param task_name      Nome da FreeRTOS task (para debug).
 * @return ESP_OK em caso de sucesso, ou código de erro.
 */
esp_err_t gpio_sensor_init(gpio_sensor_t *sensor,
                           gpio_num_t gpio_num,
                           gpio_int_type_t intr_type,
                           gpio_pullup_t pull_up,
                           gpio_pulldown_t pull_down,
                           gpio_sensor_callback_t callback,
                           void *callback_ctx,
                           uint32_t debounce_ms,
                           const char *task_name);

/**
 * @brief Deinicializa o sensor GPIO.
 *
 * Remove o ISR handler, deleta a task interna e reseta o pino.
 *
 * @param sensor  Ponteiro para a struct do sensor.
 */
void gpio_sensor_deinit(gpio_sensor_t *sensor);

#endif /* GPIO_SENSOR_H */
