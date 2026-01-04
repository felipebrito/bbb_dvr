/*
 * Controlador de Fita LED IR + Fechadura Magnética
 * 
 * Este código controla uma fita LED via IR e uma fechadura magnética.
 * 
 * Funcionamento:
 * - Alterna aleatoriamente entre cores R, G, B, W na fita LED
 * - Cada cor dura entre 15 e 30 segundos (aleatório)
 * - As cores determinam quando a porta PODE ser liberada (apenas quando verde)
 * - Chave micro no pino 3: quando pressionada E cor verde, libera a porta (relé pino 8)
 * - Chave micro no pino 4: quando pressionada, ativa relé no pino 10 por tempo definido
 * 
 * Hardware:
 * - Arduino Mega
 * - Emissor IR no pino 13
 * - Relé fechadura (pino 8): LOW = porta aberta, HIGH = porta fechada
 * - Relé sirene/auxiliar (pino 10): ativado pela chave micro do pino 4
 * - Chave micro liberar porta no pino 3 (com pull-up interno)
 * - Chave micro ativar sirene no pino 4 (com pull-up interno)
 * 
 * Comandos Serial:
 * - sirene:XXXX     - Define duração da sirene em ms (ex: sirene:5000)
 * - cores:MIN-MAX   - Define duração das cores em segundos (ex: cores:15-30)
 * 
 * Códigos IR mapeados (Protocolo NEC):
 * - R (Vermelho):  Comando 0x4, Endereço 0xEF00, Código: 0xF704EF00
 * - G (Verde):     Comando 0x5, Endereço 0xEF00, Código: 0xF805EF00
 * - B (Azul):      Comando 0x6, Endereço 0xEF00, Código: 0xF906EF00
 * - W (Branco):    Comando 0x7, Endereço 0xEF00, Código: 0xF807EF00
 */

#include <IRremote.h>

// Pinagens
#define IR_SEND_PIN 13          // Emissor IR
#define RELAY_LOCK_PIN 10       // Relé da fechadura magnética
#define RELAY_AUX_PIN 8         // Relé auxiliar/sirene (ativado pela chave)
#define SWITCH_LOCK_PIN 3       // Chave micro para liberar porta (com pull-up interno)
#define SWITCH_SIRENE_PIN 4     // Chave micro para ativar sirene (com pull-up interno)

// Códigos IR para as cores (Protocolo NEC)
#define IR_ADDRESS 0xEF00
#define IR_CODE_RED    0xF704EF00
#define IR_CODE_GREEN  0xF805EF00
#define IR_CODE_BLUE   0xF906EF00
#define IR_CODE_WHITE  0xF807EF00

// Configurações de tempo (valores padrão)
unsigned long MIN_COLOR_DURATION = 15000;  // 15 segundos (em ms) - configurável via serial
unsigned long MAX_COLOR_DURATION = 30000;  // 30 segundos (em ms) - configurável via serial
unsigned long RELAY_AUX_DURATION = 2000;   // 2 segundos que o relé auxiliar fica ativo - configurável via serial

// Estados
enum Color {
  RED,
  GREEN,
  BLUE,
  WHITE
};

Color currentColor = RED;
unsigned long colorStartTime = 0;
unsigned long colorDuration = 0;
unsigned long relayAuxStartTime = 0;
bool relayAuxActive = false;
// Estados das chaves
bool lastSwitchLockState = HIGH;
bool currentSwitchLockState = HIGH;
bool lastSwitchSireneState = HIGH;
bool currentSwitchSireneState = HIGH;

