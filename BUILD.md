# Como Criar o Executável

Este guia mostra como criar um executável (.exe) do Monitor de IPs para distribuição.

## Método 1: Usando build.bat (Windows)

1. Abra o Prompt de Comando (CMD) na pasta do projeto
2. Execute:
   ```cmd
   build.bat
   ```
3. O executável será criado na pasta `dist\MonitorIP.exe`

## Método 2: Usando build.py (Multiplataforma)

1. Abra o terminal na pasta do projeto
2. Execute:
   ```bash
   python build.py
   ```
3. O executável será criado na pasta `dist\MonitorIP.exe` (Windows) ou `dist\MonitorIP` (Linux/Mac)

## Método 3: Manualmente com PyInstaller

1. Instale o PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Execute o comando:
   ```bash
   pyinstaller --onefile --windowed --name "MonitorIP" main.py
   ```

3. O executável será criado em `dist\MonitorIP.exe`

## Incluir Arquivos de Dados

Se você quiser incluir o arquivo `ip_catalog.json` no executável (para IPs pré-cadastrados):

```bash
pyinstaller --onefile --windowed --name "MonitorIP" --add-data "ip_catalog.json;." main.py
```

**Nota para Linux/Mac:** Use `:` ao invés de `;`:
```bash
pyinstaller --onefile --windowed --name "MonitorIP" --add-data "ip_catalog.json:." main.py
```

## Distribuição

O arquivo executável estará na pasta `dist/`. Você pode:
- Copiar o arquivo `MonitorIP.exe` para qualquer computador Windows
- Executar diretamente sem precisar instalar Python
- Distribuir o executável para outros usuários

## Requisitos do Sistema

- **Windows:** O executável funciona em Windows 7 ou superior
- **Não requer Python instalado** no computador de destino
- O executável pode ser grande (~15-20MB) pois inclui o Python e todas as dependências

## Solução de Problemas

### Erro: "PyInstaller não encontrado"
```bash
pip install pyinstaller
```

### Erro: "tkinter não encontrado"
O tkinter geralmente vem com o Python. Se não estiver instalado:
- **Windows:** Instale o Python completo
- **Linux:** `sudo apt-get install python3-tk`
- **Mac:** Já vem instalado

### Executável não abre
- Verifique se o antivírus não está bloqueando
- Execute como administrador
- Verifique os logs em `dist\MonitorIP.log`

## Arquivos Gerados

Após criar o executável, você terá:
- `dist/MonitorIP.exe` - O executável principal
- `build/` - Arquivos temporários de build
- `MonitorIP.spec` - Arquivo de configuração do PyInstaller

**Nota:** Você pode excluir as pastas `build/` e `__pycache__/` após criar o executável.

