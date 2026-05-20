# Dados e cadastros — não perder contas

## Solução recomendada: Supabase (nuvem automática)

Configure **`[persistence]`** no Streamlit (guia **`CONFIGURAR_SUPABASE.md`**).

- Cada salvamento envia os CSV para o **Supabase**
- Renomear o app no Streamlit **não apaga** cadastros — o app baixa da nuvem ao abrir
- **Sem backup manual** no dia a dia

---

Tudo que o grupo cadastra fica na pasta **`data/`** do servidor (CSV), espelhada na nuvem:

| Arquivo | Conteúdo |
|---------|----------|
| `members.csv` | Contas e senhas (hash) |
| `escalas.csv` | Escalas de culto |
| `chat.csv` | Mensagens |
| … | Outros arquivos na pasta |

## Por que sumiu todo mundo ao mudar o nome no Streamlit?

**Renomear o app, criar um app novo ou apagar e republicar** no Streamlit Cloud costuma dar um **servidor novo** com a pasta `data/` **vazia**.

- Os CSV **não vão para o GitHub** (`.gitignore`) — isso protege senhas, mas cada app no Cloud tem seu próprio disco.
- Atualizar o **código** (`git push`) **não apaga** cadastros no **mesmo** app.
- Mudar o **nome/URL do app** ou duplicar o deploy **não leva** os arquivos `data/` do app antigo.

O app **não apagou de propósito** — os dados ficaram no app antigo (se ainda existir) ou só no backup que alguém baixou antes.

## O que fazer agora (recuperar)

1. **App antigo no Streamlit** — se ainda aparece na sua conta, abra com a URL antiga, faça login como desenvolvedor e use **Menu lateral → 💾 Backup / restaurar dados → Baixar backup (ZIP)**. Depois suba o ZIP no app novo com **Restaurar este ZIP**.

2. **Backup local no PC** — se você tinha `data/members.csv` (e outros) na pasta do projeto, no app novo: mesmo menu **Restaurar este ZIP** (pode zipar a pasta `data` manualmente).

3. **Backups automáticos no servidor** — se o app antigo ainda abre: pasta `data/backups/` com arquivos `members_AAAAMMDD_HHMMSS.csv`. Copie o mais recente para `data/members.csv` (via restauração ZIP ou suporte Streamlit).

4. **Sem backup** — será preciso os integrantes **cadastrarem de novo** ou você recriar contas pelo painel de líder/desenvolvedor.

## Como não perder daqui pra frente

1. **Semanal (ou antes de qualquer mudança no Cloud):** login desenvolvedor → **💾 Backup / restaurar dados** → **Baixar backup (ZIP)**. Guarde no PC ou Google Drive.

2. **Não apague o app antigo** no Streamlit até baixar o ZIP do app antigo e restaurar no novo.

3. **PC e nuvem são separados** — `git push` só envia código; cadastros do grupo estão no servidor publicado.

4. O app já faz **backup automático** em `data/backups/` antes de cada gravação e **bloqueia** salvar `members.csv` com muito menos contas do que antes (proteção contra leitura vazia).

## Proteção no código

1. Backup automático antes de cada gravação → `data/backups/`
2. Snapshot ao abrir o app (uma vez por sessão)
3. Bloqueio se tentar salvar `members.csv` com muito menos contas
4. Menu dev: exportar / restaurar ZIP completo

## Restaurar um backup manual (arquivo solto)

1. Pare o app ou use com cuidado
2. Em `data/backups/`, ache o mais recente, ex.: `members_20260519_143022.csv`
3. Copie para `data/members.csv` (substituir)
4. Reinicie o app

Ou use **Restaurar este ZIP** no menu desenvolvedor.
