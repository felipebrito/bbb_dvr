"""Gerenciamento de configuração da aplicação."""
import json
import os
import sys
from typing import Dict, List, Any


class ConfigManager:
    """Gerencia carregamento e salvamento de configuração."""
    
    def __init__(self, config_path: str = "config.json"):
        # Quando empacotado, o config.json está no diretório do executável
        if getattr(sys, 'frozen', False):
            # Se está rodando como executável empacotado
            # PyInstaller coloca arquivos de dados no diretório do executável (Contents/MacOS/)
            exec_dir = os.path.dirname(sys.executable)
            
            # Tenta várias localizações possíveis (ordem de prioridade)
            possible_paths = []
            
            # Se executável está dentro de .app, tenta Resources primeiro (onde PyInstaller coloca)
            if '.app' in sys.executable:
                # Encontra o caminho do .app
                app_path = sys.executable
                while not app_path.endswith('.app') and app_path != '/':
                    app_path = os.path.dirname(app_path)
                
                if app_path.endswith('.app'):
                    # 1. Contents/Resources/config.json (onde PyInstaller coloca dados)
                    resources_path = os.path.join(app_path, 'Contents', 'Resources', config_path)
                    possible_paths.append(resources_path)
                    
                    # 2. Contents/MacOS/config.json (alternativa)
                    macos_path = os.path.join(app_path, 'Contents', 'MacOS', config_path)
                    possible_paths.append(macos_path)
            
            # 3. Diretório do executável
            possible_paths.append(os.path.join(exec_dir, config_path))
            
            # 4. Diretório atual de trabalho
            possible_paths.append(config_path)
            
            found = False
            for alt_path in possible_paths:
                if os.path.exists(alt_path):
                    config_path = alt_path
                    print(f"ConfigManager: Encontrado config.json em: {alt_path}")
                    found = True
                    break
            
            if not found:
                print(f"ConfigManager: AVISO - config.json não encontrado. Tentou:")
                for p in possible_paths:
                    print(f"  - {p}")
        else:
            # Se está rodando como script Python
            if not os.path.exists(config_path):
                # Tenta no diretório do script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                alt_path = os.path.join(script_dir, config_path)
                if os.path.exists(alt_path):
                    config_path = alt_path
        
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()
        
        # Debug: mostra quantos DVRs foram carregados
        dvr_count = len(self.config.get("dvr_servers", []))
        total_cameras = sum(len(s.get("channels", [])) for s in self.config.get("dvr_servers", []))
        print(f"ConfigManager: {dvr_count} DVR(s), {total_cameras} câmera(s) carregadas do arquivo: {self.config_path}")
    
    def load(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo JSON."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"ConfigManager: Configuração carregada de {self.config_path}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erro ao carregar configuração de {self.config_path}: {e}")
                print("ConfigManager: Usando configuração padrão")
                self.config = self._default_config()
        else:
            print(f"ConfigManager: Arquivo não encontrado: {self.config_path}")
            print("ConfigManager: Usando configuração padrão e criando novo arquivo")
            self.config = self._default_config()
            # Só salva se não estiver empacotado
            if not getattr(sys, 'frozen', False):
                self.save()
        return self.config
    
    def save(self) -> bool:
        """Salva configuração no arquivo JSON."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor da configuração."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Define valor na configuração."""
        self.config[key] = value
    
    def get_dvr_servers(self) -> List[Dict[str, Any]]:
        """Retorna lista de servidores DVR."""
        return self.config.get("dvr_servers", [])
    
    def get_grids(self) -> List[Dict[str, Any]]:
        """Retorna lista de grids configurados."""
        return self.config.get("grids", [])
    
    def get_transition_duration(self) -> float:
        """Retorna duração da transição em segundos."""
        return self.config.get("transition_duration", 1.0)
    
    def get_window_mode(self) -> str:
        """Retorna modo da janela."""
        return self.config.get("window_mode", "fullscreen")
    
    def _default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão."""
        return {
            "dvr_servers": [
                {
                    "ip": "192.168.1.27",
                    "port": 554,
                    "username": "admin",
                    "password": "123456789@",
                    "channels": [1, 2, 3, 4]
                }
            ],
            "grids": [
                {"cameras": [0, 1, 2, 3], "display_time": 15}
            ],
            "transition_duration": 1.0,
            "window_mode": "fullscreen"
        }
