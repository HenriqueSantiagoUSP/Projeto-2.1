#include "gpio_sensor.h"
#include "esp_log.h"

static const char *TAG = "GPIO_SENSOR";

static void IRAM_ATTR gpio_sensor_isr_handler(void *arg) {
    gpio_sensor_t *sensor = (gpio_sensor_t *)arg;

    BaseType_t higher_priority_woken = pdFALSE;
    vTaskNotifyGiveFromISR(sensor->task_handle, &higher_priority_woken);
    portYIELD_FROM_ISR(higher_priority_woken);
}

static void gpio_sensor_task(void *arg) {
    gpio_sensor_t *sensor = (gpio_sensor_t *)arg;

    while (1) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        // debounce: ignora triggers muito próximos
        TickType_t now = xTaskGetTickCount();
        if ((now - sensor->last_trigger) >= sensor->debounce_ticks) {
            sensor->last_trigger = now;

            if (sensor->callback != NULL) {
                sensor->callback(sensor->callback_ctx);
            }
        }
    }
}

esp_err_t gpio_sensor_init(gpio_sensor_t *sensor,
                           gpio_num_t gpio_num,
                           gpio_int_type_t intr_type,
                           gpio_pullup_t pull_up,
                           gpio_pulldown_t pull_down,
                           gpio_sensor_callback_t callback,
                           void *callback_ctx,
                           uint32_t debounce_ms,
                           const char *task_name)
{
    if (sensor == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    sensor->gpio_num       = gpio_num;
    sensor->callback       = callback;
    sensor->callback_ctx   = callback_ctx;
    sensor->debounce_ticks = pdMS_TO_TICKS(debounce_ms);
    sensor->last_trigger   = 0;
    sensor->task_handle    = NULL;

    // configura o GPIO
    gpio_config_t config = {
        .pin_bit_mask = 1ULL << gpio_num,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = pull_up,
        .pull_down_en = pull_down,
        .intr_type    = intr_type,
    };
    esp_err_t ret = gpio_config(&config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "falha ao configurar GPIO %d: %s", gpio_num, esp_err_to_name(ret));
        return ret;
    }

    // cria a task interna
    BaseType_t task_ret = xTaskCreate(gpio_sensor_task, task_name, 2048,
                                      (void *)sensor, 5, &sensor->task_handle);
    if (task_ret != pdPASS) {
        ESP_LOGE(TAG, "falha ao criar task '%s'", task_name);
        return ESP_ERR_NO_MEM;
    }

    // registra o ISR handler
    ret = gpio_isr_handler_add(gpio_num, gpio_sensor_isr_handler, (void *)sensor);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "falha ao adicionar ISR no GPIO %d: %s", gpio_num, esp_err_to_name(ret));
        vTaskDelete(sensor->task_handle);
        sensor->task_handle = NULL;
        return ret;
    }

    ESP_LOGI(TAG, "'%s' inicializado no GPIO %d (debounce=%lums)",
             task_name, gpio_num, (unsigned long)debounce_ms);
    return ESP_OK;
}

void gpio_sensor_deinit(gpio_sensor_t *sensor) {
    if (sensor == NULL) return;

    gpio_isr_handler_remove(sensor->gpio_num);

    if (sensor->task_handle != NULL) {
        vTaskDelete(sensor->task_handle);
        sensor->task_handle = NULL;
    }

    gpio_reset_pin(sensor->gpio_num);

    ESP_LOGI(TAG, "sensor no GPIO %d deinicializado", sensor->gpio_num);
}
