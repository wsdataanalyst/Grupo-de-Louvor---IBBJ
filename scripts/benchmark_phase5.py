#!/usr/bin/env python3
"""Resumo das otimizações Fase 5."""

from __future__ import annotations

print(
    """
FASE 5 — Otimizações ativas
============================

1. CSS estático (cache do navegador)
   • static/ibbj_theme.css (~200 KB)
   • static/mobile_lab_theme.css (~28 KB)
   • Regenerar: python scripts/build_theme_css.py

2. Bootstrap enxuto
   • chat.csv: só na rota Chat (badge via poll + cache)
   • escalas bundle: só em rotas que usam (_needs_escalas_core)
   • sugestoes: cache de sessão em rotas leves (ex.: Eventos)

3. Poll mobile
   • Chat 4s só em Início, Chat, Escalas, Gerenciar, Notificações

4. Fragments nas abas
   • Escalas: trocar aba sem rerun da página inteira
   • Gerenciar: idem (web + mobile)

5. Sequência do culto
   • Sync local automático (rápido)
   • Busca na web sob demanda (botão)

Teste manual
  1. Eventos / Playlist — deve abrir mais rápido que antes
  2. Escalas: troque abas — sem flash da sidebar inteira
  3. Sequência: abre rápido; web só ao clicar no botão
  4. DevTools → Network: ibbj_theme.css cacheado após 1º load
"""
)
