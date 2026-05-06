#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "driver/i2c_master.h"
#include "esp_log.h"
#include "led_strip.h"

#include "HCSR501.h"
#include "ReedSwitch.h"
#include "MPU6050.h"

#define PIR_GPIO            GPIO_NUM_4
#define REED_SWITCH_GPIO    GPIO_NUM_5
#define BLINK_GPIO          GPIO_NUM_48
#define BLINK_PERIOD_MS     500

// I2C
#define I2C_SDA             GPIO_NUM_8
#define I2C_SCL             GPIO_NUM_9
#define I2C_SPEED           400000  // 400kHz

static const char *TAG = "MAIN";
static hcsr501_t pir;
static reed_switch_t reed_switch;
static mpu6050_t mpu;
static led_strip_handle_t led_strip;

typedef struct {
    uint8_t r, g, b;
} led_event_t;

static QueueHandle_t led_queue;

static void configure_led(void)
{
    led_strip_config_t strip_config = {
        .strip_gpio_num = BLINK_GPIO,
        .max_leds = 1,
    };

    led_strip_rmt_config_t rmt_config = {
        .resolution_hz = 10 * 1000 * 1000, // 10 MHz
        .flags.with_dma = false,
    };

    ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &led_strip));
    led_strip_clear(led_strip);
}

/**
 * @brief Inicializa o barramento I2C master.
 *
 * Separado dos sensores para que múltiplos dispositivos
 * possam compartilhar o mesmo barramento.
 */
static i2c_master_bus_handle_t i2c_bus_init(void)
{
    i2c_master_bus_handle_t bus;

    i2c_master_bus_config_t bus_config = {
        .i2c_port            = I2C_NUM_0,
        .sda_io_num          = I2C_SDA,
        .scl_io_num          = I2C_SCL,
        .clk_source          = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt   = 7,
        .flags.enable_internal_pullup = true,
    };
    ESP_ERROR_CHECK(i2c_new_master_bus(&bus_config, &bus));

    ESP_LOGI(TAG, "barramento I2C inicializado (SDA=%d, SCL=%d)", I2C_SDA, I2C_SCL);
    return bus;
}

void led_task(void *pv) {
    led_event_t event;
    while (1) {
        if (xQueueReceive(led_queue, &event, portMAX_DELAY)) {
            led_strip_set_pixel(led_strip, 0, event.r, event.g, event.b);
            led_strip_refresh(led_strip);
            vTaskDelay(pdMS_TO_TICKS(BLINK_PERIOD_MS));
            led_strip_clear(led_strip);
        }
    }
}

// callbacks — recebem ctx (não usado aqui, mas disponível para extensão)
void on_movement(void *ctx) {
    (void)ctx;
    led_event_t event = {.r = 0, .g = 20, .b = 0};
    xQueueSend(led_queue, &event, 0);
    ESP_LOGI(TAG, "movimento detectado!");
}

void on_switch(void *ctx) {
    (void)ctx;
    led_event_t event = {.r = 20, .g = 0, .b = 0};
    xQueueSend(led_queue, &event, 0);
    ESP_LOGI(TAG, "switch acionado!");
}

void mpu_task(void *pv) {
    mpu6050_t *dev = (mpu6050_t *)pv;
    mpu6050_data_t data;

    // header CSV (prefixo CSV: para o script Python filtrar)
    printf("CSV:timestamp_ms,ax,ay,az,gx,gy,gz\n");

    TickType_t start = xTaskGetTickCount();

    while (1) {
        esp_err_t ret = mpu6050_read(dev, &data);
        if (ret == ESP_OK) {
            uint32_t elapsed_ms = (xTaskGetTickCount() - start) * portTICK_PERIOD_MS;
            printf("CSV:%lu,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n",
                   (unsigned long)elapsed_ms,
                   data.ax, data.ay, data.az,
                   data.gx, data.gy, data.gz);
        } else {
            ESP_LOGW("MPU", "falha ao ler MPU6050: %s", esp_err_to_name(ret));
        }
        vTaskDelay(pdMS_TO_TICKS(5));  // 200 Hz
        
    }
}

void app_main(void) {
    led_queue = xQueueCreate(5, sizeof(led_event_t));
    gpio_install_isr_service(0);
    configure_led();

    // I2C — barramento compartilhado
    i2c_master_bus_handle_t i2c_bus = i2c_bus_init();

    // MPU6050
    ESP_ERROR_CHECK(mpu6050_init(&mpu, i2c_bus, MPU6050_ADDR_DEFAULT, I2C_SPEED));
    ESP_ERROR_CHECK(mpu6050_wake(&mpu));

    // Tasks
    xTaskCreate(mpu_task, "mpu_task", 4096, (void *)&mpu, 5, NULL);
    xTaskCreate(led_task, "led_task", 2048, NULL, 5, NULL);

    // Sensores GPIO
    ESP_ERROR_CHECK(hcsr501_init(&pir, PIR_GPIO, on_movement, NULL));
    ESP_ERROR_CHECK(reed_switch_init(&reed_switch, REED_SWITCH_GPIO, on_switch, NULL));
}