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

# Verifica se Info.plist existe
INFO_PLIST_OPTION=""
if [ -f "Info.plist" ]; then
    INFO_PLIST_OPTION="--osx-bundle-identifier=com.bbb.dvrviewer"
    echo "✅ Usando Info.plist personalizado"
fi

# Cria o .app (one-folder - mais fácil de debugar)
echo "📦 Criando aplicação..."
pyinstaller \
    --name "BBB DVR Viewer" \
    --windowed \
    --onedir \
    --noconsole \
    $ICON_OPTION \
    $INFO_PLIST_OPTION \
    --add-data "config.json:." \
    --add-data "imagens:imagens" \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=tkinter \
    --hidden-import=cv2 \
    --collect-all cv2 \
    main.py

# Copia Info.plist para o bundle se existir
if [ -f "Info.plist" ]; then
    echo "📋 Copiando Info.plist para o bundle..."
    cp Info.plist "dist/BBB DVR Viewer.app/Contents/Info.plist"
    
    # Atualiza referência do ícone no Info.plist
    ICNS_FILE=$(find "dist/BBB DVR Viewer.app/Contents/Resources" -name "*.icns" | head -1)
    if [ -n "$ICNS_FILE" ]; then
        ICNS_NAME=$(basename "$ICNS_FILE" .icns)
        echo "📋 Atualizando referência do ícone para: $ICNS_NAME"
        # Usa sed para atualizar o CFBundleIconFile no Info.plist
        sed -i '' "s/<key>CFBundleIconFile<\/key>.*/<key>CFBundleIconFile<\/key>\n    <string>$ICNS_NAME<\/string>/" "dist/BBB DVR Viewer.app/Contents/Info.plist" 2>/dev/null || \
        sed -i '' "/<key>CFBundleIconFile<\/key>/!b;n;c\\
    <string>$ICNS_NAME</string>" "dist/BBB DVR Viewer.app/Contents/Info.plist"
    fi
fi

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

