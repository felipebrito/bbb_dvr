"""Gerenciamento de configuração da aplicação."""
import json
import os
import sys
from typing import Dict, List, Any


class ConfigManager:
    """Gerencia carregamento e salvamento de configuração."""
    
    def __init__(self, config_path: str = "config.json"):
        # Se config.json não estiver no diretório atual, tenta no diretório do executável
        if not os.path.exists(config_path):
            # Tenta no diretório do executável (quando empacotado)
            exec_dir = os.path.dirname(sys.executable) if hasattr(sys, 'frozen') else os.path.dirname(os.path.abspath(__file__))
            alt_path = os.path.join(exec_dir, config_path)
            if os.path.exists(alt_path):
                config_path = alt_path
        
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """Carrega configuração do arquivo JSON."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erro ao carregar configuração: {e}")
                self.config = self._default_config()
        else:
            self.config = self._default_config()
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
