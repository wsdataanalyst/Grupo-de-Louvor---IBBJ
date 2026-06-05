#!/usr/bin/env python3
"""Resumo das otimizações Fase 2 + 3 (carregamento lazy e cache granular)."""

from __future__ import annotations

print(
    """
FASE 2 + 3 — Otimizações ativas
================================

Fase 2 — Carregamento lazy (web + mobile)
  • bootstrap_authenticated_data() por rota (app_menu / ml_page)
  • louvores: catálogo leve; lyrics_text/cifra_text só em Repertório/Escalas/Gerenciar
  • feed, eventos, playlist, chat_ensaio: só quando a rota precisa
  • members.csv com cache por revisão de arquivo
  • bundle de escalas via get_escalas_bundle() (sem reload duplicado no boot desktop)

Fase 3 — Saves e cache
  • save_data invalida só o CSV salvo (session cache granular)
  • load_data usa cache por arquivo + revisão local
  • load_chat_df → load_chat_df_live (não limpa cache global)
  • autosave sequência com debounce ~1,4s
  • polling chat/escalas só em rotas relevantes
  • mobile: uma chamada _chat_global_sync por rerun

Extras
  • fotos de perfil: sync nuvem 1x por sessão
  • Gerenciar/Montar: chat ensaio sob demanda (botão Abrir)

Teste manual
  1. Chat: envie mensagem → abra Escalas (deve responder mais rápido)
  2. Perfil / Eventos: navegação sem carregar repertório pesado
  3. Repertório / Sequência: letras e cifras continuam disponíveis
"""
)
