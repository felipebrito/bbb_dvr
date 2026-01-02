# BBB DVR Viewer

Aplicação desktop para visualização de múltiplas câmeras RTSP de DVRs em grid 2x2 com rotação automática.

## 📋 Estrutura do Projeto

```
DVR/
├── main.py              # Aplicação principal
├── config_manager.py    # Gerenciamento de configuração
├── stream_manager.py    # Gerenciamento de streams RTSP
├── display_manager.py   # Composição de grid e transições
├── config_window.py     # Interface do configurador
├── config.json          # Arquivo de configuração
├── Info.plist           # Configurações do .app (macOS)
├── requirements.txt     # Dependências Python
├── install.sh           # Script de instalação
├── run.sh              # Script de execução
├── build_app.sh         # Script para criar .app (onefile)
├── build_app_onefolder.sh  # Script para criar .app (onefolder)
├── test_app.sh         # Script para testar .app com logs
├── imagens/            # Pasta com ícone do aplicativo
│   └── logo.png
├── README.md           # Este arquivo
├── README_BUILD.md      # Guia de build do .app
└── TROUBLESHOOTING.md   # Guia de troubleshooting
```

## 🚀 Instalação Rápida

```bash
cd DVR
./install.sh
```

## ▶️ Executar

```bash
cd DVR
./run.sh
```

## 📦 Criar .app para macOS

```bash
cd DVR
./build_app_onefolder.sh
```

O .app será criado em `../dist/BBB DVR Viewer.app`

## ⌨️ Controles

- **1, 2, 3, 4**: Trocar manualmente entre grids
- **A**: Alternar modo automático/manual
- **C**: Abrir configurador
- **F**: Alternar fullscreen
- **Q**: Sair

## 📝 Configuração

Edite `config.json` para configurar:
- IPs e credenciais dos DVRs
- Canais de cada DVR
- Grids de exibição
- Tempo de exibição de cada grid
- Duração das transições

## 🔧 Troubleshooting

Consulte `TROUBLESHOOTING.md` para problemas comuns.

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🔗 Links

- Repositório: https://github.com/felipebrito/bbb_dvr
