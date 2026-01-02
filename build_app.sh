#!/bin/bash
# Script para criar aplicação .app para macOS

cd "$(dirname "$0")"

echo "🔨 Construindo aplicação .app..."

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

# Cria o .app
echo "📦 Criando aplicação..."
pyinstaller \
    --name "BBB DVR Viewer" \
    --windowed \
    --onefile \
    --noconsole \
    $ICON_OPTION \
    --add-data "config.json:." \
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
else
    echo ""
    echo "❌ Erro ao criar aplicação"
    exit 1
fi

