#!/bin/bash
# Script para testar o .app e capturar logs

# Caminho relativo ao diretório pai (onde o dist será criado)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_PATH="$SCRIPT_DIR/../dist/BBB DVR Viewer.app"
LOG_FILE="$HOME/Desktop/app_log_$(date +%Y%m%d_%H%M%S).txt"

echo "🔍 Testando aplicação e capturando logs..."
echo "📝 Logs serão salvos em: $LOG_FILE"
echo ""

# Executa o app e captura stdout/stderr
"$APP_PATH/Contents/MacOS/BBB DVR Viewer" 2>&1 | tee "$LOG_FILE"

echo ""
echo "✅ Logs salvos em: $LOG_FILE"

