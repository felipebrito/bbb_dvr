# DVR Camera Mosaic Viewer

Aplicação desktop de alta performance para exibição de feeds RTSP de câmeras DVR em grid 2x2, com rotação automática entre diferentes grupos de câmeras.

## 🎯 Características

- **Grid 2x2**: Exibe 4 câmeras simultaneamente em layout 2x2
- **Múltiplos DVRs**: Suporte para até 4 DVRs simultâneos (16 câmeras)
- **Rotação Automática**: Alterna entre diferentes grupos de câmeras automaticamente
- **Transições Fade**: Transições suaves entre grids
- **Controle Manual**: Troca manual entre grids com teclas 1, 2, 3, 4
- **Modo Automático/Manual**: Alterna entre rotação automática e controle manual
- **Barra de Progresso**: Indicador visual do tempo restante em modo automático
- **Configurador**: Interface de configuração acessível via tecla C
- **Alta Performance**: Otimizado para múltiplos streams RTSP em rede gigabit
- **Fullscreen**: Modo fullscreen sem interface visual

## 📋 Requisitos

- Python 3.9 ou superior
- OpenCV com suporte a FFmpeg
- Tkinter (interface gráfica)
- Conexão de rede com acesso aos DVRs

### Instalação do Tkinter (macOS)

Se você estiver usando Python do Homebrew e receber erro `ModuleNotFoundError: No module named '_tkinter'`, instale o suporte ao Tkinter:

```bash
brew install python-tk
```

Depois, recrie o ambiente virtual:
```bash
rm -rf .venv
/opt/homebrew/bin/python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/felipebrito/bbb_dvr.git
cd bbb_dvr
```

2. Instale as dependências:

**Opção 1 - Usando o script (recomendado):**
```bash
./install.sh
```

**Opção 2 - Manualmente:**
```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## ⚙️ Configuração

A configuração inicial está no arquivo `config.json`. Você pode editá-lo manualmente ou usar o configurador (tecla C durante a execução).

### Formato da Configuração

```json
{
  "dvr_servers": [
    {
      "ip": "192.168.1.91",
      "port": 554,
      "username": "admin",
      "password": "123456789@",
      "channels": [1, 2, 3, 4]
    }
  ],
  "grids": [
    {"cameras": [0, 1, 2, 3], "display_time": 15, "name": "DVR 1"},
    {"cameras": [4, 5, 6, 7], "display_time": 15, "name": "DVR 2"}
  ],
  "transition_duration": 1.0,
  "window_mode": "fullscreen"
}
```

### Explicação dos Campos

- **dvr_servers**: Lista de servidores DVR
  - `ip`: Endereço IP do DVR
  - `port`: Porta RTSP (geralmente 554)
  - `username`: Usuário para autenticação RTSP
  - `password`: Senha para autenticação RTSP (suporta caracteres especiais como @)
  - `channels`: Lista de canais a serem capturados

- **grids**: Lista de grids de exibição
  - `cameras`: Índices das câmeras (0-based, na ordem que aparecem nos DVRs)
  - `display_time`: Tempo de exibição em segundos (padrão: 15s)
  - `name`: Nome descritivo do grid (opcional)

- **transition_duration**: Duração da transição fade em segundos
- **window_mode**: "fullscreen" ou "windowed"

## 🎮 Uso

Execute a aplicação:

**Opção 1 - Usando o script (recomendado):**
```bash
./run.sh
```

**Opção 2 - Manualmente:**
```bash
source .venv/bin/activate
python main.py
```

### Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| **1, 2, 3, 4** | Troca manual para grid específico (desativa modo automático) |
| **A** | Ativa/desativa modo automático |
| **C** | Abre o configurador |
| **F** | Alterna modo fullscreen |
| **Q** | Sai da aplicação |

### Modo Automático

- **Ativado por padrão**: Rotaciona automaticamente entre grids a cada 15 segundos
- **Barra de progresso**: Exibe barra branca de 2px na parte inferior mostrando o progresso
- **Desativação**: Pressione qualquer tecla 1-4 para desativar e usar controle manual
- **Reativação**: Pressione A para reativar o modo automático

### Configurador (Tecla C)

O configurador permite:

- Adicionar/remover servidores DVR
- Configurar IPs, portas, credenciais e canais
- Definir grids de exibição
- Configurar tempo de exibição por grid
- Ajustar duração das transições
- Alterar modo da janela

Após salvar, a aplicação recarrega automaticamente os streams.

## 📁 Estrutura do Projeto

```
bbb_dvr/
├── main.py              # Aplicação principal
├── config_manager.py    # Gerenciamento de configuração
├── stream_manager.py    # Gerenciamento de streams RTSP
├── display_manager.py   # Composição de grid e transições
├── config_window.py     # Interface do configurador
├── config.json          # Arquivo de configuração
├── requirements.txt     # Dependências Python
├── run.sh              # Script de execução
├── install.sh          # Script de instalação
└── README.md           # Documentação
```

## ⚡ Otimizações de Performance

A aplicação utiliza várias técnicas para garantir alta performance:

1. **Threading**: Cada stream RTSP roda em thread separada
2. **Buffer Management**: Mantém apenas frames mais recentes
3. **Resolução Otimizada**: Redimensiona streams para tamanho do grid
4. **Frame Skipping**: Descarta frames antigos quando buffer está cheio
5. **Hardware Acceleration**: Usa aceleração de hardware quando disponível
6. **Carregamento Assíncrono**: Tela de loading durante inicialização

## 🔧 Notas Técnicas

- **Formato RTSP**: `rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0`
- **Resolução de Exibição**: 1920x1080 (4 câmeras de 960x540)
- **FPS Target**: 25 FPS
- **Reconexão Automática**: Tenta reconectar streams que caíram
- **Suporte a Senhas Especiais**: Trata corretamente senhas com caracteres especiais como `@`

## 🐛 Troubleshooting

### Erro 401 Unauthorized

Se você está recebendo erro **401 Unauthorized**, isso significa problema de autenticação:

1. **Teste no VLC primeiro**: Abra VLC > Media > Open Network Stream e cole a URL RTSP
2. **Verifique credenciais**: Confirme usuário e senha no `config.json`
3. **Teste com script**: Execute `python test_rtsp_detailed.py` para diagnóstico
4. **Consulte TROUBLESHOOTING.md**: Veja guia completo de solução de problemas

### Streams não conectam

- Verifique se os IPs e portas estão corretos
- Confirme credenciais RTSP
- Teste a URL RTSP manualmente com VLC ou similar
- Verifique firewall/rede
- Execute `python test_rtsp_detailed.py` para diagnóstico detalhado

### Performance baixa

- Reduza número de streams simultâneos
- Aumente `display_time` para reduzir frequência de transições
- Verifique largura de banda da rede
- Considere reduzir resolução dos streams no DVR

### Janela não abre em fullscreen

- Verifique permissões do sistema
- Tente executar como administrador (se necessário)
- Use modo "windowed" temporariamente
- Use tecla F para alternar fullscreen

## 📝 Scripts Úteis

- `run.sh`: Executa a aplicação
- `install.sh`: Instala dependências
- `test_rtsp_detailed.py`: Testa conexão RTSP com diagnóstico detalhado
- `test_from_config.py`: Testa usando configuração do config.json

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 👤 Autor

Felipe Brito

## 🔗 Links

- Repositório: https://github.com/felipebrito/bbb_dvr
