# Dados e cadastros — não perder contas

Tudo que o grupo cadastra fica na pasta **`data/`** do servidor (CSV):

| Arquivo | Conteúdo |
|---------|----------|
| `members.csv` | Contas e senhas (hash) |
| `escalas.csv` | Escalas de culto |
| `chat.csv` | Mensagens |
| … | Outros arquivos na pasta |

## O que o app faz agora (proteção no código)

1. **Backup automático** antes de cada gravação → `data/backups/`
2. **Snapshot** ao abrir o app (uma vez por sessão)
3. **Bloqueio** se alguém tentar salvar `members.csv` com muito menos contas do que já existia (evita apagar cadastros por erro de leitura)
4. Atualizações de código **não apagam** linhas de membros — só adicionam a conta técnica `wsdataanalyst` se faltar

## Streamlit Cloud (importante)

- Os CSV **não vão no GitHub** (`.gitignore`) — isso é correto por segurança.
- Os dados ficam no **disco do app publicado** e **permanecem entre reinícios** do mesmo app.
- Se você **apagar e criar outro app** do zero no Streamlit, a pasta `data/` começa vazia de novo.

**Antes de mudanças grandes no Cloud:** faça cópia de `data/members.csv` (e outros) pelo gerenciador de arquivos do servidor ou peça ao desenvolvedor um backup da pasta `data/backups/`.

## No seu PC

A pasta `data/` do projeto guarda os cadastros locais. Ao publicar código novo no Git, **os CSV locais não são enviados** — cada ambiente (PC vs Cloud) tem sua própria `data/`.

Para testar com os mesmos cadastros do grupo na nuvem, é preciso **copiar** os CSV do servidor para o PC (ou o contrário), não basta dar `git push`.

## Restaurar um backup

1. Pare o app (ou use com cuidado)
2. Em `data/backups/`, ache o arquivo mais recente, ex.: `members_20260519_143022.csv`
3. Copie para `data/members.csv` (substituir)
4. Reinicie o app
