# Mapeador de Teclas IR

Este código permite mapear teclas de um controle remoto infravermelho (IR) para identificar os códigos que cada tecla envia.

## Hardware Necessário

- Arduino (Uno, Nano, Mega, etc.)
- Receptor IR (ex: TSOP1738, VS1838B, VS1838, TSOP4838)
- Controle remoto IR qualquer

## Conexões

- **Receptor IR VCC** → Arduino 5V
- **Receptor IR GND** → Arduino GND
- **Receptor IR OUT** → Arduino Pino 13

## Instalação da Biblioteca

1. Abra o Arduino IDE
2. Vá em **Sketch → Include Library → Manage Libraries**
3. Procure por **"IRremote"** (por shirriff, z3t0, ArminJo)
4. Instale a versão mais recente

## Como Usar

1. Conecte o receptor IR conforme as conexões acima
2. Carregue o código `ir_mapper.ino` no Arduino
3. Abra o Serial Monitor (9600 baud)
4. Aponte o controle remoto para o receptor IR
5. Pressione as teclas que deseja mapear
6. Anote os códigos exibidos no Serial Monitor

## Formato da Saída

Para cada tecla pressionada, você verá:

```
----------------------------------------
Tecla #1
----------------------------------------
Protocolo: NEC
Codigo Completo (HEX): 0x20DF10EF
Codigo Completo (DEC): 551502063
Comando: 0x10 (16)
Endereco: 0x20DF (8415)
Bits: 32
----------------------------------------
```

## Informações Importantes

- **Protocolo**: Tipo de protocolo IR usado (NEC, SONY, RC5, etc.)
- **Código Completo**: Valor completo do código IR (use este para o emissor)
- **Comando**: Código específico do comando (alguns protocolos)
- **Endereço**: Endereço do dispositivo (alguns protocolos)
- **Bits**: Número de bits do código

## Próximos Passos

Após mapear todas as teclas desejadas, você pode usar esses códigos no código do emissor IR para enviar os comandos.

## Troubleshooting

- **Nenhum sinal detectado**: Verifique as conexões e se o receptor está funcionando
- **Códigos diferentes a cada vez**: Alguns controles enviam códigos diferentes para a mesma tecla (use o código completo)
- **Protocolo UNKNOWN**: O controle pode usar um protocolo não suportado, mas o código completo ainda será exibido

