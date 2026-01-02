#!/bin/bash
# Script para instalar dependências

cd "$(dirname "$0")"
source .venv/bin/activate
python -m pip install -r requirements.txt

