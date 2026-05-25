-- Execute no Supabase: SQL Editor → New query → Run
-- Projeto: Grupo de Louvor IBBJ — armazena cada CSV como texto (sincronização automática)

create table if not exists public.data_files (
  name text primary key,
  content text not null default '',
  updated_at timestamptz not null default timezone('utc'::text, now())
);

create index if not exists data_files_updated_at_idx on public.data_files (updated_at desc);

comment on table public.data_files is 'Cópia na nuvem dos CSV de data/ (members, escalas, chat, etc.)';

-- Sinais para Realtime (só nome + horário — o app usa a chave anon no navegador)
create table if not exists public.sync_signals (
  name text primary key,
  updated_at timestamptz not null default timezone('utc'::text, now())
);

create or replace function public.notify_data_file_sync()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.sync_signals (name, updated_at)
  values (new.name, coalesce(new.updated_at, timezone('utc'::text, now())))
  on conflict (name) do update
    set updated_at = excluded.updated_at;
  return new;
end;
$$;

drop trigger if exists data_files_sync_signal on public.data_files;
create trigger data_files_sync_signal
  after insert or update on public.data_files
  for each row execute function public.notify_data_file_sync();

alter table public.sync_signals enable row level security;

drop policy if exists "anon_read_sync_signals" on public.sync_signals;
create policy "anon_read_sync_signals"
  on public.sync_signals for select
  to anon, authenticated
  using (true);

-- Realtime: Database → Replication → supabase_realtime → incluir sync_signals
-- (ou SQL: alter publication supabase_realtime add table public.sync_signals;)

-- Use service_role só no Streamlit. Para chat instantâneo, adicione também:
-- supabase_anon_key = "eyJ... anon public ..." em [persistence]
