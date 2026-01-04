# Troubleshooting - Emissor IR não controla Fita LED

## Problemas Comuns e Soluções

### 1. LED IR não está emitindo sinal

**Sintomas:**
- Fita LED não responde aos comandos
- Nenhuma mudança de cor

**Verificações:**
- ✅ LED IR está conectado corretamente ao pino 2?
- ✅ Resistor de 220Ω está presente entre pino 2 e LED IR?
- ✅ LED IR está apontado para o receptor da fita LED?
- ✅ Distância entre emissor e receptor (recomendado: 30-50cm)

**Solução:**
- Teste o LED IR com o código `test_ir_emitter.ino`
- Use um receptor IR para verificar se o sinal está sendo emitido
- Verifique se o LED IR não está queimado (teste com multímetro)

### 2. Código IR incorreto

**Sintomas:**
- LED IR emite sinal (visível com câmera de celular)
- Fita LED não responde

**Verificações:**
- ✅ Códigos IR estão corretos? (verifique com `ir_mapper.ino`)
- ✅ Protocolo está correto? (deve ser NEC)
- ✅ Endereço e comando estão corretos?

**Solução:**
1. Use o `ir_mapper.ino` para mapear novamente os códigos
2. Compare os códigos mapeados com os do código principal
3. Verifique se a fita LED usa protocolo NEC

### 3. Corrente insuficiente

**Sintomas:**
- LED IR emite sinal fraco
- Fita LED responde intermitentemente

**Solução:**
- Use um transistor NPN (2N2222) para amplificar o sinal:
  ```
  Arduino Pino 2 → Resistor 470Ω → Base do Transistor
  Coletor do Transistor → LED IR → GND
  Emissor do Transistor → GND
  LED IR → Resistor 220Ω → 5V
  ```

### 4. Interferência

**Sintomas:**
- Fita LED responde aleatoriamente
- Comandos não são recebidos corretamente

**Soluções:**
- Mantenha o LED IR longe de fontes de luz intensa
- Use um LED IR com lente focada
- Aumente a distância entre emissor e receptor
- Adicione um capacitor de 100µF próximo ao LED IR

### 5. Biblioteca IRremote

**Verificações:**
- ✅ Biblioteca IRremote está instalada?
- ✅ Versão correta da biblioteca? (pode haver conflitos)
- ✅ RobotIRremote foi removida? (pode causar conflito)

**Solução:**
1. Vá em Sketch → Include Library → Manage Libraries
2. Procure por "IRremote" (por shirriff, z3t0, ArminJo)
3. Instale a versão mais recente
4. Remova qualquer biblioteca RobotIRremote antiga

## Teste Passo a Passo

### Passo 1: Teste do LED IR
1. Carregue `test_ir_emitter.ino`
2. Abra Serial Monitor (9600 baud)
3. Digite "R" e pressione Enter
4. Use uma câmera de celular para verificar se o LED IR está piscando
   (LEDs IR são visíveis através de câmeras digitais)

### Passo 2: Teste com Receptor IR
1. Conecte um receptor IR ao pino 2 (temporariamente)
2. Use o código `ir_mapper.ino` para receber os sinais
3. Envie comandos com `test_ir_emitter.ino`
4. Verifique se os códigos recebidos correspondem aos enviados

### Passo 3: Teste Direto com Controle Remoto
1. Use o controle remoto original da fita LED
2. Mapeie os códigos com `ir_mapper.ino`
3. Compare com os códigos no código principal

### Passo 4: Verificar Códigos no Código Principal
1. Abra `led_lock_controller.ino`
2. Verifique se os códigos correspondem aos mapeados:
   - R: 0xF704EF00
   - G: 0xF805EF00
   - B: 0xF906EF00
   - W: 0xF807EF00

## Código de Teste Rápido

Se quiser testar apenas o LED IR sem todo o sistema:

```cpp
#include <IRremote.h>
#define IR_SEND_PIN 2

void setup() {
  Serial.begin(9600);
  IrSender.begin(IR_SEND_PIN);
  pinMode(IR_SEND_PIN, OUTPUT);
  Serial.println("Teste LED IR - Enviando comando VERDE...");
}

void loop() {
  // Envia comando VERDE a cada 3 segundos
  IrSender.sendNEC(0xEF00, 0x5, 0);
  Serial.println("Comando enviado!");
  delay(3000);
}
```

## Checklist Final

Antes de considerar o problema resolvido, verifique:

- [ ] LED IR está conectado corretamente (pino 2)
- [ ] Resistor 220Ω está presente
- [ ] LED IR está apontado para o receptor da fita LED
- [ ] Distância adequada (30-50cm)
- [ ] Códigos IR estão corretos
- [ ] Biblioteca IRremote está instalada
- [ ] Fita LED está ligada e funcionando
- [ ] Teste com controle remoto original funciona
- [ ] Serial Monitor mostra que comandos estão sendo enviados

## Se Nada Funcionar

1. **Teste com controle remoto original**: Se funcionar, o problema é no emissor/código
2. **Teste com receptor IR**: Verifique se os sinais estão sendo emitidos
3. **Verifique a fita LED**: Pode estar com problema no receptor IR interno
4. **Use transistor**: Pode ser necessário amplificar o sinal do LED IR
5. **Verifique alimentação**: Fita LED precisa de fonte externa adequada

