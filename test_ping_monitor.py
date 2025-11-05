"""
Testes básicos para o Monitor de IPs
"""
import unittest
import time
import os
from ping_monitor import PingMonitor
from csv_logger import CSVLogger


class TestCSVLogger(unittest.TestCase):
    """Testes para o CSVLogger"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.test_file = "test_ping_logs.csv"
        self.logger = CSVLogger(self.test_file)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_logger_creates_file(self):
        """Testa se o logger cria o arquivo CSV"""
        self.assertTrue(os.path.exists(self.test_file))
    
    def test_logger_has_header(self):
        """Testa se o CSV tem o cabeçalho correto"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            header = f.readline().strip()
            self.assertEqual(header, 'timestamp,ip,rtt_ms,status')
    
    def test_logger_saves_entry(self):
        """Testa se o logger salva uma entrada"""
        self.logger.log("2024-01-15T10:30:45", "8.8.8.8", 12.5, "OK")
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)  # Header + 1 entrada
            self.assertIn("8.8.8.8", lines[1])
            self.assertIn("OK", lines[1])
    
    def test_logger_handles_none_rtt(self):
        """Testa se o logger trata RTT None corretamente"""
        self.logger.log("2024-01-15T10:30:45", "invalid.host", None, "ERROR")
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertIn("ERROR", lines[1])
            # Verifica que o campo rtt_ms está vazio
            parts = lines[1].strip().split(',')
            self.assertEqual(parts[2], '')


class TestPingMonitor(unittest.TestCase):
    """Testes para o PingMonitor"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.results = []
    
    def ping_callback(self, status, rtt_ms, timestamp):
        """Callback para coletar resultados de ping"""
        self.results.append((status, rtt_ms, timestamp))
    
    def test_monitor_creation(self):
        """Testa criação do monitor"""
        monitor = PingMonitor("8.8.8.8", interval=1, callback=self.ping_callback)
        self.assertIsNotNone(monitor)
        self.assertEqual(monitor.ip, "8.8.8.8")
        self.assertEqual(monitor.interval, 1)
        self.assertFalse(monitor.is_running)
    
    def test_monitor_start_stop(self):
        """Testa iniciar e parar o monitor"""
        monitor = PingMonitor("8.8.8.8", interval=1, callback=self.ping_callback)
        
        monitor.start()
        self.assertTrue(monitor.is_running)
        self.assertFalse(monitor.is_paused)
        
        time.sleep(2)  # Aguarda 2 segundos para ter pelo menos um ping
        
        monitor.stop()
        self.assertFalse(monitor.is_running)
        
        # Verifica se houve pelo menos um resultado
        self.assertGreater(len(self.results), 0)
        
        # Verifica formato do resultado
        status, rtt_ms, timestamp = self.results[0]
        self.assertIn(status, ['OK', 'TIMEOUT', 'ERROR'])
        self.assertIsNotNone(timestamp)
    
    def test_monitor_pause_resume(self):
        """Testa pausar e retomar o monitor"""
        monitor = PingMonitor("8.8.8.8", interval=1, callback=self.ping_callback)
        
        monitor.start()
        time.sleep(1)
        
        initial_count = len(self.results)
        
        monitor.pause()
        self.assertTrue(monitor.is_paused)
        time.sleep(2)  # Durante pausa, não deve fazer ping
        
        paused_count = len(self.results)
        # Não deve ter novos resultados durante pausa
        self.assertEqual(paused_count, initial_count)
        
        monitor.resume()
        self.assertFalse(monitor.is_paused)
        time.sleep(2)  # Após retomar, deve fazer ping
        
        monitor.stop()
        # Deve ter novos resultados após retomar
        self.assertGreater(len(self.results), paused_count)
    
    def test_monitor_invalid_ip(self):
        """Testa monitor com IP inválido"""
        monitor = PingMonitor("999.999.999.999", interval=1, callback=self.ping_callback)
        
        monitor.start()
        time.sleep(2)
        monitor.stop()
        
        # Deve ter tentado fazer ping e recebido ERROR ou TIMEOUT
        self.assertGreater(len(self.results), 0)
        status = self.results[0][0]
        self.assertIn(status, ['ERROR', 'TIMEOUT'])


class TestIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.test_file = "test_integration_logs.csv"
        self.logger = CSVLogger(self.test_file)
        self.results = []
    
    def ping_callback(self, status, rtt_ms, timestamp):
        """Callback que salva no logger"""
        ip = "8.8.8.8"
        self.logger.log(timestamp, ip, rtt_ms, status)
        self.results.append((status, rtt_ms, timestamp))
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_monitor_with_logger(self):
        """Testa integração entre monitor e logger"""
        monitor = PingMonitor("8.8.8.8", interval=1, callback=self.ping_callback)
        
        monitor.start()
        time.sleep(2)
        monitor.stop()
        
        # Verifica se há resultados
        self.assertGreater(len(self.results), 0)
        
        # Verifica se o CSV foi atualizado
        with open(self.test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Deve ter pelo menos header + 1 entrada
            self.assertGreaterEqual(len(lines), 2)


def run_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("Executando testes do Monitor de IPs")
    print("=" * 60)
    print()
    
    # Cria suíte de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adiciona testes
    suite.addTests(loader.loadTestsFromTestCase(TestCSVLogger))
    suite.addTests(loader.loadTestsFromTestCase(TestPingMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Executa testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumo
    print()
    print("=" * 60)
    print(f"Testes executados: {result.testsRun}")
    print(f"Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

