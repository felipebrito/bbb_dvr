#!/bin/bash
# Script para criar aplicação .app (one-folder) para macOS
# Esta versão cria uma pasta com todos os arquivos (mais fácil de debugar)

cd "$(dirname "$0")"

echo "🔨 Construindo aplicação .app (one-folder)..."

# Ativa ambiente virtual
source .venv/bin/activate

# Instala PyInstaller se não estiver instalado
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip install pyinstaller
fi

# Verifica se o ícone existe
ICON_PATH="imagens/logo.png"
if [ ! -f "$ICON_PATH" ]; then
    echo "⚠️  Aviso: Ícone não encontrado em $ICON_PATH"
    echo "   Continuando sem ícone personalizado..."
    ICON_OPTION=""
else
    echo "✅ Usando ícone: $ICON_PATH"
    ICON_OPTION="--icon=$ICON_PATH"
fi

# Limpa builds anteriores
echo "🧹 Limpando builds anteriores..."
rm -rf build dist *.spec

# Cria o .app (one-folder - mais fácil de debugar)
echo "📦 Criando aplicação..."
pyinstaller \
    --name "BBB DVR Viewer" \
    --windowed \
    --onedir \
    --noconsole \
    $ICON_OPTION \
    --add-data "config.json:." \
    --add-data "imagens:imagens" \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=tkinter \
    --hidden-import=cv2 \
    --collect-all cv2 \
    main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Aplicação criada com sucesso!"
    echo "📁 Localização: dist/BBB DVR Viewer.app"
    echo ""
    echo "Para testar, execute:"
    echo "  open 'dist/BBB DVR Viewer.app'"
    echo ""
    echo "Nota: Esta versão cria uma pasta com todos os arquivos."
    echo "      Para distribuição, use build_app.sh (onefile)"
else
    echo ""
    echo "❌ Erro ao criar aplicação"
    exit 1
fi