// Buffer para comandos serial
String inputString = "";

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  // Configura pinos
  pinMode(RELAY_LOCK_PIN, OUTPUT);
  pinMode(RELAY_AUX_PIN, OUTPUT);
  pinMode(SWITCH_LOCK_PIN, INPUT_PULLUP);
  pinMode(SWITCH_SIRENE_PIN, INPUT_PULLUP);
  
  // Inicializa relés (LOW = fechadura fechada, HIGH = fechadura aberta) - INVERTIDO
  digitalWrite(RELAY_LOCK_PIN, LOW);   // Porta fechada inicialmente
  digitalWrite(RELAY_AUX_PIN, LOW);    // Relé auxiliar desligado
  
  // Inicializa emissor IR
  IrSender.begin(IR_SEND_PIN, ENABLE_LED_FEEDBACK);
  
  // Testa se o pino está configurado corretamente
  pinMode(IR_SEND_PIN, OUTPUT);
  Serial.print(">>> Emissor IR inicializado no pino ");
  Serial.println(IR_SEND_PIN);
  
  // Inicializa buffer serial
  inputString.reserve(50);
  
  // Inicializa estados das chaves
  currentSwitchLockState = digitalRead(SWITCH_LOCK_PIN);
  lastSwitchLockState = currentSwitchLockState;
  currentSwitchSireneState = digitalRead(SWITCH_SIRENE_PIN);
  lastSwitchSireneState = currentSwitchSireneState;
  
  // Inicializa gerador de números aleatórios
  randomSeed(analogRead(0));
  
  // Seleciona cor inicial aleatória
  selectRandomColor();
  
  Serial.println("\n========================================");
  Serial.println("Controlador LED + Fechadura");
  Serial.println("========================================");
  Serial.println("Emissor IR: Pino 13");
  Serial.println("Chave Liberar Porta: Pino 3");
  Serial.println("Rele Fechadura: Pino 10");
  Serial.println("Chave Ativar Sirene: Pino 4");
  Serial.println("Rele Sirene: Pino 8");
  Serial.println("========================================");
  Serial.println("\nComandos disponiveis via Serial:");
  Serial.println("  sirene:XXXX     - Define duracao da sirene em ms");
  Serial.println("                   Exemplo: sirene:5000 (5 segundos)");
  Serial.println("  cores:MIN-MAX   - Define duracao das cores em segundos");
  Serial.println("                   Exemplo: cores:15-30");
  Serial.println("========================================");
  Serial.print("\nConfiguracoes atuais:\n");
  Serial.print("  Duracao cores: ");
  Serial.print(MIN_COLOR_DURATION / 1000);
  Serial.print("-");
  Serial.print(MAX_COLOR_DURATION / 1000);
  Serial.println(" segundos");
  Serial.print("  Duracao sirene: ");
  Serial.print(RELAY_AUX_DURATION);
  Serial.println(" ms");
  
  // Mostra pinout
  printPinout();
  
  Serial.println("Iniciando sequencia de cores...\n");
  
  // Inicializa porta fechada FORÇADAMENTE (LOW = fechada)
  digitalWrite(RELAY_LOCK_PIN, LOW);
  delay(10);  // Pequeno delay para garantir
  digitalWrite(RELAY_LOCK_PIN, LOW);  // Força novamente
  Serial.println(">>> Porta inicializada FECHADA");
  
  // Envia primeira cor
  sendColorCommand(currentColor);
  
  // Informa se a cor permite liberar porta
  if (currentColor == GREEN) {
    Serial.println(">>> Cor VERDE: Porta pode ser liberada ao pressionar chave");
  } else {
    Serial.print(">>> Cor ");
    Serial.print(getColorName(currentColor));
    Serial.println(": Porta NAO pode ser liberada");
  }
}

void loop() {
  unsigned long currentTime = millis();
  
  // Processa comandos serial
  processSerialCommands();
  
  // ========================================
  // SIRENE - SÓ FUNCIONA QUANDO COR É VERDE
  // ========================================
  // Verifica chave da sirene (pino 4) - SÓ funciona quando cor é verde
  currentSwitchSireneState = digitalRead(SWITCH_SIRENE_PIN);
  
  if (currentColor == GREEN) {
    // Só processa chave da sirene quando cor É verde
    if (lastSwitchSireneState == HIGH && currentSwitchSireneState == LOW) {
      // Chave foi pressionada E cor é verde: ativa sirene
      activateRelayAux();
      Serial.println(">>> SIRENE ATIVADA (chave pressionada + cor verde)");
    }
    lastSwitchSireneState = currentSwitchSireneState;
  } else {
    // Cor não é verde: não processa chave da sirene
    lastSwitchSireneState = currentSwitchSireneState;  // Atualiza estado mas não processa
  }
  
  // Verifica se o relé auxiliar precisa ser desativado (sempre verifica, mesmo se não for verde)
  if (relayAuxActive && (currentTime - relayAuxStartTime >= RELAY_AUX_DURATION)) {
    deactivateRelayAux();
  }
  
  // ========================================
  // CONTROLE DE CORES
  // ========================================
  // Verifica se é hora de trocar de cor
  if (currentTime - colorStartTime >= colorDuration) {
    Color previousColor = currentColor;
    selectRandomColor();
    sendColorCommand(currentColor);
    
    // Quando muda de cor, SEMPRE fecha porta FORÇADAMENTE (LOW = fechada)
    digitalWrite(RELAY_LOCK_PIN, LOW);  // Porta fechada
    
    if (currentColor == GREEN) {
      Serial.println(">>> Cor VERDE: Porta pode ser liberada ao pressionar chave");
    } else {
      Serial.print(">>> Cor ");
      Serial.print(getColorName(currentColor));
      Serial.println(": Porta NAO pode ser liberada - FORCADA FECHADA");
      // Força porta fechada novamente para garantir
      digitalWrite(RELAY_LOCK_PIN, LOW);
    }
  }
  
  // ========================================
  // PORTA - SÓ FUNCIONA QUANDO COR É VERDE
  // ========================================
  // Verifica chave de liberação da porta (pino 3)
  currentSwitchLockState = digitalRead(SWITCH_LOCK_PIN);
  
  // REGRA PRINCIPAL: Se cor NÃO é verde, porta SEMPRE fechada (LOW = fechada)
  if (currentColor != GREEN) {
    // Força porta fechada independente do estado da chave
    digitalWrite(RELAY_LOCK_PIN, LOW);  // LOW = porta fechada (invertido)
    // Não permite nenhuma ação quando não é verde
    lastSwitchLockState = currentSwitchLockState;  // Atualiza estado mas não processa
  } else {
    // Só processa chave quando cor É verde
    // Detecta quando a chave é pressionada (transição de HIGH para LOW)
    if (lastSwitchLockState == HIGH && currentSwitchLockState == LOW) {
      // Chave foi pressionada E cor é verde: libera porta
      digitalWrite(RELAY_LOCK_PIN, HIGH);  // HIGH = porta aberta (invertido)
      Serial.println(">>> PORTA LIBERADA (chave pressionada + cor verde)");
    }
    
    // Detecta quando a chave é solta (transição de LOW para HIGH)
    if (lastSwitchLockState == LOW && currentSwitchLockState == HIGH) {
      // Chave foi solta - fecha porta
      digitalWrite(RELAY_LOCK_PIN, LOW);  // LOW = porta fechada (invertido)
      Serial.println(">>> PORTA FECHADA (chave solta)");
    }
    
    lastSwitchLockState = currentSwitchLockState;
  }
  
  delay(50); // Pequeno delay para estabilidade
}

