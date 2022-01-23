/**
 * --------------------------------------------------------------------------------
  Sistema de controle para a fonte de indução
  Placa: v1.0
--------------------------------------------------------------------------------
  Autor: Matheus Vinícius Resende Nascimento
  Data: 13 de Julho de 2021
  Bolsista PIBIQ
--------------------------------------------------------------------------------
 * Programação utilizando RTOS */

#include "metodos.h"


// Usando apenas um núcleo
#if CONFIG_FREERTOS_UNICORE
  static const BaseType_t app_cpu = 0;
#else
  static const BaseType_t app_cpu = 1;
#endif

// Configuração
static const uint8_t msg_queue_len = 5;



// Variáveis Globais
static bool msg_flag = false;
static uint8_t operationMode = 0;




//*************************************************************
// Tasks

/** Task 1
 *  - Recebe e envia as informações através da comunicação Serial
 */
void taskRWSerial(void *parameter) {
  char c;
  char buf[buf_len];
  char msg[buf_len];
  char *msg_queue;
  struct command j;
  uint8_t idx = 0;
  bool tag = false;

  memset(buf, 0, buf_len);
  memset(msg, 0, buf_len);
  
  while(1) {
    // Ler os caracteres da Serial
    if(Serial.available() > 0) {
      c = Serial.read();
      tag = true;
      
      // Salva o caractere recebido se não encher o buffer
      if(idx < buf_len - 1) {
        buf[idx] = c;
        idx++;
      }
    } else {
        if (tag) {
        memcpy(msg, buf, idx);          // Copia a mensagem do buffer para msg  | mgs <= buf
        msg_flag = true;                // Ativa a flag (msg_flag) indicando que foi lida uma string da Serial
        memset(buf, 0, buf_len);
        idx = 0;
        tag = false;
        }
    }

    if(msg_flag) {
      j = instruction(msg);
      memset(msg, 0, buf_len);
      if(j.ok) {
          if (xQueueSend(queue_1, (void *)&j, 5) != pdTRUE) {
              Serial.println("Fila 1 lotada");
          } else {
              //Serial.println("OK");
          }
      }
      msg_flag = false;
    }
    
    // Printa os valores recebidos da fila 2
    if (xQueueReceive(queue_2, (void *)&msg_queue, 5) == pdTRUE) {
      Serial.println(msg_queue);
      //Serial.println("---------------");
    } // end if
      
  } //end while
} // end task

/** Task B
 *  - Executa as funções recebidas da Task RWSerial.
 */
void taskControl(void *parameter) {
  struct command action;
  while(1) {
    
    if (xQueueReceive(queue_1, (void *)&action, 5) == pdTRUE) {
      switch(action.select) {
      case(1): {
        setFreq(uint32_t(action.value));
        serialSend("Frequencia alterada");
        phaseControl(500000/action.value);
        break;
      }
      case(2): {
        setDuty(action.value);
        serialSend("Duty alterado");
        break;
      }
      case(3): {
        //setCurrent(action.value);
        serialSend("Corrente alterada");
        break;
      }
      case(4): {
        operationMode = int(action.value);
        serialSend("Modo alterado");
        break;
      }
      case(5): {
        xTimerChangePeriod(one_shot, (int(action.value) / portTICK_PERIOD_MS), 100);
        serialSend("Tempo de operação alterado");
        break;
      }
      case(6): {
        switch(operationMode) {
          case(1): {  // Modo Duty Cycle Constante
            setEnable(int(action.value));
            break;
          }
          case(2): {  // Modo Corrente Constante
              
            break;
          }
          case(3): {  // Modo Duty Cycle Constante e tempo de soldagem
            setEnable(1);
            xTimerStart(one_shot, portMAX_DELAY);
            break;
          }
          case(4): {  // Modo Corrente Constante e tempo de soldagem

            break;
          }
        } // end switch
        break;
      }
    } // end switch
    } //end if
  } // end while
}

//*************************************************************
// Timers

/** Software Timer 1
 *  - Executa as funções determinadas pela task Control
 */
void timerCallback(TimerHandle_t xTimer) {
  if(powerOn) {
    setEnable(0);
  }
}

/** Software Timer 2
 *  - Faz a leitura da corrente na bobina quando o processo de solda está ligado
 */
 void currentRead(TimerHandle_t xTimer) {
  uint32_t adc_reading = 0;
  char *enviar;
  for (int i = 0; i < NO_OF_SAMPLES; i++) {
    adc_reading += adc1_get_raw(ADC1_CHANNEL_0);
  }
  adc_reading /= NO_OF_SAMPLES;
  //Convert adc_reading to voltage in mV
  int voltage = esp_adc_cal_raw_to_voltage(adc_reading, adc_chars);
  enviar = (char*)malloc(20 * sizeof(char));
  int n = sprintf(enviar, "Recv C%u", voltage);
  serialSend(enviar);
 }

void setup() {

  // Inicia a Serial
  Serial.begin(115200);
  Serial.setTimeout(1);

  pinMode(PIN_ENABLE, OUTPUT);
  digitalWrite(PIN_ENABLE, HIGH);

  configADC();   // Configura o ADC

  vTaskDelay(2000 / portTICK_PERIOD_MS);
  Serial.println();
  Serial.println("---Interface de controle---");

// Inicia o PWM
  startPWM(10000);

  setFreq(100000);
  phaseControl(500000/100000);
  setDuty(48);
  
  
// -----------------------------------------------------------
//                      Criando as filas
// -----------------------------------------------------------
  queue_1 = xQueueCreate(msg_queue_len, sizeof(struct command));
  queue_2 = xQueueCreate(msg_queue_len, buf_len);


// -----------------------------------------------------------
//                      Criando os timers
// -----------------------------------------------------------
  while(one_shot == NULL) {
    one_shot = xTimerCreate(  "Timer de disparo",
                              2000 / portTICK_PERIOD_MS,
                              pdFALSE,
                              (void *)0,
                              timerCallback);
  }
  while(readSensor == NULL) {
    readSensor = xTimerCreate(  "Timer para ler Corrente",
                              100 / portTICK_PERIOD_MS,
                              pdTRUE,
                              (void *)1,
                              currentRead);
  }


// -----------------------------------------------------------
//                      Criando as tasks
// -----------------------------------------------------------  
  xTaskCreatePinnedToCore(  taskRWSerial,
                            "Le/escreve na Serial",
                            1500,
                            NULL,
                            1,
                            &task_1,
                            app_cpu);

  xTaskCreatePinnedToCore(  taskControl,
                            "Altera o PWM",
                            1024,
                            NULL,
                            1,
                            &task_2,
                            app_cpu);
  vTaskDelete(NULL);
}

void loop() {
  // put your main code here, to run repeatedly:

}
