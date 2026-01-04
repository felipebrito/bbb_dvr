#!/bin/bash
# Script para fazer upload do código e abrir monitor serial

cd "$(dirname "$0")"

echo "=========================================="
echo "Upload e Teste - Arduino Uno - 2 Reles"
echo "=========================================="
echo ""

# Verifica se Arduino está conectado
echo "Verificando Arduino conectado..."
BOARD_INFO=$(arduino-cli board list | grep -i "arduino\|uno" | head -1)

if [ -z "$BOARD_INFO" ]; then
    echo "❌ Nenhum Arduino detectado!"
    echo ""
    echo "Por favor:"
    echo "1. Conecte o Arduino Uno via USB"
    echo "2. Execute este script novamente"
    echo ""
    echo "Portas disponíveis:"
    arduino-cli board list
    exit 1
fi

# Extrai a porta
PORT=$(echo "$BOARD_INFO" | awk '{print $1}')
FQBN=$(echo "$BOARD_INFO" | awk '{print $NF}')

echo "✓ Arduino encontrado!"
echo "  Porta: $PORT"
echo "  FQBN: $FQBN"
echo ""

# Compila o código
echo "Compilando código..."
arduino-cli compile --fqbn arduino:avr:uno single_relay
if [ $? -ne 0 ]; then
    echo "❌ Erro na compilação!"
    exit 1
fi
echo "✓ Compilação concluída!"
echo ""

# Faz upload
echo "Fazendo upload para o Arduino..."
arduino-cli upload -p "$PORT" --fqbn arduino:avr:uno single_relay
if [ $? -ne 0 ]; then
    echo "❌ Erro no upload!"
    exit 1
fi
echo "✓ Upload concluído!"
echo ""

# Aguarda um pouco para o Arduino reiniciar
echo "Aguardando Arduino reiniciar..."
sleep 2

# Abre monitor serial
echo "=========================================="
echo "Monitor Serial (9600 baud)"
echo "=========================================="
echo "Comandos disponíveis:"
echo "  1on  - Liga rele 1 (pino 8)"
echo "  1off - Desliga rele 1"
echo "  2on  - Liga rele 2 (pino 10)"
echo "  2off - Desliga rele 2"
echo ""
echo "Digite os comandos abaixo:"
echo "=========================================="
echo ""

# Abre monitor serial
arduino-cli monitor -p "$PORT" -c baudrate=9600

