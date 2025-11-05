"""
Script para criar executável do Monitor de IPs
"""
import subprocess
import sys
import os

def install_pyinstaller():
    """Instala PyInstaller se não estiver instalado"""
    try:
        import PyInstaller
        print("PyInstaller já está instalado.")
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller instalado com sucesso!")

def create_icon_if_needed():
    """Cria o ícone se não existir"""
    if not os.path.exists("icon.ico"):
        print("Gerando ícone...")
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("Instalando Pillow para gerar ícone...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
            from PIL import Image, ImageDraw, ImageFont
        
        # Importa função de criação do ícone
        import create_icon
        create_icon.create_icon()
        print()

def build_executable():
    """Cria o executável usando PyInstaller"""
    print("=" * 50)
    print("Criando Executável do Monitor de IPs")
    print("=" * 50)
    print()
    
    # Instala PyInstaller se necessário
    install_pyinstaller()
    
    # Gera ícone se necessário
    create_icon_if_needed()
    
    # Limpa builds anteriores
    import shutil
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Pasta {dir_name} removida.")
            except Exception as e:
                print(f"Aviso: Não foi possível remover {dir_name}: {e}")
    
    if os.path.exists("MonitorIP.spec"):
        try:
            os.remove("MonitorIP.spec")
        except:
            pass
    
    # Adiciona ícone se existir
    icon_option = []
    if os.path.exists("icon.ico"):
        icon_option = ["--icon", "icon.ico"]
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",  # Arquivo único
        "--windowed",  # Sem console (só para Windows)
        "--name", "MonitorIP",
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "tkinter.messagebox",
        "--hidden-import", "tkinter.filedialog",
        "--hidden-import", "ping_monitor",
        "--hidden-import", "ip_catalog",
        "main.py"
    ]
    
    # Adiciona opção de ícone se existir
    if icon_option:
        cmd = cmd[:2] + icon_option + cmd[2:]
    
    # Ajusta para Linux/Mac
    if sys.platform != "win32":
        # Remove --windowed para Linux/Mac
        if "--windowed" in cmd:
            cmd.remove("--windowed")
    
    print("Executando PyInstaller...")
    print(" ".join(cmd))
    print()
    
    try:
        subprocess.check_call(cmd)
        print()
        print("=" * 50)
        if sys.platform == "win32":
            exe_name = "MonitorIP.exe"
        else:
            exe_name = "MonitorIP"
        
        exe_path = os.path.join("dist", exe_name)
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print("✓ Executável criado com sucesso!")
            print("=" * 50)
            print(f"Arquivo: {exe_path}")
            print(f"Tamanho: {file_size:.2f} MB")
            print("=" * 50)
        else:
            print("⚠ Executável não encontrado em dist/")
            print("Verifique os logs acima para erros.")
            print("=" * 50)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar executável: {e}")
        print("Verifique se todos os módulos estão instalados.")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

