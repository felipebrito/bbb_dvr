/*
 * Controle de 2 Reles via Serial - Arduino Uno
 * Comandos: 1on, 1off, 2on, 2off
 * 
 * Rele 1 conectado no pino 8
 * Rele 2 conectado no pino 10
 * 
 * NOTA: Logica normal (HIGH = ligado, LOW = desligado)
 */

#define RELAY1_PIN 8
#define RELAY2_PIN 10

// Estados dos reles
bool relay1State = false;
bool relay2State = false;

String inputString = "";

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  
  // Inicializa reles desligados (LOW = desligado)
  digitalWrite(RELAY1_PIN, LOW);
  digitalWrite(RELAY2_PIN, LOW);
  relay1State = false;
  relay2State = false;
  
  Serial.println("\n========================================");
  Serial.println("Arduino Uno - Controle de 2 Reles");
  Serial.println("========================================");
  Serial.println("Rele 1: Pino 8");
  Serial.println("Rele 2: Pino 10");
  Serial.println("========================================");
  Serial.println("\nComandos disponiveis:");
  Serial.println("  1on  - Liga rele 1");
  Serial.println("  1off - Desliga rele 1");
  Serial.println("  2on  - Liga rele 2");
  Serial.println("  2off - Desliga rele 2");
  Serial.println("========================================\n");
  
  inputString.reserve(10);
}

void loop() {
  if (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) {
        processCommand(inputString);
        inputString = "";
      }
    } else {
      inputString += inChar;
    }
  }
  
  delay(10);
}

void processCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();
  
  Serial.print("Comando recebido: ");
  Serial.println(cmd);
  
  // Logica normal: HIGH = ligado, LOW = desligado
  // Processa comando do rele 1
  if (cmd == "1on") {
    if (!relay1State) {
      digitalWrite(RELAY1_PIN, HIGH);  // HIGH = ligado
      relay1State = true;
      Serial.println(">>> Rele 1 LIGADO");
    } else {
      Serial.println(">>> Rele 1 ja estava LIGADO");
    }
  }
  else if (cmd == "1off") {
    if (relay1State) {
      digitalWrite(RELAY1_PIN, LOW);  // LOW = desligado
      relay1State = false;
      Serial.println(">>> Rele 1 DESLIGADO");
    } else {
      Serial.println(">>> Rele 1 ja estava DESLIGADO");
    }
  }
  // Processa comando do rele 2
  else if (cmd == "2on") {
    if (!relay2State) {
      digitalWrite(RELAY2_PIN, HIGH);  // HIGH = ligado
      relay2State = true;
      Serial.println(">>> Rele 2 LIGADO");
    } else {
      Serial.println(">>> Rele 2 ja estava LIGADO");
    }
  }
  else if (cmd == "2off") {
    if (relay2State) {
      digitalWrite(RELAY2_PIN, LOW);  // LOW = desligado
      relay2State = false;
      Serial.println(">>> Rele 2 DESLIGADO");
    } else {
      Serial.println(">>> Rele 2 ja estava DESLIGADO");
    }
  }
  else {
    Serial.print(">>> Comando invalido: ");
    Serial.println(cmd);
    Serial.println("Comandos validos: 1on, 1off, 2on, 2off");
  }
  
  Serial.println("---");
}

