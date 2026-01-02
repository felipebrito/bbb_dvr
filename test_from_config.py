#!/usr/bin/env python3
"""Testa RTSP usando configuração do config.json."""
import json
import cv2
import subprocess
import sys
import os

# Carrega configuração
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"Erro ao carregar config.json: {e}")
    sys.exit(1)

if not config.get('dvr_servers'):
    print("Nenhum servidor DVR configurado")
    sys.exit(1)

server = config['dvr_servers'][0]
ip = server['ip']
port = server['port']
username = server['username']
password = server['password']
channel = server['channels'][0] if server['channels'] else 1

print("=" * 70)
print("TESTE RTSP USANDO CONFIG.JSON")
print("=" * 70)
print(f"\nConfiguração carregada:")
print(f"  IP: {ip}")
print(f"  Porta: {port}")
print(f"  Usuário: {username}")
print(f"  Senha: {password} (tamanho: {len(password)}, contém @: {'@' in password})")
print(f"  Canal: {channel}")

# Testa diferentes variações
print("\n" + "=" * 70)
print("TESTANDO DIFERENTES FORMATOS DE URL")
print("=" * 70)

# Variação 1: @ codificado como %40
password_encoded = password.replace('@', '%40')
url1 = f"rtsp://{username}:{password_encoded}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
print(f"\n1. URL com @ codificado:")
print(f"   {url1}")

cap1 = cv2.VideoCapture(url1, cv2.CAP_FFMPEG)
cap1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
if cap1.isOpened():
    ret, frame = cap1.read()
    if ret and frame is not None:
        print(f"   ✅ SUCESSO! Frame: {frame.shape}")
        cap1.release()
        print("\n🎉 Esta URL funciona! Use esta configuração.")
        sys.exit(0)
    else:
        print("   ❌ Falhou: Não conseguiu ler frame")
else:
    print("   ❌ Falhou: VideoCapture não abriu")
cap1.release()

# Variação 2: Sem codificação
url2 = f"rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
print(f"\n2. URL sem codificação:")
print(f"   {url2[:80]}...")

cap2 = cv2.VideoCapture(url2, cv2.CAP_FFMPEG)
cap2.set(cv2.CAP_PROP_BUFFERSIZE, 1)
if cap2.isOpened():
    ret, frame = cap2.read()
    if ret and frame is not None:
        print(f"   ✅ SUCESSO! Frame: {frame.shape}")
        cap2.release()
        print("\n🎉 Esta URL funciona! Use esta configuração.")
        sys.exit(0)
    else:
        print("   ❌ Falhou: Não conseguiu ler frame")
else:
    print("   ❌ Falhou: VideoCapture não abriu")
cap2.release()

# Variação 3: Codificação completa
from urllib.parse import quote
encoded_user = quote(username, safe='')
encoded_pass = quote(password, safe='')
url3 = f"rtsp://{encoded_user}:{encoded_pass}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
print(f"\n3. URL com codificação completa:")
print(f"   {url3[:80]}...")

cap3 = cv2.VideoCapture(url3, cv2.CAP_FFMPEG)
cap3.set(cv2.CAP_PROP_BUFFERSIZE, 1)
if cap3.isOpened():
    ret, frame = cap3.read()
    if ret and frame is not None:
        print(f"   ✅ SUCESSO! Frame: {frame.shape}")
        cap3.release()
        print("\n🎉 Esta URL funciona! Use esta configuração.")
        sys.exit(0)
    else:
        print("   ❌ Falhou: Não conseguiu ler frame")
else:
    print("   ❌ Falhou: VideoCapture não abriu")
cap3.release()

# Variação 4: Formato alternativo (Hikvision)
url4 = f"rtsp://{username}:{password_encoded}@{ip}:{port}/Streaming/Channels/{channel:03d}"
print(f"\n4. Formato Hikvision alternativo:")
print(f"   {url4[:80]}...")

cap4 = cv2.VideoCapture(url4, cv2.CAP_FFMPEG)
cap4.set(cv2.CAP_PROP_BUFFERSIZE, 1)
if cap4.isOpened():
    ret, frame = cap4.read()
    if ret and frame is not None:
        print(f"   ✅ SUCESSO! Frame: {frame.shape}")
        cap4.release()
        print("\n🎉 Esta URL funciona! Use esta configuração.")
        sys.exit(0)
    else:
        print("   ❌ Falhou: Não conseguiu ler frame")
else:
    print("   ❌ Falhou: VideoCapture não abriu")
cap4.release()

print("\n" + "=" * 70)
print("❌ TODOS OS TESTES FALHARAM")
print("=" * 70)
print("\nPossíveis causas:")
print("1. Credenciais incorretas (usuário/senha)")
print("2. Formato de URL RTSP incorreto para este DVR")
print("3. DVR não aceita conexões RTSP desta rede")
print("4. Firewall bloqueando porta 554")
print("\nAÇÃO RECOMENDADA:")
print("Teste a URL manualmente no VLC:")
print("  Media > Open Network Stream")
print(f"  Cole: {url1}")
print("\nSe funcionar no VLC, o problema pode ser no código.")
print("Se não funcionar no VLC, verifique credenciais e formato da URL.")

