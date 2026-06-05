"""Carregamento lazy de dados por rota (Fase 2 performance — web e mobile)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from mobile_lab_nav import APP_MENU_TO_ML_PAGE

# Colunas leves vs. pesadas (letras/cifras embutidas)
LOUVOR_CATALOG_COLUMN_NAMES: tuple[str, ...] = (
    "title",
    "artist",
    "key",
    "youtube_url",
    "cifra_url",
    "ritmo",
    "letter",
    "source",
)

_EMPTY_DF = pd.DataFrame()


@dataclass
class AppDataBundle:
    members_df: pd.DataFrame
    chat_df: pd.DataFrame
    sugestoes_df: pd.DataFrame
    escalas_df: pd.DataFrame
    programa_df: pd.DataFrame
    equipe_df: pd.DataFrame
    trocas_df: pd.DataFrame
    louvores_df: pd.DataFrame
    playlist_df: pd.DataFrame
    eventos_df: pd.DataFrame
    feed_posts_df: pd.DataFrame
    feed_likes_df: pd.DataFrame
    feed_comments_df: pd.DataFrame
    chat_ensaio_df: pd.DataFrame


def current_app_route(*, mobile: bool) -> str:
    """Rota normalizada (web: app_menu, mobile: ml_page)."""
    if mobile:
        return str(st.session_state.get("ml_page", "Início")).strip() or "Início"
    return str(st.session_state.get("app_menu", "Dashboard")).strip() or "Dashboard"


def _route_web_key(route: str) -> str:
    return route.strip() or "Dashboard"


def _needs_louvores_catalog(route: str, *, mobile: bool) -> bool:
    if mobile:
        return route in (
            "Início",
            "Escalas",
            "Gerenciar Escalas",
            "Repertório",
            "Playlist",
            "Sugestões",
            "Membros",
        )
    return route in (
        "Dashboard",
        "Escalas",
        "Gerenciar Escalas",
        "Repertório",
        "Playlist",
        "Sugestão de louvor",
        "Membros",
    )


def _needs_louvores_content(route: str, *, mobile: bool) -> bool:
    if mobile:
        return route in (
            "Repertório",
            "Gerenciar Escalas",
            "Escalas",
        )
    return route in (
        "Repertório",
        "Gerenciar Escalas",
        "Escalas",
        "Membros",
    )


def _needs_chat_ensaio(route: str, *, mobile: bool) -> bool:
    return route in ("Escalas", "Gerenciar Escalas")


def _needs_feed(route: str, *, mobile: bool) -> bool:
    if mobile:
        return route in ("Início", "Notificações")
    return route in ("Dashboard", "Feed", "Avisos")


def _needs_eventos(route: str, *, mobile: bool) -> bool:
    if mobile:
        return route in ("Início", "Eventos")
    return route in ("Dashboard", "Eventos")


def _needs_playlist(route: str, *, mobile: bool) -> bool:
    if mobile:
        return route in ("Início", "Playlist")
    return route in ("Dashboard", "Playlist")


def _needs_sugestoes(route: str, *, mobile: bool) -> bool:
    if mobile:
        return route in ("Início", "Sugestões", "Gerenciar Escalas")
    return route in (
        "Dashboard",
        "Sugestão de louvor",
        "Gerenciar Escalas",
        "Escalas",
        "Repertório",
    )


def _needs_chat(route: str, *, mobile: bool) -> bool:
    if mobile:
        return route == "Chat"
    return route == "Chat"


def _needs_escalas_core(route: str, *, mobile: bool) -> bool:
    if mobile:
        return route in (
            "Início",
            "Escalas",
            "Gerenciar Escalas",
            "Perfil",
            "Membros",
        )
    return route in (
        "Dashboard",
        "Escalas",
        "Gerenciar Escalas",
        "Perfil",
        "Membros",
        "Chat",
        "Feed",
        "Repertório",
    )


def file_local_revision(file_path: Path) -> str:
    try:
        stat = file_path.stat()
        return f"local:{stat.st_mtime_ns}:{stat.st_size}"
    except OSError:
        return "local:missing"


def invalidate_session_df_cache(file_name: str) -> None:
    st.session_state.pop(f"_df_cache_{file_name}", None)
    st.session_state.pop(f"_df_rev_{file_name}", None)


def invalidate_all_session_df_caches() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("_df_cache_") or key.startswith("_df_rev_"):
            st.session_state.pop(key, None)


# CSVs que devem refletir dados ao voltar do background (PWA / aba em segundo plano).
RESUME_DATA_FILE_NAMES: tuple[str, ...] = (
    "chat.csv",
    "escalas.csv",
    "programa_culto.csv",
    "escala_equipe.csv",
    "trocas_escalas.csv",
    "programa_sequencia.csv",
    "feed_posts.csv",
    "feed_likes.csv",
    "feed_comments.csv",
    "sugestoes_louvor.csv",
    "chat_ensaio.csv",
)


def invalidate_resume_data_caches() -> None:
    """Invalidação granular ao retomar o app (Fase 4 — sem limpar louvores/members)."""
    for name in RESUME_DATA_FILE_NAMES:
        invalidate_session_df_cache(name)
    for key in (
        "_escalas_bundle",
        "_chat_df_cache",
        "_chat_rev",
        "_escalas_rev",
        "_feed_rev",
        "_sugestoes_df_cache",
    ):
        st.session_state.pop(key, None)


def load_data_session_cached(
    file_path: Path,
    columns: tuple,
    *,
    loader,
    preparer=None,
) -> pd.DataFrame:
    """Cache por arquivo + revisão local (invalidação granular no save)."""
    rev = file_local_revision(file_path)
    cache_key = f"_df_cache_{file_path.name}"
    rev_key = f"_df_rev_{file_path.name}"
    if st.session_state.get(rev_key) == rev:
        cached = st.session_state.get(cache_key)
        if cached is not None:
            df = cached
            return preparer(df) if preparer else df
    df = loader(file_path, columns)
    if preparer:
        df = preparer(df)
    st.session_state[cache_key] = df
    st.session_state[rev_key] = rev
    return df


def load_members_cached(load_members_fn, *, members_file: Path) -> pd.DataFrame:
    """Members com revisão de arquivo — evita merge remoto em todo rerun."""
    rev = file_local_revision(members_file)
    if st.session_state.get("_members_rev") == rev:
        cached = st.session_state.get("_members_df_cache")
        if cached is not None:
            return cached
    df = load_members_fn()
    st.session_state["_members_df_cache"] = df
    st.session_state["_members_rev"] = rev
    return df


def merge_louvores_content(catalog_df: pd.DataFrame, content_df: pd.DataFrame) -> pd.DataFrame:
    """Anexa lyrics_text/cifra_text ao catálogo leve."""
    if catalog_df.empty or content_df.empty:
        out = catalog_df.copy()
        for col in ("lyrics_text", "cifra_text"):
            if col not in out.columns:
                out[col] = ""
        return out
    out = catalog_df.copy()
    if "title" not in content_df.columns:
        return out
    content = content_df.copy()
    for col in ("lyrics_text", "cifra_text"):
        if col not in content.columns:
            content[col] = ""
    keys = ["title", "artist"] if "artist" in out.columns else ["title"]
    merged = out.merge(
        content[keys + ["lyrics_text", "cifra_text"]],
        on=keys,
        how="left",
        suffixes=("", "_dup"),
    )
    for col in ("lyrics_text", "cifra_text"):
        if f"{col}_dup" in merged.columns:
            merged[col] = merged[col].fillna(merged[f"{col}_dup"])
            merged.drop(columns=[f"{col}_dup"], inplace=True)
        if col not in merged.columns:
            merged[col] = ""
        merged[col] = merged[col].fillna("").astype(str)
    return merged


def bootstrap_authenticated_data(*, mobile: bool) -> AppDataBundle:
    """
    Carrega dados por rota + shell (badges/sidebar).
    Preserva funções: páginas recebem DataFrames vazios preparados quando não carregados.
    """
    from app import (
        CHAT_COLUMNS,
        CHAT_ENSAIO_COLUMNS,
        CHAT_ENSAIO_FILE,
        CHAT_FILE,
        ESCALA_COLUMNS,
        ESCALAS_FILE,
        EQUIPE_COLUMNS,
        EQUIPE_FILE,
        EVENTO_COLUMNS,
        EVENTOS_FILE,
        LOUVOR_EXTRA_COLUMNS,
        LOUVOR_SEQUENCIA_COLUMNS,
        LOUVORES_FILE,
        MEMBERS_FILE,
        PLAYLIST_COLUMNS,
        PLAYLIST_FILE,
        PROGRAMA_COLUMNS,
        PROGRAMA_FILE,
        SUGESTAO_COLUMNS,
        SUGESTOES_FILE,
        TROCA_COLUMNS,
        TROCAS_FILE,
        fix_louvor_display_title,
        get_escalas_bundle,
        load_data,
        load_feed_bundle,
        load_members_df,
        prepare_chat,
        prepare_chat_ensaio,
        prepare_escalas,
        prepare_equipe,
        prepare_eventos,
        prepare_louvores_with_meta,
        prepare_members,
        prepare_playlist,
        prepare_programa,
        prepare_sugestoes,
        prepare_trocas,
    )
    from chat_runtime import load_chat_df_live

    route = current_app_route(mobile=mobile)

    members_df = load_members_cached(load_members_df, members_file=MEMBERS_FILE)
    members_df = prepare_members(members_df)

    if _needs_chat(route, mobile=mobile):
        chat_df = load_chat_df_live()
    else:
        cached_chat = st.session_state.get("_chat_df_cache")
        if isinstance(cached_chat, pd.DataFrame):
            chat_df = cached_chat
        else:
            chat_df = prepare_chat(_EMPTY_DF.copy())

    cached_sug = st.session_state.get("_sugestoes_df_cache")
    if _needs_sugestoes(route, mobile=mobile) or not isinstance(cached_sug, pd.DataFrame):
        sugestoes_df = load_data_session_cached(
            SUGESTOES_FILE,
            SUGESTAO_COLUMNS,
            loader=load_data,
            preparer=prepare_sugestoes,
        )
        st.session_state["_sugestoes_df_cache"] = sugestoes_df
    else:
        sugestoes_df = cached_sug

    if _needs_escalas_core(route, mobile=mobile):
        escalas_df, programa_df, equipe_df, trocas_df = get_escalas_bundle()
    else:
        escalas_df = programa_df = equipe_df = trocas_df = _EMPTY_DF.copy()

    louvores_df = _EMPTY_DF.copy()
    if _needs_louvores_catalog(route, mobile=mobile):
        catalog_cols = tuple(LOUVOR_CATALOG_COLUMN_NAMES) + LOUVOR_EXTRA_COLUMNS
        louvores_df = load_data_session_cached(
            LOUVORES_FILE,
            catalog_cols,
            loader=load_data,
            preparer=prepare_louvores_with_meta,
        )
        if not louvores_df.empty and "title" in louvores_df.columns:
            louvores_df = louvores_df.copy()
            louvores_df["title"] = louvores_df["title"].astype(str).apply(
                fix_louvor_display_title
            )
        if _needs_louvores_content(route, mobile=mobile):
            content_cols = ("title", "artist", *LOUVOR_SEQUENCIA_COLUMNS)
            content_df = load_data_session_cached(
                LOUVORES_FILE,
                content_cols,
                loader=load_data,
            )
            louvores_df = merge_louvores_content(louvores_df, content_df)
            louvores_df = prepare_louvores_with_meta(louvores_df)

    playlist_df = _EMPTY_DF.copy()
    if _needs_playlist(route, mobile=mobile):
        playlist_df = load_data_session_cached(
            PLAYLIST_FILE,
            PLAYLIST_COLUMNS,
            loader=load_data,
            preparer=prepare_playlist,
        )

    eventos_df = _EMPTY_DF.copy()
    if _needs_eventos(route, mobile=mobile):
        eventos_df = load_data_session_cached(
            EVENTOS_FILE,
            EVENTO_COLUMNS,
            loader=load_data,
            preparer=prepare_eventos,
        )

    feed_posts_df = feed_likes_df = feed_comments_df = _EMPTY_DF.copy()
    if _needs_feed(route, mobile=mobile):
        feed_posts_df, feed_likes_df, feed_comments_df = load_feed_bundle()

    chat_ensaio_df = _EMPTY_DF.copy()
    if _needs_chat_ensaio(route, mobile=mobile):
        chat_ensaio_df = load_data_session_cached(
            CHAT_ENSAIO_FILE,
            CHAT_ENSAIO_COLUMNS,
            loader=load_data,
            preparer=prepare_chat_ensaio,
        )

    return AppDataBundle(
        members_df=members_df,
        chat_df=chat_df,
        sugestoes_df=sugestoes_df,
        escalas_df=escalas_df,
        programa_df=programa_df,
        equipe_df=equipe_df,
        trocas_df=trocas_df,
        louvores_df=louvores_df,
        playlist_df=playlist_df,
        eventos_df=eventos_df,
        feed_posts_df=feed_posts_df,
        feed_likes_df=feed_likes_df,
        feed_comments_df=feed_comments_df,
        chat_ensaio_df=chat_ensaio_df,
    )


def should_run_chat_poll(*, mobile: bool) -> bool:
    route = current_app_route(mobile=mobile)
    if mobile:
        return route in (
            "Início",
            "Chat",
            "Escalas",
            "Gerenciar Escalas",
            "Notificações",
        )
    return route in (
        "Dashboard",
        "Chat",
        "Escalas",
        "Gerenciar Escalas",
        "Feed",
        "Avisos",
        "Notificações",
        "Início",
    )


def should_run_escalas_poll(*, mobile: bool) -> bool:
    route = current_app_route(mobile=mobile)
    if mobile:
        return route in ("Início", "Escalas", "Gerenciar Escalas")
    return route in (
        "Dashboard",
        "Escalas",
        "Gerenciar Escalas",
        "Chat",
        "Feed",
        "Repertório",
    )
