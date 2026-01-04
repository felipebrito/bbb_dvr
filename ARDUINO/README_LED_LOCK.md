# Controlador de Fita LED IR + Fechadura Magnética + Sirene

Sistema de controle de acesso baseado em cores para experiência BBB. Controla uma fita LED via infravermelho (IR) e uma fechadura magnética, onde apenas a cor verde permite o acesso.

## Funcionamento

- **Fita LED**: Alterna aleatoriamente entre as cores R (Vermelho), G (Verde), B (Azul) e W (Branco)
- **Duração das cores**: Cada cor dura entre 15 e 30 segundos (aleatório)
- **Nunca repete a última cor**: Sempre muda para uma cor diferente
- **Controle de acesso**: 
  - **Apenas quando a cor é VERDE (G)**: As chaves podem ser usadas
  - **Outras cores (R, B, W)**: As chaves são ignoradas
- **Porta**: Só pode ser liberada quando cor = VERDE e chave do pino 3 pressionada
- **Sirene**: Só pode ser ativada quando cor = VERDE e chave do pino 4 pressionada

## Hardware Necessário

- Arduino Mega
- Módulo emissor IR (LED IR + resistor 220Ω)
- 2 módulos de relé
- 2 chaves micro (microswitch)
- Fita LED controlada por IR

## Conexões

### Emissor IR
- **LED IR ânodo** → Resistor 220Ω → Arduino Pino 13
- **LED IR cátodo** → Arduino GND

### Chaves Micro
- **Chave Liberar Porta (Pino 3)**:
  - Terminal 1 → Arduino Pino 3
  - Terminal 2 → Arduino GND
  - Usa pull-up interno do Arduino (INPUT_PULLUP)
  - Função: Libera porta quando pressionada (apenas se cor for verde)

- **Chave Ativar Sirene (Pino 4)**:
  - Terminal 1 → Arduino Pino 4
  - Terminal 2 → Arduino GND
  - Usa pull-up interno do Arduino (INPUT_PULLUP)
  - Função: Ativa sirene quando pressionada (apenas se cor for verde)

### Relés
- **Relé Fechadura (Pino 10)**:
  - IN → Arduino Pino 10
  - VCC → 5V
  - GND → GND
  - NO/NC → Fechadura Magnética
  - **Lógica invertida**: LOW = porta fechada, HIGH = porta aberta
  
- **Relé Sirene (Pino 8)**:
  - IN → Arduino Pino 8
  - VCC → 5V
  - GND → GND
  - NO/NC → Sirene ou dispositivo auxiliar
  - **Lógica**: LOW = sirene desativa, HIGH = sirene ativa
  - Duração: 2 segundos (configurável via Serial)

## Códigos IR Mapeados

Todos os códigos usam protocolo **NEC**:
- **R (Vermelho)**: Endereço 0xEF00, Comando 0x4, Código completo: 0xF704EF00
- **G (Verde)**: Endereço 0xEF00, Comando 0x5, Código completo: 0xF805EF00
- **B (Azul)**: Endereço 0xEF00, Comando 0x6, Código completo: 0xF906EF00
- **W (Branco)**: Endereço 0xEF00, Comando 0x7, Código completo: 0xF807EF00

## Configurações Ajustáveis via Serial

Você pode ajustar as configurações enviando comandos pelo Serial Monitor (9600 baud):

### Comandos Disponíveis:

1. **`sirene:XXXX`** - Define duração da sirene em milissegundos
   - Exemplo: `sirene:5000` (sirene fica 5 segundos ativa)
   - Valores válidos: 1 a 60000 ms
   - Padrão: 2000 ms (2 segundos)

2. **`cores:MIN-MAX`** - Define duração mínima e máxima das cores em segundos
   - Exemplo: `cores:15-30` (cada cor dura entre 15 e 30 segundos)
   - Valores válidos: 1 a 300 segundos
   - Padrão: 15-30 segundos

## Pinout Resumido

| Pino | Função |
|------|--------|
| 13 | Emissor IR (LED IR + resistor 220Ω) |
| 3 | Chave Liberar Porta (INPUT_PULLUP) |
| 10 | Relé Fechadura Magnética |
| 4 | Chave Ativar Sirene (INPUT_PULLUP) |
| 8 | Relé Sirene/Auxiliar |
| 5V | Alimentação dos módulos de relé |
| GND | Terra comum |

## Lógica de Funcionamento

### Porta (Pino 10)
- **Abre**: Apenas quando cor = VERDE e chave pino 3 pressionada
- **Fecha**: Em todos os outros casos (chave solta, cor não-verde, mudança de cor)
- **Lógica invertida**: LOW = fechada, HIGH = aberta

### Sirene (Pino 8)
- **Ativa**: Apenas quando cor = VERDE e chave pino 4 pressionada
- **Duração**: 2 segundos (configurável)
- **Desativa**: Automaticamente após tempo configurado
- **Lógica**: LOW = desativa, HIGH = ativa

### Cores
- **Verde**: Permite uso das chaves (porta e sirene)
- **Outras cores (R, B, W)**: Chaves são ignoradas
- **Nunca repete**: Sempre muda para uma cor diferente

## Uso

1. Conecte todos os componentes conforme o diagrama (`DIAGRAMA_CONEXOES.txt`)
2. Carregue o código `led_lock_controller.ino` no Arduino Mega
3. Abra o Serial Monitor (9600 baud) para acompanhar o funcionamento
4. O sistema inicia automaticamente, alternando entre as cores
5. Use os comandos serial para ajustar configurações em tempo real

## Saída Serial

O Serial Monitor mostra:
- Quando uma nova cor é selecionada
- Comandos IR enviados
- Estado da fechadura (aberta/fechada)
- Ativação da sirene
- Mensagens de erro quando chaves são pressionadas em cores não-verdes

## Troubleshooting

- **LED não muda de cor**: Verifique se o emissor IR está apontado para o receptor da fita LED
- **Fechadura não abre**: Verifique se o relé está conectado corretamente e se a cor é verde
- **Chave não funciona**: Verifique se a chave está conectada corretamente e se a cor é verde
- **Sirene não ativa**: Verifique se a cor é verde e se o relé está conectado corretamente

## Notas Importantes

- O sistema usa números aleatórios para selecionar cores e durações
- A sequência de cores é completamente aleatória
- Nunca repete a última cor selecionada
- Ambas as chaves só funcionam quando a cor é verde
- Os relés usam lógica invertida (verifique o diagrama)

## Arquivos Relacionados

- `led_lock_controller.ino` - Código principal
- `DIAGRAMA_CONEXOES.txt` - Diagrama detalhado de conexões
- `ir_mapper.ino` - Código para mapear códigos IR
- `test_ir_emitter.ino` - Código para testar emissor IR
