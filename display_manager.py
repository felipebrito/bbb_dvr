"""Gerenciamento de exibição de grid 2x2 com transições fade."""
import numpy as np
import cv2
import time
from typing import Optional, List, Tuple


class DisplayManager:
    """Gerencia composição de grid 2x2 e transições."""
    
    def __init__(self, stream_manager, target_width: int = 1920, target_height: int = 1080):
        self.stream_manager = stream_manager
        self.target_width = target_width
        self.target_height = target_height
        self.cell_width = target_width // 2
        self.cell_height = target_height // 2
        self.current_grid_index = 0
        self.current_grid_start_time = 0
        self.transition_start_time = 0
        self.in_transition = False
        self.transition_alpha = 0.0
        self.current_grid_frames: List[Optional[np.ndarray]] = [None, None, None, None]
        self.next_grid_frames: List[Optional[np.ndarray]] = [None, None, None, None]
    
    def get_current_grid(self, config_manager) -> List[int]:
        """Obtém lista de câmeras do grid atual."""
        grids = config_manager.get_grids()
        if not grids:
            return []
        return grids[self.current_grid_index].get("cameras", [])
    
    def should_rotate(self, config_manager) -> bool:
        """Verifica se deve rotacionar para próximo grid."""
        grids = config_manager.get_grids()
        if not grids or len(grids) <= 1:
            return False
        
        # Não deve rotacionar se já está em transição
        if self.in_transition:
            return False
        
        current_grid = grids[self.current_grid_index]
        display_time = current_grid.get("display_time", 15)
        elapsed = time.time() - self.current_grid_start_time
        
        return elapsed >= display_time
    
    def start_transition(self) -> None:
        """Inicia transição fade."""
        self.in_transition = True
        self.transition_start_time = time.time()
        self.transition_alpha = 0.0
    
    def update_transition(self, config_manager) -> bool:
        """Atualiza transição fade. Retorna True se transição completa."""
        if not self.in_transition:
            return False
        
        transition_duration = config_manager.get_transition_duration()
        elapsed = time.time() - self.transition_start_time
        
        if elapsed >= transition_duration:
            self.transition_alpha = 1.0
            # Marca transição como completa, mas não reseta aqui (deixa para o main.py)
            return True
        
        self.transition_alpha = elapsed / transition_duration
        return False
    
    def rotate_to_next_grid(self, config_manager) -> None:
        """Rotaciona para próximo grid e reseta timer."""
        grids = config_manager.get_grids()
        if not grids:
            return
        
        # Rotaciona para próximo grid
        self.current_grid_index = (self.current_grid_index + 1) % len(grids)
        # Reseta timer para começar contagem dos 15 segundos
        self.current_grid_start_time = time.time()
    
    def compose_grid(self, camera_indices: List[int], wait_for_all: bool = True) -> Optional[np.ndarray]:
        """Compõe grid 2x2 com frames das câmeras especificadas.
        
        Args:
            camera_indices: Lista de índices das câmeras
            wait_for_all: Se True, só retorna grid quando todas as câmeras tiverem frames válidos
        """
        if len(camera_indices) < 4:
            # Preenche com None se não houver 4 câmeras
            camera_indices = camera_indices + [None] * (4 - len(camera_indices))
        
        frames = []
        all_ready = True
        
        for idx in camera_indices[:4]:
            if idx is not None:
                frame = self.stream_manager.get_frame(idx)
                if frame is not None and frame.size > 0:
                    # Redimensiona para tamanho da célula
                    resized = cv2.resize(frame, (self.cell_width, self.cell_height))
                    frames.append(resized)
                else:
                    # Frame não disponível
                    all_ready = False
                    if wait_for_all:
                        # Se esperando por todos, retorna None
                        return None
                    else:
                        # Placeholder preto se não esperando
                        frames.append(np.zeros((self.cell_height, self.cell_width, 3), dtype=np.uint8))
            else:
                # Placeholder preto se índice inválido
                frames.append(np.zeros((self.cell_height, self.cell_width, 3), dtype=np.uint8))
        
        if not frames or len(frames) < 4:
            return None
        
        # Compõe grid 2x2
        # Top row: frames[0] | frames[1]
        # Bottom row: frames[2] | frames[3]
        top_row = np.hstack([frames[0], frames[1]])
        bottom_row = np.hstack([frames[2], frames[3]])
        grid = np.vstack([top_row, bottom_row])
        
        return grid
    
    def render_frame(self, config_manager, wait_for_all: bool = True) -> Optional[np.ndarray]:
        """Renderiza frame atual com transição se necessário.
        
        Args:
            config_manager: Gerenciador de configuração
            wait_for_all: Se True, só retorna quando todas as câmeras tiverem frames
        """
        grids = config_manager.get_grids()
        if not grids:
            return None
        
        # Determina qual grid usar na transição
        if self.in_transition and hasattr(self, '_target_grid_index'):
            # Transição para grid específico (tecla 1 ou 2)
            next_index = self._target_grid_index
        elif self.in_transition:
            # Transição automática para próximo
            next_index = (self.current_grid_index + 1) % len(grids)
        else:
            next_index = None
        
        current_cameras = self.get_current_grid(config_manager)
        current_frame = self.compose_grid(current_cameras, wait_for_all=wait_for_all)
        
        if current_frame is None:
            return None
        
        # Se em transição, compõe com próximo grid
        if self.in_transition and next_index is not None:
            next_cameras = grids[next_index].get("cameras", [])
            next_frame = self.compose_grid(next_cameras, wait_for_all=wait_for_all)
            
            if next_frame is not None:
                # Aplica fade: current_frame fade out, next_frame fade in
                alpha = self.transition_alpha
                blended = cv2.addWeighted(current_frame, 1.0 - alpha, next_frame, alpha, 0)
                return blended
        
        return current_frame
    
    def switch_to_grid(self, grid_index: int, config_manager) -> None:
        """Troca para um grid específico com fade."""
        grids = config_manager.get_grids()
        if not grids or grid_index < 0 or grid_index >= len(grids):
            return
        
        if grid_index != self.current_grid_index:
            self._target_grid_index = grid_index
            self.start_transition()
    
    def _apply_grid_switch(self, config_manager) -> None:
        """Aplica troca de grid após transição manual."""
        if hasattr(self, '_target_grid_index'):
            self.current_grid_index = self._target_grid_index
            # Reseta timer para começar contagem dos 15 segundos
            self.current_grid_start_time = time.time()
            self.in_transition = False
            self.transition_alpha = 0.0
            delattr(self, '_target_grid_index')
    
    def reset(self, config_manager) -> None:
        """Reseta estado do display manager."""
        grids = config_manager.get_grids()
        if grids:
            self.current_grid_index = 0
            self.current_grid_start_time = time.time()
            self.in_transition = False
            self.transition_alpha = 0.0
