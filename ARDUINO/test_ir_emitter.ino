/*
 * Teste do Emissor IR
 * 
 * Este código testa o emissor IR enviando comandos manualmente
 * para verificar se está funcionando corretamente.
 * 
 * Hardware:
 * - Arduino Mega
 * - LED IR no pino 2 (com resistor 220Ω)
 * 
 * Uso:
 * 1. Carregue este código no Arduino
 * 2. Abra Serial Monitor (9600 baud)
 * 3. Digite: R, G, B ou W para testar cada cor
 */

#include <IRremote.h>

#define IR_SEND_PIN 2

// Códigos IR mapeados
#define IR_ADDRESS 0xEF00
#define IR_CODE_RED    0xF704EF00
#define IR_CODE_GREEN  0xF805EF00
#define IR_CODE_BLUE   0xF906EF00
#define IR_CODE_WHITE  0xF807EF00

String inputString = "";

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  // Inicializa emissor IR
  IrSender.begin(IR_SEND_PIN, ENABLE_LED_FEEDBACK);
  pinMode(IR_SEND_PIN, OUTPUT);
  
  Serial.println("\n========================================");
  Serial.println("TESTE EMISSOR IR");
  Serial.println("========================================");
  Serial.println("Pino: 2");
  Serial.println("========================================");
  Serial.println("\nDigite no Serial Monitor:");
  Serial.println("  R - Enviar comando VERMELHO");
  Serial.println("  G - Enviar comando VERDE");
  Serial.println("  B - Enviar comando AZUL");
  Serial.println("  W - Enviar comando BRANCO");
  Serial.println("  T - Teste continuo (envia todas as cores)");
  Serial.println("========================================\n");
  
  inputString.reserve(10);
}

void loop() {
  // Processa comandos serial
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) {
        inputString.trim();
        inputString.toUpperCase();
        
        if (inputString == "R") {
          sendIRCommand("VERMELHO", IR_CODE_RED, 0x4);
        }
        else if (inputString == "G") {
          sendIRCommand("VERDE", IR_CODE_GREEN, 0x5);
        }
        else if (inputString == "B") {
          sendIRCommand("AZUL", IR_CODE_BLUE, 0x6);
        }
        else if (inputString == "W") {
          sendIRCommand("BRANCO", IR_CODE_WHITE, 0x7);
        }
        else if (inputString == "T") {
          Serial.println("\n>>> Iniciando teste continuo...");
          for (int i = 0; i < 5; i++) {
            Serial.print("\n--- Ciclo ");
            Serial.print(i + 1);
            Serial.println(" ---");
            sendIRCommand("VERMELHO", IR_CODE_RED, 0x4);
            delay(2000);
            sendIRCommand("VERDE", IR_CODE_GREEN, 0x5);
            delay(2000);
            sendIRCommand("AZUL", IR_CODE_BLUE, 0x6);
            delay(2000);
            sendIRCommand("BRANCO", IR_CODE_WHITE, 0x7);
            delay(2000);
          }
          Serial.println("\n>>> Teste continuo concluido");
        }
        else {
          Serial.print(">>> Comando invalido: ");
          Serial.println(inputString);
        }
        
        inputString = "";
      }
    } else {
      inputString += inChar;
    }
  }
  
  delay(10);
}

void sendIRCommand(const char* colorName, uint32_t irCode, uint8_t command) {
  Serial.print("\n>>> Enviando: ");
  Serial.println(colorName);
  Serial.print("    Codigo completo: 0x");
  Serial.println(irCode, HEX);
  Serial.print("    Endereco: 0x");
  Serial.print(IR_ADDRESS, HEX);
  Serial.print(" | Comando: 0x");
  Serial.println(command, HEX);
  
  // Método 1: Envia código completo como raw (32 bits)
  Serial.println("    Metodo 1: Enviando codigo completo (raw)...");
  IrSender.sendNEC(irCode, 32);
  delay(100);
  
  // Método 2: Envia usando address + command
  Serial.println("    Metodo 2: Enviando address + command...");
  IrSender.sendNEC(IR_ADDRESS, command, 0);
  delay(100);
  
  // Método 3: Envia novamente para garantir
  Serial.println("    Metodo 3: Reenvio...");
  IrSender.sendNEC(IR_ADDRESS, command, 0);
  delay(100);
  
  Serial.println("    >>> Comando enviado (3 tentativas)\n");
}

