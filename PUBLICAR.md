# O projeto não está no Streamlit — o que fazer?

Você tem **3 caminhos**. Escolha um:

| Caminho | Para quem | Link no celular | Notificações push |
|---------|-----------|-----------------|-------------------|
| **A — Streamlit Cloud (grátis)** | Uso do grupo na internet | `https://seu-app.streamlit.app` | ✅ Sim |
| **B — Só no seu PC** | Teste ou uso em casa | `http://localhost:8501` | ❌ Não (sem HTTPS) |
| **C — PC ligado na igreja/casa** | Rede Wi‑Fi local | `http://IP-DO-PC:8501` | ❌ Não |

**Recomendado para o grupo:** caminho **A**.

---

## Caminho A — Publicar grátis no Streamlit Cloud

Não precisa pagar. O app fica na internet 24h com HTTPS (necessário para push e instalar no celular).

### Passo 1 — Conta no GitHub

1. [https://github.com](https://github.com) → criar conta (se não tiver).
2. **New repository** → nome: `grupo-louvor-ibbj` → **Create** (pode ser privado).

### Passo 2 — Enviar o projeto para o GitHub (script automático)

No PowerShell:

```powershell
cd "C:\Users\wsana\Projeto python\Grupo de Louvor - IBBJ"
.\publicar_github.ps1
```

O script pergunta seu usuário GitHub, faz o commit e o `git push`.  
Antes, crie o repositório **vazio** em: https://github.com/new

**Manual** (se preferir): veja os comandos `git` no final deste arquivo.

> **Não envie** `.streamlit/secrets.toml` (tem senhas e chaves). O `.gitignore` já bloqueia isso.

### Passo 3 — Criar o app no Streamlit

1. [https://share.streamlit.io](https://share.streamlit.io) → login com **GitHub**.
2. **Create app** → repositório: `wsdataanalyst/Grupo-de-Louvor---IBBJ`.
3. **Main file:** `app.py` → **Deploy**.
4. Aguarde 2–5 minutos. A URL será algo como:  
   `https://grupo-louvor-ibbj.streamlit.app`

### Passo 4 — Secrets (senhas e OneSignal)

1. No app publicado → **⚙️ Manage app** → **Settings** → **Secrets**.
2. Cole o conteúdo do seu `.streamlit/secrets.toml` (criado com `python setup_onesignal.py`).
3. Ajuste a linha:

```toml
public_url = "https://grupo-louvor-ibbj.streamlit.app"
```

(use a URL **real** que o Streamlit mostrou)

4. **Save** → **Reboot app**.

### Passo 5 — OneSignal

No painel OneSignal → **Web** → **Site URL** = mesma URL do passo 4.

### Passo 6 — Enviar o link ao grupo

WhatsApp: `https://grupo-louvor-ibbj.streamlit.app`

Integrantes: login → **📲 App no celular** → **🔔 Ativar notificações**.

---

## Caminho B — Usar só no seu computador (sem publicar)

Para testar ou usar só você:

```powershell
cd "C:\Users\wsana\Projeto python\Grupo de Louvor - IBBJ"
.\iniciar.ps1
```

Abra no navegador: **http://localhost:8501**

- Dados ficam na pasta `data/` do seu PC.
- **Push e PWA no celular não funcionam bem** sem HTTPS público.
- Se fechar o PC, o app para.

---

## Caminho C — Outros celulares na mesma Wi‑Fi (sem Streamlit Cloud)

Com o app rodando no PC:

```powershell
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

1. No PC: `ipconfig` → anote o **IPv4** (ex.: `192.168.0.15`).
2. No celular (mesma Wi‑Fi): `http://192.168.0.15:8501`

- PC precisa ficar **ligado** com o app aberto.
- Notificações push **não** funcionam (sem HTTPS na internet).
- Firewall do Windows pode bloquear — permita o Python na rede privada.

---

## Resumo rápido

| Quer… | Faça |
|-------|------|
| Grupo acessar de qualquer lugar + push | **Caminho A** (GitHub + Streamlit Cloud) |
| Só testar agora | **Caminho B** (`.\iniciar.ps1`) |
| Igreja com Wi‑Fi, sem internet pública | **Caminho C** |

Dúvidas no OneSignal após publicar: `CONFIGURAR_ONESIGNAL.md`.
