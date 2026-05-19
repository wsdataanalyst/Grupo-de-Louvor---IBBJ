# Configurar e-mail (esqueci minha senha)

O app envia um link de redefinição **somente para o e-mail já cadastrado** em `data/members.csv`.

## 1. Copiar secrets

```powershell
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```

## 2. Preencher `[smtp]`

Exemplo com **Gmail**:

1. Ative verificação em 2 etapas na conta Google.
2. Crie uma **Senha de app** em [Google App Passwords](https://myaccount.google.com/apppasswords).
3. No `secrets.toml`:

```toml
public_url = "https://seu-app.streamlit.app"

[smtp]
enabled = true
host = "smtp.gmail.com"
port = 587
user = "seu-email@gmail.com"
password = "xxxx xxxx xxxx xxxx"
from_email = "Grupo de Louvor IBBJ <seu-email@gmail.com>"
use_tls = true
```

`public_url` deve ser a URL pública do app (HTTPS), para o link no e-mail funcionar no celular.

## 3. Outros provedores

| Provedor   | host                 | porta |
|-----------|----------------------|-------|
| Outlook   | smtp.office365.com   | 587   |
| Hostinger | smtp.hostinger.com   | 587   |
| Zoho      | smtp.zoho.com        | 587   |

## 4. Testar

1. Reinicie o app: `streamlit run app.py`
2. Na tela de login → **Esqueci minha senha**
3. Informe um e-mail que já existe no cadastro
4. Abra o e-mail e clique em **Redefinir minha senha**

O link expira em **1 hora** e só pode ser usado **uma vez**.

## Segurança

- Não é informado se o e-mail existe ou não (mensagem genérica).
- Máximo de **3 pedidos por hora** por e-mail.
- Tokens ficam em `data/password_reset_tokens.csv` (não versionar em produção se preferir).
