"""
Logger CSV para salvar logs de ping
"""
import csv
import os
import sys
from datetime import datetime
from typing import Optional


def get_app_data_path(filename):
    """
    Obtém o caminho para salvar dados da aplicação (mesmo diretório do executável)
    
    Args:
        filename: Nome do arquivo
        
    Returns:
        Caminho absoluto onde salvar o arquivo
    """
    if getattr(sys, 'frozen', False):
        # Se está rodando como executável (PyInstaller)
        base_path = os.path.dirname(sys.executable)
    else:
        # Se está rodando como script
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, filename)


class CSVLogger:
    """Classe para salvar logs de ping em arquivo CSV"""
    
    def __init__(self, log_file: str = None):
        """
        Inicializa o logger CSV
        
        Args:
            log_file: Caminho do arquivo CSV (None = usa diretório do executável)
        """
        if log_file is None:
            self.log_file = get_app_data_path("ping_logs.csv")
        else:
            self.log_file = log_file
        self._ensure_header()
    
    def _ensure_header(self):
        """Garante que o arquivo CSV existe com o cabeçalho"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'ip', 'rtt_ms', 'status'])
    
    def log(self, timestamp: str, ip: str, rtt_ms: Optional[float], status: str):
        """
        Salva um registro de ping no CSV
        
        Args:
            timestamp: Timestamp ISO 8601
            ip: IP ou hostname
            rtt_ms: Tempo de resposta em ms (None se não disponível)
            status: Status do ping (OK, TIMEOUT, ERROR)
        """
        try:
            with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                rtt_str = str(rtt_ms) if rtt_ms is not None else ''
                writer.writerow([timestamp, ip, rtt_str, status])
        except Exception as e:
            print(f"Erro ao salvar log: {e}")

