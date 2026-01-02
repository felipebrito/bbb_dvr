#!/bin/bash
# Script para testar conexão RTSP

cd "$(dirname "$0")"
source .venv/bin/activate
python test_rtsp_detailed.py

