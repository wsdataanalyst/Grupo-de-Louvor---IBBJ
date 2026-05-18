# App no celular (sem Play Store / App Store) + notificações

> **Configure o OneSignal primeiro:** `CONFIGURAR_ONESIGNAL.md` ou `python setup_onesignal.py`

## O que foi preparado no projeto

1. **PWA** — instalar pelo navegador (Android e iPhone)
2. **Notificações push** — chat e novas escalas (via **OneSignal**, estilo WhatsApp)
3. **APK Android** — gerar a partir do site (link para baixar)

> **iPhone não usa APK.** No iOS o equivalente é **Adicionar à Tela de Início** (Safari) ou um arquivo IPA (mais complexo, exige conta Apple Developer).

---

## 1. Ativar notificações (obrigatório — uma vez)

1. Crie conta gratuita em [https://onesignal.com](https://onesignal.com)
2. Novo app → plataforma **Web** / **Push**
3. Copie **App ID** e **REST API Key**
4. No projeto, copie `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` e preencha:

```toml
public_url = "https://SEU-DOMINIO.com"   # HTTPS obrigatório para push

push_notifications_enabled = true
onesignal_app_id = "SEU-APP-ID"
onesignal_rest_api_key = "SUA-REST-API-KEY"
```

5. No painel OneSignal → **Settings → Platforms → Web**:
   - Site URL = seu `public_url`
   - Ative **Web Push**
6. Suba o app com **HTTPS** (Streamlit Cloud, servidor com SSL, etc.)

Integrantes: ao entrar no app, toque em **Ativar notificações** e aceite no navegador.

**iPhone:** use **Safari** → Compartilhar → **Adicionar à Tela de Início**, depois abra pelo ícone e ative notificações (iOS 16.4+).

---

## 2. Instalar no Android (sem loja)

### Opção A — PWA (mais simples)

1. Abra o link do app no **Chrome**
2. Menu ⋮ → **Instalar app** ou **Adicionar à tela inicial**
3. Ative notificações dentro do app

### Opção B — APK por link

1. Publique o site em **HTTPS**
2. Acesse [https://www.pwabuilder.com](https://www.pwabuilder.com)
3. Informe a URL do app → **Package for stores** → **Android** → baixe o **APK**
4. Envie o APK no WhatsApp do grupo (Google Drive, etc.)
5. No celular: permitir **fontes desconhecidas** → instalar

Atualizou o site? Gere o APK de novo na PWABuilder.

---

## 3. Instalar no iPhone (sem App Store)

1. Abra o link no **Safari** (não no Chrome)
2. **Compartilhar** → **Adicionar à Tela de Início**
3. Abra pelo ícone na home
4. Ative notificações quando o app pedir

Não existe APK para iPhone para distribuição simples por link.

---

## O que dispara notificação

| Evento | Quem recebe |
|--------|-------------|
| Nova mensagem no **Chat** | Todos que ativaram notificações |
| **Nova escala** salva (criar culto completo) | Todos inscritos |

---

## Ícones do app (opcional)

Substitua `static/icon-192.png` e `static/icon-512.png` por logos do grupo (PNG quadrado).

Gere ícones em [https://www.pwabuilder.com/imageGenerator](https://www.pwabuilder.com/imageGenerator).
