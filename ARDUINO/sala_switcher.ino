/*
 * Controle de 4 Reles via Serial - Arduino Mega
 * Comandos: 1on, 1off, 2on, 2off, 3on, 3off, 4on, 4off
 * 
 * IMPORTANTE: Pinos 0 e 1 sao TX/RX - NAO USE!
 * Usando pinos 18, 19, 20 e 21 para os reles
 * 
 * NOTA: Este modulo de rele e ativo em LOW (LOW = ligado, HIGH = desligado)
 */

#define RELAY1_PIN 20
#define RELAY2_PIN 21
#define RELAY3_PIN 18
#define RELAY4_PIN 19

// Estados dos reles
bool relay1State = false;
bool relay2State = false;
bool relay3State = false;
bool relay4State = false;

String inputString = "";

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  pinMode(RELAY1_PIN, OUTPUT);
  pinMode(RELAY2_PIN, OUTPUT);
  pinMode(RELAY3_PIN, OUTPUT);
  pinMode(RELAY4_PIN, OUTPUT);
  
  // Inicializa reles desligados (HIGH = desligado para modulos ativos em LOW)
  digitalWrite(RELAY1_PIN, HIGH);
  digitalWrite(RELAY2_PIN, HIGH);
  digitalWrite(RELAY3_PIN, HIGH);
  digitalWrite(RELAY4_PIN, HIGH);
  relay1State = false;
  relay2State = false;
  relay3State = false;
  relay4State = false;
  
  Serial.println("\n========================================");
  Serial.println("Arduino Mega - Controle de 4 Reles");
  Serial.println("========================================");
  Serial.println("Rele 1: Pino 20");
  Serial.println("Rele 2: Pino 21");
  Serial.println("Rele 3: Pino 18");
  Serial.println("Rele 4: Pino 19");
  Serial.println("========================================");
  Serial.println("\nComandos disponiveis:");
  Serial.println("  1on  - Liga rele 1");
  Serial.println("  1off - Desliga rele 1");
  Serial.println("  2on  - Liga rele 2");
  Serial.println("  2off - Desliga rele 2");
  Serial.println("  3on  - Liga rele 3");
  Serial.println("  3off - Desliga rele 3");
  Serial.println("  4on  - Liga rele 4");
  Serial.println("  4off - Desliga rele 4");
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
  
  // Processa comando do rele 1
  // Modulo ativo em LOW: LOW = ligado, HIGH = desligado
  if (cmd == "1on") {
    if (!relay1State) {
      digitalWrite(RELAY1_PIN, LOW);  // LOW = ligado
      relay1State = true;
      Serial.println(">>> Rele 1 LIGADO");
    } else {
      Serial.println(">>> Rele 1 ja estava LIGADO");
    }
  }
  else if (cmd == "1off") {
    if (relay1State) {
      digitalWrite(RELAY1_PIN, HIGH);  // HIGH = desligado
      relay1State = false;
      Serial.println(">>> Rele 1 DESLIGADO");
    } else {
      Serial.println(">>> Rele 1 ja estava DESLIGADO");
    }
  }
  // Processa comando do rele 2
  else if (cmd == "2on") {
    if (!relay2State) {
      digitalWrite(RELAY2_PIN, LOW);  // LOW = ligado
      relay2State = true;
      Serial.println(">>> Rele 2 LIGADO");
    } else {
      Serial.println(">>> Rele 2 ja estava LIGADO");
    }
  }
  else if (cmd == "2off") {
    if (relay2State) {
      digitalWrite(RELAY2_PIN, HIGH);  // HIGH = desligado
      relay2State = false;
      Serial.println(">>> Rele 2 DESLIGADO");
    } else {
      Serial.println(">>> Rele 2 ja estava DESLIGADO");
    }
  }
  // Processa comando do rele 3
  else if (cmd == "3on") {
    if (!relay3State) {
      digitalWrite(RELAY3_PIN, LOW);  // LOW = ligado
      relay3State = true;
      Serial.println(">>> Rele 3 LIGADO");
    } else {
      Serial.println(">>> Rele 3 ja estava LIGADO");
    }
  }
  else if (cmd == "3off") {
    if (relay3State) {
      digitalWrite(RELAY3_PIN, HIGH);  // HIGH = desligado
      relay3State = false;
      Serial.println(">>> Rele 3 DESLIGADO");
    } else {
      Serial.println(">>> Rele 3 ja estava DESLIGADO");
    }
  }
  // Processa comando do rele 4
  else if (cmd == "4on") {
    if (!relay4State) {
      digitalWrite(RELAY4_PIN, LOW);  // LOW = ligado
      relay4State = true;
      Serial.println(">>> Rele 4 LIGADO");
    } else {
      Serial.println(">>> Rele 4 ja estava LIGADO");
    }
  }
  else if (cmd == "4off") {
    if (relay4State) {
      digitalWrite(RELAY4_PIN, HIGH);  // HIGH = desligado
      relay4State = false;
      Serial.println(">>> Rele 4 DESLIGADO");
    } else {
      Serial.println(">>> Rele 4 ja estava DESLIGADO");
    }
  }
  else {
    Serial.print(">>> Comando invalido: ");
    Serial.println(cmd);
    Serial.println("Comandos validos: 1on, 1off, 2on, 2off, 3on, 3off, 4on, 4off");
  }
  
  Serial.println("---");
}

