#!/usr/bin/env python3
"""Script de teste para verificar conexão RTSP."""
import cv2
import sys
from urllib.parse import quote

def test_rtsp_url(url, description):
    """Testa uma URL RTSP."""
    print(f"\nTestando: {description}")
    print(f"URL: {url[:50]}...")  # Mostra apenas início da URL por segurança
    
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        print("❌ Falha: VideoCapture não abriu")
        return False
    
    print("VideoCapture aberto, tentando ler frame...")
    ret, frame = cap.read()
    
    if ret and frame is not None:
        print(f"✅ Sucesso! Frame capturado: {frame.shape}")
        cap.release()
        return True
    else:
        print("❌ Falha: Não conseguiu ler frame")
        cap.release()
        return False

if __name__ == "__main__":
    # Configuração do exemplo
    ip = "192.168.1.27"
    port = 554
    username = "admin"
    password = "123456789@"
    channel = 1
    
    print("=" * 60)
    print("Teste de Conexão RTSP")
    print("=" * 60)
    
    # Teste 1: URL sem codificação (formato original)
    url1 = f"rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
    test_rtsp_url(url1, "URL sem codificação (original)")
    
    # Teste 2: URL com @ substituído por %40 na senha
    password_encoded = password.replace('@', '%40')
    url2 = f"rtsp://{username}:{password_encoded}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
    test_rtsp_url(url2, "URL com @ -> %40 na senha")
    
    # Teste 3: URL com codificação completa
    encoded_user = quote(username, safe='')
    encoded_pass = quote(password, safe='')
    url3 = f"rtsp://{encoded_user}:{encoded_pass}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
    test_rtsp_url(url3, "URL com codificação completa")
    
    # Teste 4: Formato alternativo - sem /cam/realmonitor
    url4 = f"rtsp://{username}:{password_encoded}@{ip}:{port}/Streaming/Channels/{channel:03d}"
    test_rtsp_url(url4, "Formato alternativo (Streaming/Channels)")
    
    # Teste 5: Formato alternativo - com /h264
    url5 = f"rtsp://{username}:{password_encoded}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0&unicast=true&proto=Onvif"
    test_rtsp_url(url5, "Formato com parâmetros adicionais")
    
    # Teste 6: Formato com path diferente
    url6 = f"rtsp://{username}:{password_encoded}@{ip}:{port}/h264/ch{channel}/main/av_stream"
    test_rtsp_url(url6, "Formato h264/ch/main")
    
    # Teste 7: Verificar se senha está correta - tentar sem @
    if '@' in password:
        password_no_at = password.replace('@', '')
        url7 = f"rtsp://{username}:{password_no_at}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
        test_rtsp_url(url7, "URL sem @ na senha (teste)")
    
    print("\n" + "=" * 60)
    print("Teste concluído")
    print("=" * 60)
    print("\nNOTA: Se todos falharam com 401 Unauthorized:")
    print("1. Verifique se IP, porta, usuário e senha estão corretos")
    print("2. Verifique se o DVR aceita conexões RTSP da sua rede")
    print("3. Teste a URL no VLC: Media > Open Network Stream")
    print("4. Alguns DVRs podem precisar de formato de URL específico")

