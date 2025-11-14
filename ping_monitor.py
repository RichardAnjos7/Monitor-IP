"""
Monitor de IPs - Classe principal para gerenciamento de pings
"""
import subprocess
import platform
import re
import time
from datetime import datetime
from typing import Optional, Callable, Dict
import threading


class PingMonitor:
    """Classe para monitorar um IP através de ping"""
    
    def __init__(self, ip: str, interval: int = 5, callback: Optional[Callable] = None):
        """
        Inicializa o monitor de ping
        
        Args:
            ip: IP ou hostname para monitorar
            interval: Intervalo entre pings em segundos (default: 5)
            callback: Função chamada após cada ping (recebe: dict com status, rtt_ms, timestamp, ttl, bytes, output, ip)
        """
        self.ip = ip
        self.interval = interval
        self.callback = callback
        self.is_running = False
        self.is_paused = False
        self.thread = None
        self._stop_event = threading.Event()
        
    def _ping(self) -> Dict:
        """
        Executa um ping e retorna informações detalhadas
        
        Returns:
            Dicionário com: status, rtt_ms, timestamp, ttl, bytes, output
        """
        timestamp = datetime.now().isoformat()
        system = platform.system().lower()
        
        try:
            if system == 'windows':
                # Windows: ping -n 1 -w timeout_ms (aumentado para 5000ms = 5 segundos)
                cmd = ['ping', '-n', '1', '-w', '5000', self.ip]
            else:
                # Linux/Mac: ping -c 1 -W timeout_sec (aumentado para 5 segundos)
                cmd = ['ping', '-c', '1', '-W', '5', self.ip]
            
            # Configuração para evitar que o CMD apareça no Windows
            kwargs = {
                'capture_output': True,
                'text': True,
                'encoding': 'utf-8',
                'errors': 'ignore',
                'timeout': 10  # Aumenta timeout para dar mais tempo
            }
            
            # No Windows, usa CREATE_NO_WINDOW para evitar que o CMD apareça
            if system == 'windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(cmd, **kwargs)
            
            # Parse do resultado
            output_text = (result.stdout or '') + (result.stderr or '')
            output_lower = output_text.lower()
            
            # Verifica se houve resposta (mais confiável que apenas returncode)
            # Windows: "Reply from" ou "Resposta de"
            # Linux: "64 bytes from"
            has_reply = (
                'reply from' in output_lower or 
                'resposta de' in output_lower or
                'bytes from' in output_lower or
                'icmp_seq' in output_lower
            )
            
            # Verifica se é timeout no output
            is_timeout = (
                'timeout' in output_lower or 
                'tempo esgotado' in output_lower or 
                'request timed out' in output_lower or
                'timed out' in output_lower
            )
            
            # Se tem resposta, é OK (independente do returncode em alguns casos)
            if has_reply:
                # Extrair informações detalhadas
                rtt = self._extract_rtt(output_text, system)
                ttl = self._extract_ttl(output_text, system)
                bytes_size = self._extract_bytes(output_text, system)
                
                return {
                    'status': 'OK',
                    'rtt_ms': rtt if rtt else 0.0,
                    'timestamp': timestamp,
                    'ttl': ttl,
                    'bytes': bytes_size,
                    'output': output_text,
                    'ip': self.ip
                }
            elif is_timeout:
                # Timeout confirmado
                return {
                    'status': 'TIMEOUT',
                    'rtt_ms': None,
                    'timestamp': timestamp,
                    'ttl': None,
                    'bytes': None,
                    'output': output_text,
                    'ip': self.ip
                }
            else:
                # Outro tipo de erro
                return {
                    'status': 'ERROR',
                    'rtt_ms': None,
                    'timestamp': timestamp,
                    'ttl': None,
                    'bytes': None,
                    'output': output_text if output_text else f'Returncode: {result.returncode}',
                    'ip': self.ip
                }
                    
        except subprocess.TimeoutExpired:
            return {
                'status': 'TIMEOUT',
                'rtt_ms': None,
                'timestamp': timestamp,
                'ttl': None,
                'bytes': None,
                'output': 'Timeout expired',
                'ip': self.ip
            }
        except Exception as e:
            # Erro de DNS ou outro erro
            return {
                'status': 'ERROR',
                'rtt_ms': None,
                'timestamp': timestamp,
                'ttl': None,
                'bytes': None,
                'output': str(e),
                'ip': self.ip
            }
    
    def _extract_ttl(self, output: str, system: str) -> Optional[int]:
        """Extrai o TTL (Time To Live) do output do ping"""
        try:
            if system == 'windows':
                # Windows: "Reply from 8.8.8.8: bytes=32 time=72ms TTL=111"
                # Procura na linha de resposta primeiro
                for line in output.split('\n'):
                    if 'reply from' in line.lower() or 'resposta de' in line.lower():
                        patterns = [
                            r'TTL\s*=\s*(\d+)',
                            r'TTL:(\d+)',
                            r'ttl=(\d+)',
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, line, re.IGNORECASE)
                            if match:
                                return int(match.group(1))
                
                # Se não encontrou na linha de resposta, tenta no texto todo
                patterns = [
                    r'TTL\s*=\s*(\d+)',
                    r'TTL:(\d+)',
                    r'ttl=(\d+)',
                ]
            else:
                # Linux: "ttl=64"
                patterns = [
                    r'ttl=(\d+)',
                    r'TTL=(\d+)',
                ]
            
            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    return int(match.group(1))
            
            return None
        except (ValueError, IndexError):
            return None
    
    def _extract_bytes(self, output: str, system: str) -> Optional[int]:
        """Extrai o tamanho do pacote em bytes do output do ping"""
        try:
            if system == 'windows':
                # Windows: "Reply from 8.8.8.8: bytes=32 time=72ms TTL=111"
                # Procura na linha de resposta primeiro
                for line in output.split('\n'):
                    if 'reply from' in line.lower() or 'resposta de' in line.lower():
                        # Procura "bytes=32" na linha
                        match = re.search(r'bytes[=:](\d+)', line, re.IGNORECASE)
                        if match:
                            return int(match.group(1))
                
                # Se não encontrou, procura padrões genéricos
                patterns = [
                    r'bytes[=:](\d+)',  # bytes=32 ou bytes:32
                    r'(\d+)\s*bytes',   # 32 bytes
                    r'(\d+)\s*Bytes',   # 32 Bytes
                ]
            else:
                # Linux: "64 bytes from 8.8.8.8"
                patterns = [
                    r'(\d+)\s*bytes',
                    r'bytes[=:](\d+)',
                ]
            
            for pattern in patterns:
                matches = re.findall(pattern, output, re.IGNORECASE)
                if matches:
                    # Pega o primeiro match (tamanho do pacote enviado)
                    return int(matches[0])
            
            return None
        except (ValueError, IndexError):
            return None
    
    def _extract_rtt(self, output: str, system: str) -> Optional[float]:
        """Extrai o tempo de resposta (RTT) do output do ping"""
        try:
            if system == 'windows':
                # Windows: "Reply from 8.8.8.8: bytes=32 time=72ms TTL=111"
                # Procura primeiro na linha de resposta (mais confiável)
                for line in output.split('\n'):
                    if 'reply from' in line.lower() or 'resposta de' in line.lower():
                        # Procura "time=72ms" ou "tempo=72ms" na linha
                        match = re.search(r'time[<>=](\d+)ms|tempo[<>=](\d+)ms', line, re.IGNORECASE)
                        if match:
                            value = match.group(1) if match.group(1) else match.group(2)
                            if value:
                                return float(value)
                
                # Se não encontrou na linha de resposta, tenta padrões gerais
                patterns = [
                    r'Tempo\s*=\s*(\d+)ms',           # PT: Tempo = 12ms
                    r'Tempo\s*médio\s*=\s*(\d+)ms',   # PT: Tempo médio = 12ms
                    r'Average\s*=\s*(\d+)ms',         # EN: Average = 12ms
                    r'time[<>=](\d+)ms',              # EN: time=72ms ou time<1ms
                    r'tempo[<>=](\d+)ms',             # PT: tempo=72ms
                    r'Minimum\s*=\s*(\d+)ms',        # EN: Minimum = 12ms
                    r'Maximum\s*=\s*(\d+)ms',        # EN: Maximum = 12ms
                ]
            else:
                # Linux/Mac: "64 bytes from 8.8.8.8: icmp_seq=1 ttl=111 time=12.345 ms"
                patterns = [
                    r'time=(\d+\.?\d*)\s*ms',         # time=12.345 ms
                    r'time[<>=](\d+\.?\d*)\s*ms',     # time<1ms ou time=12ms
                ]
            
            # Tenta cada padrão em ordem
            for pattern in patterns:
                matches = re.findall(pattern, output, re.IGNORECASE)
                if matches:
                    # Pega o primeiro match (mais confiável)
                    value = matches[0]
                    return float(value)
            
            return None
        except (ValueError, IndexError):
            return None
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.is_running and not self._stop_event.is_set():
            if not self.is_paused:
                ping_result = self._ping()
                if self.callback:
                    self.callback(ping_result)
            
            # Aguarda o intervalo (ou até ser interrompido)
            self._stop_event.wait(self.interval)
    
    def start(self):
        """Inicia o monitoramento"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self._stop_event.clear()
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Para o monitoramento"""
        self.is_running = False
        self._stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)
    
    def pause(self):
        """Pausa o monitoramento"""
        self.is_paused = True
    
    def resume(self):
        """Resume o monitoramento"""
        self.is_paused = False
    
    def toggle_pause(self):
        """Alterna entre pausado e ativo"""
        if self.is_paused:
            self.resume()
            return False  # Agora está ativo (não pausado)
        else:
            self.pause()
            return True  # Agora está pausado