void selectRandomColor() {
  // Seleciona cor aleatória (0-3), mas nunca repete a última cor
  Color previousColor = currentColor;
  Color newColor;
  
  do {
    int colorIndex = random(0, 4);
    newColor = (Color)colorIndex;
  } while (newColor == previousColor); // Garante que não repete a última cor
  
  currentColor = newColor;
  
  // Define duração aleatória entre 15 e 30 segundos
  colorDuration = random(MIN_COLOR_DURATION, MAX_COLOR_DURATION + 1);
  colorStartTime = millis();
  
  // Log no Serial
  Serial.print("Nova cor: ");
  Serial.print(getColorName(currentColor));
  Serial.print(" | Duracao: ");
  Serial.print(colorDuration / 1000);
  Serial.println(" segundos");
}

void sendColorCommand(Color color) {
  uint32_t irCode = 0;
  uint8_t command = 0;
  
  switch (color) {
    case RED:
      irCode = IR_CODE_RED;
      command = 0x4;
      break;
    case GREEN:
      irCode = IR_CODE_GREEN;
      command = 0x5;
      break;
    case BLUE:
      irCode = IR_CODE_BLUE;
      command = 0x6;
      break;
    case WHITE:
      irCode = IR_CODE_WHITE;
      command = 0x7;
      break;
  }
  
  Serial.print(">>> Enviando comando IR: ");
  Serial.print(getColorName(color));
  Serial.print(" | Codigo completo: 0x");
  Serial.print(irCode, HEX);
  Serial.print(" | Endereco: 0x");
  Serial.print(IR_ADDRESS, HEX);
  Serial.print(" | Comando: 0x");
  Serial.print(command, HEX);
  Serial.println();
  
  // Extrai address e command do código completo
  // NEC: 32 bits = 16 bits address + 8 bits command + 8 bits command invertido
  uint16_t address = (irCode >> 16) & 0xFFFF;
  uint8_t cmd = (irCode >> 8) & 0xFF;
  
  // Envia múltiplas vezes para garantir recepção
  for (int i = 0; i < 3; i++) {
    // Método 1: Usa address e command extraídos
    IrSender.sendNEC(address, cmd, 0);
    delay(40);
    
    // Método 2: Usa address padrão e command direto
    IrSender.sendNEC(IR_ADDRESS, command, 0);
    delay(40);
  }
  
  Serial.println(">>> Comando IR enviado (6 tentativas)");
}

void updateLockState() {
  // Esta função não é mais usada, mas mantida para compatibilidade
  // A porta só abre quando chave é pressionada E cor é verde
  // Por padrão, porta sempre fechada (LOW = fechada - invertido)
  digitalWrite(RELAY_LOCK_PIN, LOW);  // Porta fechada
}

void activateRelayAux() {
  // Ativa sirene independente do estado anterior (HIGH = ativa - invertido)
  digitalWrite(RELAY_AUX_PIN, HIGH);  // HIGH = sirene ativa (invertido)
  relayAuxActive = true;
  relayAuxStartTime = millis();
  Serial.print(">>> Sirene ATIVADA - Duração: ");
  Serial.print(RELAY_AUX_DURATION);
  Serial.println(" ms");
}

