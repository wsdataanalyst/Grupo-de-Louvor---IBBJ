-- Execute no Supabase: SQL Editor → New query → Run
-- Projeto: Grupo de Louvor IBBJ — armazena cada CSV como texto (sincronização automática)

create table if not exists public.data_files (
  name text primary key,
  content text not null default '',
  updated_at timestamptz not null default timezone('utc'::text, now())
);

create index if not exists data_files_updated_at_idx on public.data_files (updated_at desc);

comment on table public.data_files is 'Cópia na nuvem dos CSV de data/ (members, escalas, chat, etc.)';

-- Use a chave "service_role" do Supabase APENAS em secrets do Streamlit (nunca no front-end).
