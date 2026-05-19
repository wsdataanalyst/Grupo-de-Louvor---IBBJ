# Senha esquecida — jeito simples

## Para quem esqueceu a senha (integrante)

**Não precisa configurar nada.**

1. Fale com o **líder** ou **organizador** do louvor  
2. Ele entra no app → **Gerenciar Escalas** ou **Membros**  
3. Abre **🔑 Redefinir senha de integrante**  
4. Escolhe seu nome, define uma senha nova e te avisa (WhatsApp, etc.)  
5. Você entra com seu **e-mail cadastrado** e a **senha nova**

---

## Para líder / organizador / desenvolvedor

No app, com sua conta de gestão:

**Gerenciar Escalas** → aba **Integrantes** → **🔑 Redefinir senha de integrante**

ou

**Membros** → **🔑 Redefinir senha de integrante**

Exemplo: redefinir a senha do Willame (`willsousaa7x@gmail.com`) e avisá-lo.

---

## E-mail automático (opcional)

Só se quiser que **Esqueci minha senha** envie link sozinho, sem passar pelo líder.

### Opção A — Resend (mais fácil que Gmail)

1. Conta grátis em https://resend.com  
2. Copie a **API Key** (`re_...`)  
3. No Streamlit Cloud → **Secrets**:

```toml
public_url = "https://seu-app.streamlit.app"
resend_api_key = "re_SUA_CHAVE"
resend_from_email = "Louvor IBBJ <onboarding@resend.dev>"
```

### Opção B — Gmail SMTP

Veja `python setup_smtp.py` ou o bloco `[smtp]` em `secrets.toml.example`.

---

## Resumo

| Situação | O que fazer |
|----------|-------------|
| Will esqueceu a senha | Líder redefine no app (sem Gmail) |
| Quer link por e-mail | Configurar Resend ou SMTP **uma vez** no servidor |
| Integrante | Só pedir ao líder — zero configuração |
