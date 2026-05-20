# Persistência na nuvem (Supabase) — cadastros não somem

Com isso ativo, **cada gravação** no app envia os CSV para o **Supabase**.  
Renomear o app no Streamlit **não apaga** contas: na primeira abertura o app **baixa** tudo da nuvem de novo.

## 1. Criar projeto gratuito

1. Acesse [https://supabase.com](https://supabase.com) e crie uma conta.
2. **New project** → nome ex.: `louvor-ibbj` → senha do banco (guarde) → região próxima ao Brasil.
3. Aguarde o projeto ficar pronto.

## 2. Criar a tabela

1. No menu: **SQL Editor** → **New query**.
2. Cole o conteúdo do arquivo `supabase/schema.sql` deste repositório.
3. **Run**.

## 3. Chaves para o Streamlit

1. **Project Settings** → **API**.
2. Copie:
   - **Project URL** → `supabase_url`
   - **service_role** (secret) → `supabase_key`  
     ⚠️ Use **service_role**, não a chave `anon` pública.

## 4. Secrets no Streamlit Cloud

Em **Settings → Secrets**, adicione (mantendo o que já existe):

```toml
[persistence]
enabled = true
supabase_url = "https://SEU-PROJETO.supabase.co"
supabase_key = "eyJhbGciOi... service_role ..."
```

No PC, o mesmo bloco em `.streamlit/secrets.toml`.

## 5. Reimplantar

**Manage app → Reboot** (ou aguarde o deploy após `git push`).

No menu lateral (desenvolvedor) deve aparecer: **Nuvem conectada (Supabase)**.

## Migração do app antigo (uma vez)

Se ainda tiver o **app antigo** no Streamlit com cadastros:

1. Abra o app antigo → dev → **Baixar backup ZIP** (última vez).
2. No app novo com Supabase já configurado: **Restaurar ZIP** **ou** abra o app antigo com os mesmos secrets `[persistence]` — na primeira sessão o app envia os CSV locais para a nuvem.

Depois disso, só o Supabase importa; backups ZIP ficam opcionais.

## Sem Supabase

Se `[persistence]` não estiver configurado, o app continua usando só a pasta `data/` no servidor (como antes), com risco ao renomear o app.

## Custo

Plano gratuito do Supabase costuma bastar para dezenas de integrantes e anos de mensagens em CSV.
