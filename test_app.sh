#!/bin/bash
# Script para testar o .app e capturar logs

APP_PATH="/Users/brito/Dropbox/@ENTREQUADRA/@2025/BBB Experience/dist/BBB DVR Viewer.app"
LOG_FILE="$HOME/Desktop/app_log_$(date +%Y%m%d_%H%M%S).txt"

echo "🔍 Testando aplicação e capturando logs..."
echo "📝 Logs serão salvos em: $LOG_FILE"
echo ""

# Executa o app e captura stdout/stderr
"$APP_PATH/Contents/MacOS/BBB DVR Viewer" 2>&1 | tee "$LOG_FILE"

echo ""
echo "✅ Logs salvos em: $LOG_FILE"

