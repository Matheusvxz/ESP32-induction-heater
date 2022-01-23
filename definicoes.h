/**
 * --------------------------------------------------------------------------------
  Sistema de controle para a fonte de indução
  Placa: v1.0
--------------------------------------------------------------------------------
  Autor: Matheus Vinícius Resende Nascimento
  Data: 13 de Julho de 2021
  Bolsista PIBIQ
--------------------------------------------------------------------------------
 * Definição dos parâmetros */

#define buf_len         30
#define DEFAULT_VREF    1072
#define NO_OF_SAMPLES   64

/* -----------------------------------------------------
 *  Definição dos pinos de saída do microcontrolador
 * ----------------------------------------------------- */
 
#define GPIO_PWM0A_OUT    12    //Declara GPIO 12 como PWM0A
#define GPIO_PWM1A_OUT    14    //Declara GPIO 14 como PWM1A
#define PIN_ENABLE        2     //Declara o Pino que ativa o Gate Driver

/* -----------------------------------------------------
 *             Definição dos Registradores
 * ----------------------------------------------------- */

  uint32_t PWM_TIMER0_SYNC_REG =      0b00000000000000000000000000000111;
  uint32_t PWM_TIMER1_SYNC_REG =      0b00000000000100000000000000000011;
  uint32_t PWM_TIMER_SYNCI_CFG_REG =  0b00000000000000000000000000001000;

 /* -----------------------------------------------------
 *                Definição das structs
 * ----------------------------------------------------- */

struct command {
  int select = 0;
  float value;
  bool ok = false;
};

/* -----------------------------------------------------
 *                Variáveis Globais
 * ----------------------------------------------------- */

static bool powerOn = false;

/* -----------------------------------------------------
 *                Definição dos handles
 * ----------------------------------------------------- */
static QueueHandle_t queue_1;
static QueueHandle_t queue_2;

static TaskHandle_t task_1 = NULL;
static TaskHandle_t task_2 = NULL;

static TimerHandle_t one_shot = NULL;
static TimerHandle_t readSensor = NULL;
