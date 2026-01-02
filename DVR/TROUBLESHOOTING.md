# Troubleshooting - Problemas de Conexão RTSP

## Erro 401 Unauthorized

Se você está recebendo erro **401 Unauthorized**, isso significa que o servidor está rejeitando as credenciais. Siga estes passos:

### 1. Verifique as Credenciais

Abra o arquivo `config.json` e verifique:
- **IP**: Está correto? (ex: 192.168.1.27)
- **Porta**: Geralmente 554 para RTSP
- **Usuário**: Geralmente "admin" ou outro usuário configurado
- **Senha**: **ATENÇÃO** - Verifique se a senha está correta

**Importante sobre a senha:**
- Se a senha original é `123456789@`, o `@` pode ser parte da senha ou pode ser um caractere especial
- Tente testar sem os `@@@` primeiro
- Alguns DVRs podem ter senha diferente

### 2. Teste Manualmente no VLC

1. Abra o VLC Media Player
2. Vá em **Media > Open Network Stream** (ou Ctrl+N)
3. Cole uma das URLs abaixo (substitua a senha se necessário):

```
rtsp://admin:123456789%40%40%40@192.168.1.27:554/cam/realmonitor?channel=1&subtype=0
```

ou

```
rtsp://admin:123456789@192.168.1.25:554/cam/realmonitor?channel=1&subtype=0
```

4. Se funcionar no VLC, copie a URL exata que funcionou
5. Use essa URL no `config.json` (você pode precisar ajustar o código)

### 3. Verifique o Formato da URL RTSP

Diferentes marcas de DVR usam formatos diferentes:

**Formato comum:**
```
rtsp://usuario:senha@ip:porta/cam/realmonitor?channel=X&subtype=0
```

**Formato Hikvision:**
```
rtsp://usuario:senha@ip:porta/Streaming/Channels/XXX
```

**Formato Dahua:**
```
rtsp://usuario:senha@ip:porta/cam/realmonitor?channel=X&subtype=0
```

### 4. Teste com Scripts de Diagnóstico

Execute os scripts de teste:

```bash
source .venv/bin/activate
python test_rtsp_detailed.py
```

### 5. Verifique Rede e Firewall

- O computador está na mesma rede do DVR?
- Há firewall bloqueando a porta 554?
- O DVR aceita conexões RTSP externas?

### 6. Possíveis Soluções

1. **Senha incorreta**: Verifique a senha no painel do DVR
2. **Formato de URL errado**: Teste diferentes formatos
3. **Autenticação diferente**: Alguns DVRs precisam de autenticação digest
4. **Porta diferente**: Alguns DVRs usam porta diferente para RTSP

### 7. Como Ajustar a Senha no Config

Se descobrir que a senha está incorreta ou precisa ser diferente:

1. Abra `config.json`
2. Edite o campo `"password"` com a senha correta
3. Se a senha contém caracteres especiais, eles serão tratados automaticamente
4. Salve o arquivo
5. Execute a aplicação novamente

### 8. Exemplo de Config Correto

```json
{
  "dvr_servers": [
    {
      "ip": "192.168.1.27",
      "port": 554,
      "username": "admin",
      "password": "SUA_SENHA_AQUI",
      "channels": [1, 2, 3, 4]
    }
  ],
  "grids": [
    {"cameras": [0, 1, 2, 3], "display_time": 10}
  ],
  "transition_duration": 1.0,
  "window_mode": "fullscreen"
}
```

## Próximos Passos

1. Teste a URL no VLC primeiro
2. Se funcionar no VLC, use a mesma URL no config
3. Se não funcionar no VLC, verifique credenciais e formato da URL
4. Consulte o manual do seu DVR para o formato RTSP correto