void deactivateRelayAux() {
  if (relayAuxActive) {
    digitalWrite(RELAY_AUX_PIN, LOW);  // LOW = sirene desativa (invertido)
    relayAuxActive = false;
    Serial.println(">>> Sirene DESATIVADA (tempo esgotado)");
  }
}

const char* getColorName(Color color) {
  switch (color) {
    case RED:   return "VERMELHO (R)";
    case GREEN: return "VERDE (G)";
    case BLUE:  return "AZUL (B)";
    case WHITE: return "BRANCO (W)";
    default:     return "DESCONHECIDO";
  }
}

void processSerialCommands() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) {
        inputString.trim();
        inputString.toLowerCase();
        
        // Comando: sirene:XXXX (duração em milissegundos)
        if (inputString.startsWith("sirene:")) {
          String valueStr = inputString.substring(7);
          unsigned long newDuration = valueStr.toInt();
          if (newDuration > 0 && newDuration <= 60000) { // Máximo 60 segundos
            RELAY_AUX_DURATION = newDuration;
            Serial.print(">>> Duracao da sirene alterada para: ");
            Serial.print(RELAY_AUX_DURATION);
            Serial.println(" ms");
          } else {
            Serial.println(">>> Erro: Valor invalido (1-60000 ms)");
          }
        }
        // Comando: cores:MIN-MAX (duração em segundos)
        else if (inputString.startsWith("cores:")) {
          String valueStr = inputString.substring(6);
          int dashIndex = valueStr.indexOf('-');
          if (dashIndex > 0) {
            int minSec = valueStr.substring(0, dashIndex).toInt();
            int maxSec = valueStr.substring(dashIndex + 1).toInt();
            if (minSec > 0 && maxSec > 0 && minSec <= maxSec && maxSec <= 300) {
              MIN_COLOR_DURATION = minSec * 1000;
              MAX_COLOR_DURATION = maxSec * 1000;
              Serial.print(">>> Duracao das cores alterada para: ");
              Serial.print(minSec);
              Serial.print("-");
              Serial.print(maxSec);
              Serial.println(" segundos");
            } else {
              Serial.println(">>> Erro: Valores invalidos (ex: cores:15-30)");
            }
          } else {
            Serial.println(">>> Erro: Formato invalido. Use: cores:MIN-MAX");
          }
        }
        else {
          Serial.print(">>> Comando desconhecido: ");
          Serial.println(inputString);
          Serial.println(">>> Comandos validos: sirene:XXXX ou cores:MIN-MAX");
        }
        
        inputString = "";
      }
    } else {
      inputString += inChar;
    }
  }
}

void printPinout() {
  Serial.println("\n========================================");
  Serial.println("PINOUT - ARDUINO MEGA");
  Serial.println("========================================");
  Serial.println("Pino 13 - Emissor IR (LED IR + resistor 220Ω)");
  Serial.println("Pino 3  - Chave Liberar Porta (com pull-up interno)");
  Serial.println("Pino 10 - Relé Fechadura Magnética");
  Serial.println("Pino 4  - Chave Ativar Sirene (com pull-up interno)");
  Serial.println("Pino 8  - Relé Sirene/Auxiliar");
  Serial.println("========================================");
  Serial.println("\nCONEXOES DETALHADAS:");
  Serial.println("----------------------------------------");
  Serial.println("EMISSOR IR (Pino 13):");
  Serial.println("  LED IR Anodo -> Resistor 220Ω -> Pino 13");
  Serial.println("  LED IR Catodo -> GND");
  Serial.println("");
  Serial.println("CHAVE LIBERAR PORTA (Pino 3):");
  Serial.println("  Terminal 1 -> Pino 3");
  Serial.println("  Terminal 2 -> GND");
  Serial.println("  (Usa pull-up interno do Arduino)");
  Serial.println("  Funcao: Libera porta quando pressionada");
  Serial.println("");
  Serial.println("CHAVE ATIVAR SIRENE (Pino 4):");
  Serial.println("  Terminal 1 -> Pino 4");
  Serial.println("  Terminal 2 -> GND");
  Serial.println("  (Usa pull-up interno do Arduino)");
  Serial.println("  Funcao: Ativa sirene quando pressionada");
  Serial.println("");
  Serial.println("RELE FECHADURA (Pino 10):");
  Serial.println("  IN -> Pino 10");
  Serial.println("  VCC -> 5V");
  Serial.println("  GND -> GND");
  Serial.println("  NO/NC -> Fechadura Magnética");
  Serial.println("  (LOW = porta fechada, HIGH = porta aberta)");
  Serial.println("");
  Serial.println("RELE SIRENE (Pino 8):");
  Serial.println("  IN -> Pino 8");
  Serial.println("  VCC -> 5V");
  Serial.println("  GND -> GND");
  Serial.println("  NO/NC -> Sirene ou dispositivo auxiliar");
  Serial.println("========================================\n");
}

