# Configurar OneSignal (passo a passo)

Tempo estimado: **15 minutos**.

---

## Parte 1 — Conta OneSignal

1. Acesse [https://onesignal.com](https://onesignal.com) e crie conta (plano gratuito serve).
2. Clique em **New App/Organization**.
3. Nome do app: `Grupo de Louvor IBBJ`.
4. Selecione **Web** como plataforma.

---

## Parte 2 — Web Push no painel

1. No menu do app → **Settings** → **Platforms** → **Web** → **Configure**.
2. Preencha:
   - **Site URL:** a URL **HTTPS** onde o Streamlit está publicado  
     Exemplo: `https://grupo-louvor-ibbj.streamlit.app`
   - **Auto Resubscribe:** ligado
   - **Default Icon URL:** opcional (pode usar `https://SUA-URL/icon-192.png`)
3. Salve.

> **Teste local:** em Site URL você pode usar `http://localhost:8501` temporariamente. Em produção use só HTTPS.

---

## Parte 3 — Copiar chaves

1. **Settings** → **Keys & IDs**
2. Copie:
   - **OneSignal App ID** (UUID)
   - **REST API Key** (clique em **Reveal** se necessário)

---

## Parte 4 — Configurar o projeto (automático)

No PowerShell, na pasta do projeto:

```powershell
cd "C:\Users\wsana\Projeto python\Grupo de Louvor - IBBJ"
pip install -r requirements.txt
python setup_onesignal.py
```

O script cria `.streamlit/secrets.toml` com suas chaves.

---

## Parte 5 — Publicar (Streamlit Cloud)

1. Suba o projeto no GitHub.
2. [share.streamlit.io](https://share.streamlit.io) → **New app** → escolha o repositório.
3. Em **Settings** → **Secrets**, cole o conteúdo de `secrets.toml`:

```toml
public_url = "https://SEU-APP.streamlit.app"

push_notifications_enabled = true
onesignal_app_id = "COLE-APP-ID"
onesignal_rest_api_key = "COLE-REST-API-KEY"

developer_emails = ["wsdataanalyst", "willsousaa7x@gmail.com"]
dev_default_password = "IbbjDev2024"
```

4. **Importante:** `public_url` deve ser **igual** à URL do Streamlit e à **Site URL** no OneSignal.
5. Reimplante o app (Reboot) após salvar secrets.

---

## Parte 6 — Ativar no celular (cada integrante)

1. Abra o link do app no celular (**HTTPS**).
2. Faça login.
3. Abra o expander **📲 App no celular e notificações**.
4. Toque em **🔔 Ativar notificações** → **Permitir**.

**Android:** Chrome → Instalar app (opcional).  
**iPhone:** Safari → Compartilhar → Adicionar à Tela de Início → abrir pelo ícone → ativar notificações.

---

## Parte 7 — Testar

1. Login como desenvolvedor (`wsdataanalyst` / senha do secrets).
2. No menu lateral: **🔔 Configurar push (admin)**.
3. Toque em **Enviar notificação de teste**.
4. Envie uma mensagem no **Chat** ou crie uma **Nova escala** — todos inscritos devem receber.

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| Botão de notificação não aparece | `push_notifications_enabled = true` e chaves preenchidas |
| API retorna erro 403 | REST API Key errada |
| Ninguém recebe push | Integrantes precisam clicar **Ativar notificações** |
| iPhone não notifica | Abrir pelo ícone PWA (Safari), iOS 16.4+ |
| Site URL diferente | Igualar URL no OneSignal, `public_url` e Streamlit |

---

## APK Android (opcional)

1. Com o site no ar em HTTPS.
2. [https://www.pwabuilder.com](https://www.pwabuilder.com) → sua URL → **Package for Android** → baixar APK.
3. Enviar o APK no WhatsApp do grupo.

Veja também: `MOBILE.md`.
