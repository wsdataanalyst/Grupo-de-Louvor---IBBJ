# Grupo de Louvor — IBBJ

App em Streamlit para escalas, catálogo de louvores, chat do grupo e **notificações no celular** (sem Play Store / App Store).

## Início rápido

```powershell
cd "C:\Users\wsana\Projeto python\Grupo de Louvor - IBBJ"
.\iniciar.ps1
```

Ou manualmente:

```powershell
pip install -r requirements.txt
python setup_onesignal.py    # primeira vez — configura push
python setup_smtp.py         # esqueci minha senha (e-mail)
streamlit run app.py
```

Acesse: `http://localhost:8501`

**Conta desenvolvedor (testes):** usuário `wsdataanalyst` — senha em `.streamlit/secrets.toml` (`dev_default_password`).

---

## App no celular + notificações

| Recurso | Arquivo |
|---------|---------|
| Configurar OneSignal (passo a passo) | `CONFIGURAR_ONESIGNAL.md` |
| Assistente automático | `python setup_onesignal.py` |
| PWA, APK Android, iPhone | `MOBILE.md` |

**Resumo:** configure OneSignal → rode `setup_onesignal.py` → publique em HTTPS (Streamlit Cloud) → cada integrante toca **🔔 Ativar notificações** no app.

---

## Publicar na internet (ainda não está no Streamlit?)

**Guia completo:** `PUBLICAR.md` — GitHub + Streamlit Cloud grátis, ou uso só no PC / Wi‑Fi local.

Resumo Streamlit Cloud:

1. Repositório: [github.com/wsdataanalyst/Grupo-de-Louvor---IBBJ](https://github.com/wsdataanalyst/Grupo-de-Louvor---IBBJ)
2. [share.streamlit.io](https://share.streamlit.io) → **Create app** → `wsdataanalyst/Grupo-de-Louvor---IBBJ` → `app.py`.
3. **Settings → Secrets:** cole o `.streamlit/secrets.toml`.
4. `public_url` = URL do app; mesma URL no OneSignal.

---

## Funções principais

- Cadastro e login de integrantes
- **Esqueci minha senha** — link por e-mail (SMTP em `secrets.toml`, guia: `CONFIGURAR_EMAIL.md`)
- Escalas completas (equipe + louvores por parte do culto)
- Chat do grupo com **push**
- **Nova escala** com **push** para todos inscritos
- Catálogo de louvores, playlist, perfil
- Gerenciar escalas (líderes / organizadores / desenvolvedor)

---

## Estrutura

```
app.py                 # aplicativo principal
push_notifications.py  # envio OneSignal
password_reset.py      # recuperação de senha por e-mail
setup_onesignal.py     # assistente de configuração
static/                # PWA (manifest, ícones, service worker)
.streamlit/
  config.toml
  secrets.toml.example
data/                  # CSVs (local, não versionados exceto louvores)
```

---

## Segurança

- **Nunca** commite `.streamlit/secrets.toml` (contém chaves OneSignal).
- Use senhas fortes em produção e altere `dev_default_password`.
