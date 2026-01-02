# Como Criar o .app para Distribuição

Este guia explica como criar um arquivo `.app` (aplicação macOS) para distribuir a aplicação.

## Pré-requisitos

1. Ambiente virtual configurado e dependências instaladas
2. PyInstaller instalado (será instalado automaticamente pelo script)

## Métodos de Build

### Opção 1: One-file (Recomendado para distribuição)

Cria um único arquivo executável:

```bash
./build_app.sh
```

**Vantagens:**
- Um único arquivo .app
- Mais fácil de distribuir
- Menor tamanho

**Desvantagens:**
- Inicialização mais lenta
- Mais difícil de debugar

### Opção 2: One-folder (Recomendado para desenvolvimento/teste)

Cria uma pasta com todos os arquivos:

```bash
./build_app_onefolder.sh
```

**Vantagens:**
- Mais rápido para iniciar
- Mais fácil de debugar
- Pode ver os arquivos internos

**Desvantagens:**
- Múltiplos arquivos
- Maior tamanho total

## Após o Build

A aplicação será criada em:
```
dist/BBB DVR Viewer.app
```

### Testar a Aplicação

```bash
open "dist/BBB DVR Viewer.app"
```

Ou arraste o .app para a pasta Aplicações e execute normalmente.

## Ícone

O script procura o ícone em `imagens/logo.png`. Se não encontrar, a aplicação será criada sem ícone personalizado.

Para adicionar um ícone:
1. Coloque o arquivo `logo.png` na pasta `imagens/`
2. O formato deve ser PNG
3. Tamanho recomendado: 512x512 ou 1024x1024 pixels

## Notas Importantes

1. **Primeira execução**: Na primeira vez que executar o .app, o macOS pode bloquear. Vá em Configurações do Sistema > Privacidade e Segurança e permita a execução.

2. **config.json**: O arquivo `config.json` será incluído no .app. Se precisar alterar, edite o arquivo dentro do bundle ou recrie o .app.

3. **Dependências**: Todas as dependências (OpenCV, NumPy, etc.) serão incluídas no .app.

4. **Tamanho**: O .app pode ter vários MB devido às dependências incluídas.

## Troubleshooting

### Erro: "PyInstaller não encontrado"
Execute:
```bash
source .venv/bin/activate
pip install pyinstaller
```

### Erro: "Ícone não encontrado"
Verifique se o arquivo `imagens/logo.png` existe. O build continuará sem ícone.

### Aplicação não abre
1. Verifique os logs no Console do macOS
2. Tente executar via terminal:
   ```bash
   open "dist/BBB DVR Viewer.app" --args --debug
   ```

### Aplicação muito grande
Use a opção one-file (`build_app.sh`) que é mais compacta.

