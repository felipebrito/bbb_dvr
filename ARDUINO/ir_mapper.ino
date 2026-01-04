/*
 * Mapeador de Teclas IR (Infravermelho)
 * 
 * Este código recebe sinais IR de um controle remoto e exibe
 * os códigos no Serial Monitor para mapeamento.
 * 
 * Hardware necessário:
 * - Receptor IR (ex: TSOP1738, VS1838B) conectado no pino 2
 * - Arduino Mega
 * - Biblioteca: IRremote (instalar via Library Manager)
 * 
 * Uso:
 * 1. Abra o Serial Monitor (9600 baud)
 * 2. Aponte o controle remoto para o receptor
 * 3. Pressione as teclas que deseja mapear
 * 4. Anote os códigos exibidos no Serial Monitor
 */

#include <IRremote.h>

// Pino do receptor IR
#define IR_RECEIVE_PIN 2

// Variáveis para debounce e contagem
unsigned long lastReceiveTime = 0;
unsigned long debounceDelay = 200; // 200ms entre leituras
int keyCount = 0;

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  // Inicializa o receptor IR
  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
  
  Serial.println("\n========================================");
  Serial.println("Mapeador de Teclas IR");
  Serial.println("========================================");
  Serial.println("Receptor IR: Pino 2");
  Serial.println("Placa: Arduino Mega");
  Serial.println("========================================");
  Serial.println("\nInstrucoes:");
  Serial.println("1. Aponte o controle remoto para o receptor");
  Serial.println("2. Pressione as teclas que deseja mapear");
  Serial.println("3. Anote os codigos exibidos abaixo");
  Serial.println("4. Cada tecla mostra: Protocolo, Codigo (hex), Codigo (dec)");
  Serial.println("\n========================================\n");
  Serial.println("Aguardando sinais IR...\n");
}

void loop() {
  // Verifica se há um sinal IR recebido
  if (IrReceiver.decode()) {
    unsigned long currentTime = millis();
    
    // Debounce: ignora sinais muito próximos
    if (currentTime - lastReceiveTime > debounceDelay) {
      keyCount++;
      
      Serial.println("----------------------------------------");
      Serial.print("Tecla #");
      Serial.println(keyCount);
      Serial.println("----------------------------------------");
      
      // Protocolo
      Serial.print("Protocolo: ");
      Serial.print(IrReceiver.decodedIRData.protocol);
      Serial.print(" (");
      // Tenta obter nome do protocolo
      Serial.print(getProtocolString(IrReceiver.decodedIRData.protocol));
      Serial.println(")");
      
      // Código completo em hexadecimal (raw data)
      Serial.print("Codigo Completo (HEX): 0x");
      Serial.println(IrReceiver.decodedIRData.decodedRawData, HEX);
      
      // Código completo em decimal
      Serial.print("Codigo Completo (DEC): ");
      Serial.println(IrReceiver.decodedIRData.decodedRawData, DEC);
      
      // Código de comando (para protocolos que suportam)
      if (IrReceiver.decodedIRData.protocol != UNKNOWN) {
        Serial.print("Comando: 0x");
        Serial.print(IrReceiver.decodedIRData.command, HEX);
        Serial.print(" (");
        Serial.print(IrReceiver.decodedIRData.command, DEC);
        Serial.println(")");
      }
      
      // Endereço (para protocolos que suportam)
      if (IrReceiver.decodedIRData.protocol == NEC || 
          IrReceiver.decodedIRData.protocol == SAMSUNG ||
          IrReceiver.decodedIRData.protocol == LG ||
          IrReceiver.decodedIRData.protocol == PANASONIC) {
        Serial.print("Endereco: 0x");
        Serial.print(IrReceiver.decodedIRData.address, HEX);
        Serial.print(" (");
        Serial.print(IrReceiver.decodedIRData.address, DEC);
        Serial.println(")");
      }
      
      // Número de bits
      Serial.print("Bits: ");
      Serial.println(IrReceiver.decodedIRData.numberOfBits);
      
      // Flags adicionais
      if (IrReceiver.decodedIRData.flags) {
        Serial.print("Flags: 0x");
        Serial.println(IrReceiver.decodedIRData.flags, HEX);
      }
      
      Serial.println("----------------------------------------\n");
      
      lastReceiveTime = currentTime;
    }
    
    // Prepara para receber o próximo sinal
    IrReceiver.resume();
  }
  
  delay(10);
}

