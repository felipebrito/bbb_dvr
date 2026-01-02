"""Aplicação principal do DVR Camera Mosaic Viewer."""
import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import time
import sys
import os
from PIL import Image, ImageTk
from config_manager import ConfigManager
from stream_manager import StreamManager
from display_manager import DisplayManager
from config_window import ConfigWindow

# Ajusta path para funcionar quando empacotado como .app
if getattr(sys, 'frozen', False):
    # Se está rodando como executável empacotado
    application_path = sys._MEIPASS
    os.chdir(os.path.dirname(sys.executable))
else:
    # Se está rodando como script Python
    application_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(application_path)


class CameraViewerApp:
    """Aplicação principal de visualização de câmeras."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.config_manager = ConfigManager()
        self.stream_manager = StreamManager(self.config_manager)
        self.display_manager = DisplayManager(self.stream_manager)
        self.config_window = None
        
        # Configura janela
        self.root.title("DVR Camera Viewer")
        self.root.configure(bg='black')
        
        # Remove bordas e decorações para modo fullscreen
        if self.config_manager.get_window_mode() == "fullscreen":
            self.root.attributes('-fullscreen', True)
            self.root.overrideredirect(True)
        else:
            self.root.geometry("1920x1080")
        
        # Canvas para exibição de vídeo
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Tela de loading
        self.loading_canvas = None
        self.loading_text_id = None
        self.loading_progress_id = None
        self.loading_animation_id = None
        self._show_loading_screen()
        
        # Barra de progresso (2px de altura na parte inferior)
        self.progress_bar_id = None
        
        # Bind hotkeys
        self.root.bind('<Key-c>', self._open_config)
        self.root.bind('<Key-C>', self._open_config)
        self.root.bind('<Key-q>', self._quit_app)
        self.root.bind('<Key-Q>', self._quit_app)
        self.root.bind('<Key-1>', lambda e: self._switch_to_grid(0))
        self.root.bind('<Key-2>', lambda e: self._switch_to_grid(1))
        self.root.bind('<Key-3>', lambda e: self._switch_to_grid(2))
        self.root.bind('<Key-4>', lambda e: self._switch_to_grid(3))
        self.root.bind('<Key-a>', self._toggle_auto_mode)
        self.root.bind('<Key-A>', self._toggle_auto_mode)
        self.root.bind('<Key-f>', self._toggle_fullscreen)
        self.root.bind('<Key-F>', self._toggle_fullscreen)
        self.root.focus_set()  # Garante que a janela receba eventos de teclado
        
        # Modo automático ativado por padrão
        self.auto_mode = True
        
        # Variáveis de controle
        self.running = False
        self.last_frame_time = 0
        self.target_fps = 25
        self.frame_interval = 1.0 / self.target_fps
        self.wait_for_all_frames = True
        
        # Inicia carregamento assíncrono
        self.root.after(100, self._start_loading)
    
    def _show_loading_screen(self):
        """Mostra tela de loading."""
        self.loading_canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.loading_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Texto de loading
        canvas_width = self.root.winfo_screenwidth()
        canvas_height = self.root.winfo_screenheight()
        
        self.loading_canvas.create_text(
            canvas_width // 2, 
            canvas_height // 2 - 50,
            text="Conectando às câmeras...",
            fill='white',
            font=('Arial', 24, 'bold'),
            tags='loading_text'
        )
        
        # Barra de progresso animada
        self.loading_progress_id = self.loading_canvas.create_rectangle(
            canvas_width // 2 - 200,
            canvas_height // 2 + 20,
            canvas_width // 2 - 200,
            canvas_height // 2 + 30,
            fill='white',
            outline='',
            tags='loading_progress'
        )
        
        # Anima a barra de progresso
        self._animate_loading()
    
    def _animate_loading(self):
        """Anima a barra de loading."""
        if self.loading_canvas is None:
            return
        
        canvas_width = self.root.winfo_screenwidth()
        canvas_height = self.root.winfo_screenheight()
        
        # Calcula progresso baseado no tempo (animação visual)
        elapsed = time.time() % 2.0  # Ciclo de 2 segundos
        progress = (elapsed / 2.0) * 400  # 400px de largura
        
        x1 = canvas_width // 2 - 200
        x2 = canvas_width // 2 - 200 + progress
        
        self.loading_canvas.coords(
            self.loading_progress_id,
            x1, canvas_height // 2 + 20,
            x2, canvas_height // 2 + 30
        )
        
        # Continua animando enquanto estiver carregando
        if self.loading_canvas:
            self.root.after(50, self._animate_loading)
    
    def _update_loading_text(self, text: str, progress: float = None):
        """Atualiza texto de loading e progresso."""
        if self.loading_canvas is None:
            return
        
        canvas_width = self.root.winfo_screenwidth()
        canvas_height = self.root.winfo_screenheight()
        
        # Atualiza texto
        self.loading_canvas.delete('loading_text')
        self.loading_canvas.create_text(
            canvas_width // 2,
            canvas_height // 2 - 50,
            text=text,
            fill='white',
            font=('Arial', 24, 'bold'),
            tags='loading_text'
        )
        
        # Atualiza barra de progresso se fornecido
        if progress is not None:
            x1 = canvas_width // 2 - 200
            x2 = canvas_width // 2 - 200 + (progress * 400)
            self.loading_canvas.coords(
                self.loading_progress_id,
                x1, canvas_height // 2 + 20,
                x2, canvas_height // 2 + 30
            )
    
    def _start_loading(self):
        """Inicia carregamento dos streams de forma assíncrona."""
        # Inicia streams
        self.stream_manager.start_all()
        
        # Inicia verificação de conexão
        self._check_connections()
    
    def _check_connections(self):
        """Verifica conexões de forma assíncrona."""
        total_streams = self.stream_manager.get_stream_count()
        connected_count = sum(1 for i in range(total_streams) 
                            if self.stream_manager.streams[i].is_connected())
        
        progress = connected_count / total_streams if total_streams > 0 else 0
        
        # Atualiza texto de loading
        self._update_loading_text(
            f"Conectando às câmeras... {connected_count}/{total_streams}",
            progress
        )
        
        # Verifica se todos estão conectados
        if connected_count == total_streams and total_streams > 0:
            # Todos conectados, finaliza loading
            self.root.after(500, self._finish_loading)  # Aguarda 0.5s para estabilizar
        else:
            # Continua verificando
            self.root.after(500, self._check_connections)
    
    def _finish_loading(self):
        """Finaliza carregamento e inicia exibição."""
        # Remove tela de loading
        if self.loading_canvas:
            self.loading_canvas.destroy()
            self.loading_canvas = None
        
        # Inicializa display manager
        self.display_manager.reset(self.config_manager)
        
        # Garante que o timer do grid atual está inicializado para modo automático
        if self.auto_mode:
            self.display_manager.current_grid_start_time = time.time()
        
        # Inicia loop de exibição
        self.running = True
        self._update_display()
        
        print("Aplicação pronta!")
    
    def _open_config(self, event=None):
        """Abre janela de configuração."""
        if self.config_window and self.config_window.window and self.config_window.window.winfo_exists():
            return
        
        # Sai do fullscreen temporariamente
        was_fullscreen = self.root.attributes('-fullscreen')
        if was_fullscreen:
            self.root.attributes('-fullscreen', False)
            self.root.overrideredirect(False)
        
        self.config_window = ConfigWindow(self.config_manager, on_save_callback=self._on_config_saved)
        self.config_window.show()
        
        # Aguarda fechamento da janela
        self.root.wait_window(self.config_window.window)
        
        # Volta ao fullscreen se estava antes
        if was_fullscreen and self.config_manager.get_window_mode() == "fullscreen":
            self.root.attributes('-fullscreen', True)
            self.root.overrideredirect(True)
    
    def _exit_fullscreen(self, event=None):
        """Sai do modo fullscreen."""
        if self.config_manager.get_window_mode() == "fullscreen":
            self.root.attributes('-fullscreen', False)
            self.root.overrideredirect(False)
    
    def _toggle_fullscreen(self, event=None):
        """Alterna modo fullscreen (tecla F)."""
        is_fullscreen = self.root.attributes('-fullscreen')
        if is_fullscreen:
            self.root.attributes('-fullscreen', False)
            self.root.overrideredirect(False)
            print("Modo fullscreen DESATIVADO")
        else:
            self.root.attributes('-fullscreen', True)
            self.root.overrideredirect(True)
            print("Modo fullscreen ATIVADO")
    
    def _switch_to_grid(self, grid_index: int):
        """Troca para grid específico com fade (teclas 1, 2, 3, 4)."""
        grids = self.config_manager.get_grids()
        if grid_index < len(grids):
            # Desativa modo automático quando troca manualmente
            if self.auto_mode:
                self.auto_mode = False
                print("Modo automático desativado (pressione A para reativar)")
            self.display_manager.switch_to_grid(grid_index, self.config_manager)
            print(f"Trocando para grid {grid_index + 1}: {grids[grid_index].get('name', f'Grid {grid_index + 1}')}")
    
    def _toggle_auto_mode(self, event=None):
        """Ativa/desativa modo automático (tecla A)."""
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            print("Modo automático ATIVADO - Rotação a cada 15s")
            # Reseta timer do grid atual para começar contagem
            self.display_manager.current_grid_start_time = time.time()
        else:
            print("Modo automático DESATIVADO - Use teclas 1, 2, 3, 4 para trocar")
    
    def _quit_app(self, event=None):
        """Sai da aplicação (tecla Q)."""
        print("Saindo da aplicação...")
        self.stop()
    
    def _draw_progress_bar(self, canvas_width: int, canvas_height: int):
        """Desenha barra de progresso de 2px na parte inferior."""
        grids = self.config_manager.get_grids()
        if not grids:
            return
        
        current_grid = grids[self.display_manager.current_grid_index]
        display_time = current_grid.get("display_time", 15)
        elapsed = time.time() - self.display_manager.current_grid_start_time
        
        # Calcula progresso (0.0 a 1.0)
        progress = min(elapsed / display_time, 1.0)
        
        # Desenha barra de progresso (2px de altura, da esquerda para direita)
        bar_height = 2
        bar_y = canvas_height - bar_height
        bar_width = int(canvas_width * progress)
        
        # Cor da barra (branco)
        self.canvas.create_rectangle(0, bar_y, bar_width, canvas_height, 
                                   fill='white', outline='', tags='progress_bar')
    
    def _on_config_saved(self):
        """Callback quando configuração é salva."""
        # Recarrega streams
        self.stream_manager.reload()
        time.sleep(1)
        
        # Reseta display manager
        self.display_manager.reset(self.config_manager)
    
    def _update_display(self):
        """Atualiza exibição de vídeo."""
        if not self.running:
            return
        
        current_time = time.time()
        
        # Controla FPS
        if current_time - self.last_frame_time < self.frame_interval:
            self.root.after(10, self._update_display)
            return
        
        self.last_frame_time = current_time
        
        # Atualiza transição se em progresso
        if self.display_manager.in_transition:
            transition_complete = self.display_manager.update_transition(self.config_manager)
            if transition_complete:
                # Verifica se há troca manual de grid pendente
                if hasattr(self.display_manager, '_target_grid_index'):
                    self.display_manager._apply_grid_switch(self.config_manager)
                else:
                    # Rotação automática - finaliza transição e reseta timer
                    self.display_manager.rotate_to_next_grid(self.config_manager)
                    # Garante que a transição foi finalizada
                    self.display_manager.in_transition = False
                    self.display_manager.transition_alpha = 0.0
        else:
            # Verifica se deve rotacionar grid automaticamente (só se modo automático ativo)
            if self.auto_mode:
                if self.display_manager.should_rotate(self.config_manager):
                    self.display_manager.start_transition()
        
        # Renderiza frame (aguarda todos os frames estarem prontos)
        frame = self.display_manager.render_frame(self.config_manager, wait_for_all=self.wait_for_all_frames)
        
        # Se todos os frames estão prontos, pode desabilitar espera
        if frame is not None and self.wait_for_all_frames:
            self.wait_for_all_frames = False
        
        if frame is not None:
            # Converte BGR para RGB para Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Redimensiona para tamanho do canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                frame_resized = cv2.resize(frame_rgb, (canvas_width, canvas_height))
                
                # Converte para ImageTk
                image = Image.fromarray(frame_resized)
                photo = ImageTk.PhotoImage(image=image)
                
                # Atualiza canvas
                self.canvas.delete("all")
                self.canvas.create_image(canvas_width // 2, canvas_height // 2, 
                                       image=photo, anchor=tk.CENTER)
                self.canvas.image = photo  # Mantém referência
                
                # Desenha barra de progresso se modo automático ativo
                if self.auto_mode and not self.display_manager.in_transition:
                    self._draw_progress_bar(canvas_width, canvas_height)
        
        # Agenda próxima atualização
        self.root.after(10, self._update_display)
    
    def run(self):
        """Inicia aplicação."""
        self.running = True
        self._update_display()
        self.root.mainloop()
    
    def stop(self):
        """Para aplicação."""
        self.running = False
        self.stream_manager.stop_all()
        self.root.quit()


def main():
    """Função principal."""
    try:
        app = CameraViewerApp()
        app.run()
    except KeyboardInterrupt:
        print("Aplicação interrompida pelo usuário")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro fatal: {e}")
        raise


if __name__ == "__main__":
    main()
