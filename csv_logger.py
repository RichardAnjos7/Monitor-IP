"""
Logger CSV para salvar logs de ping
"""
import csv
import os
from datetime import datetime
from typing import Optional


class CSVLogger:
    """Classe para salvar logs de ping em arquivo CSV"""
    
    def __init__(self, log_file: str = "ping_logs.csv"):
        """
        Inicializa o logger CSV
        
        Args:
            log_file: Caminho do arquivo CSV
        """
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

