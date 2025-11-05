# Monitor de IPs

Aplicação desktop para monitorar múltiplos IPs ou hostnames simultaneamente através de ping.

## Características

- ✅ Interface gráfica simples e intuitiva
- ✅ Até 8 painéis de monitoramento simultâneos
- ✅ Suporte para IPs IPv4 e hostnames
- ✅ Ping automático configurável (padrão: 5 segundos)
- ✅ Exibição de status (OK/TIMEOUT/ERROR), tempo de resposta (ms) e timestamp ISO 8601
- ✅ Histórico dos últimos 20 pings por painel
- ✅ Controles de pausar/retomar e remover IPs
- ✅ Logs automáticos em arquivo CSV
- ✅ Compatível com Windows e Linux
- ✅ Tratamento robusto de erros (DNS, timeouts, etc.)

## Requisitos

- Python 3.7 ou superior
- Sistema operacional: Windows ou Linux

**Nota:** Não são necessárias dependências externas além do Python padrão. A aplicação usa apenas bibliotecas da biblioteca padrão do Python.

## Instalação

1. Clone ou baixe este repositório
2. Certifique-se de ter Python 3.7+ instalado:
   ```bash
   python --version
   ```
   ou
   ```bash
   python3 --version
   ```

## Uso

### Executar a aplicação

```bash
python main.py
```

ou

```bash
python3 main.py
```

### Como usar

1. **Configurar intervalo**: Defina o intervalo entre pings (em segundos) no campo "Configurações" no topo da janela (padrão: 5 segundos)

2. **Adicionar IP**:

   - Digite um IP (ex: `8.8.8.8`) ou hostname (ex: `google.com`) no campo "IP/Host" de qualquer painel
   - Pressione Enter ou clique em "Iniciar"
   - O monitoramento começa automaticamente

3. **Pausar/Retomar**: Clique no botão "Pausar" para pausar o monitoramento. O botão muda para "Retomar" quando pausado.

4. **Remover**: Clique em "Remover" para parar o monitoramento e limpar o painel

5. **Visualizar histórico**: Cada painel mostra os últimos 20 pings no campo "Histórico"

### Logs CSV

Os logs são salvos automaticamente no arquivo `ping_logs.csv` no mesmo diretório da aplicação.

Formato do CSV:

```csv
timestamp,ip,rtt_ms,status
2024-01-15T10:30:45.123456,8.8.8.8,12.5,OK
2024-01-15T10:30:50.234567,8.8.8.8,TIMEOUT
```

Campos:

- `timestamp`: Timestamp ISO 8601 do ping
- `ip`: IP ou hostname monitorado
- `rtt_ms`: Tempo de resposta em milissegundos (vazio se não disponível)
- `status`: Status do ping (OK, TIMEOUT, ERROR)

## Estrutura do Projeto

```
Monitor Ping/
├── main.py              # Aplicação principal com interface gráfica
├── ping_monitor.py      # Classe para gerenciamento de pings
├── csv_logger.py        # Classe para salvar logs em CSV
├── test_ping_monitor.py # Testes básicos
├── README.md            # Este arquivo
└── ping_logs.csv        # Arquivo de logs (criado automaticamente)
```

## Testes

Execute os testes básicos:

```bash
python test_ping_monitor.py
```

ou

```bash
python3 test_ping_monitor.py
```

## Tratamento de Erros

A aplicação trata automaticamente:

- **Timeouts**: Quando o ping não recebe resposta dentro do tempo limite
- **Erros de DNS**: Quando o hostname não pode ser resolvido
- **IPs inválidos**: Quando o IP informado não é válido
- **Erros de rede**: Problemas de conectividade

Todos os erros são registrados no CSV com status apropriado.

## Compatibilidade

### Windows

- Usa o comando `ping -n 1 -w 3000` (timeout de 3 segundos)
- Detecta automaticamente o formato de saída do Windows

### Linux

- Usa o comando `ping -c 1 -W 3` (1 pacote, timeout de 3 segundos)
- Compatível com distribuições baseadas em Debian, Red Hat, etc.

## Limitações

- Máximo de 8 painéis simultâneos
- Histórico limitado a 20 pings por painel
- Timeout fixo de 3 segundos por ping (configurável no código se necessário)

## Solução de Problemas

### A aplicação não inicia

- Verifique se o Python 3.7+ está instalado
- Certifique-se de estar executando o comando no diretório correto

### Pings sempre retornam TIMEOUT

- Verifique sua conexão com a internet
- Teste manualmente o ping no terminal:
  - Windows: `ping 8.8.8.8`
  - Linux: `ping -c 1 8.8.8.8`

### Erro de permissão ao salvar CSV

- Verifique se você tem permissão de escrita no diretório
- Tente executar como administrador (se necessário)

## Licença

Este projeto é de código aberto e pode ser usado livremente.

## Autor

Desenvolvido como projeto de monitoramento de IPs.
