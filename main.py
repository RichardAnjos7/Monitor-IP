"""
Monitor de IPs - Aplicação Desktop
Interface gráfica com até 4 painéis de monitoramento
Tema Matrix/Hacking
"""
import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from typing import Optional
from ping_monitor import PingMonitor
from ip_catalog import IPCatalog


class PingPanel:
    """Painel individual para monitorar um IP"""
    
    # Cores do tema Matrix/Hacking
    BG_COLOR = "#0a0a0a"  # Preto muito escuro
    FG_COLOR = "#00ff41"  # Verde Matrix
    ACCENT_COLOR = "#00cc33"  # Verde mais escuro
    DARK_GREEN = "#003300"  # Verde muito escuro
    BORDER_COLOR = "#00ff41"  # Borda verde
    ERROR_COLOR = "#ff0040"  # Vermelho neon
    WARNING_COLOR = "#ffaa00"  # Laranja neon
        
    def __init__(self, parent_frame, app, panel_id: int):
        self.parent_frame = parent_frame
        self.app = app
        self.panel_id = panel_id
        self.monitor: Optional[PingMonitor] = None
        self.history = deque(maxlen=20)  # Histórico dos últimos 20 pings
        
        # Frame principal do painel com tema Matrix
        self.frame = tk.Frame(parent_frame, bg=self.BG_COLOR, relief='solid', bd=2, highlightbackground=self.BORDER_COLOR, highlightthickness=1)
        # Permite que o frame se adapte ao tamanho disponível
        
        # Título do painel
        title_frame = tk.Frame(self.frame, bg=self.BG_COLOR)
        title_label = tk.Label(
            title_frame,
            text=f">>> PAINEL {panel_id + 1} <<<",
            font=('Consolas', 11, 'bold'),
            bg=self.BG_COLOR,
            fg=self.FG_COLOR
        )
        title_label.pack()
        title_frame.pack(fill='x', pady=(10, 5))
        
        # Campo de entrada de IP
        self.ip_frame = tk.Frame(self.frame, bg=self.BG_COLOR)
        self.ip_label = tk.Label(
            self.ip_frame,
            text="[IP/HOST]:",
            font=('Consolas', 9, 'bold'),
            bg=self.BG_COLOR,
            fg=self.FG_COLOR
        )
        self.ip_entry = tk.Entry(
            self.ip_frame,
            width=20,  # Largura base, será ajustada dinamicamente
            font=('Consolas', 10),
            bg="#000000",
            fg=self.FG_COLOR,
            insertbackground=self.FG_COLOR,
            selectbackground=self.DARK_GREEN,
            selectforeground=self.FG_COLOR,
            relief='solid',
            bd=1,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1,
            highlightcolor=self.FG_COLOR
        )
        self.ip_entry.bind('<Return>', lambda e: self.start_monitoring())
        self.ip_entry.bind('<FocusIn>', lambda e: self.ip_entry.config(highlightbackground=self.FG_COLOR))
        self.ip_entry.bind('<FocusOut>', lambda e: self.ip_entry.config(highlightbackground=self.BORDER_COLOR))
        
        # Botões de controle com estilo hacker
        self.control_frame = tk.Frame(self.frame, bg=self.BG_COLOR)
        
        def create_hacker_button(parent, text, command, width=12, state='normal'):
            btn = tk.Button(
                parent,
                text=f"[{text}]",
                command=command,
                width=width,
                font=('Consolas', 8, 'bold'),
                bg="#000000",
                fg=self.FG_COLOR,
                activebackground=self.DARK_GREEN,
                activeforeground=self.FG_COLOR,
                relief='solid',
                bd=1,
                highlightbackground=self.BORDER_COLOR,
                highlightthickness=1,
                cursor='hand2',
                state=state
            )
            btn.bind('<Enter>', lambda e: btn.config(bg=self.DARK_GREEN, highlightbackground=self.FG_COLOR))
            btn.bind('<Leave>', lambda e: btn.config(bg="#000000", highlightbackground=self.BORDER_COLOR))
            return btn
        
        self.start_btn = create_hacker_button(
            self.control_frame,
            "INICIAR",
            self.start_monitoring,
            width=12
        )
        self.pause_btn = create_hacker_button(
            self.control_frame,
            "PAUSAR",
            self.toggle_pause,
            width=12,
            state='disabled'
        )
        self.remove_btn = create_hacker_button(
            self.control_frame,
            "REMOVER",
            self.remove,
            width=12
        )
        
        # Frame de status com estilo terminal
        self.status_frame = tk.Frame(self.frame, bg=self.BG_COLOR)
        self.status_label = tk.Label(
            self.status_frame,
            text="[STATUS]: -",
            font=('Consolas', 10, 'bold'),
            bg=self.BG_COLOR,
            fg=self.FG_COLOR,
            anchor='w'
        )
        self.rtt_label = tk.Label(
            self.status_frame,
            text="[RTT]: -",
            font=('Consolas', 9),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            anchor='w'
        )
        self.timestamp_label = tk.Label(
            self.status_frame,
            text="[TIMESTAMP]: -",
            font=('Consolas', 8),
            bg=self.BG_COLOR,
            fg=self.ACCENT_COLOR,
            anchor='w'
        )
        
        # Histórico com estilo terminal hacker
        self.history_frame = tk.Frame(self.frame, bg=self.BG_COLOR)
        self.history_label = tk.Label(
            self.history_frame,
            text="[LOG] Últimas 20 entradas:",
            font=('Consolas', 8, 'bold'),
            bg=self.BG_COLOR,
            fg=self.FG_COLOR,
            anchor='w'
        )
        self.history_text = tk.Text(
            self.history_frame,
            height=8,  # Altura base, será ajustada dinamicamente
            width=50,  # Largura base, será ajustada dinamicamente
            font=('Consolas', 9),
            state='disabled',
            wrap='word',
            bg="#000000",
            fg=self.FG_COLOR,
            insertbackground=self.FG_COLOR,
            selectbackground=self.DARK_GREEN,
            selectforeground=self.FG_COLOR,
            relief='solid',
            bd=1,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.history_scroll = tk.Scrollbar(
            self.history_frame,
            orient='vertical',
            command=self.history_text.yview,
            bg=self.BG_COLOR,
            troughcolor=self.BG_COLOR,
            activebackground=self.DARK_GREEN,
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=1
        )
        self.history_text.configure(yscrollcommand=self.history_scroll.set)
        
        # Botão de ação (Salvar) com estilo hacker
        self.action_frame = tk.Frame(self.frame, bg=self.BG_COLOR)
        self.save_btn = create_hacker_button(
            self.action_frame,
            "SALVAR",
            self.save_details,
            width=18
        )
        
        # Layout responsivo
        self.ip_label.pack(side='left', padx=5)
        self.ip_entry.pack(side='left', padx=5, fill='x', expand=True)
        self.ip_frame.pack(fill='x', pady=5)
        
        self.start_btn.pack(side='left', padx=3, fill='x', expand=True)
        self.pause_btn.pack(side='left', padx=3, fill='x', expand=True)
        self.remove_btn.pack(side='left', padx=3, fill='x', expand=True)
        self.control_frame.pack(fill='x', pady=5)
        
        self.status_label.pack(anchor='w', padx=5, fill='x')
        self.rtt_label.pack(anchor='w', padx=5, fill='x')
        self.timestamp_label.pack(anchor='w', padx=5, fill='x')
        self.status_frame.pack(fill='x', pady=5)
        
        self.history_label.pack(anchor='w', padx=5, pady=(0, 3), fill='x')
        # Layout responsivo do histórico
        self.history_text.pack(side='left', fill='both', expand=True)
        self.history_scroll.pack(side='right', fill='y')
        self.history_frame.pack(fill='both', expand=True, pady=5)
        
        # Botão de ação
        self.save_btn.pack(side='left', padx=3, fill='x', expand=True)
        self.action_frame.pack(fill='x', pady=5)
    
    def start_monitoring(self):
        """Inicia o monitoramento do IP"""
        ip = self.ip_entry.get().strip()
        if not ip:
            messagebox.showwarning("Aviso", "Por favor, digite um IP ou hostname.")
            return
        
        # Para monitoramento anterior se existir
        if self.monitor:
            self.monitor.stop()
        
        # Obtém intervalo da aplicação (tela de monitoramento)
        if hasattr(self.app, 'frames') and 'MonitorScreen' in self.app.frames:
            interval = self.app.frames['MonitorScreen'].get_interval()
        else:
            interval = 5
        
        # Cria novo monitor
        self.monitor = PingMonitor(ip, interval, self.on_ping_result)
        self.monitor.start()
        
        # Atualiza UI
        self.ip_entry.config(state='disabled')
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal', text="[PAUSAR]")
        self.status_label.config(text=f"[STATUS]: Monitorando {ip}...", fg=self.FG_COLOR)
    
    def on_ping_result(self, ping_result: dict):
        """Callback chamado após cada ping"""
        # Salva no histórico
        self.history.append(ping_result)
        
        # Atualiza UI (precisa ser thread-safe)
        self.frame.after(0, self._update_ui, ping_result)
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Formata timestamp para o formato: 2024-01-15 | 14:30:45"""
        try:
            if 'T' in timestamp:
                # Formato ISO 8601: 2024-01-15T14:30:45.123456
                date_part, time_part = timestamp.split('T')
                time_part = time_part.split('.')[0]  # Remove milissegundos
                return f"{date_part} | {time_part}"
            else:
                # Tenta outros formatos
                if len(timestamp) >= 19:
                    date_part = timestamp[:10]
                    time_part = timestamp[11:19]
                    return f"{date_part} | {time_part}"
                else:
                    return timestamp
        except:
            return timestamp
    
    def _format_ping_line(self, ping_result: dict) -> str:
        """Formata a linha do ping no estilo hacker/terminal"""
        status = ping_result.get('status', 'UNKNOWN')
        ip = ping_result.get('ip', '')
        if not ip:
            ip = self.ip_entry.get().strip()
        rtt_ms = ping_result.get('rtt_ms')
        ttl = ping_result.get('ttl')
        bytes_size = ping_result.get('bytes')
        timestamp = ping_result.get('timestamp', '')
        
        # Formata timestamp: 2024-01-15 | 14:30:45
        formatted_timestamp = self._format_timestamp(timestamp) if timestamp else "N/A"
        
        if status == 'OK':
            # Formato estilo hacker
            parts = []
            
            # Bytes (padrão 32 bytes no Windows)
            if bytes_size:
                parts.append(f"bytes={bytes_size}")
            else:
                parts.append("bytes=32")
            
            # Tempo de resposta
            if rtt_ms is not None and rtt_ms > 0:
                if rtt_ms < 1:
                    parts.append("time<1ms")
                else:
                    parts.append(f"time={int(round(rtt_ms))}ms")
            else:
                parts.append("time=?")
            
            # TTL
            if ttl:
                parts.append(f"TTL={ttl}")
            
            # Formato estilo terminal hacker
            result_line = f"[{formatted_timestamp}] >> Resposta de {ip}: {' '.join(parts)}"
            return result_line
        elif status == 'TIMEOUT':
            return f"[{formatted_timestamp}] >> !!! Tempo esgotado."
        else:  # ERROR
            error_msg = ping_result.get('output', 'Erro desconhecido').lower()
            if 'could not find host' in error_msg or 'não foi possível encontrar' in error_msg or 'não conseguiu encontrar' in error_msg:
                return f"[{formatted_timestamp}] >> !!! Não foi possível encontrar o host {ip}. Por favor, verifique o nome e tente novamente."
            elif 'destination host unreachable' in error_msg or 'host de destino inacessível' in error_msg:
                return f"[{formatted_timestamp}] >> !!! Host de destino inacessível."
            elif 'request timed out' in error_msg or 'tempo esgotado' in error_msg:
                return f"[{formatted_timestamp}] >> !!! Tempo esgotado."
            else:
                # Trunca mensagem de erro se muito longa
                short_error = error_msg[:60].strip()
                return f"[{formatted_timestamp}] >> !!! ERRO para {ip}: {short_error}"
    
    def _update_ui(self, ping_result: dict):
        """Atualiza a interface do usuário"""
        status = ping_result.get('status', 'UNKNOWN')
        rtt_ms = ping_result.get('rtt_ms')
        ttl = ping_result.get('ttl')
        bytes_size = ping_result.get('bytes')
        timestamp = ping_result.get('timestamp', '')
        ip = ping_result.get('ip', self.ip_entry.get().strip())
        
        # Atualiza status com cores Matrix
        status_color = {
            'OK': self.FG_COLOR,
            'TIMEOUT': self.WARNING_COLOR,
            'ERROR': self.ERROR_COLOR
        }
        status_text_map = {
            'OK': 'CONECTADO',
            'TIMEOUT': 'TEMPO ESGOTADO',
            'ERROR': 'ERRO'
        }
        color = status_color.get(status, self.FG_COLOR)
        status_text = status_text_map.get(status, status)
        self.status_label.config(
            text=f"[STATUS]: {status_text}",
            fg=color
        )
        
        # Atualiza informações detalhadas com estilo hacker
        info_parts = []
        if rtt_ms is not None:
            info_parts.append(f"RTT: {rtt_ms:.2f}ms")
        if ttl is not None:
            info_parts.append(f"TTL: {ttl}")
        if bytes_size is not None:
            info_parts.append(f"BYTES: {bytes_size}")
        
        if info_parts:
            self.rtt_label.config(text=f"[INFO]: {' | '.join(info_parts)}")
        else:
            self.rtt_label.config(text="[INFO]: RTT: -")
        
        # Atualiza timestamp no formato: 2024-01-15 | 14:30:45
        formatted_timestamp = self._format_timestamp(timestamp) if timestamp else "N/A"
        self.timestamp_label.config(text=f"[TIMESTAMP]: {formatted_timestamp}")
        
        # Atualiza histórico no formato CMD
        self.history_text.config(state='normal')
        try:
            # Garante que o IP está no resultado
            if 'ip' not in ping_result:
                ping_result['ip'] = ip
            
            ping_line = self._format_ping_line(ping_result)
            if ping_line and ping_line.strip():
                self.history_text.insert('end', ping_line + '\n')
            else:
                # Fallback se a formatação falhar
                self.history_text.insert('end', f"[{formatted_timestamp}] Reply from {ip}: Status: {status}\n")
            self.history_text.see('end')
        except Exception as e:
            # Em caso de erro, mostra pelo menos o status com informações básicas
            error_info = f"Status: {status}"
            if rtt_ms is not None:
                error_info += f" | RTT: {rtt_ms:.2f}ms"
            self.history_text.insert('end', f"[{formatted_timestamp}] Reply from {ip}: {error_info} (Erro na formatação)\n")
            self.history_text.see('end')
        finally:
            self.history_text.config(state='disabled')
    
    def toggle_pause(self):
        """Alterna entre pausar e retomar"""
        if self.monitor:
            # Alterna o estado
            is_paused = self.monitor.toggle_pause()
            
            # Atualiza o botão imediatamente
            if is_paused:
                self.pause_btn.config(text="[RETOMAR]")
                self.status_label.config(text=f"[STATUS]: PAUSADO", fg=self.WARNING_COLOR)
            else:
                self.pause_btn.config(text="[PAUSAR]")
                # Restaura status de monitoramento se houver IP
                ip = self.ip_entry.get().strip()
                if ip:
                    self.status_label.config(text=f"[STATUS]: Monitorando {ip}...", fg=self.FG_COLOR)
            
            # Força atualização da UI
            self.frame.update_idletasks()
    
    def remove(self):
        """Remove o monitoramento e limpa o painel"""
        if self.monitor:
            self.monitor.stop()
            self.monitor = None
        
        # Limpa UI
        self.ip_entry.config(state='normal')
        self.ip_entry.delete(0, 'end')
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text="[PAUSAR]")
        self.status_label.config(text="[STATUS]: -", fg=self.FG_COLOR)
        self.rtt_label.config(text="[INFO]: RTT: -")
        self.timestamp_label.config(text="[TIMESTAMP]: -")
        
        self.history_text.config(state='normal')
        self.history_text.delete('1.0', 'end')
        self.history_text.config(state='disabled')
        
        self.history.clear()
        
        # Esconde o painel (remove do grid)
        self.frame.grid_remove()
        
        # Atualiza contagem de painéis visíveis na aplicação
        if self.app:
            self.app.visible_panels = max(0, self.app.visible_panels - 1)
            self.app._update_panels_count()
    
    def save_details(self):
        """Salva os detalhes do histórico em um arquivo"""
        from tkinter import filedialog
        from datetime import datetime
        
        # Obtém o conteúdo do histórico
        self.history_text.config(state='normal')
        history_content = self.history_text.get('1.0', 'end-1c')
        self.history_text.config(state='disabled')
        
        if not history_content.strip():
            messagebox.showwarning("Aviso", "Não há histórico para salvar.")
            return
        
        # Obtém IP do painel
        ip = self.ip_entry.get().strip() or "unknown"
        
        # Sugere nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"ping_details_{ip}_{timestamp}.txt"
        
        # Abre diálogo para salvar arquivo
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Arquivo de Texto", "*.txt"),
                ("Todos os arquivos", "*.*")
            ],
            initialfile=default_filename,
            title="Salvar Detalhes do Ping"
        )
        
        if filename:
            try:
                # Prepara conteúdo completo
                header = f"{'='*70}\n"
                header += f"Detalhes do Monitor de Ping - {ip}\n"
                header += f"Painel: {self.panel_id + 1}\n"
                header += f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                header += f"{'='*70}\n\n"
                
                # Status atual
                status_text = self.status_label.cget('text')
                rtt_text = self.rtt_label.cget('text')
                timestamp_text = self.timestamp_label.cget('text')
                
                current_info = f"Status Atual:\n"
                current_info += f"  {status_text}\n"
                current_info += f"  {rtt_text}\n"
                current_info += f"  {timestamp_text}\n\n"
                current_info += f"{'='*70}\n"
                current_info += f"Histórico de Pings:\n"
                current_info += f"{'='*70}\n\n"
                
                full_content = header + current_info + history_content
                
                # Salva arquivo
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(full_content)
                
                messagebox.showinfo("Sucesso", f"Detalhes salvos em:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")
    
    def stop(self):
        """Para o monitoramento"""
        if self.monitor:
            self.monitor.stop()


class HomeScreen(tk.Frame):
    """Tela inicial da aplicação"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#0a0a0a")
        self.controller = controller
        
        # Container centralizado
        center_frame = tk.Frame(self, bg="#0a0a0a")
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Título
        title_label = tk.Label(
            center_frame,
            text=">>> MONITOR DE IPS <<<",
            font=('Consolas', 24, 'bold'),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        title_label.pack(pady=(0, 20))
        
        subtitle_label = tk.Label(
            center_frame,
            text="Sistema de Monitoramento de Rede",
            font=('Consolas', 12),
            bg="#0a0a0a",
            fg="#00cc33"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Botões
        buttons_frame = tk.Frame(center_frame, bg="#0a0a0a")
        buttons_frame.pack()
        
        btn_monitor = controller.create_add_button(
            buttons_frame,
            "MONITORAR",
            lambda: controller.show_frame('MonitorScreen'),
            width=30
        )
        btn_monitor.pack(pady=10)
        
        btn_catalog = controller.create_add_button(
            buttons_frame,
            "CATALOGO",
            lambda: controller.show_frame('CatalogScreen'),
            width=30
        )
        btn_catalog.pack(pady=10)


class MonitorScreen(tk.Frame):
    """Tela de monitoramento de IPs"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#0a0a0a")
        self.controller = controller
        
        # Botão voltar
        back_frame = tk.Frame(self, bg="#0a0a0a")
        back_frame.pack(fill='x', padx=10, pady=10)
        
        btn_back = controller.create_add_button(
            back_frame,
            "< VOLTAR",
            lambda: controller.show_frame('HomeScreen'),
            width=15
        )
        btn_back.pack(side='left')
        
        # Título
        title_frame = tk.Frame(self, bg="#0a0a0a")
        title_label = tk.Label(
            title_frame,
            text=">>> MONITORAMENTO <<<",
            font=('Consolas', 16, 'bold'),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        title_label.pack()
        title_frame.pack(pady=10)
        
        # Configuração de intervalo
        self.config_frame = tk.Frame(self, bg="#0a0a0a", relief='solid', bd=2, highlightbackground="#00ff41", highlightthickness=1)
        config_inner = tk.Frame(self.config_frame, bg="#0a0a0a")
        interval_label = tk.Label(
            config_inner,
            text="[INTERVALO]:",
            font=('Consolas', 9, 'bold'),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        self.interval_var = tk.IntVar(value=5)
        self.interval_spinbox = tk.Spinbox(
            config_inner,
            from_=1,
            to=60,
            textvariable=self.interval_var,
            width=10,
            font=('Consolas', 10),
            bg="#000000",
            fg="#00ff41",
            insertbackground="#00ff41",
            selectbackground="#003300",
            selectforeground="#00ff41",
            relief='solid',
            bd=1,
            highlightbackground="#00ff41",
            highlightthickness=1,
            highlightcolor="#00ff41"
        )
        interval_unit_label = tk.Label(
            config_inner,
            text="segundos",
            font=('Consolas', 9),
            bg="#0a0a0a",
            fg="#00cc33"
        )
        self.config_frame.pack(fill='x', padx=10, pady=5)
        config_inner.pack(pady=8)
        interval_label.pack(side='left', padx=5)
        self.interval_spinbox.pack(side='left', padx=5)
        interval_unit_label.pack(side='left', padx=5)
        
        # Frame para botão de adicionar painel
        self.add_panel_frame = tk.Frame(self, bg="#0a0a0a")
        self.add_panel_frame.pack(fill='x', padx=10, pady=5)
        
        # Frame para painéis
        self.panels_frame = tk.Frame(self, bg="#0a0a0a")
        self.panels_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Vincula redimensionamento
        self._resize_timer = None
        self.controller.root.bind('<Configure>', self._on_window_resize)
        
        self.add_panel_btn = controller.create_add_button(
            self.add_panel_frame,
            "+ ADICIONAR PAINEL",
            self.add_panel,
            width=22
        )
        self.add_panel_btn.pack(side='left', padx=5)
        
        # Label para mostrar quantidade de painéis
        self.panels_count_label = tk.Label(
            self.add_panel_frame,
            text="[PAINEIS]: 1/4",
            font=('Consolas', 9, 'bold'),
            bg="#0a0a0a",
            fg="#00cc33"
        )
        self.panels_count_label.pack(side='left', padx=15)
        
        # Cria lista de painéis (máximo 4)
        self.panels = []
        self.max_panels = 4
        self.visible_panels = 0
        
        # Cria o primeiro painel
        self.add_panel()
    
    def add_panel(self):
        """Adiciona um novo painel"""
        if self.visible_panels >= self.max_panels:
            messagebox.showinfo("Limite atingido", f"Máximo de {self.max_panels} painéis permitidos.")
            return
        
        if len(self.panels) > self.visible_panels:
            panel = self.panels[self.visible_panels]
            row = self.visible_panels // 2
            col = self.visible_panels % 2
            panel.frame.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
        else:
            panel = PingPanel(self.panels_frame, self.controller, self.visible_panels)
            self.panels.append(panel)
            row = self.visible_panels // 2
            col = self.visible_panels % 2
            panel.frame.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
        
        self.visible_panels += 1
        self._update_panels_layout()
        self._update_panels_count()
    
    def _update_panels_layout(self):
        """Atualiza o layout dos painéis"""
        max_cols = 2
        num_rows = (self.visible_panels + 1) // 2 if self.visible_panels > 0 else 1
        
        window_width = self.controller.root.winfo_width()
        window_height = self.controller.root.winfo_height()
        
        available_height = max(400, window_height - 220)
        available_width = max(600, window_width - 40)
        
        if num_rows > 0:
            row_height = max(200, int(available_height / num_rows) - 10)
        else:
            row_height = 200
        
        col_width = max(300, int(available_width / 2) - 10)
        
        for i in range(max_cols):
            self.panels_frame.grid_columnconfigure(i, weight=1, minsize=col_width)
        for i in range(num_rows):
            self.panels_frame.grid_rowconfigure(i, weight=1, minsize=row_height)
    
    def _update_panels_count(self):
        """Atualiza o label com a quantidade de painéis"""
        self.panels_count_label.config(text=f"[PAINEIS]: {self.visible_panels}/{self.max_panels}")
        
        if self.visible_panels >= self.max_panels:
            self.add_panel_btn.config(state='disabled', fg="#00cc33")
        else:
            self.add_panel_btn.config(state='normal', fg="#00ff41")
    
    def get_interval(self) -> int:
        """Retorna o intervalo configurado"""
        return self.interval_var.get()
    
    def _on_window_resize(self, event):
        """Atualiza layout quando a janela é redimensionada"""
        if event.widget == self.controller.root:
            if self._resize_timer:
                self.controller.root.after_cancel(self._resize_timer)
            self._resize_timer = self.controller.root.after(200, self._update_panels_layout)


class CatalogScreen(tk.Frame):
    """Tela de catálogo de IPs"""
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#0a0a0a")
        self.controller = controller
        
        # Botão voltar
        back_frame = tk.Frame(self, bg="#0a0a0a")
        back_frame.pack(fill='x', padx=10, pady=10)
        
        btn_back = controller.create_add_button(
            back_frame,
            "< VOLTAR",
            lambda: controller.show_frame('HomeScreen'),
            width=15
        )
        btn_back.pack(side='left')
        
        # Título
        title_frame = tk.Frame(self, bg="#0a0a0a")
        title_label = tk.Label(
            title_frame,
            text=">>> CATALOGO DE IPS <<<",
            font=('Consolas', 16, 'bold'),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        title_label.pack()
        title_frame.pack(pady=10)
        
        # Frame superior direito para adicionar novos IPs
        top_frame = tk.Frame(self, bg="#0a0a0a")
        top_frame.pack(fill='x', padx=10, pady=10)
        
        add_frame = tk.Frame(top_frame, bg="#0a0a0a", relief='solid', bd=2, highlightbackground="#00ff41", highlightthickness=1)
        add_frame.pack(side='right', padx=10)
        
        add_label = tk.Label(
            add_frame,
            text="[ADICIONAR NOVO IP]:",
            font=('Consolas', 10, 'bold'),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        add_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Campos de entrada
        fields_frame = tk.Frame(add_frame, bg="#0a0a0a")
        fields_frame.pack(fill='x', padx=10, pady=5)
        
        # Nome
        name_label = tk.Label(
            fields_frame,
            text="[NOME]:",
            font=('Consolas', 9, 'bold'),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.name_entry = tk.Entry(
            fields_frame,
            font=('Consolas', 10),
            bg="#000000",
            fg="#00ff41",
            insertbackground="#00ff41",
            selectbackground="#003300",
            selectforeground="#00ff41",
            relief='solid',
            bd=1,
            highlightbackground="#00ff41",
            highlightthickness=1,
            width=25
        )
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # IP
        ip_label = tk.Label(
            fields_frame,
            text="[IP/HOST]:",
            font=('Consolas', 9, 'bold'),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        ip_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        self.ip_entry = tk.Entry(
            fields_frame,
            font=('Consolas', 10),
            bg="#000000",
            fg="#00ff41",
            insertbackground="#00ff41",
            selectbackground="#003300",
            selectforeground="#00ff41",
            relief='solid',
            bd=1,
            highlightbackground="#00ff41",
            highlightthickness=1,
            width=25
        )
        self.ip_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        fields_frame.grid_columnconfigure(1, weight=1)
        
        # Botão salvar
        btn_frame = tk.Frame(add_frame, bg="#0a0a0a")
        btn_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        btn_save = controller.create_add_button(
            btn_frame,
            "SALVAR",
            self.save_ip,
            width=18
        )
        btn_save.pack(side='right', padx=5)
        
        # Bind Enter nos campos
        self.name_entry.bind('<Return>', lambda e: self.ip_entry.focus())
        self.ip_entry.bind('<Return>', lambda e: self.save_ip())
        
        # Frame para lista de IPs
        list_frame = tk.Frame(self, bg="#0a0a0a")
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        list_label = tk.Label(
            list_frame,
            text="[IPS CADASTRADOS]:",
            font=('Consolas', 10, 'bold'),
            bg="#0a0a0a",
            fg="#00ff41"
        )
        list_label.pack(anchor='w', pady=(0, 10))
        
        # Container para os cards de IPs (4 por linha)
        self.cards_container = tk.Frame(list_frame, bg="#0a0a0a")
        self.cards_container.pack(fill='both', expand=True)
        
        # Atualiza a lista
        self.refresh_catalog()
    
    def save_ip(self):
        """Salva um novo IP no catálogo"""
        name = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()
        
        if not name or not ip:
            messagebox.showwarning("Aviso", "Por favor, preencha nome e IP.")
            return
        
        if self.controller.ip_catalog.add(name, ip):
            self.name_entry.delete(0, tk.END)
            self.ip_entry.delete(0, tk.END)
            self.refresh_catalog()
            messagebox.showinfo("Sucesso", f"IP '{name}' adicionado ao catálogo.")
        else:
            messagebox.showwarning("Aviso", f"O nome '{name}' já existe no catálogo.")
    
    def refresh_catalog(self):
        """Atualiza a exibição do catálogo em formato de grid"""
        # Limpa cards existentes
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        
        # Obtém todos os IPs
        all_ips = self.controller.ip_catalog.get_all()
        
        if not all_ips:
            empty_label = tk.Label(
                self.cards_container,
                text="[Nenhum IP cadastrado]",
                font=('Consolas', 10),
                bg="#0a0a0a",
                fg="#00cc33"
            )
            empty_label.pack(pady=50)
            return
        
        # Organiza em colunas de 4
        items_per_row = 4
        row = 0
        col = 0
        
        for name, ip in all_ips:
            # Card para cada IP
            card = tk.Frame(
                self.cards_container,
                bg="#000000",
                relief='solid',
                bd=1,
                highlightbackground="#00ff41",
                highlightthickness=1
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            # Frame para o botão X no canto superior direito
            top_frame = tk.Frame(card, bg="#000000")
            top_frame.pack(fill='x', side='top')
            
            # Botão X para remover
            btn_remove_x = tk.Button(
                top_frame,
                text="✕",
                font=('Consolas', 12, 'bold'),
                bg="#000000",
                fg="#ff0040",
                activebackground="#003300",
                activeforeground="#ff0040",
                relief='flat',
                bd=0,
                cursor='hand2',
                command=lambda n=name: self.remove_ip(n),
                width=3,
                height=1
            )
            btn_remove_x.pack(side='right', padx=5, pady=5)
            btn_remove_x.bind('<Enter>', lambda e: btn_remove_x.config(bg="#003300"))
            btn_remove_x.bind('<Leave>', lambda e: btn_remove_x.config(bg="#000000"))
            
            # Nome
            name_label = tk.Label(
                card,
                text=name,
                font=('Consolas', 12, 'bold'),
                bg="#000000",
                fg="#00ff41"
            )
            name_label.pack(pady=(5, 10), padx=15)
            
            # Botão PING
            btn_ping = self.controller.create_add_button(
                card,
                "PING",
                lambda ip_addr=ip: self.ping_ip(ip_addr),
                width=12
            )
            btn_ping.pack(pady=(0, 15))
            
            col += 1
            if col >= items_per_row:
                col = 0
                row += 1
        
        # Configura grid weights
        for i in range(items_per_row):
            self.cards_container.grid_columnconfigure(i, weight=1)
    
    def remove_ip(self, name):
        """Remove um IP do catálogo"""
        if messagebox.askyesno("Confirmar", f"Remover '{name}' do catálogo?"):
            if self.controller.ip_catalog.remove(name):
                self.refresh_catalog()
                messagebox.showinfo("Sucesso", f"'{name}' removido do catálogo.")
            else:
                messagebox.showerror("Erro", f"Erro ao remover '{name}'.")
    
    def ping_ip(self, ip_addr):
        """Inicia monitoramento do IP selecionado"""
        self.controller.show_frame('MonitorScreen')
        # Aguarda um pouco para a tela carregar
        self.controller.root.after(100, lambda: self._start_ping(ip_addr))
    
    def _start_ping(self, ip_addr):
        """Inicia o ping no primeiro painel disponível"""
        monitor_screen = self.controller.frames['MonitorScreen']
        if monitor_screen.panels:
            panel = monitor_screen.panels[0]
            panel.ip_entry.config(state='normal')
            panel.ip_entry.delete(0, tk.END)
            panel.ip_entry.insert(0, ip_addr)
            panel.start_monitoring()


class PingMonitorApp:
    """Aplicação principal do Monitor de IPs"""
    
    # Cores do tema Matrix/Hacking
    BG_COLOR = "#0a0a0a"
    FG_COLOR = "#00ff41"
    ACCENT_COLOR = "#00cc33"
    DARK_GREEN = "#003300"
    BORDER_COLOR = "#00ff41"
    
    def __init__(self, root):
        self.root = root
        self.root.title(">>> MONITOR DE IPS <<<")
        # Obtém o tamanho da tela
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        # Define tamanho inicial como 90% da tela
        initial_width = int(screen_width * 0.9)
        initial_height = int(screen_height * 0.9)
        self.root.geometry(f"{initial_width}x{initial_height}")
        self.root.configure(bg=self.BG_COLOR)
        # Permite redimensionamento - mínimo responsivo
        min_width = min(800, int(screen_width * 0.5))
        min_height = min(600, int(screen_height * 0.5))
        self.root.minsize(min_width, min_height)
        # Centraliza a janela
        x = (screen_width - initial_width) // 2
        y = (screen_height - initial_height) // 2
        self.root.geometry(f"{initial_width}x{initial_height}+{x}+{y}")
        
        # Catálogo de IPs
        self.ip_catalog = IPCatalog()
        
        # Função auxiliar para criar botões com estilo hacker
        def create_add_button(parent, text, command, width=20):
            btn = tk.Button(
                parent,
                text=f"[{text}]",
                command=command,
                width=width,
                font=('Consolas', 9, 'bold'),
                bg="#000000",
                fg=self.FG_COLOR,
                activebackground=self.DARK_GREEN,
                activeforeground=self.FG_COLOR,
                relief='solid',
                bd=1,
                highlightbackground=self.BORDER_COLOR,
                highlightthickness=1,
                cursor='hand2'
            )
            btn.bind('<Enter>', lambda e: btn.config(bg=self.DARK_GREEN, highlightbackground=self.FG_COLOR))
            btn.bind('<Leave>', lambda e: btn.config(bg="#000000", highlightbackground=self.BORDER_COLOR))
            return btn
        
        # Guarda a função para uso posterior
        self.create_add_button = create_add_button
        
        # Container principal para todas as telas
        self.container = tk.Frame(root, bg=self.BG_COLOR)
        self.container.pack(fill='both', expand=True)
        
        # Dicionário para armazenar as telas
        self.frames = {}
        
        # Cria todas as telas
        for F in (HomeScreen, MonitorScreen, CatalogScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        
        # Mostra a tela inicial
        self.show_frame('HomeScreen')
        
        # Handler para fechar aplicação
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_frame(self, page_name):
        """Mostra um frame e esconde os outros"""
        frame = self.frames[page_name]
        frame.tkraise()
    
    def on_closing(self):
        """Handler para fechamento da aplicação"""
        # Para todos os monitores de todas as telas
        if 'MonitorScreen' in self.frames:
            monitor_screen = self.frames['MonitorScreen']
            for panel in monitor_screen.panels:
                panel.stop()
        self.root.destroy()


def main():
    """Função principal"""
    root = tk.Tk()
    app = PingMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

