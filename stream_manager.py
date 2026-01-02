"""Gerenciamento de streams RTSP com threading e buffer management."""
import cv2
import threading
import time
from typing import Optional, Dict, List
from queue import Queue, Empty
import numpy as np
from urllib.parse import quote


class StreamCapture:
    """Captura de um único stream RTSP em thread separada."""
    
    def __init__(self, rtsp_url: str, stream_id: int, buffer_size: int = 2, alt_url: Optional[str] = None):
        self.rtsp_url = rtsp_url
        self.alt_url = alt_url  # URL alternativa (sem codificação, por exemplo)
        self.stream_id = stream_id
        self.buffer_size = buffer_size
        self.frame_queue: Queue = Queue(maxsize=buffer_size)
        self.current_frame: Optional[np.ndarray] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.last_frame_time = 0
        self.connected = False
        self.lock = threading.Lock()
        self.connection_attempts = 0
        self.current_url = rtsp_url  # URL atual sendo usada
    
    def start(self) -> None:
        """Inicia thread de captura."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
    
    def stop(self) -> None:
        """Para thread de captura."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Obtém frame mais recente."""
        with self.lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def is_connected(self) -> bool:
        """Verifica se stream está conectado."""
        return self.connected
    
    def _capture_loop(self) -> None:
        """Loop principal de captura em thread separada."""
        reconnect_delay = 5.0
        last_reconnect_attempt = 0
        
        while self.running:
            try:
                # Tenta conectar/reconectar
                if not self.connected or self.cap is None or not self.cap.isOpened():
                    current_time = time.time()
                    if current_time - last_reconnect_attempt >= reconnect_delay:
                        last_reconnect_attempt = current_time
                        self._connect()
                    else:
                        time.sleep(0.1)
                        continue
                
                # Captura frame
                ret, frame = self.cap.read()
                
                if ret and frame is not None:
                    self.connected = True
                    self.last_frame_time = time.time()
                    
                    # Atualiza frame atual (thread-safe)
                    with self.lock:
                        self.current_frame = frame.copy()
                    
                    # Tenta adicionar ao buffer (descarta se cheio)
                    try:
                        self.frame_queue.put_nowait(frame)
                    except:
                        # Buffer cheio, descarta frame mais antigo
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(frame)
                        except:
                            pass
                else:
                    # Frame inválido, marca como desconectado
                    self.connected = False
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"Erro no stream {self.stream_id}: {e}")
                self.connected = False
                if self.cap:
                    self.cap.release()
                    self.cap = None
                time.sleep(1.0)
    
    def _connect(self) -> None:
        """Conecta ao stream RTSP."""
        try:
            if self.cap:
                self.cap.release()
            
            # Tenta URL alternativa se a principal falhou várias vezes
            url_to_try = self.current_url
            if self.connection_attempts > 3 and self.alt_url:
                url_to_try = self.alt_url
                self.current_url = self.alt_url
                print(f"Stream {self.stream_id}: Tentando URL alternativa")
            
            # Configurações para melhor performance e autenticação RTSP
            # Usa backend FFMPEG com opções RTSP
            self.cap = cv2.VideoCapture(url_to_try, cv2.CAP_FFMPEG)
            
            # Configurações de buffer e FPS
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo
            self.cap.set(cv2.CAP_PROP_FPS, 15)  # Limita FPS
            
            # Aguarda um pouco para conexão RTSP se estabelecer
            # RTSP pode demorar alguns segundos para conectar
            time.sleep(2)
            
            # Verifica se VideoCapture foi aberto
            # Nota: isOpened() pode retornar True mesmo que ainda não tenha conectado
            # Por isso tentamos ler frames diretamente
            
            # Tenta ler primeiro frame para verificar conexão
            # Dá várias tentativas para streams RTSP que podem demorar
            max_attempts = 5
            for attempt in range(max_attempts):
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.connected = True
                    self.connection_attempts = 0  # Reset contador em caso de sucesso
                    # Não imprime URL completa por segurança (pode conter senha)
                    print(f"Stream {self.stream_id} conectado com sucesso")
                    return
                # Aguarda um pouco mais entre tentativas
                time.sleep(1)
            
            # Se chegou aqui, não conseguiu conectar
            self.connection_attempts += 1
            self.connected = False
            if self.cap:
                self.cap.release()
                self.cap = None
            if self.connection_attempts <= 3:
                print(f"Stream {self.stream_id} falhou ao conectar (tentativa {self.connection_attempts})")
                    
        except Exception as e:
            self.connection_attempts += 1
            print(f"Erro ao conectar stream {self.stream_id}: {e}")
            self.connected = False
            if self.cap:
                self.cap.release()
                self.cap = None


class StreamManager:
    """Gerencia múltiplos streams RTSP."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.streams: Dict[int, StreamCapture] = {}
        self._build_streams()
        
        # Debug: mostra quantos streams foram criados
        print(f"StreamManager: {len(self.streams)} stream(s) criado(s)")
    
    def _build_streams(self) -> None:
        """Constrói streams a partir da configuração."""
        # Para todos os streams existentes
        for stream in self.streams.values():
            stream.stop()
        self.streams.clear()
        
        # Cria novos streams
        dvr_servers = self.config_manager.get_dvr_servers()
        stream_id = 0
        
        for server in dvr_servers:
            ip = server.get("ip")
            port = server.get("port", 554)
            username = server.get("username", "")
            password = server.get("password", "")
            channels = server.get("channels", [])
            
            for channel in channels:
                # Para RTSP, testamos primeiro sem codificação (funcionou no VLC)
                # Se falhar, tentamos com codificação como fallback
                if '@' in password:
                    # Abordagem 1: Sem codificação (testado e funcionou no VLC)
                    rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
                    
                    # Abordagem 2: Com @ codificado como %40 (fallback)
                    password_encoded = password.replace('@', '%40')
                    alt_url = f"rtsp://{username}:{password_encoded}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
                else:
                    # Senha sem caracteres especiais, usa direto
                    rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0"
                    alt_url = None
                
                stream = StreamCapture(rtsp_url, stream_id, buffer_size=2, alt_url=alt_url)
                self.streams[stream_id] = stream
                stream_id += 1
    
    def start_all(self) -> None:
        """Inicia todos os streams."""
        for stream in self.streams.values():
            stream.start()
    
    def stop_all(self) -> None:
        """Para todos os streams."""
        for stream in self.streams.values():
            stream.stop()
    
    def get_frame(self, camera_index: int) -> Optional[np.ndarray]:
        """Obtém frame de uma câmera específica."""
        if camera_index in self.streams:
            return self.streams[camera_index].get_frame()
        return None
    
    def reload(self) -> None:
        """Recarrega streams com nova configuração."""
        self.stop_all()
        self._build_streams()
        self.start_all()
    
    def get_stream_count(self) -> int:
        """Retorna número total de streams."""
        return len(self.streams)
