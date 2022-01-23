/**
 * --------------------------------------------------------------------------------
  Sistema de controle para a fonte de indução
  Placa: v1.0
--------------------------------------------------------------------------------
  Autor: Matheus Vinícius Resende Nascimento
  Data: 13 de Julho de 2021
  Bolsista PIBIQ
--------------------------------------------------------------------------------
 * Definição dos Métodos */

#include "definicoes.h"
#include "driver/mcpwm.h"   // Inclui a biblioteca "Motor Control PWM" nativa do ESP32
#include "driver/adc.h"     // Inclui a biblioteca "Analog Digital Converter" nativa do ESP32
#include "esp_adc_cal.h"    // Inclui a biblioteca para auto calibração do ADC

/**
 * função para decodificar o comando recebido pela Serial.
 * Comandos:
 * 1 = Frequência
 * 2 = Duty Cycle
 * 3 = Corrente
 * 4 = Modo de Operação
 * 5 = Tempo de Operação
 * 6 = Ligar/Desligar a bobina
 */
static const char validCommands[] = "FDCMTE";

static const adc_channel_t canal = ADC_CHANNEL_0;     //GPIO36
static const adc_bits_width_t resolucao = ADC_WIDTH_BIT_12;

static const adc_atten_t atten = ADC_ATTEN_DB_0;
static const adc_unit_t unit = ADC_UNIT_1;

static esp_adc_cal_characteristics_t *adc_chars;

command instruction(char *mensagem) {
  int c;
  struct command out;
  char *token;
  char text[buf_len];
  float t;
  bool erro = false;
  
  memcpy(text,mensagem,buf_len);
  if(text[0] == 'C') {
    for(int i = 0; i < 6; i++) {
      if(text[1] == validCommands[i]) {
        out.select = i + 1;
      }
    }
    if(out.select == 0) {
      erro = true;
    } else {
      token = strtok(text, " ");
      token = strtok(NULL, " ");
      t = atof(token);
      out.value = t;
      out.ok = true;
      return out;
    }    
  }
  else {
    erro = true;
  }
  if(erro) {
    Serial.println("Comando inválido");
    out.ok = false;
    return out;
  }
} // end function instruction

// Função para definir no registrador o valor da fase entre os sinais de PWM
static void phaseControl(uint32_t phase) {
  REG_CLR_BIT(0x3FF5E01C, 0xFFFF0);
  REG_SET_BIT(0x3FF5E01C,(phase<<4));
} // end function phaseControl

//Função que configura o MCPWM operador A (Unidade, Timer, Porcentagem (ciclo de trabalho))
static void startPWM(int freq)
{
  //mcpwm_gpio_init(unidade PWM 0, saida A, porta GPIO)     => Instancia o MCPWM0A no pino GPIO_PWM0A_OUT declarado no começo do código
  mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM0A, GPIO_PWM0A_OUT);

  //mcpwm_gpio_init(unidade PWM 0, saida B, porta GPIO)     => Instancia o MCPWM1A no pino GPIO_PWM1A_OUT declarado no começo do código
  mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM1A, GPIO_PWM1A_OUT);

  mcpwm_config_t pwm_config;

  pwm_config.frequency = freq;                            //frequência do PWM
  pwm_config.cmpr_a = 0;                                 //Ciclo de trabalho (duty cycle) do PWMxA = 0
  pwm_config.cmpr_b = 0;                                  //Ciclo de trabalho (duty cycle) do PWMxb = 0
  pwm_config.counter_mode = MCPWM_UP_COUNTER;             //Para MCPWM assimetrico
  pwm_config.duty_mode = MCPWM_DUTY_MODE_0;               //Define ciclo de trabalho em nível alto
  
  //Inicia(Unidade 0, Timer 0, Config PWM)
  mcpwm_init(MCPWM_UNIT_0, MCPWM_TIMER_0, &pwm_config); 
  
  //Inicia(Unidade 0, Timer 1, Config PWM)
  mcpwm_init(MCPWM_UNIT_0, MCPWM_TIMER_1, &pwm_config);

  REG_WRITE(0x3FF5E00C, PWM_TIMER0_SYNC_REG);
  REG_WRITE(0x3FF5E01C, PWM_TIMER1_SYNC_REG);
  REG_WRITE(0x3FF5E034, PWM_TIMER_SYNCI_CFG_REG);
  
} // end function startPWM

// Função para definir o valor do duty cycle
static void setDuty(float v) {
    mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_A, v);
    mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_1, MCPWM_OPR_A, v); 
} // end function setDuty

// Função para definir o valor da frequência do PWM.
static void setFreq(uint32_t f) {
  mcpwm_set_frequency(MCPWM_UNIT_0, MCPWM_TIMER_0, f);
  mcpwm_set_frequency(MCPWM_UNIT_0, MCPWM_TIMER_1, f);
} // end function setFreq

// Adiciona uma mensagem na fila para ser enviada pela Serial
static void serialSend(char msg[30]) {
  
  if (xQueueSend(queue_2, (void *)&msg, 5) != pdTRUE) {
    Serial.println("Mensagem não enviada");
  }
} // end function serialSend

// Função para habilitar os gate Drivers
static void setEnable(int f) {
  if(f == 1) {
    digitalWrite(PIN_ENABLE, LOW);
    serialSend("Bobina ativa");
    powerOn = true;
    xTimerStart(readSensor, portMAX_DELAY);
  } else {
    digitalWrite(PIN_ENABLE, HIGH);
    serialSend("Bobina desativa");
    powerOn = false;
    xTimerStop(readSensor, portMAX_DELAY);
  }
} // end function setEnable

static void configADC() {
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_0);

  adc_chars = (esp_adc_cal_characteristics_t *)calloc(1, sizeof(esp_adc_cal_characteristics_t));
  esp_adc_cal_value_t val_type = esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_0, ADC_WIDTH_BIT_12, DEFAULT_VREF, adc_chars);
} // end function configADC
