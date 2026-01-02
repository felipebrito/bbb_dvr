"""Janela de configuração acessível via hotkey F12."""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from config_manager import ConfigManager


class ConfigWindow:
    """Janela de configuração para editar settings da aplicação."""
    
    def __init__(self, config_manager: ConfigManager, on_save_callback=None):
        self.config_manager = config_manager
        self.on_save_callback = on_save_callback
        self.window = None
        self.dvr_entries = []
        self.grid_entries = []
    
    def show(self):
        """Mostra janela de configuração."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return
        
        self.window = tk.Toplevel()
        self.window.title("Configuração - DVR Camera Viewer")
        self.window.geometry("800x700")
        self.window.resizable(True, True)
        
        # Frame principal com scroll
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seção DVR Servers
        dvr_frame = ttk.LabelFrame(main_frame, text="Servidores DVR", padding="10")
        dvr_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.dvr_container = ttk.Frame(dvr_frame)
        self.dvr_container.pack(fill=tk.BOTH, expand=True)
        
        self._load_dvr_servers()
        
        btn_add_dvr = ttk.Button(dvr_frame, text="+ Adicionar DVR", command=self._add_dvr_server)
        btn_add_dvr.pack(pady=5)
        
        # Seção Grids
        grids_frame = ttk.LabelFrame(main_frame, text="Grids de Exibição", padding="10")
        grids_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.grids_container = ttk.Frame(grids_frame)
        self.grids_container.pack(fill=tk.BOTH, expand=True)
        
        self._load_grids()
        
        btn_add_grid = ttk.Button(grids_frame, text="+ Adicionar Grid", command=self._add_grid)
        btn_add_grid.pack(pady=5)
        
        # Configurações Gerais
        general_frame = ttk.LabelFrame(main_frame, text="Configurações Gerais", padding="10")
        general_frame.pack(fill=tk.BOTH, pady=5)
        
        ttk.Label(general_frame, text="Duração da Transição (segundos):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.transition_entry = ttk.Entry(general_frame, width=10)
        self.transition_entry.insert(0, str(self.config_manager.get_transition_duration()))
        self.transition_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(general_frame, text="Modo da Janela:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.window_mode_var = tk.StringVar(value=self.config_manager.get_window_mode())
        window_mode_combo = ttk.Combobox(general_frame, textvariable=self.window_mode_var, 
                                        values=["fullscreen", "windowed"], width=15, state="readonly")
        window_mode_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Salvar", command=self._save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self._close).pack(side=tk.LEFT, padx=5)
    
    def _load_dvr_servers(self):
        """Carrega servidores DVR na interface."""
        for widget in self.dvr_container.winfo_children():
            widget.destroy()
        self.dvr_entries.clear()
        
        servers = self.config_manager.get_dvr_servers()
        for i, server in enumerate(servers):
            self._create_dvr_entry(i, server)
    
    def _create_dvr_entry(self, index, server=None):
        """Cria entrada de DVR na interface."""
        frame = ttk.Frame(self.dvr_container)
        frame.pack(fill=tk.X, pady=2)
        
        entry_data = {}
        
        ttk.Label(frame, text="IP:").grid(row=0, column=0, padx=2)
        ip_entry = ttk.Entry(frame, width=15)
        ip_entry.insert(0, server.get("ip", "") if server else "")
        ip_entry.grid(row=0, column=1, padx=2)
        entry_data["ip"] = ip_entry
        
        ttk.Label(frame, text="Porta:").grid(row=0, column=2, padx=2)
        port_entry = ttk.Entry(frame, width=8)
        port_entry.insert(0, str(server.get("port", 554)) if server else "554")
        port_entry.grid(row=0, column=3, padx=2)
        entry_data["port"] = port_entry
        
        ttk.Label(frame, text="Usuário:").grid(row=0, column=4, padx=2)
        user_entry = ttk.Entry(frame, width=12)
        user_entry.insert(0, server.get("username", "") if server else "")
        user_entry.grid(row=0, column=5, padx=2)
        entry_data["username"] = user_entry
        
        ttk.Label(frame, text="Senha:").grid(row=0, column=6, padx=2)
        pass_entry = ttk.Entry(frame, width=12, show="*")
        pass_entry.insert(0, server.get("password", "") if server else "")
        pass_entry.grid(row=0, column=7, padx=2)
        entry_data["password"] = pass_entry
        
        ttk.Label(frame, text="Canais:").grid(row=0, column=8, padx=2)
        channels_entry = ttk.Entry(frame, width=15)
        channels_str = ",".join(map(str, server.get("channels", []))) if server else ""
        channels_entry.insert(0, channels_str)
        channels_entry.grid(row=0, column=9, padx=2)
        entry_data["channels"] = channels_entry
        
        btn_remove = ttk.Button(frame, text="Remover", command=lambda: self._remove_dvr(index))
        btn_remove.grid(row=0, column=10, padx=2)
        
        entry_data["frame"] = frame
        self.dvr_entries.append(entry_data)
    
    def _add_dvr_server(self):
        """Adiciona novo servidor DVR."""
        self._create_dvr_entry(len(self.dvr_entries), None)
    
    def _remove_dvr(self, index):
        """Remove servidor DVR."""
        if index < len(self.dvr_entries):
            self.dvr_entries[index]["frame"].destroy()
            self.dvr_entries.pop(index)
            # Recria entradas para atualizar índices
            self._load_dvr_servers()
    
    def _load_grids(self):
        """Carrega grids na interface."""
        for widget in self.grids_container.winfo_children():
            widget.destroy()
        self.grid_entries.clear()
        
        grids = self.config_manager.get_grids()
        for i, grid in enumerate(grids):
            self._create_grid_entry(i, grid)
    
    def _create_grid_entry(self, index, grid=None):
        """Cria entrada de grid na interface."""
        frame = ttk.Frame(self.grids_container)
        frame.pack(fill=tk.X, pady=2)
        
        entry_data = {}
        
        ttk.Label(frame, text="Câmeras (índices separados por vírgula):").grid(row=0, column=0, padx=2)
        cameras_entry = ttk.Entry(frame, width=20)
        cameras_str = ",".join(map(str, grid.get("cameras", []))) if grid else ""
        cameras_entry.insert(0, cameras_str)
        cameras_entry.grid(row=0, column=1, padx=2)
        entry_data["cameras"] = cameras_entry
        
        ttk.Label(frame, text="Tempo de Exibição (segundos):").grid(row=0, column=2, padx=2)
        time_entry = ttk.Entry(frame, width=10)
        time_entry.insert(0, str(grid.get("display_time", 10)) if grid else "10")
        time_entry.grid(row=0, column=3, padx=2)
        entry_data["display_time"] = time_entry
        
        btn_remove = ttk.Button(frame, text="Remover", command=lambda: self._remove_grid(index))
        btn_remove.grid(row=0, column=4, padx=2)
        
        entry_data["frame"] = frame
        self.grid_entries.append(entry_data)
    
    def _add_grid(self):
        """Adiciona novo grid."""
        self._create_grid_entry(len(self.grid_entries), None)
    
    def _remove_grid(self, index):
        """Remove grid."""
        if index < len(self.grid_entries):
            self.grid_entries[index]["frame"].destroy()
            self.grid_entries.pop(index)
            # Recria entradas para atualizar índices
            self._load_grids()
    
    def _save_config(self):
        """Salva configuração."""
        try:
            # Salva servidores DVR
            dvr_servers = []
            for entry in self.dvr_entries:
                try:
                    channels_str = entry["channels"].get()
                    channels = [int(c.strip()) for c in channels_str.split(",") if c.strip()]
                    
                    dvr_servers.append({
                        "ip": entry["ip"].get(),
                        "port": int(entry["port"].get()),
                        "username": entry["username"].get(),
                        "password": entry["password"].get(),
                        "channels": channels
                    })
                except ValueError as e:
                    messagebox.showerror("Erro", f"Erro ao processar servidor DVR: {e}")
                    return
            
            # Salva grids
            grids = []
            for entry in self.grid_entries:
                try:
                    cameras_str = entry["cameras"].get()
                    cameras = [int(c.strip()) for c in cameras_str.split(",") if c.strip()]
                    
                    grids.append({
                        "cameras": cameras,
                        "display_time": float(entry["display_time"].get())
                    })
                except ValueError as e:
                    messagebox.showerror("Erro", f"Erro ao processar grid: {e}")
                    return
            
            # Atualiza configuração
            self.config_manager.set("dvr_servers", dvr_servers)
            self.config_manager.set("grids", grids)
            self.config_manager.set("transition_duration", float(self.transition_entry.get()))
            self.config_manager.set("window_mode", self.window_mode_var.get())
            
            # Salva arquivo
            if self.config_manager.save():
                messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
                if self.on_save_callback:
                    self.on_save_callback()
                self._close()
            else:
                messagebox.showerror("Erro", "Erro ao salvar configuração.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def _close(self):
        """Fecha janela."""
        if self.window:
            self.window.destroy()
            self.window = None
