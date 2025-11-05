"""
Gerenciador de Catálogo de IPs
Salva e carrega IPs cadastrados com nomes
"""
import json
import os
import sys
from typing import Dict, List, Tuple, Optional


def get_resource_path(relative_path):
    """
    Obtém o caminho absoluto do recurso, funciona para desenvolvimento e para PyInstaller
    
    Args:
        relative_path: Caminho relativo do recurso
        
    Returns:
        Caminho absoluto do recurso
    """
    try:
        # PyInstaller cria um arquivo temporário e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se não estiver em PyInstaller, usa o diretório atual
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


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


class IPCatalog:
    """Gerenciador do catálogo de IPs cadastrados"""
    
    def __init__(self, catalog_file: str = None):
        """
        Inicializa o catálogo
        
        Args:
            catalog_file: Caminho do arquivo JSON para salvar o catálogo (None = usa diretório do executável)
        """
        if catalog_file is None:
            self.catalog_file = get_app_data_path("ip_catalog.json")
        else:
            self.catalog_file = catalog_file
        self.catalog: Dict[str, str] = {}  # {nome: ip}
        self.load()
    
    def load(self):
        """Carrega o catálogo do arquivo"""
        if os.path.exists(self.catalog_file):
            try:
                with open(self.catalog_file, 'r', encoding='utf-8') as f:
                    self.catalog = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar catálogo: {e}")
                self.catalog = {}
        else:
            self.catalog = {}
            # Adiciona alguns exemplos
            self.catalog = {
                "Google DNS": "8.8.8.8",
                "Cloudflare DNS": "1.1.1.1",
                "Gateway Padrão": "192.168.1.1"
            }
            self.save()
    
    def save(self):
        """Salva o catálogo no arquivo"""
        try:
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump(self.catalog, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar catálogo: {e}")
    
    def add(self, name: str, ip: str) -> bool:
        """
        Adiciona um novo IP ao catálogo
        
        Args:
            name: Nome do IP
            ip: Endereço IP ou hostname
            
        Returns:
            True se adicionado com sucesso, False se o nome já existe
        """
        if name.strip() in self.catalog:
            return False
        self.catalog[name.strip()] = ip.strip()
        self.save()
        return True
    
    def remove(self, name: str) -> bool:
        """
        Remove um IP do catálogo
        
        Args:
            name: Nome do IP a remover
            
        Returns:
            True se removido, False se não encontrado
        """
        if name in self.catalog:
            del self.catalog[name]
            self.save()
            return True
        return False
    
    def get_ip(self, name: str) -> Optional[str]:
        """
        Obtém o IP pelo nome
        
        Args:
            name: Nome do IP
            
        Returns:
            IP ou None se não encontrado
        """
        return self.catalog.get(name)
    
    def get_all(self) -> List[Tuple[str, str]]:
        """
        Retorna todos os IPs do catálogo
        
        Returns:
            Lista de tuplas (nome, ip) ordenada por nome
        """
        return sorted(self.catalog.items(), key=lambda x: x[0])
    
    def get_names(self) -> List[str]:
        """
        Retorna apenas os nomes do catálogo
        
        Returns:
            Lista de nomes ordenada
        """
        return sorted(self.catalog.keys())

