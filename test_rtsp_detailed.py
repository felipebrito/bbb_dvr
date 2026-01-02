#!/usr/bin/env python3
"""Script de teste detalhado para verificar conexão RTSP com mais informações."""
import sys
import os

# Verifica se está no ambiente virtual ou tenta ativar
if 'VIRTUAL_ENV' not in os.environ:
    venv_activate = os.path.join(os.path.dirname(__file__), '.venv', 'bin', 'activate_this.py')
    if os.path.exists(venv_activate):
        exec(open(venv_activate).read(), {'__file__': venv_activate})

try:
    import cv2
    import subprocess
except ImportError:
    print("=" * 70)
    print("ERRO: Módulos não encontrados!")
    print("=" * 70)
    print("\nExecute com o ambiente virtual ativado:")
    print("  source .venv/bin/activate")
    print("  python test_rtsp_detailed.py")
    print("\nOu use o script run.sh:")
    print("  ./run.sh")
    sys.exit(1)

def test_with_ffmpeg(url, description):
    """Testa URL RTSP usando ffmpeg diretamente."""
    print(f"\n🔍 Testando com ffmpeg: {description}")
    print(f"URL: {url[:70]}...")
    
    try:
        # Tenta conectar com ffmpeg (timeout de 5 segundos)
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',  # Usa TCP (mais confiável)
            '-i', url,
            '-frames:v', '1',  # Apenas 1 frame
            '-f', 'null',
            '-'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ ffmpeg: Sucesso!")
            return True
        else:
            print(f"❌ ffmpeg: Falhou")
            # Mostra apenas erros relevantes
            errors = [line for line in result.stderr.split('\n') 
                     if 'error' in line.lower() or 'unauthorized' in line.lower() 
                     or '401' in line or 'failed' in line.lower()]
            if errors:
                print("   Erros:", errors[:2])
            return False
    except subprocess.TimeoutExpired:
        print("❌ ffmpeg: Timeout")
        return False
    except FileNotFoundError:
        print("⚠️  ffmpeg não encontrado (não é crítico)")
        return None
    except Exception as e:
        print(f"❌ ffmpeg: Erro - {e}")
        return False

def test_with_opencv(url, description):
    """Testa URL RTSP usando OpenCV."""
    print(f"\n🔍 Testando com OpenCV: {description}")
    print(f"URL: {url[:70]}...")
    
    try:
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        # Nota: CAP_PROP_RTSP_TRANSPORT pode não estar disponível em todas as versões
        
        if not cap.isOpened():
            print("❌ OpenCV: VideoCapture não abriu")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            print(f"✅ OpenCV: Sucesso! Frame: {frame.shape}")
            return True
        else:
            print("❌ OpenCV: Não conseguiu ler frame")
            return False
    except Exception as e:
        print(f"❌ OpenCV: Erro - {e}")
        return False

if __name__ == "__main__":
    # Configuração
    ip = "192.168.1.27"
    port = 554
    username = "admin"
    password = "123456789@"
    channel = 1
    
    print("=" * 70)
    print("TESTE DETALHADO DE CONEXÃO RTSP")
    print("=" * 70)
    print(f"\nConfiguração:")
    print(f"  IP: {ip}")
    print(f"  Porta: {port}")
    print(f"  Usuário: {username}")
    print(f"  Senha: {'*' * len(password)} (contém @)")
    print(f"  Canal: {channel}")
    
    # URLs para testar
    password_encoded = password.replace('@', '%40')
    
    urls_to_test = [
        (f"rtsp://{username}:{password_encoded}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0",
         "Formato padrão com @ codificado"),
        (f"rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0",
         "Formato padrão sem codificação"),
        (f"rtsp://{username}:{password_encoded}@{ip}:{port}/Streaming/Channels/{channel:03d}",
         "Formato Hikvision alternativo"),
    ]
    
    results = []
    for url, desc in urls_to_test:
        print(f"\n{'='*70}")
        print(f"TESTE: {desc}")
        print(f"{'='*70}")
        
        # Testa com ffmpeg primeiro (mais informativo)
        ffmpeg_result = test_with_ffmpeg(url, desc)
        
        # Testa com OpenCV
        opencv_result = test_with_opencv(url, desc)
        
        results.append((desc, ffmpeg_result, opencv_result))
    
    # Resumo
    print(f"\n{'='*70}")
    print("RESUMO DOS TESTES")
    print(f"{'='*70}")
    for desc, ffmpeg, opencv in results:
        status = "✅" if (ffmpeg or opencv) else "❌"
        print(f"{status} {desc}")
        if ffmpeg:
            print(f"   - ffmpeg: OK")
        if opencv:
            print(f"   - OpenCV: OK")
    
    print(f"\n{'='*70}")
    print("RECOMENDAÇÕES:")
    print(f"{'='*70}")
    print("1. Verifique as credenciais no config.json")
    print("2. Teste a URL manualmente no VLC:")
    print("   Media > Open Network Stream > Cole a URL")
    print("3. Verifique se o DVR aceita conexões RTSP")
    print("4. Alguns DVRs precisam de formato de URL específico")
    print("5. Verifique firewall/rede se necessário")
    print(f"\nExemplo de URL para testar no VLC:")
    print(f"rtsp://{username}:{password_encoded}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0")

