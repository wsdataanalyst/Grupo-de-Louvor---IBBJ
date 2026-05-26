import base64
import hashlib
import html
import inspect
import io
import os
import re
import unicodedata
import uuid
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime, timedelta

from app_time import (
    REMEMBER_EMAIL_KEY,
    SESSION_IDLE_MINUTES,
    SESSION_REMEMBER_DAYS,
    format_local,
    now_local,
    parse_timestamp,
    to_local_timestamps,
    session_expired_user_message,
    session_is_valid,
    session_logout,
    session_touch,
    timestamp_now,
)
from chat_media import (
    ensure_chat_media_columns,
    media_absolute_path,
    save_audio_upload,
    save_image_upload,
)
from chat_whatsapp import render_whatsapp_chat_composer
from data_persistence import (
    backup_csv_if_exists,
    latest_backup,
    load_csv_preserve_rows,
    members_save_allowed,
    prepare_members,
    snapshot_data_folder,
)
from password_reset import (
    apply_password_reset,
    create_password_reset_request,
    email_is_configured,
    validate_reset_token,
)
from catalog_sanitize import fix_louvor_display_title
from escala_member_stats import (
    format_date_br,
    member_escala_occurrences,
    member_escala_stats,
)
from app_features import (
    count_pending_sugestoes,
    feed_image_display_path,
    inject_app_notification_badges,
    inject_hidden_sidebar_script,
    lookup_louvor_meta,
    member_escala_option_label,
    programa_duracao_total,
    render_dashboard_future_escalas,
    render_dashboard_section_end,
    render_dashboard_section_start,
    quick_nav_css_class,
    render_escala_planner_panel,
    save_feed_image_file,
)
from feed_graphics import generate_novo_louvor_banner
from feed_scheduler import (
    FEED_QUEUE_COLUMNS,
    merge_queue,
    process_due_posts,
    schedule_culto_prayers,
    schedule_weekly_team_post,
)
from instrument_kit_links import instrument_kits_from_roles, kit_youtube_url
from whatsapp_share import (
    build_escala_share_message,
    inject_copy_whatsapp_message,
    inject_share_pdf_whatsapp,
    share_escala_text,
    whatsapp_auto_prompt_enabled,
    whatsapp_automation_status,
    whatsapp_group_phone,
    whatsapp_share_url,
)
from louvor_meta import (
    LOUVOR_THEMES,
    classify_themes,
    ensure_louvor_row_metadata,
    format_duracao_total,
    guia_ministracao_text,
    parse_duracao_min,
    suggest_biblical_refs,
    themes_from_csv,
    themes_to_csv,
    validate_louvor,
)
from escala_pdf import (
    build_escalas_pdf,
    filter_escalas_by_period,
    format_period_label,
    suggested_filename,
)
from sequencia_culto import (
    PROGRAMA_SEQUENCIA_COLUMNS,
    TOM_OPCOES,
    build_trechos_banda_ui,
    build_trechos_vocal_ui,
    default_cifra_from_louvor,
    default_lyrics_from_louvor,
    display_cifra_transposed,
    effective_tom,
    get_sequencia_row,
    join_paragraphs,
    markup_to_json,
    parse_markup,
    render_cifra_direcoes_html,
    render_cifra_html,
    render_lyrics_annotated_html,
    split_lyrics_paragraphs,
    trechos_banda_from_markup,
    trechos_from_markup,
    upsert_sequencia_row,
    autosave_sequencia_trabalho,
    integrantes_marcacao_opts,
    banda_escala,
)
from user_feedback import (
    MSG_IMPROVEMENTS,
    show_exception_error,
    show_form_error,
    show_technical_error,
)
from push_notifications import (
    notify_chat_message,
    notify_new_escala,
    onesignal_app_id,
    push_config_status,
    push_is_enabled,
    send_test_notification,
)

APP_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = APP_ROOT / "assets"
_TEXT_INPUT_HAS_BIND = "bind" in inspect.signature(st.text_input).parameters
CROSS_IMAGE = ASSETS_DIR / "cruz.svg"
GROUP_NAME = "Grupo de Louvor - IBBJ"
LOGIN_DISPLAY_TITLE = "IBBJ - Louvor"
CADASTRO_QUERY_PARAM = "cadastro"
FORGOT_PASSWORD_QUERY_PARAM = "esqueci"
RESET_PASSWORD_QUERY_PARAM = "redefinir"

DATA_DIR = Path("data")
RESET_TOKENS_FILE = DATA_DIR / "password_reset_tokens.csv"
PROFILE_PHOTOS_DIR = DATA_DIR / "profile_photos"
MEMBERS_FILE = DATA_DIR / "members.csv"
MEMBER_COLUMNS = (
    "first_name",
    "last_name",
    "email",
    "roles",
    "password_hash",
    "created_at",
    "profile_photo",
    "phone",
    "bio",
)
CHAT_FILE = DATA_DIR / "chat.csv"
ESCALAS_FILE = DATA_DIR / "escalas.csv"
TROCAS_FILE = DATA_DIR / "trocas_escalas.csv"
PROGRAMA_FILE = DATA_DIR / "programa_culto.csv"
PROGRAMA_SEQUENCIA_FILE = DATA_DIR / "programa_sequencia.csv"
EQUIPE_FILE = DATA_DIR / "escala_equipe.csv"
PLAYLIST_FILE = DATA_DIR / "playlist.csv"
LOUVORES_FILE = DATA_DIR / "louvores.csv"
EVENTOS_FILE = DATA_DIR / "eventos.csv"
FEED_POSTS_FILE = DATA_DIR / "feed_posts.csv"
FEED_LIKES_FILE = DATA_DIR / "feed_likes.csv"
FEED_COMMENTS_FILE = DATA_DIR / "feed_comments.csv"
FEED_QUEUE_FILE = DATA_DIR / "feed_queue.csv"
# Orações/posts automáticos no feed (desativado: geravam centenas de posts e lentidão).
FEED_AUTO_SCHEDULE_ENABLED = False
# Limpeza única após deploy (incremente se precisar rodar de novo).
FEED_ONE_TIME_PURGE_VERSION = 1
SUGESTOES_FILE = DATA_DIR / "sugestoes_louvor.csv"
PLAYLIST_COLUMNS = (
    "id",
    "member_email",
    "title",
    "artist",
    "key",
    "youtube_url",
    "cifra_url",
    "ritmo",
    "notes",
    "added_at",
)
FEED_POST_COLUMNS = (
    "id",
    "post_type",
    "title",
    "body",
    "youtube_url",
    "cifra_url",
    "ref_id",
    "author_email",
    "author_name",
    "created_at",
    "image_url",
)
FEED_LIKE_COLUMNS = ("id", "post_id", "email", "created_at")
FEED_COMMENT_COLUMNS = ("id", "post_id", "email", "name", "message", "created_at")
CHAT_ENSAIO_FILE = DATA_DIR / "chat_ensaio.csv"

CULTO_PARTES = [
    "Abertura / Entrada",
    "Louvor 1",
    "Louvor 2",
    "Louvor 3",
    "Momento de adoração",
    "Oferta",
    "Louvor pós-mensagem",
    "Apelo / Encerramento",
]
PROGRAMA_COLUMNS = (
    "id",
    "escala_id",
    "ordem",
    "parte",
    "louvor_title",
    "artist",
    "key",
    "youtube_url",
    "cifra_url",
    "leader_email",
    "leader_name",
    "notes",
)
EQUIPE_COLUMNS = ("id", "escala_id", "member_email", "member_name", "funcao")

ESCALA_COLUMNS = (
    "id",
    "date",
    "event",
    "responsible",
    "member_email",
    "member_name",
    "notes",
    "rehearsal_date",
)
TROCA_COLUMNS = (
    "id",
    "escala_id_origem",
    "escala_id_destino",
    "requester_email",
    "requester_name",
    "target_email",
    "target_name",
    "status",
    "message",
    "created_at",
    "responded_at",
    "tipo",
    "accepter_email",
    "accepter_name",
)
CHAT_COLUMNS = ("timestamp", "email", "name", "message", "message_type", "media_file")
CHAT_ENSAIO_COLUMNS = (
    "timestamp",
    "escala_id",
    "email",
    "name",
    "message",
    "message_type",
    "media_file",
)
CHAT_AUDIO_DIR = DATA_DIR / "chat_audio"
CHAT_IMAGES_DIR = DATA_DIR / "chat_images"
FEED_IMAGES_DIR = DATA_DIR / "feed_images"
LOUVOR_EXTRA_COLUMNS = (
    "temas",
    "ref_biblica",
    "duracao_min",
    "validacao_status",
    "validacao_nota",
)
LOUVOR_SEQUENCIA_COLUMNS = ("lyrics_text", "cifra_text")
ENSAIO_AUDIO_DIR = DATA_DIR / "audios_ensaio"
EVENTO_COLUMNS = (
    "id",
    "title",
    "description",
    "event_date",
    "end_date",
    "image_url",
    "created_at",
    "created_by_email",
    "created_by_name",
)
SUGESTAO_COLUMNS = (
    "id",
    "title",
    "youtube_url",
    "suggester_email",
    "suggester_name",
    "status",
    "created_at",
    "review_notes",
)
SUGESTAO_STATUS_PENDENTE = "pendente"
SUGESTAO_STATUS_EM_ANALISE = "em_analise"
SUGESTAO_STATUS_APROVADA = "aprovada"
SUGESTAO_STATUS_RECUSADA = "recusada"
SUGESTAO_STATUS_LABELS = {
    SUGESTAO_STATUS_PENDENTE: "Pendente",
    SUGESTAO_STATUS_EM_ANALISE: "Em análise",
    SUGESTAO_STATUS_APROVADA: "Aprovada",
    SUGESTAO_STATUS_RECUSADA: "Recusada",
}
FUNCAO_MINISTRADOR = "Ministrador"
FUNCAO_TECNICO_SOM = "Técnico de som"

MENU_ITEMS_BASE = [
    ("Feed", "📰", "Novidades, músicas e comunicados"),
    ("Dashboard", "🎼", "Sua semana, equipe e novidades"),
    ("Gerenciar Escalas", "🎯", "Montar cultos, equipe e louvores"),
    ("Repertório", "🎶", "Todas as músicas do ministério"),
    ("Escalas", "🎤", "Escalas, ensaio e trocas"),
    ("Eventos", "📅", "Próximos eventos do ministério"),
    ("Sugestão de louvor", "💡", "Sugerir música para o repertório"),
    ("Playlist", "🎧", "Sua playlist de treino"),
    ("Chat", "💬", "Comunicação"),
    ("Membros", "🎹", "Integrantes do ministério"),
    ("Perfil", "👤", "Sua foto e dados cadastrais"),
]
MENU_HEADERS = {
    "Dashboard": "Sua semana no ministério",
    "Gerenciar Escalas": "Painel de gestão de escalas",
    "Repertório": "Repertório de louvores",
    "Escalas": "Escalas, ensaio e trocas",
    "Feed": "Feed do ministério",
    "Eventos": "Eventos e novidades",
    "Sugestão de louvor": "Sugerir música ao repertório",
    "Playlist": "Sua playlist pessoal",
    "Chat": "Chat do grupo",
    "Membros": "Integrantes do grupo",
    "Perfil": "Sua foto e dados cadastrais",
    "Avisos": "Comunicados e avisos do ministério",
}
MENU_ACCENTS = {
    "Dashboard": "#20b2aa",
    "Gerenciar Escalas": "#d4af37",
    "Repertório": "#d4af37",
    "Escalas": "#20b2aa",
    "Feed": "#00c2cb",
    "Eventos": "#6b7280",
    "Sugestão de louvor": "#d4af37",
    "Playlist": "#00c2cb",
    "Chat": "#34d399",
    "Membros": "#9ca3af",
    "Perfil": "#d4af37",
}

# Organização do menu por áreas (sidebar — layout premium v2)
NAV_GROUP_ORDER = (
    ("Principal", ("Dashboard", "Feed")),
    (
        "Ministério",
        ("Escalas", "Gerenciar Escalas", "Repertório", "Playlist", "Sugestão de louvor"),
    ),
    ("Comunicação", ("Chat", "Eventos", "Avisos")),
    ("Pessoas", ("Membros", "Perfil")),
)

DASHBOARD_QUICK_LINKS = (
    "Escalas",
    "Chat",
    "Eventos",
    "Playlist",
    "Feed",
    "Repertório",
    "Sugestão de louvor",
    "Perfil",
)

AVISOS_NAV_ITEM = ("Avisos", "🔔", "Comunicados e avisos do ministério")

ROLE_LIDER = "Líder"
ROLE_ORG_MUSICAL = "Organizador Musical"
ROLE_ORG_VOCAL = "Organizador Vocal"
ROLE_DESENVOLVEDOR = "Desenvolvedor"
LEADERSHIP_ROLES = {ROLE_LIDER, ROLE_ORG_MUSICAL, ROLE_ORG_VOCAL, ROLE_DESENVOLVEDOR}

# Reconhecimento automático pelo primeiro nome no cadastro
RECOGNIZED_BY_FIRST_NAME = {
    "marcos": ROLE_LIDER,
    "david": ROLE_ORG_MUSICAL,
    "willame": ROLE_ORG_VOCAL,
}
CATALOG_PAGE_SIZE = 20

MUSICIAN_ROLES = [
    "Vocalista - Tenor",
    "Vocalista - Contralto",
    "Vocalista - Soprano",
    "Vocalista - Mezzo Soprano",
    "Vocalista - Baritono",
    "Baixista",
    "Guitarrista",
    "Violonista",
    "Baterista",
    "Tecladista",
    "Técnico de som",
]
ROLES = MUSICIAN_ROLES  # compatibilidade


def normalize_first_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name.strip().lower())
    return "".join(ch for ch in name if not unicodedata.combining(ch))


def recognized_leadership_role(first_name: str) -> str | None:
    return RECOGNIZED_BY_FIRST_NAME.get(normalize_first_name(first_name))


def parse_primary_role(roles: str) -> str:
    roles_lower = str(roles).lower()
    if ROLE_LIDER.lower() in roles_lower or "lider" in roles_lower:
        return ROLE_LIDER
    if ROLE_ORG_MUSICAL.lower() in roles_lower:
        return ROLE_ORG_MUSICAL
    if ROLE_ORG_VOCAL.lower() in roles_lower:
        return ROLE_ORG_VOCAL
    if ROLE_DESENVOLVEDOR.lower() in roles_lower:
        return ROLE_DESENVOLVEDOR
    return "membro"


def is_scale_manager(roles: str) -> bool:
    return parse_primary_role(roles) in LEADERSHIP_ROLES


def can_reset_member_passwords(roles: str | None = None) -> bool:
    """Líderes, organizadores e desenvolvedores podem redefinir senhas."""
    roles = roles if roles is not None else str(st.session_state.get("user_roles", ""))
    if is_scale_manager(roles):
        return True
    return is_current_developer()


def is_leader(roles: str) -> bool:
    return parse_primary_role(roles) == ROLE_LIDER


def build_roles_for_registration(first_name: str, musician_roles: list) -> list:
    special = recognized_leadership_role(first_name)
    if special:
        extra = [r for r in musician_roles if r not in LEADERSHIP_ROLES]
        return [special] + extra
    return musician_roles


def sync_recognized_member_roles(members_df: pd.DataFrame) -> pd.DataFrame:
    updated = False
    for idx, row in members_df.iterrows():
        special = recognized_leadership_role(str(row.get("first_name", "")))
        if not special:
            continue
        current = str(row.get("roles", ""))
        if special not in current:
            parts = [p.strip() for p in current.split(",") if p.strip()]
            parts = [special] + [p for p in parts if p not in LEADERSHIP_ROLES]
            members_df.at[idx, "roles"] = ", ".join(parts)
            updated = True
    if updated:
        save_data(members_df, MEMBERS_FILE, quiet=True)
    return members_df


def get_menu_items_for_user(roles: str) -> list:
    hidden_for_members = {"Gerenciar Escalas", "Repertório", "Membros"}
    items = [
        item for item in MENU_ITEMS_BASE if item[0] not in hidden_for_members
    ]
    if is_scale_manager(roles) or can_reset_member_passwords(roles):
        items = [item for item in MENU_ITEMS_BASE if item[0] != "Gerenciar Escalas"]
        items.insert(1, ("Gerenciar Escalas", "🎯", "Montar cultos, equipe e louvores"))
        if not is_scale_manager(roles) and can_reset_member_passwords(roles):
            # Desenvolvedor sem papel de líder: Membros + redefinir senhas
            if not any(n == "Membros" for n, _, _ in items):
                membros = next(x for x in MENU_ITEMS_BASE if x[0] == "Membros")
                items.append(membros)
    labels = {f"{icon}  {name}": name for name, icon, _ in items}
    icons = {name: icon for name, icon, _ in items}
    return items, labels, icons


def build_nav_groups_for_user(roles: str) -> list[tuple[str, list[tuple[str, str, str]]]]:
    """Agrupa itens do menu em seções para navegação na sidebar."""
    items, _, _ = get_menu_items_for_user(roles)
    by_name = {name: (name, icon, desc) for name, icon, desc in items}
    groups: list[tuple[str, list[tuple[str, str, str]]]] = []
    for group_label, names in NAV_GROUP_ORDER:
        section: list[tuple[str, str, str]] = []
        for n in names:
            if n == "Avisos":
                if "Feed" in by_name:
                    section.append(AVISOS_NAV_ITEM)
                continue
            if n in by_name:
                section.append(by_name[n])
        if section:
            groups.append((group_label, section))
    placed = {n for _, section in groups for n, _, _ in section}
    rest = [item for item in items if item[0] not in placed]
    if rest:
        groups.append(("Mais", rest))
    return groups


def menu_icons_map(roles: str) -> dict[str, str]:
    _, _, icons = get_menu_items_for_user(roles)
    return icons


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _query_param_value(key: str) -> str:
    raw = st.query_params.get(key, "")
    if isinstance(raw, list):
        return str(raw[0]).strip() if raw else ""
    return str(raw).strip()


def is_register_page() -> bool:
    cadastro = _query_param_value(CADASTRO_QUERY_PARAM).lower()
    if cadastro in ("1", "true", "sim", "yes"):
        return True
    page = _query_param_value("page").lower()
    return page in ("cadastro", "cadastrar", "register", "signup")


def _login_view_mode() -> str:
    """login | register | forgot | reset — telas da página inicial."""
    return str(st.session_state.get("login_view", "login")).strip().lower()


def _set_login_view(mode: str) -> None:
    st.session_state.login_view = mode


def _sync_login_view_from_url() -> None:
    if is_reset_password_page():
        _set_login_view("reset")
    elif is_forgot_password_page():
        _set_login_view("forgot")
    elif is_register_page():
        _set_login_view("register")


def is_forgot_password_page() -> bool:
    esqueci = _query_param_value(FORGOT_PASSWORD_QUERY_PARAM).lower()
    if esqueci in ("1", "true", "sim", "yes"):
        return True
    page = _query_param_value("page").lower()
    return page in ("esqueci", "esqueci-senha", "forgot", "recuperar")


def get_reset_password_token() -> str:
    return _query_param_value(RESET_PASSWORD_QUERY_PARAM)


def is_reset_password_page() -> bool:
    return len(get_reset_password_token()) >= 20


def get_password_reset_base_url() -> str:
    base = get_public_app_url()
    if base:
        return base
    try:
        port = int(st.get_option("server.port") or 8501)
        addr = str(st.get_option("server.address") or "localhost")
        if addr in ("0.0.0.0", ""):
            addr = "localhost"
        return f"http://{addr}:{port}"
    except Exception:
        return ""


def get_public_app_url() -> str:
    url = os.environ.get("PUBLIC_APP_URL", os.environ.get("STREAMLIT_APP_URL", "")).strip()
    if not url:
        try:
            url = str(st.secrets.get("public_url", "")).strip()
        except (FileNotFoundError, KeyError, AttributeError):
            url = ""
        if not url:
            try:
                url = str(st.secrets.get("app", {}).get("public_url", "")).strip()
            except (FileNotFoundError, KeyError, AttributeError):
                url = ""
    return url.rstrip("/")


def get_registration_url() -> str:
    base = get_public_app_url()
    if base:
        return f"{base}/?{CADASTRO_QUERY_PARAM}=1"
    try:
        port = int(st.get_option("server.port") or 8501)
        addr = str(st.get_option("server.address") or "localhost")
        if addr in ("0.0.0.0", ""):
            addr = "localhost"
        return f"http://{addr}:{port}/?{CADASTRO_QUERY_PARAM}=1"
    except Exception:
        return f"?{CADASTRO_QUERY_PARAM}=1"


def render_registration_link_box(compact: bool = False):
    link = get_registration_url()
    if compact:
        st.sidebar.caption("🔗 Link para novos membros")
        st.sidebar.code(link, language=None)
    else:
        st.markdown("##### 🔗 Link de cadastro (compartilhe com o grupo)")
        st.code(link, language=None)
        st.caption(
            "Qualquer pessoa com este link abre direto o formulário de cadastro. "
            "Para publicar na internet, defina `public_url` em `.streamlit/secrets.toml`."
        )


def render_register_form(members_df: pd.DataFrame) -> pd.DataFrame:
    with st.form(key="register_form"):
        first_name = st.text_input("Nome", key="reg_first_name")
        last_name = st.text_input("Sobrenome", key="reg_last_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Senha", type="password", key="reg_password")
        confirm_password = st.text_input(
            "Confirme a senha", type="password", key="reg_confirm_password"
        )
        special_hint = recognized_leadership_role(first_name)
        if special_hint:
            st.info(
                f"✨ Nome reconhecido: você será cadastrado como **{special_hint}**. "
                "As funções musicais abaixo são opcionais."
            )
        roles = st.multiselect(
            "Função(ões) no ministério (música, técnico de som, etc.)",
            MUSICIAN_ROLES,
            key="reg_roles",
        )
        register_button = st.form_submit_button(
            "Criar conta", type="primary", use_container_width=True
        )

    if register_button:
        if not first_name or not last_name or not email or not password:
            show_form_error("Preencha nome, sobrenome, email e senha.")
        elif not special_hint and not roles:
            show_form_error("Escolha pelo menos uma função (música ou técnico de som).")
        elif not is_valid_email(email):
            show_form_error("Informe um email válido.")
        elif len(password) < 6:
            show_form_error("A senha deve ter pelo menos 6 caracteres.")
        elif password != confirm_password:
            show_form_error("As senhas não coincidem.")
        else:
            new_member, error = register_user(
                first_name, last_name, email, password, roles, members_df
            )
            if error:
                show_form_error(str(error))
            else:
                role_msg = new_member["roles"]
                st.success(
                    f"Cadastro criado como **{role_msg}**! "
                    "Agora faça login com seu email e senha."
                )
                members_df = load_data(MEMBERS_FILE, MEMBER_COLUMNS)
                _set_login_view("login")
                try:
                    st.query_params.clear()
                except Exception:
                    pass
    return members_df


@st.cache_data
def load_data(file_path: Path, columns: tuple):
    from remote_store import (
        dataframe_from_remote,
        is_remote_enabled,
        push_file_from_disk,
        should_sync_file,
    )

    df = None
    if should_sync_file(file_path) and is_remote_enabled():
        remote_df = None
        try:
            remote_df = dataframe_from_remote(columns, file_path.name)
        except Exception:
            remote_df = None
        local_df = load_csv_preserve_rows(file_path, columns)
        if remote_df is not None and not (
            file_path == MEMBERS_FILE and remote_df.empty
        ):
            df = remote_df
            file_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(file_path, index=False)
        else:
            df = local_df
            if not df.empty and file_path != MEMBERS_FILE:
                try:
                    push_file_from_disk(file_path)
                except Exception:
                    pass
            elif (
                file_path == MEMBERS_FILE
                and not df.empty
                and remote_df is not None
                and remote_df.empty
            ):
                try:
                    push_file_from_disk(file_path)
                except Exception:
                    pass
    else:
        df = load_csv_preserve_rows(file_path, columns)

    if file_path == MEMBERS_FILE:
        df = prepare_members(df)
        if df.empty:
            backup = latest_backup(file_path, DATA_DIR)
            if backup:
                recovered = prepare_members(load_csv_preserve_rows(backup, columns))
                if not recovered.empty:
                    df = recovered
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    df.to_csv(file_path, index=False)
                    if is_remote_enabled():
                        try:
                            push_file_from_disk(file_path)
                        except Exception:
                            pass
    return df


def save_data(
    df: pd.DataFrame,
    file_path: Path,
    *,
    force: bool = False,
    quiet: bool = False,
) -> bool:
    """Grava CSV local + nuvem (Supabase). Retorna False se proteção bloquear members."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path == MEMBERS_FILE:
        df = prepare_members(df)
        ok, msg = members_save_allowed(df, file_path, force=force)
        if not ok:
            if not quiet:
                show_technical_error(msg)
            return False

    backup_csv_if_exists(file_path, DATA_DIR)
    df.to_csv(file_path, index=False)

    from remote_store import is_remote_enabled, push_file_from_disk, should_sync_file

    if should_sync_file(file_path) and is_remote_enabled():
        try:
            if not push_file_from_disk(file_path):
                if is_current_developer():
                    show_technical_error(
                        "Salvo no servidor, mas não foi possível sincronizar com a nuvem. "
                        "Verifique CONFIGURAR_SUPABASE.md."
                    )
        except Exception:
            if is_current_developer():
                show_technical_error(
                    "Salvo localmente; falha ao enviar para Supabase. Veja secrets [persistence]."
                )

    load_data.clear()
    if file_path.name in ESCALA_LIVE_FILE_NAMES:
        try:
            refresh_escalas_bundle()
        except Exception:
            pass
    return True


def new_id() -> str:
    return str(uuid.uuid4())[:8]


def email_to_photo_slug(email: str) -> str:
    return email.strip().lower().replace("@", "_at_").replace(".", "_")


def ensure_local_profile_photos(members_df: pd.DataFrame) -> None:
    """Restaura fotos da nuvem após reboot (Streamlit Cloud)."""
    if members_df.empty:
        return
    from remote_store import is_remote_enabled, pull_profile_photo_file

    if not is_remote_enabled():
        return
    PROFILE_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    members_df = prepare_members(members_df)
    for _, row in members_df.iterrows():
        fn = str(row.get("profile_photo", "")).strip()
        if not fn:
            continue
        dest = PROFILE_PHOTOS_DIR / fn
        if not dest.exists():
            pull_profile_photo_file(fn, PROFILE_PHOTOS_DIR)
        elif dest.is_file():
            from remote_store import push_profile_photo_file

            push_profile_photo_file(dest)


def profile_photo_file(email: str, stored_name: str = "") -> Path | None:
    PROFILE_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    if stored_name:
        path = PROFILE_PHOTOS_DIR / stored_name
        if path.exists():
            return path
    slug = email_to_photo_slug(email)
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        path = PROFILE_PHOTOS_DIR / f"{slug}{ext}"
        if path.exists():
            return path
    return None


def _profile_upload_bytes(uploaded_file) -> tuple[str, bytes]:
    """Bytes + nome a partir de UploadedFile ou dict guardado na sessão."""
    if isinstance(uploaded_file, dict):
        name = str(uploaded_file.get("name") or "photo.jpg")
        raw = bytes(uploaded_file.get("bytes") or b"")
        return name, raw
    name = str(getattr(uploaded_file, "name", None) or "photo.jpg")
    return name, uploaded_file.getvalue()


def save_profile_photo(email: str, uploaded_file) -> str:
    PROFILE_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    upload_name, raw = _profile_upload_bytes(uploaded_file)
    if not raw:
        raise ValueError("Arquivo de imagem vazio.")
    if len(raw) > 5 * 1024 * 1024:
        raise ValueError("Imagem muito grande (máx. 5 MB).")
    ext = Path(upload_name).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    slug = email_to_photo_slug(email)
    for old in PROFILE_PHOTOS_DIR.glob(f"{slug}.*"):
        old.unlink(missing_ok=True)
    filename = f"{slug}{ext}"
    dest = PROFILE_PHOTOS_DIR / filename
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(raw))
        img = img.convert("RGB")
        img.thumbnail((800, 800))
        if ext in (".png", ".webp"):
            img.save(dest, format="PNG", optimize=True)
            filename = f"{slug}.png"
            dest = PROFILE_PHOTOS_DIR / filename
        else:
            img.save(dest, format="JPEG", quality=88, optimize=True)
            filename = f"{slug}.jpg"
            dest = PROFILE_PHOTOS_DIR / filename
    except Exception:
        dest.write_bytes(raw)
    try:
        from remote_store import push_profile_photo_file

        push_profile_photo_file(dest)
    except Exception:
        pass
    return filename


def profile_photo_to_data_uri(email: str, stored_name: str = "") -> str | None:
    path = profile_photo_file(email, stored_name)
    if not path:
        return None
    mime = "image/jpeg"
    if path.suffix.lower() == ".png":
        mime = "image/png"
    elif path.suffix.lower() == ".webp":
        mime = "image/webp"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def member_photo_html(email: str, members_df: pd.DataFrame, size: int = 56) -> str:
    email_l = email.strip().lower()
    stored = ""
    if not members_df.empty and "email" in members_df.columns:
        match = members_df[members_df["email"].astype(str).str.lower() == email_l]
        if not match.empty:
            stored = str(match.iloc[0].get("profile_photo", ""))
    uri = profile_photo_to_data_uri(email_l, stored)
    if uri:
        return (
            f'<img class="member-avatar" src="{uri}" alt="" '
            f'style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;" />'
        )
    return (
        f'<motion-placeholder class="member-avatar-ph" '
        f'style="width:{size}px;height:{size}px;border-radius:50%;'
        f"display:inline-flex;align-items:center;justify-content:center;"
        f'background:rgba(139,92,246,0.35);font-size:{size//2}px;">🎤</motion-placeholder>'
    ).replace("motion-placeholder", "span")


def split_member_roles(roles_str: str) -> tuple[list[str], list[str]]:
    parts = [p.strip() for p in str(roles_str).split(",") if p.strip()]
    leadership = [p for p in parts if p in LEADERSHIP_ROLES]
    musician = [p for p in parts if p in MUSICIAN_ROLES]
    return leadership, musician


def merge_member_roles(leadership: list[str], musician: list[str]) -> str:
    seen = set()
    merged = []
    for role in leadership + musician:
        if role and role not in seen:
            seen.add(role)
            merged.append(role)
    return ", ".join(merged)


# Funções exibidas ao montar a equipe da escala (papéis de liderança ficam no perfil)
ESCALA_FUNCOES_EXIBICAO = ["Integrante", "Banda", FUNCAO_TECNICO_SOM]


def roles_for_public_display(roles_str: str) -> str:
    """Oculta Líder/Organizador/Desenvolvedor — mostra funções musicais ou Integrante."""
    _, musician = split_member_roles(roles_str)
    if musician:
        return ", ".join(musician)
    return "Integrante"


def normalize_funcao_escala(funcao: str) -> str:
    """Normaliza função gravada na equipe da escala para exibição consistente."""
    f = str(funcao).strip()
    fl = f.lower().replace("é", "e")
    if f == FUNCAO_TECNICO_SOM or "tecnico" in fl and "som" in fl:
        return FUNCAO_TECNICO_SOM
    if f in ("Integrante", "Banda", "Responsável", FUNCAO_MINISTRADOR):
        if f == "Responsável":
            return FUNCAO_MINISTRADOR
        return f
    if f in LEADERSHIP_ROLES:
        return "Integrante"
    if f in MUSICIAN_ROLES:
        return "Banda"
    if any(k in fl for k in ("vocal", "guitar", "baix", "bater", "teclad", "violon")):
        return "Banda"
    return "Integrante"


def default_funcao_para_escala(row) -> str:
    _, musician = split_member_roles(str(row.get("roles", "")))
    if FUNCAO_TECNICO_SOM in musician:
        return FUNCAO_TECNICO_SOM
    if musician:
        return "Banda"
    return "Integrante"


def default_funcao_escala_index(members_df: pd.DataFrame, member_map: dict, labels: list) -> int:
    """Sugere função na escala conforme o cadastro do primeiro integrante selecionado."""
    if not labels:
        return 0
    email = member_map.get(labels[0], "").strip().lower()
    if not email or members_df.empty:
        return 0
    match = members_df[members_df["email"].astype(str).str.strip().str.lower() == email]
    if match.empty:
        return 0
    sug = default_funcao_para_escala(match.iloc[0])
    try:
        return ESCALA_FUNCOES_EXIBICAO.index(sug)
    except ValueError:
        return 0


def members_options_escala(members_df: pd.DataFrame) -> dict[str, str]:
    """Lista de integrantes para escalas — apenas nome, sem cargos de liderança."""
    options = {}
    for _, row in members_visible_to_group(members_df).iterrows():
        email = str(row["email"]).strip().lower()
        if email:
            options[member_display_name(row)] = email
    return options


def member_escala_select_format(
    label: str,
    member_map: dict[str, str],
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    culto_ref: date,
) -> str:
    email = member_map.get(label, "")
    if not email:
        return label
    return member_escala_option_label(label, email, escalas_df, equipe_df, culto_ref)


def prepare_louvores_with_meta(df: pd.DataFrame) -> pd.DataFrame:
    from catalog_sanitize import prepare_louvores_df

    df = prepare_louvores_df(df)
    for col in LOUVOR_EXTRA_COLUMNS + LOUVOR_SEQUENCIA_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df


def purge_all_feed_data() -> int:
    """Apaga todos os posts, curtidas, comentários e fila do feed (local + nuvem)."""
    removed = 0
    try:
        from remote_store import dataframe_from_remote, is_remote_enabled

        if is_remote_enabled():
            remote_df = dataframe_from_remote(FEED_POST_COLUMNS, FEED_POSTS_FILE.name)
            if remote_df is not None:
                removed = len(remote_df)
        elif FEED_POSTS_FILE.exists():
            removed = len(pd.read_csv(FEED_POSTS_FILE, encoding="utf-8"))
    except Exception:
        pass
    save_data(pd.DataFrame(columns=list(FEED_POST_COLUMNS)), FEED_POSTS_FILE)
    save_data(pd.DataFrame(columns=list(FEED_LIKE_COLUMNS)), FEED_LIKES_FILE)
    save_data(pd.DataFrame(columns=list(FEED_COMMENT_COLUMNS)), FEED_COMMENTS_FILE)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=list(FEED_QUEUE_COLUMNS)).to_csv(
        FEED_QUEUE_FILE, index=False, encoding="utf-8"
    )
    load_data.clear()
    try:
        st.session_state.pop("_feed_rev", None)
    except Exception:
        pass
    return removed


def delete_feed_post(post_id: str) -> None:
    posts, likes, comments = load_feed_bundle()
    pid = str(post_id)
    save_data(posts[posts["id"].astype(str) != pid], FEED_POSTS_FILE)
    save_data(likes[likes["post_id"].astype(str) != pid], FEED_LIKES_FILE)
    save_data(comments[comments["post_id"].astype(str) != pid], FEED_COMMENTS_FILE)


def delete_feed_comment(comment_id: str) -> None:
    df = prepare_feed_comments(load_data(FEED_COMMENTS_FILE, FEED_COMMENT_COLUMNS))
    save_data(df[df["id"].astype(str) != str(comment_id)], FEED_COMMENTS_FILE)


def delete_own_chat_message(timestamp: str, email: str) -> None:
    df = prepare_chat(load_data(CHAT_FILE, CHAT_COLUMNS))
    mask = ~(
        (df["timestamp"].astype(str) == str(timestamp))
        & (df["email"].astype(str).str.lower() == email.strip().lower())
    )
    save_data(df[mask], CHAT_FILE)
    load_chat_df.clear()


def update_own_chat_message(timestamp: str, email: str, new_text: str) -> None:
    df = prepare_chat(load_data(CHAT_FILE, CHAT_COLUMNS))
    email_l = email.strip().lower()
    mask = (df["timestamp"].astype(str) == str(timestamp)) & (
        df["email"].astype(str).str.lower() == email_l
    )
    if not mask.any():
        return
    df.loc[mask, "message"] = str(new_text).strip()
    df.loc[mask, "message_type"] = "text"
    df.loc[mask, "media_file"] = ""
    save_data(df, CHAT_FILE)
    load_chat_df.clear()


def process_feed_queue() -> None:
    """Publica posts agendados (orações 6h, escala da semana, etc.)."""
    if not FEED_QUEUE_FILE.exists():
        return
    qdf = load_csv_preserve_rows(FEED_QUEUE_FILE, FEED_QUEUE_COLUMNS)
    if qdf.empty:
        return

    def _append(**kwargs):
        append_feed_post(**kwargs)

    updated = process_due_posts(qdf, _append)
    updated.to_csv(FEED_QUEUE_FILE, index=False)


def delete_own_ensaio_message(timestamp: str, escala_id: str, email: str) -> None:
    df = prepare_chat_ensaio(load_data(CHAT_ENSAIO_FILE, CHAT_ENSAIO_COLUMNS))
    mask = ~(
        (df["timestamp"].astype(str) == str(timestamp))
        & (df["escala_id"].astype(str) == str(escala_id))
        & (df["email"].astype(str).str.lower() == email.strip().lower())
    )
    save_data(df[mask], CHAT_ENSAIO_FILE)


def update_own_ensaio_message(
    timestamp: str, escala_id: str, email: str, new_text: str
) -> None:
    df = prepare_chat_ensaio(load_data(CHAT_ENSAIO_FILE, CHAT_ENSAIO_COLUMNS))
    email_l = email.strip().lower()
    mask = (df["timestamp"].astype(str) == str(timestamp)) & (
        df["escala_id"].astype(str) == str(escala_id)
    ) & (df["email"].astype(str).str.lower() == email_l)
    if not mask.any():
        return
    df.loc[mask, "message"] = str(new_text).strip()
    df.loc[mask, "message_type"] = "text"
    df.loc[mask, "media_file"] = ""
    save_data(df, CHAT_ENSAIO_FILE)


def schedule_feed_posts_for_escala(
    escala_id: str,
    escala_row: dict,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    """Agenda posts no feed (desativado por padrão)."""
    if not FEED_AUTO_SCHEDULE_ENABLED:
        return
    dt_culto = pd.to_datetime(escala_row.get("date"), errors="coerce")
    culto_d = dt_culto.date() if pd.notna(dt_culto) else date.today()
    event = str(escala_row.get("event", "Culto"))
    ensaio = format_rehearsal_date_pt(escala_row) if rehearsal_date_is_set(escala_row) else ""
    escala_series = (
        escala_row
        if isinstance(escala_row, pd.Series)
        else pd.Series(escala_row)
    )
    team_lines = []
    for p in integrantes_escalados(escala_series, equipe_df, members_df):
        team_lines.append(f"• {p.get('name', '')} — {p.get('funcao', '')}")
    team_body = "\n".join(team_lines) if team_lines else "Equipe em formação."
    new_rows = [
        schedule_weekly_team_post(
            escala_id=escala_id,
            event=event,
            culto_date=culto_d,
            ensaio_txt=ensaio,
            team_html_body=team_body,
        )
    ]
    themes_all: list[str] = []
    louvor_titles: list[str] = []
    prog = programa_por_escala(programa_df, escala_id)
    for _, pr in prog.iterrows():
        t = str(pr.get("louvor_title", ""))
        louvor_titles.append(t)
        if not louvores_df.empty:
            m = lookup_louvor_meta(louvores_df, t, str(pr.get("artist", "")))
            themes_all.extend(themes_from_csv(str(m.get("temas", ""))))
    new_rows.extend(
        schedule_culto_prayers(
            escala_id=escala_id,
            event=event,
            culto_date=culto_d,
            themes=list(dict.fromkeys(themes_all)),
            louvor_titles=louvor_titles,
        )
    )
    if FEED_QUEUE_FILE.exists():
        qdf = load_csv_preserve_rows(FEED_QUEUE_FILE, FEED_QUEUE_COLUMNS)
    else:
        qdf = pd.DataFrame(columns=list(FEED_QUEUE_COLUMNS))
    qdf = merge_queue(qdf, new_rows)
    FEED_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    qdf.to_csv(FEED_QUEUE_FILE, index=False)
    process_feed_queue()


def feed_data_revision() -> str:
    from remote_store import fetch_sync_revisions, is_remote_enabled

    if is_remote_enabled():
        try:
            remote = fetch_sync_revisions(FEED_LIVE_FILE_NAMES)
            if remote:
                return f"remote:{remote}"
        except Exception:
            pass
    parts: list[str] = []
    for path in (FEED_POSTS_FILE, FEED_LIKES_FILE, FEED_COMMENTS_FILE):
        try:
            stat = path.stat()
            parts.append(f"{path.name}:{stat.st_mtime_ns}:{stat.st_size}")
        except OSError:
            parts.append(f"{path.name}:missing")
    return "local:" + "|".join(parts)


def chat_data_revision() -> str:
    """Fingerprint do chat.csv (local + nuvem) para detectar mensagens novas."""
    from remote_store import fetch_sync_revisions, is_remote_enabled

    if is_remote_enabled():
        try:
            remote = fetch_sync_revisions(CHAT_LIVE_FILE_NAMES)
            if remote:
                return f"remote:{remote}"
        except Exception:
            pass
    try:
        stat = CHAT_FILE.stat()
        return f"local:{stat.st_mtime_ns}:{stat.st_size}"
    except OSError:
        return "local:missing"


def refresh_chat_live() -> pd.DataFrame:
    """Recarrega chat do disco/nuvem e atualiza cache da sessão."""
    from remote_store import is_remote_enabled, pull_file_to_disk

    if is_remote_enabled():
        try:
            pull_file_to_disk(CHAT_FILE)
        except Exception:
            pass
    chat_df = load_chat_df()
    st.session_state["_chat_df_cache"] = chat_df
    st.session_state._chat_rev = chat_data_revision()
    update_chat_latest_ts(chat_df)
    return chat_df


def sync_member_name_in_records(
    email: str,
    full_name: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    email_l = email.strip().lower()
    if not escalas_df.empty and "member_email" in escalas_df.columns:
        mask = escalas_df["member_email"].astype(str).str.lower() == email_l
        escalas_df.loc[mask, "member_name"] = full_name
        escalas_df.loc[mask, "responsible"] = full_name
    if not equipe_df.empty and "member_email" in equipe_df.columns:
        mask_eq = equipe_df["member_email"].astype(str).str.lower() == email_l
        equipe_df.loc[mask_eq, "member_name"] = full_name
    return escalas_df, equipe_df


def get_current_member_row(members_df: pd.DataFrame):
    email = st.session_state.user_email.strip().lower()
    match = members_df[members_df["email"].astype(str).str.lower() == email]
    if match.empty:
        return None, None
    idx = match.index[0]
    return idx, match.iloc[0]


def member_display_name(row) -> str:
    first = str(row.get("first_name", "")).strip()
    last = str(row.get("last_name", "")).strip()
    return f"{first} {last}".strip() or str(row.get("email", ""))


def member_label(row) -> str:
    name = member_display_name(row)
    roles = str(row.get("roles", "")).strip()
    if roles:
        return f"{name} ({roles})"
    return name


def members_options(members_df: pd.DataFrame) -> dict[str, str]:
    options = {}
    for _, row in members_visible_to_group(members_df).iterrows():
        email = str(row["email"]).strip().lower()
        if email:
            options[member_label(row)] = email
    return options


def prepare_escalas(df: pd.DataFrame) -> pd.DataFrame:
    for column in ESCALA_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[list(ESCALA_COLUMNS)].copy()
    empty_ids = df["id"].astype(str).str.strip() == ""
    if empty_ids.any():
        df.loc[empty_ids, "id"] = [new_id() for _ in range(empty_ids.sum())]
    if "member_name" in df.columns:
        no_email = df["member_email"].astype(str).str.strip() == ""
        df.loc[no_email, "member_name"] = df.loc[no_email, "responsible"]
    return df


def sort_chat_messages(df: pd.DataFrame) -> pd.DataFrame:
    """Ordena mensagens pela data/hora real (fuso BR), não pela ordem do CSV."""
    if df.empty:
        return df
    from app_time import LOCAL_TZ, parse_timestamp

    out = df.copy().reset_index(drop=True)
    keys: list[tuple[datetime, int]] = []
    for i, row in out.iterrows():
        ts = parse_timestamp(str(row.get("timestamp", "")))
        if ts is None:
            keys.append((datetime(1970, 1, 1, tzinfo=LOCAL_TZ), int(i)))
        else:
            keys.append((ts, int(i)))
    keys.sort()
    order = [i for _, i in keys]
    return out.iloc[order].reset_index(drop=True)


def prepare_chat(df: pd.DataFrame) -> pd.DataFrame:
    from app_time import normalize_chat_timestamp_str

    df = ensure_chat_media_columns(df, CHAT_COLUMNS)
    if df.empty:
        return df
    df = df.copy()
    df["email"] = df["email"].astype(str).str.strip().str.lower()
    df["timestamp"] = df["timestamp"].apply(normalize_chat_timestamp_str)
    df = df[df["timestamp"].astype(str).str.strip() != ""].copy()
    df = df.drop_duplicates(
        subset=["email", "message", "timestamp"], keep="first"
    )
    return sort_chat_messages(df)


def prepare_trocas(df: pd.DataFrame) -> pd.DataFrame:
    for column in TROCA_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    out = df[list(TROCA_COLUMNS)].copy()
    # CSV com responded_at vazio vira float64 (NaN) — impede gravar data ao aceitar/assumir troca
    for column in TROCA_COLUMNS:
        out[column] = out[column].fillna("").astype(str)
    return out


def prepare_chat_ensaio(df: pd.DataFrame) -> pd.DataFrame:
    return ensure_chat_media_columns(df, CHAT_ENSAIO_COLUMNS)


def event_plain_text(value, max_len: int = 280) -> str:
    """Remove tags HTML e limita tamanho para exibição em eventos."""
    text = re.sub(r"<[^>]+>", "", str(value or ""))
    text = html.unescape(text).strip()
    if len(text) > max_len:
        text = text[: max_len - 1].rstrip() + "…"
    return text


def prepare_eventos(df: pd.DataFrame) -> pd.DataFrame:
    for column in EVENTO_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[list(EVENTO_COLUMNS)].copy()
    if not df.empty:
        if "title" in df.columns:
            df["title"] = df["title"].apply(lambda v: event_plain_text(v, max_len=200))
        if "description" in df.columns:
            df["description"] = df["description"].apply(
                lambda v: event_plain_text(v, max_len=2000)
            )
    return df


def normalize_sugestao_status(raw: str) -> str:
    s = str(raw).strip().lower().replace(" ", "_")
    aliases = {
        "aprovado": SUGESTAO_STATUS_APROVADA,
        "recusado": SUGESTAO_STATUS_RECUSADA,
        "em_análise": SUGESTAO_STATUS_EM_ANALISE,
        "analise": SUGESTAO_STATUS_EM_ANALISE,
        "em_analise": SUGESTAO_STATUS_EM_ANALISE,
    }
    s = aliases.get(s, s)
    if s in SUGESTAO_STATUS_LABELS:
        return s
    return SUGESTAO_STATUS_PENDENTE


def csv_cell_text(value) -> str:
    """Texto seguro para células CSV (evita exibir/gravar 'nan' em colunas float64)."""
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    if text.lower() in ("nan", "nat", "none", "<na>"):
        return ""
    return text


def prepare_sugestoes(df: pd.DataFrame) -> pd.DataFrame:
    for column in SUGESTAO_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    out = df[list(SUGESTAO_COLUMNS)].copy()
    # Células vazias no CSV viram float64 (NaN) — impedem gravar status/notas na gestão
    for column in SUGESTAO_COLUMNS:
        out[column] = out[column].fillna("").astype(str)
    if not out.empty and "status" in out.columns:
        out["status"] = out["status"].map(normalize_sugestao_status)
    return out


def count_sugestoes_news_for_user(sugestoes_df: pd.DataFrame, email: str) -> int:
    """Sugestões do usuário com status novo desde a última visita à página."""
    email = str(email or "").strip().lower()
    if not email or sugestoes_df.empty:
        return 0
    seen: dict = st.session_state.get("sugestoes_seen_map") or {}
    count = 0
    mine = sugestoes_df[
        sugestoes_df["suggester_email"].astype(str).str.strip().str.lower() == email
    ]
    for _, row in mine.iterrows():
        sid = str(row.get("id", ""))
        status = normalize_sugestao_status(str(row.get("status", "")))
        if status == SUGESTAO_STATUS_PENDENTE:
            continue
        if seen.get(sid) != status:
            count += 1
    return count


def mark_user_sugestoes_seen(sugestoes_df: pd.DataFrame, email: str) -> None:
    email = str(email or "").strip().lower()
    if not email or sugestoes_df.empty:
        return
    seen = dict(st.session_state.get("sugestoes_seen_map") or {})
    mine = sugestoes_df[
        sugestoes_df["suggester_email"].astype(str).str.strip().str.lower() == email
    ]
    for _, row in mine.iterrows():
        seen[str(row.get("id", ""))] = normalize_sugestao_status(str(row.get("status", "")))
    st.session_state["sugestoes_seen_map"] = seen


def sugestao_status_badge_html(status: str) -> str:
    key = normalize_sugestao_status(status)
    label = SUGESTAO_STATUS_LABELS.get(key, key)
    return (
        f'<span class="sugestao-status-pill sugestao-status--{html.escape(key)}">'
        f"{html.escape(label)}</span>"
    )


def _aprovar_sugestao_louvor(
    s: pd.Series,
    sugestoes_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    meta = ensure_louvor_row_metadata(str(s["title"]), "", "", "", "")
    row = {
        "title": s["title"],
        "artist": "",
        "key": "",
        "youtube_url": s["youtube_url"],
        "cifra_url": "",
        "ritmo": "",
        "letter": s["title"][0].upper() if s["title"] else "A",
        "source": "sugestao",
        **meta,
    }
    save_data(
        pd.concat([louvores_df, pd.DataFrame([row])], ignore_index=True),
        LOUVORES_FILE,
    )
    sid = str(s["id"])
    sugestoes_df = prepare_sugestoes(sugestoes_df)
    mask = sugestoes_df["id"].astype(str) == sid
    sugestoes_df.loc[mask, "status"] = SUGESTAO_STATUS_APROVADA
    save_data(sugestoes_df, SUGESTOES_FILE)
    post_feed_louvor_aprovado(
        suggester_name=str(s["suggester_name"]),
        suggester_email=str(s["suggester_email"]),
        title=str(s["title"]),
        youtube_url=str(s["youtube_url"]),
        suggestion_id=sid,
    )


def _prepare_text_columns(df: pd.DataFrame, columns: tuple) -> pd.DataFrame:
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    out = df[list(columns)].copy()
    for column in columns:
        out[column] = out[column].fillna("").astype(str)
    return out


def prepare_playlist(df: pd.DataFrame) -> pd.DataFrame:
    return _prepare_text_columns(df, PLAYLIST_COLUMNS)


def prepare_feed_posts(df: pd.DataFrame) -> pd.DataFrame:
    df = _prepare_text_columns(df, FEED_POST_COLUMNS)
    if df.empty or "id" not in df.columns:
        return df
    df = df.drop_duplicates(subset=["id"], keep="last")
    return df


def prepare_feed_likes(df: pd.DataFrame) -> pd.DataFrame:
    return _prepare_text_columns(df, FEED_LIKE_COLUMNS)


def prepare_feed_comments(df: pd.DataFrame) -> pd.DataFrame:
    return _prepare_text_columns(df, FEED_COMMENT_COLUMNS)


def load_feed_bundle() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        prepare_feed_posts(load_data(FEED_POSTS_FILE, FEED_POST_COLUMNS)),
        prepare_feed_likes(load_data(FEED_LIKES_FILE, FEED_LIKE_COLUMNS)),
        prepare_feed_comments(load_data(FEED_COMMENTS_FILE, FEED_COMMENT_COLUMNS)),
    )


def append_feed_post(
    *,
    post_type: str,
    title: str,
    body: str,
    youtube_url: str = "",
    cifra_url: str = "",
    ref_id: str = "",
    author_email: str = "",
    author_name: str = "",
    image_url: str = "",
) -> None:
    posts_df, _, _ = load_feed_bundle()
    ref_id = str(ref_id).strip()
    title_s = title.strip()
    post_type_s = post_type.strip()
    if ref_id and not posts_df.empty:
        dup = posts_df[posts_df["ref_id"].astype(str).str.strip() == ref_id]
        if post_type_s:
            dup = dup[dup["post_type"].astype(str).str.strip() == post_type_s]
        if title_s:
            dup = dup[dup["title"].astype(str).str.strip() == title_s]
        if not dup.empty:
            return
    row = {
        "id": new_id(),
        "post_type": post_type.strip(),
        "title": title.strip(),
        "body": body.strip(),
        "youtube_url": youtube_url.strip(),
        "cifra_url": cifra_url.strip(),
        "ref_id": ref_id.strip(),
        "author_email": author_email.strip().lower(),
        "author_name": author_name.strip(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_url": image_url.strip(),
    }
    save_data(
        pd.concat([posts_df, pd.DataFrame([row])], ignore_index=True),
        FEED_POSTS_FILE,
    )


def post_feed_louvor_aprovado(
    *,
    suggester_name: str,
    suggester_email: str,
    title: str,
    youtube_url: str,
    suggestion_id: str,
) -> None:
    nome = suggester_name.strip() or "Integrante"
    titulo_musica = title.strip()
    img_rel = generate_novo_louvor_banner(titulo_musica, FEED_IMAGES_DIR)
    yt = youtube_url.strip()
    body = (
        "**Tem louvor novo na área!!** 🎉\n\n"
        "Clique e confira a nova música do repertório do GDL.\n\n"
        f"🎵 **{titulo_musica}** — sugerida por {nome}.\n\n"
    )
    if yt.startswith("http"):
        body += f"[▶ Ouvir no YouTube]({yt})"
    append_feed_post(
        post_type="louvor_aprovado",
        title="Tem louvor novo na área!!",
        body=body,
        youtube_url=yt,
        ref_id=str(suggestion_id),
        author_email=suggester_email.strip().lower(),
        author_name=nome,
        image_url=img_rel,
    )


def feed_likes_count(post_id: str, likes_df: pd.DataFrame) -> int:
    if likes_df.empty:
        return 0
    return int((likes_df["post_id"].astype(str) == str(post_id)).sum())


def user_liked_post(post_id: str, email: str, likes_df: pd.DataFrame) -> bool:
    if likes_df.empty:
        return False
    email_l = email.strip().lower()
    mask = (likes_df["post_id"].astype(str) == str(post_id)) & (
        likes_df["email"].astype(str).str.strip().str.lower() == email_l
    )
    return bool(mask.any())


def toggle_feed_like(post_id: str, email: str, likes_df: pd.DataFrame) -> pd.DataFrame:
    likes_df = prepare_feed_likes(likes_df)
    email_l = email.strip().lower()
    mask = (likes_df["post_id"].astype(str) == str(post_id)) & (
        likes_df["email"].astype(str).str.strip().str.lower() == email_l
    )
    if mask.any():
        likes_df = likes_df[~mask]
    else:
        likes_df = pd.concat(
            [
                likes_df,
                pd.DataFrame(
                    [
                        {
                            "id": new_id(),
                            "post_id": str(post_id),
                            "email": email_l,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    save_data(likes_df, FEED_LIKES_FILE)
    return likes_df


def append_feed_comment(
    post_id: str,
    email: str,
    name: str,
    message: str,
    comments_df: pd.DataFrame,
) -> pd.DataFrame:
    comments_df = prepare_feed_comments(comments_df)
    row = {
        "id": new_id(),
        "post_id": str(post_id),
        "email": email.strip().lower(),
        "name": name.strip(),
        "message": message.strip(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    comments_df = pd.concat([comments_df, pd.DataFrame([row])], ignore_index=True)
    save_data(comments_df, FEED_COMMENTS_FILE)
    return comments_df


def playlist_for_user(playlist_df: pd.DataFrame, email: str) -> pd.DataFrame:
    if playlist_df.empty:
        return playlist_df
    return playlist_df[
        playlist_df["member_email"].astype(str).str.strip().str.lower()
        == email.strip().lower()
    ].copy()


def add_louvor_to_playlist(
    playlist_df: pd.DataFrame,
    louvor_data: dict,
    *,
    notes: str = "",
) -> pd.DataFrame:
    from catalog_sanitize import sanitize_catalog_text

    playlist_df = prepare_playlist(playlist_df)
    my_email = st.session_state.user_email.strip().lower()
    title = sanitize_catalog_text(louvor_data.get("title", ""))
    if not title:
        return playlist_df
    dup = playlist_df[
        (playlist_df["member_email"].astype(str).str.lower() == my_email)
        & (playlist_df["title"].astype(str).str.lower() == title.lower())
    ]
    if not dup.empty:
        return playlist_df
    artist = sanitize_catalog_text(louvor_data.get("artist", ""))
    yt = sanitize_catalog_text(louvor_data.get("youtube_url", ""))
    cifra = sanitize_catalog_text(louvor_data.get("cifra_url", ""))
    if cifra and not cifra.startswith("http"):
        cifra = ""
    if not cifra:
        cifra = cifra_search_url(title, artist)
    row = {
        "id": new_id(),
        "member_email": my_email,
        "title": title,
        "artist": artist,
        "key": sanitize_catalog_text(louvor_data.get("key", "")),
        "youtube_url": yt,
        "cifra_url": cifra,
        "ritmo": sanitize_catalog_text(louvor_data.get("ritmo", "")),
        "notes": notes.strip(),
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    playlist_df = pd.concat([playlist_df, pd.DataFrame([row])], ignore_index=True)
    save_data(playlist_df, PLAYLIST_FILE)
    return playlist_df


def user_on_escala_semana(
    escalas_df: pd.DataFrame, equipe_df: pd.DataFrame, email: str, start: date, end: date
) -> list[dict]:
    """Escalas da semana em que o usuário participa (ministrador ou equipe)."""
    email = email.strip().lower()
    semana = escalas_na_semana(escalas_df, start, end)
    found = []
    for _, row in semana.iterrows():
        escala_id = str(row.get("id", ""))
        principal_email = str(row.get("member_email", "")).strip().lower()
        if principal_email == email:
            found.append({"escala": row, "funcao": FUNCAO_MINISTRADOR})
            continue
        eq = equipe_por_escala(equipe_df, escala_id)
        for _, er in eq.iterrows():
            if str(er.get("member_email", "")).strip().lower() == email:
                found.append(
                    {
                        "escala": row,
                        "funcao": normalize_funcao_escala(str(er.get("funcao", "Integrante"))),
                    }
                )
                break
    return found


_DIAS_SEMANA_PT = ("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo")


def rehearsal_date_is_set(escala_row) -> bool:
    raw = str(escala_row.get("rehearsal_date", "")).strip()
    if not raw or raw.lower() in ("nan", "nat", "none"):
        return False
    return bool(pd.notna(pd.to_datetime(raw, errors="coerce")))


def format_rehearsal_date_pt(escala_row) -> str:
    raw = str(escala_row.get("rehearsal_date", "")).strip()
    rd = pd.to_datetime(raw, errors="coerce")
    if pd.isna(rd):
        return raw
    return f"{_DIAS_SEMANA_PT[rd.weekday()]}, {rd.strftime('%d/%m/%Y')}"


def ensaio_reminder_html(escala_row, *, is_manager: bool) -> str:
    """Lembrete de ensaio para integrantes escalados (data definida ou pendente)."""
    if rehearsal_date_is_set(escala_row):
        fmt = html.escape(format_rehearsal_date_pt(escala_row))
        return (
            '<p class="escala-ensaio ensaio-ok">'
            f"📅 <strong>Ensaio:</strong> {fmt}"
            "</p>"
        )
    if is_manager:
        texto = (
            "⚠️ <strong>Definir data do ensaio</strong> — "
            "cadastre a data em <em>Gerenciar Escalas</em> para avisar a equipe."
        )
    else:
        texto = (
            "⏳ <strong>Definir data do ensaio</strong> — "
            "aguardando confirmação do líder. Fique atento(a)!"
        )
    return f'<p class="escala-ensaio ensaio-pendente">{texto}</p>'


def ensaio_aviso_banner_html(escala_row, *, is_manager: bool) -> str:
    if rehearsal_date_is_set(escala_row):
        return ""
    ev = html.escape(str(escala_row.get("event", "Culto")))
    if is_manager:
        sub = "Abra <strong>Gerenciar Escalas</strong> e informe a data do ensaio para o grupo."
    else:
        sub = "O líder ainda vai confirmar. Assim que definir, a data aparecerá aqui e no painel."
    return (
        '<div class="ensaio-aviso-banner">'
        f'<p class="ensaio-aviso-titulo">⏳ Definir data do ensaio — {ev}</p>'
        f'<p class="ensaio-aviso-sub">{sub}</p>'
        "</div>"
    )


def trocas_abertas_pendentes(trocas_df: pd.DataFrame) -> pd.DataFrame:
    if trocas_df.empty:
        return trocas_df
    pend = trocas_df[trocas_df["status"].astype(str).str.lower() == "pendente"].copy()
    if "tipo" not in pend.columns:
        pend["tipo"] = ""
    tipo_l = pend["tipo"].astype(str).str.lower()
    target_empty = pend["target_email"].astype(str).str.strip() == ""
    return pend[(tipo_l == "aberta") | target_empty]


SWAP_ALERT_MENUS = frozenset({"Dashboard", "Escalas"})


def swap_alerts_for_user(
    trocas_df: pd.DataFrame,
    my_email: str,
    escalas_df: pd.DataFrame | None = None,
    equipe_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Abertas (assumir), recebidas (responder) e enviadas (aguardando) para o usuário."""
    my_email = my_email.strip().lower()
    if trocas_df.empty:
        return trocas_df, trocas_df, trocas_df
    pend = trocas_df[trocas_df["status"].astype(str).str.lower() == "pendente"].copy()
    abertas = trocas_abertas_pendentes(trocas_df)
    abertas = abertas[
        abertas["requester_email"].astype(str).str.strip().str.lower() != my_email
    ]
    rec = pend[pend["target_email"].astype(str).str.strip().str.lower() == my_email]
    env = pend[pend["requester_email"].astype(str).str.strip().str.lower() == my_email]

    if escalas_df is not None and not escalas_df.empty:
        eq = equipe_df if equipe_df is not None else pd.DataFrame()

        def _troca_visivel(row) -> bool:
            eid = str(row.get("escala_id_origem", ""))
            return not user_already_on_escala(escalas_df, eq, eid, my_email)

        if not abertas.empty:
            mask = abertas.apply(_troca_visivel, axis=1)
            abertas = abertas[mask]
        if not rec.empty:
            mask_r = rec.apply(_troca_visivel, axis=1)
            rec = rec[mask_r]

    return abertas, rec, env


def count_swap_alerts_for_user(
    trocas_df: pd.DataFrame,
    my_email: str,
    escalas_df: pd.DataFrame | None = None,
    equipe_df: pd.DataFrame | None = None,
) -> int:
    abertas, rec, _ = swap_alerts_for_user(
        trocas_df, my_email, escalas_df=escalas_df, equipe_df=equipe_df
    )
    return len(abertas) + len(rec)


def _escala_label_from_troca(trocas_row, escalas_df: pd.DataFrame) -> str:
    o = escalas_df[escalas_df["id"].astype(str) == str(trocas_row["escala_id_origem"])]
    return escala_label(o.iloc[0]) if not o.empty else "Escala"


def render_swap_alerts_panel(
    trocas_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    key_prefix: str = "swap",
):
    """Painel em destaque: trocas abertas, pedidos recebidos e solicitações enviadas."""
    my_email = st.session_state.user_email.strip().lower()
    name = st.session_state.user_full_name or st.session_state.user_name
    abertas, rec, env = swap_alerts_for_user(
        trocas_df, my_email, escalas_df=escalas_df, equipe_df=equipe_df
    )
    if abertas.empty and rec.empty and env.empty:
        return

    st.markdown(
        """
        <div class="swap-priority-panel">
            <p class="swap-priority-title">🔄 Solicitações de troca de escala</p>
            <p class="swap-priority-sub">Prioridade do ministério — responda ou assuma abaixo.
            Detalhes também em <strong>Escalas → Solicitações</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not rec.empty:
        st.markdown("**📥 Pedidos aguardando sua resposta**")
        for _, t in rec.iterrows():
            label = _escala_label_from_troca(t, escalas_df)
            st.markdown(
                f'<div class="swap-banner"><strong>{html.escape(str(t["requester_name"]))}</strong> '
                f"pediu que você assuma · <em>{html.escape(label)}</em></div>",
                unsafe_allow_html=True,
            )
            if t.get("message"):
                st.caption(str(t["message"]))
            c1, c2 = st.columns(2)
            with c1:
                if st.button(
                    "✅ Aceitar",
                    key=f"{key_prefix}_rec_ok_{t['id']}",
                    use_container_width=True,
                    type="primary",
                ):
                    escalas_df, equipe_df, trocas_df, ok = accept_open_swap(
                        t, my_email, name, escalas_df, equipe_df, trocas_df
                    )
                    if ok:
                        save_data(escalas_df, ESCALAS_FILE)
                        save_data(equipe_df, EQUIPE_FILE)
                        save_data(trocas_df, TROCAS_FILE)
                        st.success("Troca aceita! A escala já foi atualizada para todos.")
                        st.rerun()
                    else:
                        st.error(
                            "Você já está escalado neste culto — não é possível assumir esta troca."
                        )
            with c2:
                if st.button(
                    "❌ Recusar",
                    key=f"{key_prefix}_rec_no_{t['id']}",
                    use_container_width=True,
                ):
                    trocas_df = prepare_trocas(trocas_df)
                    trocas_df.loc[trocas_df["id"].astype(str) == str(t["id"]), "status"] = (
                        "recusada"
                    )
                    trocas_df.loc[
                        trocas_df["id"].astype(str) == str(t["id"]), "responded_at"
                    ] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_data(trocas_df, TROCAS_FILE)
                    st.rerun()

    if not abertas.empty:
        st.markdown("**📢 Disponíveis para qualquer integrante assumir**")
        for _, t in abertas.iterrows():
            label = _escala_label_from_troca(t, escalas_df)
            st.markdown(
                f'<div class="swap-banner"><strong>{html.escape(str(t["requester_name"]))}</strong> '
                f"divulgou troca · <em>{html.escape(label)}</em></div>",
                unsafe_allow_html=True,
            )
            if t.get("message"):
                st.caption(str(t["message"]))
            if st.button(
                "✅ Assumir esta troca",
                key=f"{key_prefix}_open_{t['id']}",
                use_container_width=True,
                type="primary",
            ):
                escalas_df, equipe_df, trocas_df, ok = accept_open_swap(
                    t, my_email, name, escalas_df, equipe_df, trocas_df
                )
                if ok:
                    save_data(escalas_df, ESCALAS_FILE)
                    save_data(equipe_df, EQUIPE_FILE)
                    save_data(trocas_df, TROCAS_FILE)
                    st.success("Troca realizada! A solicitação saiu do painel de todos.")
                    st.rerun()
                else:
                    st.error(
                        "Você já está escalado neste culto — não é possível assumir esta troca."
                    )

    if not env.empty:
        st.markdown("**📤 Suas solicitações aguardando**")
        for _, t in env.iterrows():
            label = _escala_label_from_troca(t, escalas_df)
            alvo = str(t.get("target_name") or "").strip() or "qualquer integrante do grupo"
            st.caption(f"Aguardando {alvo} · {label}")

    st.markdown("---")


def accept_open_swap(
    troca_row,
    accepter_email: str,
    accepter_name: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, bool]:
    """Aceita troca aberta ou assume vaga — atualiza escala e encerra pedidos relacionados."""
    trocas_df = prepare_trocas(trocas_df)
    escala_id = str(troca_row["escala_id_origem"])
    dest_id = str(troca_row.get("escala_id_destino", "")).strip()
    tipo = str(troca_row.get("tipo", "")).lower()

    req_email = str(troca_row.get("requester_email", "")).strip().lower()
    accepter_email = accepter_email.strip().lower()

    if accepter_email != req_email and user_already_on_escala(
        escalas_df, equipe_df, escala_id, accepter_email
    ):
        return escalas_df, equipe_df, trocas_df, False

    if dest_id and tipo in ("direta", "com_escala", ""):
        escalas_df = execute_swap(escalas_df, escala_id, dest_id)
        if req_email and not equipe_df.empty:
            equipe_df = equipe_df.copy()
            for eid in (escala_id, dest_id):
                mask_eq = (equipe_df["escala_id"].astype(str) == eid) & (
                    equipe_df["member_email"].astype(str).str.strip().str.lower() == req_email
                )
                if mask_eq.any():
                    equipe_df.loc[mask_eq, "member_email"] = accepter_email
                    equipe_df.loc[mask_eq, "member_name"] = accepter_name
    else:
        equipe_df = equipe_df.copy() if not equipe_df.empty else equipe_df
        swapped_in_equipe = False
        if req_email and not equipe_df.empty:
            mask_eq = (equipe_df["escala_id"].astype(str) == escala_id) & (
                equipe_df["member_email"].astype(str).str.strip().str.lower() == req_email
            )
            if mask_eq.any():
                equipe_df.loc[mask_eq, "member_email"] = accepter_email
                equipe_df.loc[mask_eq, "member_name"] = accepter_name
                swapped_in_equipe = True
        if not swapped_in_equipe:
            idx = escalas_df.index[escalas_df["id"].astype(str) == escala_id]
            if len(idx) and str(escalas_df.loc[idx[0], "member_email"]).strip().lower() == req_email:
                escalas_df.loc[idx[0], ["member_email", "member_name", "responsible"]] = [
                    accepter_email,
                    accepter_name,
                    accepter_name,
                ]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tid = str(troca_row["id"])
    trocas_df.loc[trocas_df["id"].astype(str) == tid, "status"] = "aceita"
    trocas_df.loc[trocas_df["id"].astype(str) == tid, "responded_at"] = now
    trocas_df.loc[trocas_df["id"].astype(str) == tid, "accepter_email"] = accepter_email
    trocas_df.loc[trocas_df["id"].astype(str) == tid, "accepter_name"] = accepter_name
    # Encerra outras solicitações pendentes para a mesma escala de origem
    pend_mask = (
        (trocas_df["escala_id_origem"].astype(str) == escala_id)
        & (trocas_df["status"].astype(str).str.lower() == "pendente")
        & (trocas_df["id"].astype(str) != tid)
    )
    trocas_df.loc[pend_mask, "status"] = "cancelada"
    trocas_df.loc[pend_mask, "responded_at"] = now
    return escalas_df, equipe_df, trocas_df, True


def enrich_programa_from_catalog(
    programa_df: pd.DataFrame, louvores_df: pd.DataFrame
) -> pd.DataFrame:
    """Preenche youtube/cifra do repertório quando ausentes na programação."""
    from catalog_sanitize import sanitize_catalog_text

    if programa_df.empty or louvores_df.empty:
        return programa_df
    df = programa_df.copy()
    titles = louvores_df["title"].astype(str).str.strip().str.lower()
    for idx, row in df.iterrows():
        titulo = str(row.get("louvor_title", "")).strip().lower()
        if not titulo:
            continue
        match = louvores_df[titles == titulo]
        if match.empty:
            match = louvores_df[titles.str.contains(re.escape(titulo[:20]), na=False, regex=True)]
        if match.empty:
            continue
        cat = match.iloc[0]
        if not str(row.get("youtube_url", "")).strip():
            df.at[idx, "youtube_url"] = sanitize_catalog_text(cat.get("youtube_url", ""))
        if not str(row.get("cifra_url", "")).strip():
            df.at[idx, "cifra_url"] = sanitize_catalog_text(cat.get("cifra_url", ""))
        if not sanitize_catalog_text(row.get("artist", "")):
            df.at[idx, "artist"] = sanitize_catalog_text(cat.get("artist", ""))
        if not sanitize_catalog_text(row.get("key", "")):
            df.at[idx, "key"] = sanitize_catalog_text(cat.get("key", ""))
    return df


def render_voice_kit_link(
    roles: str | None = None,
    bio: str = "",
    song_title: str = "",
) -> None:
    """Exibe link do YouTube para kit de voz (nipe + música, quando informada)."""
    from voice_kit_links import (
        vocal_nipe_from_roles,
        voice_kit_search_query,
        voice_kit_youtube_url,
    )

    roles = roles if roles is not None else str(st.session_state.get("user_roles", ""))
    nipe = vocal_nipe_from_roles(roles, bio=bio)
    if not nipe:
        return
    title = str(song_title).strip()
    label = voice_kit_search_query(nipe, title)
    url = voice_kit_youtube_url(nipe, title)
    hint = (
        f"Busca: {label}"
        if title
        else "Cadastre sua função vocal e use o kit em cada música do culto"
    )
    st.markdown(
        f'<div class="voice-kit-banner">'
        f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
        f"🎤 {html.escape(label)}</a>"
        f"<span>{html.escape(hint)}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def cifra_search_url(title: str, artist: str = "") -> str:
    from catalog_sanitize import sanitize_catalog_text

    q = f"{sanitize_catalog_text(title)} {sanitize_catalog_text(artist)}".strip()
    return f"https://www.cifraclub.com.br/?q={q.replace(' ', '+')}"


def youtube_search_url(title: str, artist: str = "") -> str:
    from catalog_sanitize import sanitize_catalog_text

    q = f"{sanitize_catalog_text(title)} {sanitize_catalog_text(artist)}".strip()
    return f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}"


def escala_label(row) -> str:
    date = str(row.get("date", ""))
    event = str(row.get("event", ""))
    name = str(row.get("member_name") or row.get("responsible", ""))
    return f"{date} · {event} · {name}"


def _format_escala_date(raw: str) -> str:
    try:
        return pd.to_datetime(raw, errors="coerce").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(raw)


def escala_label_for_user(
    row,
    email: str,
    equipe_df: pd.DataFrame,
) -> str:
    """Rótulo do culto para troca — mostra data, evento e função do usuário logado."""
    email = email.strip().lower()
    escala_id = str(row.get("id", ""))
    event = str(row.get("event", ""))
    date_fmt = _format_escala_date(str(row.get("date", "")))
    if str(row.get("member_email", "")).strip().lower() == email:
        func = FUNCAO_MINISTRADOR
    else:
        eq = equipe_por_escala(equipe_df, escala_id)
        match = eq[eq["member_email"].astype(str).str.strip().str.lower() == email]
        func = (
            normalize_funcao_escala(str(match.iloc[0].get("funcao", "Integrante")))
            if not match.empty
            else "Integrante"
        )
    return f"{date_fmt} · {event} · {func}"


def user_already_on_escala(
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    escala_id: str,
    email: str,
) -> bool:
    """True se o integrante já é ministrador principal ou está na equipe do culto."""
    email = str(email or "").strip().lower()
    escala_id = str(escala_id or "")
    if not email or not escala_id:
        return False
    idx = escalas_df.index[escalas_df["id"].astype(str) == escala_id]
    if len(idx):
        principal = str(escalas_df.loc[idx[0], "member_email"]).strip().lower()
        if principal == email:
            return True
    if equipe_df is not None and not equipe_df.empty:
        on_team = equipe_df[
            (equipe_df["escala_id"].astype(str) == escala_id)
            & (
                equipe_df["member_email"].astype(str).str.strip().str.lower()
                == email
            )
        ]
        if not on_team.empty:
            return True
    return False


def user_escalas(
    escalas_df: pd.DataFrame,
    email: str,
    equipe_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Cultos em que o usuário participa (ministrador principal ou equipe do culto)."""
    email = email.strip().lower()
    escala_ids: set[str] = set()

    principal_mask = escalas_df["member_email"].astype(str).str.strip().str.lower() == email
    escala_ids.update(escalas_df.loc[principal_mask, "id"].astype(str))

    if not escala_ids:
        try:
            name = st.session_state.user_name.strip().lower()
        except Exception:
            name = ""
        if name:
            resp_mask = escalas_df["responsible"].astype(str).str.lower().str.contains(
                name, na=False
            )
            escala_ids.update(escalas_df.loc[resp_mask, "id"].astype(str))

    if equipe_df is not None and not equipe_df.empty:
        eq_mask = equipe_df["member_email"].astype(str).str.strip().str.lower() == email
        escala_ids.update(equipe_df.loc[eq_mask, "escala_id"].astype(str))

    if not escala_ids:
        return escalas_df.iloc[0:0].copy()
    return escalas_df[escalas_df["id"].astype(str).isin(escala_ids)].copy()


def prepare_programa_sequencia(df: pd.DataFrame) -> pd.DataFrame:
    for column in PROGRAMA_SEQUENCIA_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[list(PROGRAMA_SEQUENCIA_COLUMNS)].copy()
    # Células vazias no CSV viram float64 (NaN) — impedem gravar texto na sequência
    for column in PROGRAMA_SEQUENCIA_COLUMNS:
        df[column] = df[column].fillna("").astype(str)
    capo_num = pd.to_numeric(df["capo"], errors="coerce").fillna(0).astype(int)
    df["capo"] = capo_num.astype(str)
    return df


def load_programa_sequencia_df() -> pd.DataFrame:
    return prepare_programa_sequencia(
        _load_csv_fresh(PROGRAMA_SEQUENCIA_FILE, PROGRAMA_SEQUENCIA_COLUMNS)
    )


def save_programa_sequencia_df(df: pd.DataFrame) -> None:
    save_data(prepare_programa_sequencia(df), PROGRAMA_SEQUENCIA_FILE)


def hydrate_escala_sequencia_content(
    escala_id: str,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    use_web: bool = True,
    save_catalog: bool = True,
) -> tuple[int, int]:
    """Repertório local e, se faltar, busca letra/cifra na web. Retorna (total, da_web)."""
    from louvor_content import hydrate_escala_sequencia_with_web

    save_louv = None
    if save_catalog and is_scale_manager(st.session_state.get("user_roles", [])):
        save_louv = lambda df: save_data(df, LOUVORES_FILE)

    return hydrate_escala_sequencia_with_web(
        escala_id,
        programa_df,
        louvores_df,
        load_seq=load_programa_sequencia_df,
        save_seq=save_programa_sequencia_df,
        save_louvores=save_louv,
        use_web=use_web,
    )


def prepare_programa(df: pd.DataFrame) -> pd.DataFrame:
    from catalog_sanitize import sanitize_catalog_text

    for column in PROGRAMA_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[list(PROGRAMA_COLUMNS)].copy()
    for col in ("louvor_title", "artist", "key", "youtube_url", "cifra_url", "leader_name", "notes", "parte"):
        if col in df.columns:
            df[col] = df[col].apply(sanitize_catalog_text)
    empty_ids = df["id"].astype(str).str.strip() == ""
    if empty_ids.any():
        df.loc[empty_ids, "id"] = [new_id() for _ in range(empty_ids.sum())]
    df["ordem"] = pd.to_numeric(df["ordem"], errors="coerce").fillna(0).astype(int)
    return df


def prepare_equipe(df: pd.DataFrame) -> pd.DataFrame:
    for column in EQUIPE_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[list(EQUIPE_COLUMNS)].copy()
    empty_ids = df["id"].astype(str).str.strip() == ""
    if empty_ids.any():
        df.loc[empty_ids, "id"] = [new_id() for _ in range(empty_ids.sum())]
    return df


def week_bounds(offset: int = 0) -> tuple[date, date]:
    today = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def escalas_na_semana(escalas_df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    if escalas_df.empty:
        return escalas_df
    df = escalas_df.copy()
    df["_d"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    mask = (df["_d"] >= start) & (df["_d"] <= end)
    return df[mask].sort_values("_d").drop(columns=["_d"])


def louvor_label_from_row(row) -> str:
    from catalog_sanitize import format_louvor_display

    title = str(row.get("title", "")).strip()
    if not title:
        return ""
    return format_louvor_display(title, str(row.get("artist", "")))


def louvores_catalog_options(louvores_df: pd.DataFrame) -> dict[str, dict]:
    options = {}
    for _, row in louvores_df.iterrows():
        label = louvor_label_from_row(row)
        if label:
            options[label] = row.to_dict()
    return options


def filter_louvores_for_picker(louvores_df: pd.DataFrame, query: str) -> pd.DataFrame:
    if louvores_df.empty:
        return louvores_df
    df = louvores_df.copy()
    titles = df["title"].astype(str).str.lower()
    artists = df["artist"].astype(str).str.lower()
    q = query.strip().lower()
    if not q:
        return df.sort_values("title")
    starts = titles.str.startswith(q) | artists.str.startswith(q)
    contains = titles.str.contains(q, na=False) | artists.str.contains(q, na=False)
    filtered = df[starts | contains].copy()
    filtered["_prio"] = starts.astype(int) * 2 + (titles.str.contains(q, na=False)).astype(int)
    return filtered.sort_values(["_prio", "title"], ascending=[False, True]).drop(
        columns=["_prio"], errors="ignore"
    )


def delete_escala_completa(
    escala_id: str,
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
):
    escalas_df = escalas_df[escalas_df["id"].astype(str) != str(escala_id)]
    programa_df = programa_df[programa_df["escala_id"].astype(str) != str(escala_id)]
    equipe_df = equipe_df[equipe_df["escala_id"].astype(str) != str(escala_id)]
    save_data(escalas_df, ESCALAS_FILE)
    save_data(programa_df, PROGRAMA_FILE)
    save_data(equipe_df, EQUIPE_FILE)


def escalas_ordenadas(escalas_df: pd.DataFrame) -> pd.DataFrame:
    if escalas_df.empty:
        return escalas_df
    df = escalas_df.copy()
    df["_d"] = pd.to_datetime(df["date"], errors="coerce")
    return df.sort_values("_d", ascending=False).drop(columns=["_d"])


def programa_por_escala(programa_df: pd.DataFrame, escala_id: str) -> pd.DataFrame:
    prog = programa_df[programa_df["escala_id"].astype(str) == str(escala_id)].copy()
    return prog.sort_values("ordem")


def equipe_por_escala(equipe_df: pd.DataFrame, escala_id: str) -> pd.DataFrame:
    return equipe_df[equipe_df["escala_id"].astype(str) == str(escala_id)].copy()


def integrantes_escalados(
    escala_row,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> list[dict]:
    escala_id = str(escala_row.get("id", ""))
    team = []

    def _nome_por_email(email: str, fallback: str = "") -> str:
        em = str(email or "").strip().lower()
        if em and not members_df.empty and "email" in members_df.columns:
            m = members_df[members_df["email"].astype(str).str.lower() == em]
            if not m.empty:
                return member_display_name(m.iloc[0])
        return str(fallback or "").strip()

    principal = {
        "nome": str(escala_row.get("member_name") or escala_row.get("responsible", "")),
        "funcao": FUNCAO_MINISTRADOR,
        "email": str(escala_row.get("member_email", "")),
    }
    if not principal["nome"]:
        principal["nome"] = _nome_por_email(principal["email"])
    if principal["nome"]:
        team.append(principal)

    for _, row in equipe_por_escala(equipe_df, escala_id).iterrows():
        nome = str(row.get("member_name", "")).strip()
        email = str(row.get("member_email", ""))
        if not nome:
            nome = _nome_por_email(email)
        if not nome:
            continue
        team.append(
            {
                "nome": nome,
                "funcao": normalize_funcao_escala(str(row.get("funcao", "Integrante"))),
                "email": email,
            }
        )

    return team


def execute_swap(escalas_df: pd.DataFrame, escala_a: str, escala_b: str) -> pd.DataFrame:
    escala_a, escala_b = str(escala_a), str(escala_b)
    idx_a = escalas_df.index[escalas_df["id"].astype(str) == escala_a]
    idx_b = escalas_df.index[escalas_df["id"].astype(str) == escala_b]
    if len(idx_a) == 0 or len(idx_b) == 0:
        return escalas_df

    fields = ["member_email", "member_name", "responsible"]
    temp = {field: escalas_df.loc[idx_a[0], field] for field in fields}
    for field in fields:
        escalas_df.loc[idx_a[0], field] = escalas_df.loc[idx_b[0], field]
        escalas_df.loc[idx_b[0], field] = temp[field]
    return escalas_df


def is_valid_email(email: str) -> bool:
    email = email.strip()
    return "@" in email and "." in email.split("@")[-1] and len(email) >= 5


# Contas técnicas (não aparecem em listas do ministério; só login de manutenção)
TECHNICAL_DEV_EMAILS = frozenset({"wsdataanalyst"})


def get_developer_emails() -> list[str]:
    """E-mails com acesso total de Desenvolvedor (menu Gerenciar Escalas, etc.)."""
    emails = ["wsdataanalyst", "willsousaa7x@gmail.com"]
    extra = os.environ.get("DEVELOPER_EMAILS", "")
    if extra.strip():
        emails.extend(e.strip() for e in extra.split(",") if e.strip())
    try:
        from_secrets = st.secrets.get("developer_emails", [])
        if isinstance(from_secrets, str):
            emails.append(from_secrets)
        elif isinstance(from_secrets, list):
            emails.extend(from_secrets)
    except (FileNotFoundError, KeyError, AttributeError):
        pass
    return list(dict.fromkeys(e.strip().lower() for e in emails if e and str(e).strip()))


def get_dev_default_password() -> str:
    pwd = os.environ.get("DEV_DEFAULT_PASSWORD", "").strip()
    if pwd:
        return pwd
    try:
        pwd = str(st.secrets.get("dev_default_password", "")).strip()
    except (FileNotFoundError, KeyError, AttributeError):
        pwd = ""
    return pwd or "IbbjDev2024"


def add_developer_role(roles_str: str) -> str:
    roles_str = str(roles_str).strip()
    if ROLE_DESENVOLVEDOR.lower() in roles_str.lower():
        return roles_str
    if roles_str:
        return f"{ROLE_DESENVOLVEDOR}, {roles_str}"
    return ROLE_DESENVOLVEDOR


def ensure_developer_access(members_df: pd.DataFrame) -> pd.DataFrame:
    """Garante conta técnica e papel Desenvolvedor — só adiciona/atualiza dev, nunca remove contas."""
    dev_emails = get_developer_emails()
    default_password = get_dev_default_password()
    password_hash = hash_password(default_password)
    updated = False

    if members_df.empty:
        members_df = pd.DataFrame(columns=list(MEMBER_COLUMNS))

    emails_series = members_df["email"].astype(str).str.strip().str.lower()

    for dev_email in dev_emails:
        if dev_email == "wsdataanalyst":
            if dev_email not in emails_series.values:
                default_member = {
                    "first_name": "Desenvolvedor",
                    "last_name": "Admin",
                    "email": dev_email,
                    "roles": ROLE_DESENVOLVEDOR,
                    "password_hash": password_hash,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "profile_photo": "",
                    "phone": "",
                    "bio": "",
                }
                members_df = pd.concat(
                    [members_df, pd.DataFrame([default_member])], ignore_index=True
                )
                emails_series = members_df["email"].astype(str).str.strip().str.lower()
                updated = True
            else:
                idx = members_df.index[emails_series == dev_email][0]
                new_roles = add_developer_role(members_df.at[idx, "roles"])
                if str(members_df.at[idx, "roles"]) != new_roles:
                    members_df.at[idx, "roles"] = new_roles
                    updated = True
                # Conta técnica: senha sempre igual à padrão configurada (IbbjDev2024)
                if str(members_df.at[idx, "password_hash"]).strip() != password_hash:
                    members_df.at[idx, "password_hash"] = password_hash
                    updated = True
            continue

        if "@" not in dev_email:
            continue

        match = members_df[emails_series == dev_email]
        if match.empty:
            continue
        idx = match.index[0]
        new_roles = add_developer_role(members_df.at[idx, "roles"])
        if str(members_df.at[idx, "roles"]) != new_roles:
            members_df.at[idx, "roles"] = new_roles
            updated = True

    if updated:
        save_data(members_df, MEMBERS_FILE, quiet=True)
    return members_df


def authenticate(email: str, password: str, users_df: pd.DataFrame):
    email = email.strip().lower()
    if not email or not password:
        return None
    hashed = hash_password(password)
    emails = users_df["email"].astype(str).str.strip().str.lower()
    match = users_df[(emails == email) & (users_df["password_hash"] == hashed)]
    if not match.empty:
        return match.iloc[0]
    return None


def register_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    roles,
    members_df: pd.DataFrame,
):
    email = email.strip().lower()
    if not is_valid_email(email):
        return None, "Informe um email válido."
    if len(password) < 6:
        return None, "A senha deve ter pelo menos 6 caracteres."
    if not members_df.empty and email in members_df["email"].values:
        return None, "Este email já está cadastrado."

    final_roles = build_roles_for_registration(first_name, roles)
    if not final_roles:
        return None, "Escolha pelo menos uma função musical ou use um nome reconhecido pelo sistema."

    new_member = {
        "first_name": first_name.strip().title(),
        "last_name": last_name.strip().title(),
        "email": email,
        "roles": ", ".join(final_roles),
        "password_hash": hash_password(password),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "profile_photo": "",
        "phone": "",
        "bio": "",
    }
    members_df = pd.concat([members_df, pd.DataFrame([new_member])], ignore_index=True)
    save_data(members_df, MEMBERS_FILE)
    return new_member, None


def set_user_session(
    user_row,
    *,
    remember_me: bool = False,
    device_token: str | None = None,
):
    st.session_state.authenticated = True
    st.session_state.user_name = user_row["first_name"]
    st.session_state.user_full_name = member_display_name(user_row)
    st.session_state.user_email = user_row["email"]
    st.session_state.user_roles = user_row["roles"]
    st.session_state.user_primary_role = parse_primary_role(user_row["roles"])
    st.session_state.user_profile_photo = str(user_row.get("profile_photo", ""))
    st.session_state.remember_login = bool(remember_me)
    if device_token:
        st.session_state.device_session_token = str(device_token).strip()
    session_touch(st.session_state)


def issue_device_session_token(email: str) -> str:
    from device_session import create_device_session_token

    return create_device_session_token(email, DATA_DIR)


def inject_device_auth_token(token: str) -> None:
    """Guarda token no navegador para restaurar login após reload (ex.: voltar do YouTube)."""
    from device_session import AUTH_TOKEN_LS_KEY

    safe = str(token).replace("\\", "\\\\").replace("'", "\\'")
    inject_page_html(
        f"""
        <script>
        (function () {{
          try {{
            localStorage.setItem("{AUTH_TOKEN_LS_KEY}", "{safe}");
          }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
    )


def inject_device_auth_clear() -> None:
    from device_session import AUTH_TOKEN_LS_KEY

    inject_page_html(
        f"""
        <script>
        (function () {{
          try {{
            localStorage.removeItem("{AUTH_TOKEN_LS_KEY}");
          }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
    )


def inject_device_auth_restore_redirect() -> None:
    """Se há token salvo, recarrega a URL com ?ibbj_auth= para o servidor restaurar a sessão."""
    from device_session import AUTH_TOKEN_LS_KEY, AUTH_TOKEN_QUERY_PARAM

    inject_page_html(
        f"""
        <script>
        (function () {{
          try {{
            var w = window.parent;
            var u = new URL(w.location.href);
            if (u.searchParams.get("{AUTH_TOKEN_QUERY_PARAM}")) return;
            var t = localStorage.getItem("{AUTH_TOKEN_LS_KEY}");
            if (!t || t.length < 24) return;
            u.searchParams.set("{AUTH_TOKEN_QUERY_PARAM}", t);
            w.location.replace(u.toString());
          }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
    )


def try_restore_device_session(members_df: pd.DataFrame) -> bool:
    """Restaura login a partir do token na URL (após voltar ao app / nova sessão Streamlit)."""
    if st.session_state.get("authenticated"):
        return False
    from device_session import AUTH_TOKEN_QUERY_PARAM, validate_device_session_token

    token = str(st.query_params.get(AUTH_TOKEN_QUERY_PARAM, "")).strip()
    if not token:
        return False
    email = validate_device_session_token(token, DATA_DIR)
    if not email:
        return False
    match = members_df[members_df["email"].astype(str).str.strip().str.lower() == email]
    if match.empty:
        return False
    user = match.iloc[0]
    set_user_session(user, remember_me=True, device_token=token)
    try:
        qp = dict(st.query_params)
        qp.pop(AUTH_TOKEN_QUERY_PARAM, None)
        st.query_params.from_dict(qp)
    except Exception:
        pass
    return True


def logout_user() -> None:
    token = str(st.session_state.get("device_session_token", "")).strip()
    if token:
        from device_session import revoke_device_session_token

        revoke_device_session_token(token, DATA_DIR)
    session_logout(st.session_state)
    inject_device_auth_clear()
    inject_login_remember(False)


def member_avatar_for_chat(email: str, members_df: pd.DataFrame) -> str | None:
    email_l = email.strip().lower()
    stored = ""
    if not members_df.empty and "email" in members_df.columns:
        match = members_df[members_df["email"].astype(str).str.lower() == email_l]
        if not match.empty:
            stored = str(match.iloc[0].get("profile_photo", ""))
    path = profile_photo_file(email_l, stored)
    return str(path) if path else None


def update_chat_latest_ts(chat_df: pd.DataFrame) -> None:
    if chat_df.empty:
        st.session_state["_chat_latest_ts"] = ""
        return
    st.session_state["_chat_latest_ts"] = str(chat_df["timestamp"].max())


def chat_has_new_messages() -> bool:
    return count_unread_chat_messages() > 0


def count_unread_chat_messages(chat_df: pd.DataFrame | None = None) -> int:
    """Mensagens de outros integrantes após o último acesso ao chat."""
    if st.session_state.get("app_menu") == "Chat":
        return 0
    if chat_df is None:
        chat_df = st.session_state.get("_chat_df_cache")
    if chat_df is None or chat_df.empty:
        return 0
    my_email = st.session_state.user_email.strip().lower()
    others = chat_df[
        chat_df["email"].astype(str).str.strip().str.lower() != my_email
    ].copy()
    if others.empty:
        return 0
    seen = str(st.session_state.get("chat_seen_at", "")).strip()
    if not seen:
        return len(others)
    seen_ts = parse_timestamp(seen)
    if not seen_ts:
        return len(others)
    ts = to_local_timestamps(others["timestamp"])
    seen_cmp = to_local_timestamps(seen_ts).iloc[0]
    return int((ts > seen_cmp).sum())


def mark_chat_seen(chat_df: pd.DataFrame) -> None:
    if chat_df.empty:
        st.session_state.chat_seen_at = timestamp_now()
    else:
        st.session_state.chat_seen_at = str(chat_df["timestamp"].max())
    st.session_state.chat_unread_count = 0
    st.session_state._chat_unread_prev = 0
    st.session_state.pop("_chat_has_new", None)


def mark_chat_scroll_bottom() -> None:
    st.session_state["_chat_scroll_bottom"] = True


def inject_chat_unread_badges(unread: int) -> None:
    """Badge flutuante no item Chat da sidebar e nos atalhos do dashboard."""
    unread = max(0, int(unread))
    label = "99+" if unread > 99 else str(unread)
    show = "flex" if unread > 0 else "none"
    inject_page_html(
        f"""
        <style>
        section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
            position: relative !important;
        }}
        .chat-unread-badge {{
            position: absolute;
            top: 0.15rem;
            right: 0.35rem;
            min-width: 1.15rem;
            height: 1.15rem;
            padding: 0 0.3rem;
            border-radius: 999px;
            background: #ef4444;
            color: #fff !important;
            font-size: 0.65rem;
            font-weight: 700;
            display: {show};
            align-items: center;
            justify-content: center;
            line-height: 1;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.55);
            z-index: 6;
            pointer-events: none;
        }}
        .quick-nav-btn--chat {{
            position: relative;
        }}
        .quick-nav-btn--chat .chat-unread-badge {{
            top: 0.4rem;
            right: 0.55rem;
        }}
        </style>
        <script>
        (function () {{
          var count = {unread};
          var label = {label!r};
          var display = count > 0 ? "flex" : "none";
          var doc = window.parent.document;
          function attach() {{
            var sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (sidebar) {{
              sidebar.querySelectorAll('[data-testid="stRadio"] label').forEach(function (el) {{
                var t = (el.innerText || "");
                if (t.indexOf("Chat") >= 0 && t.toLowerCase().indexOf("ensaio") < 0) {{
                  var b = el.querySelector(".chat-unread-badge");
                  if (!b) {{
                    b = doc.createElement("span");
                    b.className = "chat-unread-badge";
                    el.appendChild(b);
                  }}
                  b.textContent = label;
                  b.style.display = display;
                }}
              }});
            }}
            doc.querySelectorAll(".quick-nav-btn--chat").forEach(function (wrap) {{
              var b = wrap.querySelector(".chat-unread-badge");
              if (!b) {{
                b = doc.createElement("span");
                b.className = "chat-unread-badge";
                wrap.appendChild(b);
              }}
              b.textContent = label;
              b.style.display = display;
            }});
          }}
          attach();
          setTimeout(attach, 350);
          setTimeout(attach, 1100);
        }})();
        </script>
        """,
        height=0,
    )


def inject_swap_alerts_badges(count: int) -> None:
    """Badge na sidebar no item Escalas quando há trocas pendentes para o usuário."""
    count = max(0, int(count))
    label = "99+" if count > 99 else str(count)
    show = "flex" if count > 0 else "none"
    inject_page_html(
        f"""
        <style>
        section[data-testid="stSidebar"] [data-testid="stRadio"] label {{
            position: relative !important;
        }}
        </style>
        <script>
        (function () {{
          var count = {count};
          var label = {label!r};
          var display = count > 0 ? "flex" : "none";
          var doc = window.parent.document;
          function attach() {{
            var sidebar = doc.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return;
            sidebar.querySelectorAll('[data-testid="stRadio"] label').forEach(function (el) {{
              var t = (el.innerText || "");
              if (t.indexOf("Escalas") >= 0 && t.indexOf("Gerenciar") < 0) {{
                var b = el.querySelector(".swap-unread-badge");
                if (!b) {{
                  b = doc.createElement("span");
                  b.className = "swap-unread-badge";
                  el.appendChild(b);
                }}
                b.textContent = label;
                b.style.display = display;
              }}
            }});
          }}
          attach();
          setTimeout(attach, 350);
          setTimeout(attach, 1100);
        }})();
        </script>
        """,
        height=0,
    )


def inject_chat_scroll_to_bottom():
    inject_page_html(
        """
        <script>
        (function () {
          var doc = window.parent.document;
          function scrollChat() {
            var box = doc.getElementById("chat-scroll-box");
            if (box) {
              box.scrollTop = box.scrollHeight + 9999;
            }
            var end = doc.getElementById("chat-scroll-end");
            if (end) end.scrollIntoView({ block: "end", inline: "nearest" });
            var anchor = doc.getElementById("chat-page-end");
            if (anchor) anchor.scrollIntoView({ block: "end" });
          }
          function watchBox() {
            var box = doc.getElementById("chat-scroll-box");
            if (!box || box.dataset.waObs) return;
            box.dataset.waObs = "1";
            new MutationObserver(scrollChat).observe(box, {
              childList: true,
              subtree: true,
              attributes: true,
            });
          }
          scrollChat();
          watchBox();
          [80, 200, 450, 900, 1500, 2500].forEach(function (ms) {
            setTimeout(function () {
              scrollChat();
              watchBox();
            }, ms);
          });
        })();
        </script>
        """,
        height=0,
    )


def inject_login_remember(save: bool, email: str = "", password: str = ""):
    em = email.replace("\\", "\\\\").replace("'", "\\'")
    pw = password.replace("\\", "\\\\").replace("'", "\\'")
    flag = "1" if save else "0"
    inject_page_html(
        f"""
        <script>
        (function () {{
          var KE = "{REMEMBER_EMAIL_KEY}";
          var KP = "ibbj_remember_password";
          var KR = "ibbj_remember_enabled";
          if ("{flag}" === "1") {{
            localStorage.setItem(KR, "1");
            localStorage.setItem(KE, "{em}");
            localStorage.setItem(KP, "{pw}");
          }} else {{
            localStorage.removeItem(KR);
            localStorage.removeItem(KE);
            localStorage.removeItem(KP);
          }}
        }})();
        </script>
        """,
        height=0,
    )


def inject_login_restore_fields():
    inject_page_html(
        f"""
        <script>
        (function () {{
          var KE = "{REMEMBER_EMAIL_KEY}";
          var KP = "ibbj_remember_password";
          var KR = "ibbj_remember_enabled";
          if (localStorage.getItem(KR) !== "1") return;
          var email = localStorage.getItem(KE) || "";
          var pwd = localStorage.getItem(KP) || "";
          function fill() {{
            var doc = window.parent.document;
            var inputs = doc.querySelectorAll('[data-testid="stTextInput"] input');
            if (inputs.length >= 2) {{
              if (email && !inputs[0].value) {{
                inputs[0].value = email;
                inputs[0].dispatchEvent(new Event("input", {{ bubbles: true }}));
              }}
              if (pwd && !inputs[1].value) {{
                inputs[1].value = pwd;
                inputs[1].dispatchEvent(new Event("input", {{ bubbles: true }}));
              }}
            }}
          }}
          setTimeout(fill, 400);
          setTimeout(fill, 900);
        }})();
        </script>
        """,
        height=0,
    )


def inject_auto_login_submit():
    """Com «Lembrar login», envia o formulário após preencher (volta ao app sem clicar Entrar)."""
    inject_page_html(
        """
        <script>
        (function () {
          if (localStorage.getItem("ibbj_remember_enabled") !== "1") return;
          function trySubmit() {
            var doc = window.parent.document;
            var form = doc.querySelector('form[data-testid="stForm"]');
            if (!form) return;
            var btn = form.querySelector('button[kind="primaryFormSubmit"]')
              || form.querySelector('button[type="submit"]');
            if (btn && !btn.disabled) btn.click();
          }
          setTimeout(trySubmit, 1100);
          setTimeout(trySubmit, 2200);
        })();
        </script>
        """,
        height=0,
    )


def inject_app_resume_listener():
    """Ao voltar ao app (aba visível), atualiza dados e preserva login via token no dispositivo."""
    from device_session import AUTH_TOKEN_LS_KEY, AUTH_TOKEN_QUERY_PARAM

    inject_hidden_sidebar_script(
        f"""
        <script>
        (function () {{
          var last = 0;
          var KL = "{AUTH_TOKEN_LS_KEY}";
          var KP = "{AUTH_TOKEN_QUERY_PARAM}";
          document.addEventListener("visibilitychange", function () {{
            if (document.visibilityState !== "visible") return;
            var now = Date.now();
            if (now - last < 8000) return;
            last = now;
            try {{
              var w = window.parent;
              var u = new URL(w.location.href);
              u.searchParams.set("ibbj_resume", String(now));
              var t = localStorage.getItem(KL);
              if (t && t.length >= 24) {{
                u.searchParams.set(KP, t);
              }}
              w.location.replace(u.toString());
            }} catch (e) {{}}
          }});
        }})();
        </script>
        """
    )


def handle_app_resume_query_params() -> bool:
    """Recarrega caches quando o usuário retorna ao app. Retorna True se houve resume."""
    resume = str(st.query_params.get("ibbj_resume", "")).strip()
    if not resume:
        return False
    try:
        qp = dict(st.query_params)
        qp.pop("ibbj_resume", None)
        st.query_params.from_dict(qp)
    except Exception:
        pass
    load_data.clear()
    st.session_state.pop("_escalas_bundle", None)
    st.session_state.pop("_feed_rev", None)
    st.session_state.pop("_chat_df_cache", None)
    try:
        refresh_escalas_bundle()
    except Exception:
        pass
    session_touch(st.session_state)
    return True


def catalog_link_label(url: str) -> str:
    u = str(url).strip().lower()
    if not u.startswith("http"):
        return "—"
    if "search_query=" in u or "/?q=" in u:
        return "🔍"
    if "cifra" in u:
        return "🎸"
    if "youtube" in u or "youtu.be" in u:
        return "▶"
    return "🔗"


def ensure_media_dirs():
    CHAT_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    CHAT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    FEED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    ENSAIO_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def ensure_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_name = ""
        st.session_state.user_full_name = ""
        st.session_state.user_email = ""
        st.session_state.user_roles = ""
        st.session_state.user_primary_role = "membro"
        st.session_state.user_profile_photo = ""


def apply_music_theme():
    from app_theme import inject_ibbj_theme

    inject_ibbj_theme()


def inject_page_html(html_fragment: str, height: int = 0):
    """Injeta HTML/JS sem iframes vazios que deslocam o layout no desktop."""
    body = html_fragment.strip()
    if not body:
        return

    if height <= 0:
        try:
            st.html(body, unsafe_allow_javascript=True)
            return
        except Exception:
            pass
        import streamlit.components.v1 as components

        wrapped = (
            '<div style="position:fixed;left:0;top:0;width:1px;height:1px;'
            'overflow:hidden;opacity:0;pointer-events:none;z-index:-1;">'
            f"{body}</div>"
        )
        components.html(wrapped, height=1, scrolling=False)
        return

    import streamlit.components.v1 as components

    components.html(body, height=height, scrolling=False)


def inject_mobile_app_shell():
    """PWA (instalar pelo link) + service worker + OneSignal (se configurado)."""
    st.markdown(
        """
        <link rel="manifest" href="/manifest.webmanifest">
        <meta name="theme-color" content="#121212">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Louvor IBBJ">
        <link rel="apple-touch-icon" href="/icon-192.png">
        """,
        unsafe_allow_html=True,
    )
    inject_hidden_sidebar_script(
        """
        <script>
        if ("serviceWorker" in navigator) {
          navigator.serviceWorker.register("/sw.js").catch(function () {});
        }
        </script>
        """
    )
    app_id = onesignal_app_id()
    if push_is_enabled() and app_id:
        inject_hidden_sidebar_script(
            f"""
            <script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>
            <script>
            window.OneSignalDeferred = window.OneSignalDeferred || [];
            OneSignalDeferred.push(async function (OneSignal) {{
              await OneSignal.init({{
                appId: "{app_id}",
                allowLocalhostAsSecureOrigin: true,
                serviceWorkerPath: "/sw.js",
                serviceWorkerParam: {{ scope: "/" }},
              }});
            }});
            </script>
            """
        )


def render_mobile_and_push_panel(
    *,
    expander_title: str = "App no celular e notificações",
    expander_key: str = "ig_tool_mobile",
):
    """Instalação no celular + ativar notificações."""
    with st.sidebar.expander(expander_title, expanded=False, key=expander_key):
        st.markdown(
            """
            **Android:** abra no Chrome → menu **Instalar app** (ou use um **APK** gerado em
            [PWABuilder](https://www.pwabuilder.com) com a URL do site.

            **iPhone:** abra no **Safari** → Compartilhar → **Adicionar à Tela de Início**
            (não existe APK no iOS).

            **Notificações** (chat e novas escalas): toque no botão abaixo e permita no navegador.
            No iPhone, abra pelo ícone na tela inicial (iOS 16.4+).
            """
        )
        if push_is_enabled():
            if st.button(
                "🔔 Ativar notificações",
                key="btn_enable_push",
                use_container_width=True,
            ):
                st.session_state["_onesignal_request"] = True
            if st.session_state.pop("_onesignal_request", False):
                inject_page_html(
                    """
                    <script>
                    (function () {
                      function ask() {
                        if (typeof OneSignal === "undefined") return;
                        OneSignal.Notifications.requestPermission();
                      }
                      if (window.OneSignalDeferred) {
                        OneSignalDeferred.push(ask);
                      } else {
                        setTimeout(ask, 1500);
                      }
                    })();
                    </script>
                    """,
                    height=0,
                )
                st.info("Se aparecer um pedido do navegador, toque em **Permitir**.")
        else:
            st.caption(
                "Notificações push ainda não configuradas no servidor. "
                "Execute `python setup_onesignal.py` ou veja **CONFIGURAR_ONESIGNAL.md**."
            )


def is_current_developer() -> bool:
    from user_feedback import is_dev_viewer

    return is_dev_viewer()


def render_push_admin_sidebar(members_df: pd.DataFrame | None = None):
    """Painel do desenvolvedor: push e redefinição de senhas."""
    if not is_current_developer():
        return

    if members_df is not None:
        with st.sidebar.expander("Redefinir senhas (dev)", expanded=False, key="ig_tool_lock"):
            render_password_reset_panel(members_df, form_key_prefix="dev_sidebar")

    with st.sidebar.expander("Configurar push (admin)", expanded=False, key="ig_tool_bell"):
        status = push_config_status()
        if status["enabled"]:
            st.success("Push ativo no servidor")
            st.caption(f"App ID: `{status['app_id'][:8]}…`")
            if status["public_url"]:
                st.caption(f"URL: {status['public_url']}")
            if not status["https_ok"]:
                st.warning("Use HTTPS em `public_url` para celular.")
        else:
            st.error("Push não configurado")
            st.caption("Rode: `python setup_onesignal.py`")

        if st.button("📤 Enviar notificação de teste", use_container_width=True):
            ok, msg = send_test_notification()
            if ok:
                st.success("Enviado! Quem já ativou notificações deve receber.")
            else:
                st.error("Falha ao enviar")
                st.code(msg[:500] if msg else "Erro desconhecido")

        st.caption("OneSignal → Site URL = mesma URL do app (HTTPS).")

    render_data_backup_sidebar()


def render_data_backup_sidebar():
    """Download / upload ZIP dos CSVs — evita perder cadastros ao mudar app no Streamlit."""
    if not is_current_developer():
        return

    from data_backup_io import build_data_backup_zip, restore_data_from_zip

    from remote_store import (
        is_remote_enabled,
        remote_config_hint,
        remote_status_message,
        sync_all_local_to_remote,
        test_remote_connection,
    )

    with st.sidebar.expander("Dados na nuvem / backup", expanded=False, key="ig_tool_cloud"):
        status = remote_status_message()
        if "desconectado" in status.lower() or "desativada" in status.lower():
            st.warning(status)
        else:
            st.success(status)

        if st.button(
            "🔌 Testar conexão Supabase",
            use_container_width=True,
            key="test_supabase_connection",
        ):
            ok, detail = test_remote_connection()
            if ok:
                st.success(detail)
            else:
                st.error(detail)

        if is_remote_enabled():
            if st.button(
                "☁️ Enviar tudo para a nuvem agora",
                use_container_width=True,
                key="sync_all_to_remote",
            ):
                n = sync_all_local_to_remote(DATA_DIR)
                load_data.clear()
                st.success(f"{n} arquivo(s) enviado(s) ao Supabase.")
                st.rerun()
        else:
            hint = remote_config_hint()
            if hint:
                st.caption(hint)
            with st.expander("Exemplo de Secrets (copiar)"):
                st.code(
                    '[persistence]\n'
                    "enabled = true\n"
                    'supabase_url = "https://SEU-ID.supabase.co"\n'
                    'supabase_key = "eyJ... service_role ..."',
                    language="toml",
                )
            st.caption("Guia completo: **CONFIGURAR_SUPABASE.md**.")
        st.caption("Backup ZIP (opcional, emergência):")
        stamp = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            "⬇️ Baixar backup (ZIP)",
            data=build_data_backup_zip(DATA_DIR),
            file_name=f"ibbj_backup_{stamp}.zip",
            mime="application/zip",
            use_container_width=True,
            key="download_data_backup_zip",
        )
        uploaded = st.file_uploader(
            "Arquivo ZIP de backup",
            type=["zip"],
            key="upload_data_backup_zip",
        )
        if uploaded is not None and st.button(
            "⚠️ Restaurar este ZIP",
            type="primary",
            use_container_width=True,
            key="confirm_restore_data_zip",
        ):
            count, notes = restore_data_from_zip(DATA_DIR, uploaded.getvalue())
            load_data.clear()
            if count:
                st.success(f"Restaurados {count} arquivo(s). A página vai recarregar.")
                if notes:
                    st.caption("Alguns itens ignorados: " + "; ".join(notes[:5]))
                st.rerun()
            else:
                show_form_error(
                    "Nenhum CSV encontrado no ZIP. Use um backup gerado por este app."
                )


def render_data_loss_warning(members_df: pd.DataFrame):
    """Avisa líder/dev quando o servidor parece sem cadastros (ex.: app Streamlit novo)."""
    roles = str(st.session_state.get("user_roles", ""))
    if not is_current_developer() and not is_scale_manager(roles):
        return
    if len(members_visible_to_group(members_df)) > 1:
        return
    from remote_store import is_remote_enabled

    if is_remote_enabled():
        hint = (
            "A nuvem está ativa, mas quase não há contas aqui. "
            "Restaure o ZIP do app antigo (menu **Dados na nuvem / backup**) "
            "ou confira o Supabase."
        )
    else:
        hint = (
            "Configure **Supabase** (`CONFIGURAR_SUPABASE.md`) para não perder cadastros "
            "ao atualizar o app, ou restaure um ZIP do backup."
        )
    st.warning(f"**Poucos integrantes neste servidor.** {hint}")


def nav_sidebar_button_key(menu_name: str) -> str:
    slug_map = {
        "Dashboard": "dashboard",
        "Feed": "feed",
        "Escalas": "escalas",
        "Gerenciar Escalas": "gerenciar_escalas",
        "Repertório": "repertorio",
        "Playlist": "playlist",
        "Sugestão de louvor": "sugestao_louvor",
        "Chat": "chat",
        "Eventos": "eventos",
        "Membros": "membros",
        "Perfil": "perfil",
        "Avisos": "avisos",
    }
    slug = slug_map.get(menu_name) or re.sub(r"[^a-z0-9]+", "_", menu_name.lower()).strip("_")
    return f"ig_nav_{slug or 'item'}"


def format_sidebar_role_display(roles: str) -> tuple[str, str]:
    """Linha principal de funções + badge secundário (card do usuário na sidebar)."""
    parts = [p.strip() for p in str(roles).split(",") if p.strip()]
    if not parts:
        return "Membro", ""
    vocal = [p for p in parts if "vocal" in p.lower()]
    leadership = [p for p in parts if p in LEADERSHIP_ROLES]
    music = [
        p
        for p in parts
        if p not in vocal and p not in leadership and p not in LEADERSHIP_ROLES
    ]
    if vocal:
        main = " · ".join(vocal[:2])
    elif leadership:
        main = leadership[0]
    else:
        main = parts[0]
    badge = ""
    for pool in (music, parts):
        for p in pool:
            if p != main and p not in main:
                badge = p
                break
        if badge:
            break
    return main, badge


def render_sidebar_profile(members_df: pd.DataFrame | None = None):
    from sidebar_brand import sidebar_brand_header_html
    from sidebar_icons import sidebar_user_placeholder_svg

    from ui_html import html_block, inject_ui_html

    cross_img = _login_cross_img_html()
    inject_ui_html(
        sidebar_brand_header_html(cross_img, title=LOGIN_DISPLAY_TITLE),
        sidebar=True,
    )

    email = str(st.session_state.get("user_email", "")).strip().lower()
    stored_photo = str(st.session_state.get("user_profile_photo", "")).strip()
    if members_df is not None and not members_df.empty and email:
        match = members_df[members_df["email"].astype(str).str.lower() == email]
        if not match.empty:
            stored_photo = str(match.iloc[0].get("profile_photo", "")).strip() or stored_photo

    display_name = (
        str(st.session_state.get("user_full_name", "")).strip()
        or str(st.session_state.get("user_name", "")).strip()
        or "Integrante"
    )
    photo_uri = profile_photo_to_data_uri(email, stored_photo) if email else None
    if photo_uri:
        avatar_inner = f'<img src="{photo_uri}" alt="" />'
    else:
        ph_uri = sidebar_user_placeholder_svg()
        avatar_inner = (
            f'<span class="ig-sb-avatar-ph" style="background:center/72% no-repeat '
            f'url({ph_uri})" aria-hidden="true"></span>'
        )

    roles = str(st.session_state.get("user_roles", "")).strip()
    role_main, role_badge = format_sidebar_role_display(roles)
    badge_html = (
        f'<span class="ig-sb-role-badge">{html.escape(role_badge)}</span>'
        if role_badge
        else ""
    )
    inject_ui_html(
        html_block(
            f"""
            <div class="ig-sb-profile-card">
                <div class="ig-sb-avatar-wrap">
                    <div class="ig-sb-avatar-glow" aria-hidden="true"></div>
                    <div class="ig-sb-avatar-ring" aria-hidden="true"></div>
                    <div class="ig-sb-avatar">{avatar_inner}</div>
                </div>
                <div class="ig-sb-profile-text">
                    <div class="ig-sb-user-name">{html.escape(display_name)}</div>
                    <div class="ig-sb-user-role">{html.escape(role_main)}</div>
                    {badge_html}
                </div>
            </div>
            """
        ),
        sidebar=True,
    )


def render_sidebar_navigation() -> str:
    """Menu lateral por seções (botões) — compatível com badges e atalhos do Dashboard."""
    groups = build_nav_groups_for_user(st.session_state.user_roles)
    flat: list[tuple[str, str, str]] = []
    for _, section in groups:
        flat.extend(section)
    names = [name for name, _, _ in flat]

    nav_names = list(names)
    if "Feed" in nav_names:
        nav_names.append("Avisos")
    if "app_menu" not in st.session_state or st.session_state.app_menu not in nav_names:
        st.session_state.app_menu = (
            "Dashboard" if "Dashboard" in names else ("Feed" if "Feed" in names else (names[0] if names else "Dashboard"))
        )

    current = str(st.session_state.app_menu)
    st.sidebar.markdown('<nav class="ig-sb-nav" aria-label="Menu principal">', unsafe_allow_html=True)
    for group_label, section in groups:
        st.sidebar.markdown(
            f'<p class="ig-sb-nav-group">{html.escape(group_label.upper())}</p>',
            unsafe_allow_html=True,
        )
        for name, _icon, _desc in section:
            is_active = name == current or (name == "Avisos" and current == "Feed")
            if st.sidebar.button(
                name,
                key=nav_sidebar_button_key(name),
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                if not is_active:
                    st.session_state.app_menu = "Feed" if name == "Avisos" else name
                    st.rerun()
    st.sidebar.markdown("</nav>", unsafe_allow_html=True)
    return current


def render_dashboard_quick_actions(roles: str):
    """Atalhos visuais na home para as telas mais usadas."""
    icons = menu_icons_map(roles)
    items, _, _ = get_menu_items_for_user(roles)
    available_names = {name for name, _, _ in items}
    links = [n for n in DASHBOARD_QUICK_LINKS if n in available_names and n != "Dashboard"]
    if not links:
        return

    render_dashboard_section_start("Acesso rápido", "⚡", "#f59e0b")
    cols = st.columns(min(len(links), 4))
    for col, name in zip(cols, links[:4]):
        with col:
            nav_cls = quick_nav_css_class(name)
            st.markdown(f'<div class="quick-nav-btn {nav_cls}">', unsafe_allow_html=True)
            if st.button(
                f"{icons.get(name, '🎵')}\n{name}",
                key=f"quick_nav_{name}",
                use_container_width=True,
            ):
                st.session_state.app_menu = name
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if len(links) > 4:
        cols2 = st.columns(min(len(links) - 4, 4))
        for col, name in zip(cols2, links[4:8]):
            with col:
                nav_cls = quick_nav_css_class(name)
                st.markdown(f'<div class="quick-nav-btn {nav_cls}">', unsafe_allow_html=True)
                if st.button(
                    f"{icons.get(name, '🎵')}\n{name}",
                    key=f"quick_nav2_{name}",
                    use_container_width=True,
                ):
                    st.session_state.app_menu = name
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
    render_dashboard_section_end()


def render_sidebar_tools_panel(members_df: pd.DataFrame | None = None):
    """Ferramentas (dev/admin) + app no celular — card inferior da sidebar."""
    dev = is_current_developer()
    from ui_html import inject_ui_html

    inject_ui_html('<div class="ig-sb-tools-sep" aria-hidden="true"></div>', sidebar=True)
    inject_ui_html('<div class="ig-sb-tools-card">', sidebar=True)
    if dev:
        inject_ui_html('<p class="ig-sb-tools-title">Ferramentas</p>', sidebar=True)
        if members_df is not None:
            render_push_admin_sidebar(members_df)
        render_mobile_and_push_panel(
            expander_title="Configurações",
            expander_key="ig_tool_settings",
        )
    else:
        render_mobile_and_push_panel(
            expander_title="App no celular e notificações",
            expander_key="ig_tool_mobile",
        )
    inject_ui_html("</div>", sidebar=True)


def render_sidebar_footer(
    *,
    members_df: pd.DataFrame | None = None,
    chat_unread: int = 0,
    sug_badge: int = 0,
    swap_alert_count: int = 0,
):
    inject_app_resume_listener()
    inject_app_notification_badges(chat_unread, sug_badge, swap_alert_count)
    render_sidebar_tools_panel(members_df)
    if st.sidebar.button(
        "Sair do sistema",
        key="ig_sidebar_logout",
        use_container_width=True,
        type="secondary",
    ):
        logout_user()
        st.rerun()
    from ui_html import inject_ui_html

    inject_ui_html(
        """
        <div class="ig-sb-footer-verse">
            <span class="ig-sb-footer-heart" aria-hidden="true">♥</span>
            <p class="ig-sb-footer-text">Tudo quanto tem fôlego louve ao Senhor!</p>
            <p class="ig-sb-footer-ref">Salmos 150:6</p>
        </div>
        """,
        sidebar=True,
    )


def page_header(menu: str):
    if menu in (
        "Gerenciar Escalas",
        "Repertório",
        "Playlist",
        "Sugestão de louvor",
        "Chat",
    ):
        return
    items, _, icons = get_menu_items_for_user(st.session_state.user_roles)
    icon = icons.get(menu, "🎵")
    title = MENU_HEADERS.get(menu, menu)
    subtitle = next((desc for name, _, desc in items if name == menu), "")
    accent = MENU_ACCENTS.get(menu, "#d4af37")
    group_label = next(
        (g for g, section_names in NAV_GROUP_ORDER if menu in section_names),
        "",
    )
    breadcrumb = f"{group_label} · " if group_label else ""
    st.markdown(
        f"""
        <div class="music-hero" style="--accent: {accent}">
            <h2>{icon} {title}</h2>
            <p>{breadcrumb}{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def humanize_stat(value: int, label: str) -> tuple[str, str]:
    """Texto amigável quando não há dados (evita '0' seco na interface)."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = 0
    if n > 0:
        return str(n), label
    label_l = label.lower()
    if "chat" in label_l or "mensagem" in label_l:
        return "—", "Sem mensagens no momento"
    if "culto" in label_l:
        return "—", "Nenhum culto nesta semana"
    if "músico" in label_l or "musico" in label_l or "integrante" in label_l:
        return "—", "Equipe em formação"
    if "louvor" in label_l:
        return "—", "Repertório disponível no menu"
    if "escala" in label_l:
        return "—", "Nenhuma escala registrada"
    return "—", "Sem informações no momento"


def render_music_stats(stats: list[tuple[str, str, int]]):
    if not stats:
        st.caption("Resumo indisponível no momento.")
        return
    cards = []
    for i, (icon, label, value) in enumerate(stats):
        display_val, display_label = humanize_stat(value, label)
        cards.append(
            f'<div class="ig-kpi-card ig-kpi-card--{i % 4}">'
            f'<span class="ig-kpi-icon">{icon}</span>'
            f'<span class="ig-kpi-value">{html.escape(display_val)}</span>'
            f'<span class="ig-kpi-label">{html.escape(display_label)}</span>'
            f"</div>"
        )
    st.markdown(
        f'<div class="ig-kpi-row">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def paginate_dataframe(df: pd.DataFrame, page_size: int, key: str) -> pd.DataFrame:
    if df.empty:
        st.caption("Nada para exibir no momento.")
        return df

    total = len(df)
    total_pages = max(1, (total + page_size - 1) // page_size)
    state_key = f"page_{key}"

    if state_key not in st.session_state:
        st.session_state[state_key] = 1

    st.markdown(
        f"""
        <div class="music-pagination">
            <span>🎵 Página <strong>{st.session_state[state_key]}</strong> de
            <strong>{total_pages}</strong> · <strong>{total}</strong> itens</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c_prev, c_next = st.columns(2)
    with c_prev:
        if st.button(
            "⏮ Anterior",
            key=f"prev_{key}",
            use_container_width=True,
            disabled=st.session_state[state_key] <= 1,
        ):
            st.session_state[state_key] -= 1
            st.rerun()
    with c_next:
        if st.button(
            "Próxima ⏭",
            key=f"next_{key}",
            use_container_width=True,
            disabled=st.session_state[state_key] >= total_pages,
        ):
            st.session_state[state_key] += 1
            st.rerun()

    page = min(st.session_state[state_key], total_pages)
    start = (page - 1) * page_size
    return df.iloc[start : start + page_size]


def _login_cross_img_html() -> str:
    if CROSS_IMAGE.exists():
        cross_b64 = base64.b64encode(CROSS_IMAGE.read_bytes()).decode()
        return (
            f'<img class="login-cross" src="data:image/svg+xml;base64,{cross_b64}" '
            f'alt="Cruz" />'
        )
    return '<div class="login-cross" style="font-size:3rem;color:#d4af37;">✝</div>'


def render_login_v2_header():
    cross_img = _login_cross_img_html()
    st.markdown(
        f"""
        <div class="login-v2-header">
            <div class="login-logo-stack">
                {cross_img}
                <div class="login-eq" aria-hidden="true">
                    <span></span><span></span><span></span><span></span>
                    <span></span><span></span><span></span>
                </div>
            </div>
            <h1 class="login-v2-title">{html.escape(LOGIN_DISPLAY_TITLE)}</h1>
            <p class="login-v2-tagline">
                Conectando corações para
                <span class="login-v2-script">adorar juntos.</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_mode_switch(*, active: str) -> None:
    """Abas Entrar / Criar conta na mesma tela (sem mudar de página)."""
    active = active if active in ("login", "register") else "login"
    st.markdown(
        f"""
        <div class="login-mode-switch" role="tablist" aria-label="Modo de acesso">
            <span class="login-mode-tab {"is-active" if active == "login" else ""}">Entrar</span>
            <span class="login-mode-tab {"is-active" if active == "register" else ""}">Criar conta</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "Entrar",
            key="login_mode_btn_login",
            use_container_width=True,
            type="primary" if active == "login" else "secondary",
        ):
            _set_login_view("login")
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.rerun()
    with c2:
        if st.button(
            "Criar conta",
            key="login_mode_btn_register",
            use_container_width=True,
            type="primary" if active == "register" else "secondary",
        ):
            _set_login_view("register")
            st.rerun()


def render_login_register_panel(members_df: pd.DataFrame) -> pd.DataFrame:
    st.markdown(
        '<p class="login-panel-title">Cadastro de novo membro</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="login-panel-sub">Preencha seus dados para participar do ministério de louvor.</p>',
        unsafe_allow_html=True,
    )
    members_df = render_register_form(members_df)
    st.markdown('<div class="login-back-row">', unsafe_allow_html=True)
    if st.button("← Já tenho conta — voltar ao login", key="login_back_from_register", use_container_width=True):
        _set_login_view("login")
        try:
            st.query_params.clear()
        except Exception:
            pass
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    return members_df


def render_login_v2_footer():
    year = date.today().year
    st.markdown(
        f"""
        <div class="login-v2-quote">
            <div class="login-v2-quote-mark">"</div>
            <p class="login-v2-quote-text">
                Cantem ao Senhor um cântico novo; cantem ao Senhor,
                todos os moradores da terra.
            </p>
            <p class="login-v2-quote-ref">Salmos 96:1</p>
        </div>
        <p class="login-v2-copy">
            © {year} {html.escape(LOGIN_DISPLAY_TITLE)}. Todos os direitos reservados.
        </p>
        """,
        unsafe_allow_html=True,
    )


def render_login_v2_form(members_df: pd.DataFrame):
    render_login_mode_switch(active="login")
    inject_device_auth_restore_redirect()
    inject_login_restore_fields()
    inject_auto_login_submit()
    with st.form(key="login_form"):
        login_email = st.text_input("E-mail", placeholder="seu@email.com")
        login_password = st.text_input("Senha", type="password", placeholder="••••••••")
        remember_me = st.checkbox(
            f"Lembrar login neste dispositivo (até {SESSION_REMEMBER_DAYS} dias)",
            value=True,
            help=(
                f"Mantém você logado por até {SESSION_REMEMBER_DAYS} dias neste aparelho, "
                "mesmo ao abrir links (YouTube) e voltar. Preenche email/senha se precisar. "
                "Use só em dispositivo pessoal."
            ),
        )
        login_button = st.form_submit_button("Entrar", type="primary", use_container_width=True)

    st.markdown('<div class="login-forgot-row">', unsafe_allow_html=True)
    if st.button("Esqueci minha senha", key="login_forgot_pw"):
        _set_login_view("forgot")
        st.query_params.clear()
        st.query_params[FORGOT_PASSWORD_QUERY_PARAM] = "1"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if login_button:
        user = authenticate(login_email, login_password, members_df)
        if user is not None:
            members_df = sync_recognized_member_roles(members_df)
            email = user["email"]
            refreshed = members_df[
                members_df["email"].astype(str).str.lower() == email
            ]
            if not refreshed.empty:
                user = refreshed.iloc[0]
            dev_tok = issue_device_session_token(str(user["email"]))
            set_user_session(
                user,
                remember_me=True,
                device_token=dev_tok,
            )
            inject_device_auth_token(dev_tok)
            inject_login_remember(
                remember_me,
                login_email.strip(),
                login_password,
            )
            special = recognized_leadership_role(user["first_name"])
            if special:
                st.success(f"Bem-vindo! Você está como **{special}**.")
            st.rerun()
        else:
            show_form_error("Email ou senha incorretos.")


def render_forgot_password_form(members_df: pd.DataFrame):
    st.markdown(
        '<p class="login-panel-title">Esqueci minha senha</p>',
        unsafe_allow_html=True,
    )

    st.success(
        "**Jeito mais fácil:** peça ao **líder** ou **organizador** do louvor para redefinir "
        "sua senha no app.\n\n"
        "Eles entram em **Gerenciar Escalas** ou **Membros** → "
        "**Redefinir senha de integrante**, escolhem seu nome e definem uma senha nova. "
        "Você só precisa fazer login de novo — sem configurar nada."
    )

    if email_is_configured():
        st.markdown(
            '<p class="login-panel-sub">Ou receba um <strong>link por e-mail</strong> '
            "(use o mesmo e-mail do seu cadastro):</p>",
            unsafe_allow_html=True,
        )
        with st.form(key="forgot_password_form"):
            email = st.text_input("E-mail cadastrado", key="forgot_email")
            submit = st.form_submit_button(
                "Enviar link por e-mail", use_container_width=True
            )

        if submit:
            if not is_valid_email(email):
                show_form_error("Informe um e-mail válido.")
            else:
                ok, msg, _ = create_password_reset_request(
                    email,
                    members_df,
                    RESET_TOKENS_FILE,
                    reset_url_base=get_password_reset_base_url(),
                    reset_query_param=RESET_PASSWORD_QUERY_PARAM,
                    group_name=GROUP_NAME,
                )
                if ok:
                    st.success(msg)
                else:
                    show_technical_error(str(msg))
    else:
        st.caption(
            "Envio automático por e-mail ainda não está ativo neste servidor. "
            "Use o caminho com o líder acima — funciona sempre."
        )

    st.markdown('<div class="login-back-row">', unsafe_allow_html=True)
    if st.button("← Voltar ao login", use_container_width=True):
        st.query_params.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_reset_password_form(members_df: pd.DataFrame):
    token = get_reset_password_token()
    email, err = validate_reset_token(token, RESET_TOKENS_FILE)

    st.markdown(
        '<p class="login-panel-title">Nova senha</p>',
        unsafe_allow_html=True,
    )

    if not email:
        show_form_error(str(err))
        if st.button("Solicitar novo link", use_container_width=True):
            st.query_params.clear()
            st.query_params[FORGOT_PASSWORD_QUERY_PARAM] = "1"
            st.rerun()
        return

    st.markdown(
        f'<p class="login-panel-sub">Defina uma nova senha para <strong>{email}</strong>.</p>',
        unsafe_allow_html=True,
    )

    with st.form(key="reset_password_form"):
        nova = st.text_input("Nova senha", type="password", key="reset_new_pwd")
        conf = st.text_input("Confirmar nova senha", type="password", key="reset_conf_pwd")
        submit = st.form_submit_button(
            "Salvar nova senha", type="primary", use_container_width=True
        )

    if submit:
        if nova != conf:
            show_form_error("As senhas não coincidem.")
        else:
            ok, err_msg = apply_password_reset(
                token,
                nova,
                members_df,
                RESET_TOKENS_FILE,
                hash_password_fn=hash_password,
            )
            if ok:
                save_data(members_df, MEMBERS_FILE)
                st.query_params.clear()
                st.success("Senha alterada! Faça login com a nova senha.")
                st.balloons()
                st.rerun()
            else:
                show_form_error(str(err_msg))

    st.markdown('<div class="login-back-row">', unsafe_allow_html=True)
    if st.button("← Voltar ao login", use_container_width=True):
        _set_login_view("login")
        st.query_params.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def show_login_page(members_df: pd.DataFrame):
    from app_theme import inject_login_v2_theme

    apply_music_theme()
    inject_login_v2_theme()
    _sync_login_view_from_url()
    st.markdown('<div class="login-page">', unsafe_allow_html=True)

    render_login_v2_header()

    view = _login_view_mode()
    if view == "reset" or is_reset_password_page():
        render_reset_password_form(members_df)
    elif view == "forgot" or is_forgot_password_page():
        render_forgot_password_form(members_df)
    elif view == "register":
        render_login_mode_switch(active="register")
        members_df = render_login_register_panel(members_df)
    else:
        render_login_v2_form(members_df)

    render_login_v2_footer()

    st.markdown("</div>", unsafe_allow_html=True)


def load_chat_df() -> pd.DataFrame:
    """Recarrega o chat do disco (evita DataFrame desatualizado na sessão)."""
    load_data.clear()
    return prepare_chat(load_data(CHAT_FILE, CHAT_COLUMNS))


ESCALA_LIVE_FILE_NAMES = frozenset(
    {
        "escalas.csv",
        "escala_equipe.csv",
        "programa_culto.csv",
        "programa_sequencia.csv",
        "trocas_escalas.csv",
    }
)
MENUS_AUTO_REFRESH_ESCALA = frozenset(
    {
        "Dashboard",
        "Escalas",
        "Gerenciar Escalas",
        "Chat",
        "Feed",
        "Repertório",
    }
)
ESCALA_POLL_SECONDS = 8
CHAT_POLL_SECONDS = 4
CHAT_FORCE_RELOAD_EVERY_POLLS = 2
CHAT_LIVE_FILE_NAMES = frozenset({"chat.csv"})
FEED_LIVE_FILE_NAMES = frozenset(
    {"feed_posts.csv", "feed_likes.csv", "feed_comments.csv"}
)
ESCALA_FORCE_RELOAD_EVERY_POLLS = 15


def _load_csv_fresh(file_path: Path, columns: tuple) -> pd.DataFrame:
    """Lê CSV direto da nuvem/disco, sem cache do Streamlit."""
    from remote_store import dataframe_from_remote, is_remote_enabled, should_sync_file

    if should_sync_file(file_path) and is_remote_enabled():
        try:
            df = dataframe_from_remote(columns, file_path.name)
            if df is not None:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(file_path, index=False)
                return df
        except Exception:
            pass
    return load_csv_preserve_rows(file_path, columns)


def escalas_data_revision() -> str:
    """Identificador da versão atual dos arquivos de escala (nuvem ou mtime local)."""
    from remote_store import fetch_sync_revisions, is_remote_enabled

    if is_remote_enabled():
        try:
            remote = fetch_sync_revisions(ESCALA_LIVE_FILE_NAMES)
            if remote:
                return f"remote:{remote}"
        except Exception:
            pass
    parts: list[str] = []
    for path in (ESCALAS_FILE, EQUIPE_FILE, PROGRAMA_FILE, PROGRAMA_SEQUENCIA_FILE, TROCAS_FILE):
        try:
            stat = path.stat()
            parts.append(f"{path.name}:{stat.st_mtime_ns}:{stat.st_size}")
        except OSError:
            parts.append(f"{path.name}:missing")
    return "local:" + "|".join(parts)


def load_escalas_bundle_live() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Recarrega escalas, equipe, programa e trocas sempre da fonte oficial."""
    escalas_df = prepare_escalas(_load_csv_fresh(ESCALAS_FILE, ESCALA_COLUMNS))
    programa_df = prepare_programa(_load_csv_fresh(PROGRAMA_FILE, PROGRAMA_COLUMNS))
    equipe_df = prepare_equipe(_load_csv_fresh(EQUIPE_FILE, EQUIPE_COLUMNS))
    trocas_df = prepare_trocas(_load_csv_fresh(TROCAS_FILE, TROCA_COLUMNS))
    return escalas_df, programa_df, equipe_df, trocas_df


def refresh_escalas_bundle() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    bundle = load_escalas_bundle_live()
    st.session_state["_escalas_bundle"] = bundle
    st.session_state["_escalas_rev"] = escalas_data_revision()
    return bundle


def get_escalas_bundle() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cached = st.session_state.get("_escalas_bundle")
    if cached:
        return cached
    return refresh_escalas_bundle()


@st.fragment(run_every=timedelta(seconds=ESCALA_POLL_SECONDS))
def _escalas_global_sync():
    """Sincronização em tempo real: detecta mudanças na nuvem e atualiza a tela aberta."""
    if not st.session_state.get("authenticated"):
        return

    poll = int(st.session_state.get("_escalas_poll_count", 0)) + 1
    st.session_state._escalas_poll_count = poll
    force_reload = poll % ESCALA_FORCE_RELOAD_EVERY_POLLS == 0

    try:
        new_rev = escalas_data_revision()
    except Exception:
        return

    old_rev = st.session_state.get("_escalas_rev")
    if (
        not force_reload
        and new_rev
        and old_rev == new_rev
        and st.session_state.get("_escalas_bundle")
    ):
        return

    try:
        refresh_escalas_bundle()
    except Exception:
        return

    menu = st.session_state.get("app_menu", "")
    changed = old_rev is not None and new_rev != old_rev
    if menu in MENUS_AUTO_REFRESH_ESCALA and changed:
        st.session_state["_pending_menu_refresh"] = menu


def _feed_global_sync():
    """Atualiza revisão do feed sem rerun automático (evita avisos de formulário)."""
    if not st.session_state.get("authenticated"):
        return
    try:
        st.session_state._feed_rev = feed_data_revision()
    except Exception:
        pass


@st.fragment(run_every=timedelta(seconds=CHAT_POLL_SECONDS))
def _chat_global_sync():
    """Atualiza contagem de não lidas e badge do menu Chat em tempo quase real."""
    if not st.session_state.get("authenticated"):
        return

    poll = int(st.session_state.get("_chat_poll_count", 0)) + 1
    st.session_state._chat_poll_count = poll
    force_reload = poll % CHAT_FORCE_RELOAD_EVERY_POLLS == 0

    try:
        new_rev = chat_data_revision()
    except Exception:
        return

    old_rev = st.session_state.get("_chat_rev")
    rev_changed = old_rev is not None and new_rev != old_rev

    if force_reload or rev_changed or st.session_state.get("_chat_df_cache") is None:
        refresh_chat_live()
    else:
        st.session_state._chat_rev = new_rev

    menu = str(st.session_state.get("app_menu", ""))
    if menu == "Chat":
        st.session_state.chat_unread_count = 0
        st.session_state._chat_unread_prev = 0
        return

    unread = count_unread_chat_messages(st.session_state.get("_chat_df_cache"))
    st.session_state.chat_unread_count = unread
    st.session_state._chat_unread_prev = unread


def append_chat_message(
    *,
    message: str,
    message_type: str = "text",
    media_file: str = "",
    notify: bool = True,
) -> pd.DataFrame:
    base = load_chat_df()
    new_message = {
        "timestamp": timestamp_now(),
        "email": st.session_state.user_email,
        "name": st.session_state.user_full_name or st.session_state.user_name,
        "message": message,
        "message_type": message_type,
        "media_file": media_file,
    }
    updated = pd.concat([base, pd.DataFrame([new_message])], ignore_index=True)
    if not save_data(updated, CHAT_FILE):
        show_technical_error("Não foi possível salvar a mensagem no chat.")
        return base
    st.session_state["_chat_df_cache"] = updated
    update_chat_latest_ts(updated)
    mark_chat_scroll_bottom()
    if notify:
        try:
            notify_chat_message(new_message["name"], new_message["message"])
        except Exception:
            pass
    return updated


def _escape_chat_html(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


def _chat_media_html(mtype: str, media_file: str) -> str:
    path = media_absolute_path(str(media_file).strip(), DATA_DIR)
    if not path:
        return '<p class="chat-text"><em>Mídia indisponível</em></p>'
    try:
        size = path.stat().st_size
    except OSError:
        return '<p class="chat-text"><em>Mídia indisponível</em></p>'
    if mtype == "image":
        if size > 900_000:
            return '<p class="chat-text">📷 Foto</p>'
        try:
            from PIL import Image

            img = Image.open(path).convert("RGB")
            img.thumbnail((720, 720))
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=82)
            b64 = base64.b64encode(buf.getvalue()).decode()
            return (
                f'<img src="data:image/jpeg;base64,{b64}" alt="foto" '
                f'style="max-width:100%;border-radius:8px;" />'
            )
        except Exception:
            return '<p class="chat-text">📷 Foto</p>'
    if mtype == "audio":
        if size > 2_000_000:
            return '<p class="chat-text">🎤 Áudio</p>'
        ext = path.suffix.lower()
        mime = {
            ".webm": "audio/webm",
            ".ogg": "audio/ogg",
            ".mp3": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".wav": "audio/wav",
        }.get(ext, "audio/webm")
        b64 = base64.b64encode(path.read_bytes()).decode()
        return (
            f'<audio controls preload="metadata" style="width:min(100%,280px);">'
            f'<source src="data:{mime};base64,{b64}" type="{mime}"></audio>'
        )
    return ""


def pending_text_key(key_prefix: str) -> str:
    """Chave session_state para texto enviado via chat_input (antes do rerun)."""
    return f"{key_prefix}_pending_text"


def _member_roles_lookup(members_df: pd.DataFrame) -> dict[str, str]:
    out: dict[str, str] = {}
    if members_df is None or members_df.empty:
        return out
    for _, row in members_df.iterrows():
        em = str(row.get("email", "")).strip().lower()
        if em:
            out[em] = str(row.get("roles", ""))
    return out


def render_chat_messages(
    chat_df: pd.DataFrame,
    members_df: pd.DataFrame,
    *,
    delete_fn=None,
    update_fn=None,
    key_prefix: str = "chat",
    premium: bool = False,
):
    from chat_ui import premium_message_html, role_badge_meta

    feed_cls = "chat-feed ig-chat-feed" if premium else "chat-feed"
    st.markdown(f'<div id="chat-scroll-box" class="{feed_cls}">', unsafe_allow_html=True)
    if chat_df.empty:
        if premium:
            st.markdown(
                """
                <div class="ig-chat-empty">
                    <strong>💬 Nenhuma mensagem ainda</strong>
                    <div>Envie a primeira mensagem para iniciar a conversa do grupo.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("💬 Nenhuma mensagem ainda — use o campo abaixo.")
        st.markdown("</div>", unsafe_allow_html=True)
        inject_chat_scroll_to_bottom()
        return

    my_email = st.session_state.user_email.strip().lower()
    chat_sorted = sort_chat_messages(chat_df)
    delete_fn = delete_fn or delete_own_chat_message
    update_fn = update_fn or update_own_chat_message
    roles_map = _member_roles_lookup(members_df)
    show_reaction_once = True
    for _, row in chat_sorted.iterrows():
        is_me = str(row.get("email", "")).strip().lower() == my_email
        display_name = "Você" if is_me else str(row.get("name", "Integrante"))
        time_str = format_local(row.get("timestamp"), "%d/%m %H:%M")
        email = str(row.get("email", "")).strip().lower()
        foto = member_photo_html(email, members_df, 34 if premium else 32)
        css = "me" if is_me else "other"
        mtype = str(row.get("message_type", "text") or "text").strip().lower()
        ts = str(row.get("timestamp", ""))
        if mtype == "audio":
            body = _chat_media_html("audio", str(row.get("media_file", "")))
        elif mtype == "image":
            body = _chat_media_html("image", str(row.get("media_file", "")))
        else:
            body = f'<p class="chat-text">{_escape_chat_html(row.get("message", ""))}</p>'

        if premium:
            role_label, role_cls = role_badge_meta(roles_map.get(email, ""))
            if is_me:
                role_label, role_cls = role_badge_meta(
                    str(st.session_state.get("user_roles", ""))
                )
            react = show_reaction_once and not is_me and mtype == "text"
            if react:
                show_reaction_once = False
            st.markdown(
                premium_message_html(
                    is_me=is_me,
                    display_name=display_name,
                    role_label=role_label,
                    role_cls=role_cls,
                    time_str=time_str,
                    body_html=body,
                    avatar_html=foto,
                    show_reaction=react,
                ),
                unsafe_allow_html=True,
            )
            if is_me and mtype == "text":
                with st.popover("⋮", use_container_width=True):
                    st.caption("Sua mensagem")
                    edit_key = f"{key_prefix}_edit_{ts}"
                    if st.button(
                        "✏️ Editar",
                        key=f"{key_prefix}_edbtn_{ts}",
                        use_container_width=True,
                    ):
                        st.session_state[edit_key] = str(row.get("message", ""))
                    if st.button(
                        "🗑️ Apagar",
                        key=f"{key_prefix}_del_{ts}",
                        use_container_width=True,
                    ):
                        delete_fn(ts, my_email)
                        st.rerun()
                if st.session_state.get(f"{key_prefix}_edit_{ts}") is not None:
                    novo = st.text_input(
                        "Editar mensagem",
                        value=st.session_state.get(f"{key_prefix}_edit_{ts}", ""),
                        key=f"{key_prefix}_editinp_{ts}",
                    )
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button(
                            "Salvar",
                            key=f"{key_prefix}_save_{ts}",
                            type="primary",
                        ):
                            if novo.strip():
                                update_fn(ts, my_email, novo.strip())
                            st.session_state.pop(f"{key_prefix}_edit_{ts}", None)
                            st.rerun()
                    with ec2:
                        if st.button("Cancelar", key=f"{key_prefix}_cancel_{ts}"):
                            st.session_state.pop(f"{key_prefix}_edit_{ts}", None)
                            st.rerun()
            continue

        if is_me and mtype == "text":
            c_msg, c_act = st.columns([11, 1])
            with c_msg:
                st.markdown(
                    f'<div class="chat-bubble {css}">'
                    f'<div class="chat-row-head">{foto}'
                    f'<span class="chat-row-name">{_escape_chat_html(display_name)}</span>'
                    f'<span class="chat-row-time"> · {time_str}</span></div>'
                    f"{body}</div>",
                    unsafe_allow_html=True,
                )
            with c_act:
                with st.popover("⋮", use_container_width=True):
                    st.caption("Sua mensagem")
                    edit_key = f"{key_prefix}_edit_{ts}"
                    if st.button(
                        "✏️ Editar",
                        key=f"{key_prefix}_edbtn_{ts}",
                        use_container_width=True,
                    ):
                        st.session_state[edit_key] = str(row.get("message", ""))
                    if st.button(
                        "🗑️ Apagar",
                        key=f"{key_prefix}_del_{ts}",
                        use_container_width=True,
                    ):
                        delete_fn(ts, my_email)
                        st.rerun()
            if st.session_state.get(f"{key_prefix}_edit_{ts}") is not None:
                novo = st.text_input(
                    "Editar mensagem",
                    value=st.session_state.get(f"{key_prefix}_edit_{ts}", ""),
                    key=f"{key_prefix}_editinp_{ts}",
                )
                ec1, ec2 = st.columns(2)
                with ec1:
                    if st.button("Salvar", key=f"{key_prefix}_save_{ts}", type="primary"):
                        if novo.strip():
                            update_fn(ts, my_email, novo.strip())
                        st.session_state.pop(f"{key_prefix}_edit_{ts}", None)
                        st.rerun()
                with ec2:
                    if st.button("Cancelar", key=f"{key_prefix}_cancel_{ts}"):
                        st.session_state.pop(f"{key_prefix}_edit_{ts}", None)
                        st.rerun()
        else:
            st.markdown(
                f'<div class="chat-bubble {css}">'
                f'<div class="chat-row-head">{foto}'
                f'<span class="chat-row-name">{_escape_chat_html(display_name)}</span>'
                f'<span class="chat-row-time"> · {time_str}</span></div>'
                f"{body}</div>",
                unsafe_allow_html=True,
            )
    st.markdown(
        '<div id="chat-scroll-end" style="height:1px;"></div></div>',
        unsafe_allow_html=True,
    )
    inject_chat_scroll_to_bottom()


def render_chat_composer(
    *,
    key_prefix: str,
    append_fn,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path | None = None,
    image_prefix: str = "chat",
):
    """Compositor compacto: mensagem + ➕ anexos."""
    img_dir = images_dir or CHAT_IMAGES_DIR
    render_whatsapp_chat_composer(
        key_prefix=key_prefix,
        append_fn=append_fn,
        audio_dir=audio_dir,
        audio_prefix=audio_prefix,
        images_dir=img_dir,
        image_prefix=image_prefix,
        data_dir=DATA_DIR,
    )
    inject_chat_scroll_to_bottom()


def show_group_chat(chat_df: pd.DataFrame, members_df: pd.DataFrame):
    from chat_ui import (
        CHAT_LIST_TABS,
        count_chat_media,
        last_group_preview,
        render_chat_page_close,
        render_chat_page_open,
        render_conv_items_after_search,
        render_info_panel_html,
        render_thread_header_html,
        role_badge_meta,
    )
    from ui_html import inject_ui_html

    pending_key = pending_text_key("group_chat")
    pending = st.session_state.pop(pending_key, None)
    if pending and str(pending).strip():
        append_chat_message(message=str(pending).strip(), message_type="text", media_file="")

    chat_df = load_chat_df()
    mark_chat_seen(chat_df)
    unread = count_unread_chat_messages(chat_df)
    preview, prev_time = last_group_preview(chat_df)
    n_members = len(members_visible_to_group(members_df))
    imgs, auds, _ = count_chat_media(chat_df)

    from mobile_ui import mobile_hdr_close, mobile_hdr_open

    render_chat_page_open()
    mobile_hdr_open()
    hdr_l, hdr_r = st.columns([4, 1])
    with hdr_l:
        inject_ui_html(
            """
            <div class="ig-chat-header" style="margin-bottom:0.85rem;">
                <div class="ig-chat-header-left">
                    <div class="ig-chat-header-ico"></div>
                    <div>
                        <h1 class="ig-chat-header-title">Chat</h1>
                        <p class="ig-chat-header-sub">Converse com sua equipe e ministério</p>
                    </div>
                </div>
            </div>
            """
        )
    with hdr_r:
        st.markdown('<div style="padding-top:1.1rem">', unsafe_allow_html=True)
        st.button(
            "+ Novo grupo",
            key="chat_new_group_btn",
            disabled=True,
            help="Criação de novos grupos em breve.",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    mobile_hdr_close()

    inject_ui_html('<div class="ig-chat-mobile-order ig-m-layout-stack">')
    col_l, col_m, col_r = st.columns([0.92, 1.75, 0.95])

    with col_l:
        inject_ui_html('<div class="ig-chat-col ig-chat-col--list">')
        list_tab = st.radio(
            "Filtro",
            list(CHAT_LIST_TABS),
            horizontal=True,
            label_visibility="collapsed",
            key="chat_list_tab",
        )
        st.text_input(
            "Buscar conversas",
            placeholder="Buscar conversas...",
            key="chat_search_conv",
            label_visibility="collapsed",
        )
        render_conv_items_after_search(
            preview=preview,
            time_str=prev_time,
            unread=unread,
            list_tab=list_tab,
        )
        inject_ui_html("</div>")

    with col_m:
        inject_ui_html('<div class="ig-chat-col ig-chat-col--main">')
        render_thread_header_html(n_members)
        _chat_group_live(members_df, premium=True)
        inject_ui_html("</div>")

    with col_r:
        member_rows: list[tuple[str, str, str, str]] = []
        visible = members_visible_to_group(members_df)
        online_n = min(6, len(visible)) if not visible.empty else 0
        if not visible.empty:
            for _, row in visible.sort_values(
                by=["first_name", "last_name"],
                key=lambda s: s.str.lower(),
            ).head(8).iterrows():
                email = str(row["email"]).strip().lower()
                nome = member_display_name(row)
                rl, rc = role_badge_meta(str(row.get("roles", "")))
                av = member_photo_html(email, members_df, 28)
                member_rows.append((av, nome, rl, rc))
        render_info_panel_html(
            member_rows,
            media_images=imgs,
            media_audio=auds,
            online_label=str(online_n) if online_n else "0",
        )

    inject_ui_html("</div>")
    render_chat_page_close()


@st.fragment(run_every=timedelta(seconds=4))
def _chat_group_live(members_df: pd.DataFrame, *, premium: bool = False):
    """Atualiza o histórico a cada poucos segundos para refletir mensagens de outros integrantes."""
    chat_df = load_chat_df()
    st.session_state["_chat_df_cache"] = chat_df
    st.session_state.chat_unread_count = 0

    def _append(**kwargs):
        append_chat_message(**kwargs)

    render_chat_messages(chat_df, members_df, premium=premium)
    if premium:
        st.markdown('<div class="ig-chat-compose-wrap">', unsafe_allow_html=True)
    render_chat_composer(
        key_prefix="group_chat",
        append_fn=_append,
        audio_dir=CHAT_AUDIO_DIR,
        audio_prefix="chat",
        images_dir=CHAT_IMAGES_DIR,
        image_prefix="chat",
    )
    if premium:
        st.markdown("</div>", unsafe_allow_html=True)


def render_team_grid_html(
    escala_row,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> str:
    team = integrantes_escalados(escala_row, equipe_df, members_df)
    if not team:
        return ""
    parts = []
    for p in team:
        email = str(p.get("email", "")).strip()
        foto = member_photo_html(email, members_df, 64) if email else ""
        funcao = normalize_funcao_escala(str(p.get("funcao", "Integrante")))
        parts.append(
            f'<motion class="team-member-card">{foto}'
            f'<p class="tm-name">{p["nome"]}</p>'
            f'<p class="tm-role">{funcao}</p></div>'
        )
    return '<div class="team-grid">' + "".join(
        x.replace('<motion class="team-member-card">', '<div class="team-member-card">')
        for x in parts
    ) + "</div>"


def collect_escala_whatsapp_message(
    escala_row,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame | None = None,
) -> str:
    """Monta texto completo da escala para WhatsApp."""
    from catalog_sanitize import (
        fix_louvor_display_title,
        format_louvor_display,
        sanitize_catalog_text,
    )

    row = escala_row if isinstance(escala_row, pd.Series) else pd.Series(escala_row)
    escala_id = str(row.get("id", ""))
    event = str(row.get("event", "Culto"))
    dt = pd.to_datetime(row.get("date"), errors="coerce")
    culto_date = dt.strftime("%d/%m/%Y") if pd.notna(dt) else str(row.get("date", ""))
    ensaio_date = (
        format_rehearsal_date_pt(row) if rehearsal_date_is_set(row) else ""
    )
    ministrador = str(row.get("member_name") or row.get("responsible", ""))
    equipe = [
        (str(p.get("nome", "")), str(p.get("funcao", "")))
        for p in integrantes_escalados(row, equipe_df, members_df)
        if str(p.get("nome", "")).strip()
    ]
    programa: list[tuple[str, str, str, str]] = []
    prog = programa_por_escala(programa_df, escala_id)
    if louvores_df is not None and not louvores_df.empty:
        prog = enrich_programa_from_catalog(prog, louvores_df)
    for _, item in prog.iterrows():
        louvor = fix_louvor_display_title(
            sanitize_catalog_text(item.get("louvor_title", ""))
        )
        artist = sanitize_catalog_text(item.get("artist", ""))
        titulo = format_louvor_display(louvor, artist)
        programa.append(
            (
                str(item.get("ordem", "")),
                str(item.get("parte", "")),
                titulo,
                sanitize_catalog_text(item.get("key", "")),
            )
        )
    return build_escala_share_message(
        event=event,
        culto_date=culto_date,
        ensaio_date=ensaio_date,
        ministrador=ministrador,
        equipe=equipe,
        programa=programa,
        notas=str(row.get("notes", "")),
    )


def generate_single_escala_pdf(
    escala_row,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
) -> tuple[bytes, str]:
    row = escala_row if isinstance(escala_row, pd.Series) else pd.Series(escala_row)
    one = pd.DataFrame([row.to_dict()])
    culto_d = pd.to_datetime(row.get("date"), errors="coerce")
    label = (
        culto_d.strftime("%d-%m-%Y") if pd.notna(culto_d) else "escala"
    )
    pdf_bytes = build_escalas_pdf(
        one,
        programa_df,
        equipe_df,
        period_label=str(row.get("event", "Culto")),
        integrantes_escalados=integrantes_escalados,
        normalize_funcao_escala=normalize_funcao_escala,
        programa_por_escala=programa_por_escala,
        fix_louvor_display_title=fix_louvor_display_title,
        funcao_ministrador=FUNCAO_MINISTRADOR,
        rehearsal_date_is_set=rehearsal_date_is_set,
        format_rehearsal_date_pt=format_rehearsal_date_pt,
    )
    fname = suggested_filename(str(row.get("event", "escala")), 1).replace(" ", "_")
    return pdf_bytes, fname or f"escala_{label}.pdf"


def render_escala_whatsapp_actions(
    message: str,
    *,
    pdf_bytes: bytes | None = None,
    pdf_filename: str = "escala_gdl.pdf",
    key_prefix: str = "wa_esc",
) -> None:
    """Botões: WhatsApp texto, copiar, PDF (celular)."""
    phone = whatsapp_group_phone()
    st.markdown("**📲 Compartilhar escala no WhatsApp**")
    c1, c2 = st.columns(2)
    with c1:
        st.link_button(
            "💬 Abrir WhatsApp com escala completa",
            whatsapp_share_url(message, phone=phone),
            use_container_width=True,
            key=f"{key_prefix}_link",
        )
    with c2:
        inject_copy_whatsapp_message(message, element_id=f"{key_prefix}_copy")
    if pdf_bytes:
        if len(pdf_bytes) <= 2_500_000:
            inject_share_pdf_whatsapp(
                pdf_bytes,
                pdf_filename,
                message[:300],
                element_id=f"{key_prefix}_pdf",
            )
        else:
            st.caption(
                "PDF grande demais para envio direto pelo navegador — use **Baixar PDF** e anexe no grupo."
            )
    st.caption(whatsapp_automation_status())


def render_pending_whatsapp_share_banner() -> None:
    """Após salvar escala, oferece envio ao grupo."""
    pending = st.session_state.get("pending_wa_escala")
    if not pending:
        return
    st.markdown("---")
    st.markdown(
        '<div style="background:rgba(37,211,102,0.12);border:1px solid rgba(37,211,102,0.45);'
        'border-radius:14px;padding:1rem 1.15rem;margin:0.5rem 0;">',
        unsafe_allow_html=True,
    )
    st.markdown("#### ✅ Escala publicada — envie ao grupo")
    render_escala_whatsapp_actions(
        pending.get("message", ""),
        pdf_bytes=pending.get("pdf_bytes"),
        pdf_filename=pending.get("pdf_filename", "escala_gdl.pdf"),
        key_prefix="pending_wa",
    )
    if st.button("Dispensar este aviso", key="pending_wa_dismiss", use_container_width=True):
        st.session_state.pop("pending_wa_escala", None)
        st.session_state.pop("wa_auto_open_url", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def queue_whatsapp_after_escala_save(
    escala_row: dict,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
) -> None:
    """Prepara mensagem/PDF e notifica; opcionalmente abre WhatsApp."""
    msg = collect_escala_whatsapp_message(
        escala_row, programa_df, equipe_df, members_df, louvores_df
    )
    pdf_bytes = None
    pdf_name = "escala_gdl.pdf"
    try:
        pdf_bytes, pdf_name = generate_single_escala_pdf(
            escala_row, programa_df, equipe_df, members_df
        )
    except Exception:
        pass
    st.session_state.pending_wa_escala = {
        "message": msg,
        "pdf_bytes": pdf_bytes,
        "pdf_filename": pdf_name,
        "escala_id": str(escala_row.get("id", "")),
    }
    notify_new_escala(
        str(escala_row.get("event", "Culto")),
        str(escala_row.get("date", "")),
        str(escala_row.get("responsible", "")),
        detail=msg,
    )
    if whatsapp_auto_prompt_enabled() and whatsapp_group_phone():
        st.session_state.wa_auto_open_url = whatsapp_share_url(
            msg, phone=whatsapp_group_phone()
        )


def render_culto_programa(
    escala_row,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame | None = None,
    *,
    ensaio_notice: bool = False,
    widget_key_prefix: str = "",
):
    escala_id = str(escala_row.get("id", ""))
    wkey = widget_key_prefix.strip() or f"culto_{escala_id}"
    event = str(escala_row.get("event", "Culto"))
    culto_date = str(escala_row.get("date", ""))
    is_mgr = is_scale_manager(st.session_state.get("user_roles", []))
    try:
        dt = pd.to_datetime(culto_date)
        date_fmt = f"{_DIAS_SEMANA_PT[dt.weekday()]}, {dt.strftime('%d/%m/%Y')}"
    except (ValueError, TypeError):
        date_fmt = culto_date

    ensaio_fmt = ""
    if rehearsal_date_is_set(escala_row):
        ensaio_fmt = f" · Ensaio: {format_rehearsal_date_pt(escala_row)}"

    if ensaio_notice:
        banner = ensaio_aviso_banner_html(escala_row, is_manager=is_mgr)
        if banner:
            st.markdown(banner, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="culto-week-card">
            <h3>🎤 {event}</h3>
            <p class="culto-date">📅 {date_fmt}{ensaio_fmt}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    team_html = render_team_grid_html(escala_row, equipe_df, members_df)
    if team_html:
        st.markdown("**👥 Equipe escalada**")
        st.markdown(team_html, unsafe_allow_html=True)
    else:
        st.caption("Equipe ainda em formação.")

    prog = programa_por_escala(programa_df, escala_id)
    if louvores_df is not None and not louvores_df.empty:
        prog = enrich_programa_from_catalog(prog, louvores_df)
    if prog.empty:
        st.caption(
            "🎶 Programação do culto ainda não montada — configure em **Gerenciar Escalas**."
        )
        return

    st.markdown("**🎶 Sequência do culto**")
    from catalog_sanitize import format_louvor_display, sanitize_catalog_text
    from voice_kit_links import vocal_nipe_from_roles, voice_kit_search_query, voice_kit_youtube_url

    idx_me, row_me = get_current_member_row(members_df)
    bio_me = str(row_me.get("bio", "")) if row_me is not None else ""
    roles_me = str(row_me.get("roles", "")) if row_me is not None else str(
        st.session_state.get("user_roles", "")
    )
    kits_me = instrument_kits_from_roles(roles_me, bio=bio_me)
    if kits_me:
        kit_names = ", ".join(k[0] for k in kits_me)
        st.caption(f"Seus kits no YouTube: **{kit_names}** (conforme funções no Perfil).")
    else:
        st.caption(
            "Cadastre sua função (vocal, bateria, guitarra, etc.) em **Perfil** "
            "para ver os botões de kit em cada louvor."
        )

    total_prog_min = 0.0
    for _, item in prog.iterrows():
        artist = sanitize_catalog_text(item.get("artist", ""))
        louvor = fix_louvor_display_title(sanitize_catalog_text(item.get("louvor_title", "")))
        titulo = format_louvor_display(louvor, artist)
        tom = sanitize_catalog_text(item.get("key", ""))
        leader = sanitize_catalog_text(item.get("leader_name", ""))
        meta_l = (
            lookup_louvor_meta(louvores_df, louvor, artist) if louvores_df is not None else {}
        )
        dur_item = parse_duracao_min(meta_l.get("duracao_min", ""))
        total_prog_min += dur_item
        dur_txt = format_duracao_total(dur_item)
        yt = sanitize_catalog_text(item.get("youtube_url", ""))
        cifra = sanitize_catalog_text(item.get("cifra_url", ""))
        if cifra and not cifra.startswith("http"):
            cifra = ""
        if not cifra:
            cifra = cifra_search_url(louvor, artist)
        btns = []
        if yt:
            btns.append(
                f'<a class="prog-btn prog-btn-yt" href="{yt}" target="_blank" rel="noopener">▶ YouTube</a>'
            )
        for kit_label, _kit_key, kit_prefix in kits_me:
            ku = kit_youtube_url(kit_prefix, louvor)
            short = kit_label.replace("Kit ", "")
            btns.append(
                f'<a class="prog-btn prog-btn-kit" href="{ku}" target="_blank" rel="noopener" '
                f'title="{html.escape(kit_label)}">🎵 {html.escape(short)}</a>'
            )
        btns.append(
            f'<a class="prog-btn prog-btn-letra" href="{cifra}" target="_blank" rel="noopener">📜 Letra / Cifra</a>'
        )
        btns_html = f'<div class="prog-actions">{"".join(btns)}</div>' if btns else ""
        meta_parts = [
            f"Tom: {tom}" if tom else "",
            f"🎤 {leader}" if leader else "",
            f"⏱ ~{dur_txt}",
        ]
        ref_b = str(meta_l.get("ref_biblica", "")).strip()
        if ref_b:
            meta_parts.append(f"📖 {html.escape(ref_b[:80])}")
        meta = " · ".join(x for x in meta_parts if x)
        st.markdown(
            f"""
            <div class="prog-card">
                <span class="seq-badge">{item['ordem']}</span>
                <span class="prog-parte">{item['parte']}</span>
                <p class="prog-louvor">{titulo}</p>
                <p class="prog-meta">{meta}</p>
                {btns_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if total_prog_min > 0:
        st.caption(
            f"⏱ Duração estimada do bloco de louvor: **{format_duracao_total(total_prog_min)}**"
        )

    if st.button(
        "🎼 Abrir Sequência do Culto (letras e cifras no app)",
        key=f"{wkey}_open_seq_culto",
        use_container_width=True,
    ):
        st.session_state["focus_sequencia_escala_id"] = escala_id
        st.session_state["_open_sequencia_tab"] = True
        st.info("Abra a aba **🎼 Sequência do Culto** neste menu para ver e editar.")

    my_email = st.session_state.user_email.strip().lower()
    is_ministrador_culto = (
        str(escala_row.get("member_email", "")).strip().lower() == my_email
    )
    if not is_ministrador_culto and not equipe_df.empty:
        eq = equipe_por_escala(equipe_df, escala_id)
        is_ministrador_culto = any(
            str(r.get("member_email", "")).strip().lower() == my_email
            and FUNCAO_MINISTRADOR in normalize_funcao_escala(str(r.get("funcao", "")))
            for _, r in eq.iterrows()
        )
    can_guia = is_ministrador_culto or is_scale_manager(st.session_state.get("user_roles", ""))
    if can_guia:
        nomes_l = []
        refs_por: list[tuple[str, str]] = []
        themes_lines: list[str] = []
        for _, p in prog.iterrows():
            louv_t = fix_louvor_display_title(
                sanitize_catalog_text(p.get("louvor_title", ""))
            )
            art = sanitize_catalog_text(p.get("artist", ""))
            nomes_l.append(format_louvor_display(louv_t, art))
            if louvores_df is not None:
                m = lookup_louvor_meta(louvores_df, louv_t, art)
                th = themes_from_csv(str(m.get("temas", "")))
                themes_lines.extend(th)
                refs_por.append((louv_t, str(m.get("ref_biblica", "")) or suggest_biblical_refs(th, louv_t)))
        with st.expander("📖 Guia de ministração", expanded=False, key=f"{wkey}_guia_min"):
            st.markdown(
                guia_ministracao_text(
                    evento=event,
                    culto_date=date_fmt,
                    louvores=nomes_l,
                    themes_lines=list(dict.fromkeys(themes_lines))[:8],
                    refs_por_louvor=refs_por,
                )
            )

    wa_msg = collect_escala_whatsapp_message(
        escala_row, programa_df, equipe_df, members_df, louvores_df
    )
    pdf_b, pdf_n = None, "escala.pdf"
    try:
        pdf_b, pdf_n = generate_single_escala_pdf(
            escala_row, programa_df, equipe_df, members_df
        )
    except Exception:
        pass
    render_escala_whatsapp_actions(
        wa_msg, pdf_bytes=pdf_b, pdf_filename=pdf_n, key_prefix=f"{wkey}_wa_culto"
    )


def _feed_post_badge(post_type: str) -> str:
    badges = {
        "louvor_aprovado": "🎵 Nova no repertório",
        "evento": "📅 Evento",
        "comunicado": "📢 Comunicado",
    }
    return badges.get(str(post_type).strip(), "📰 Novidade")


def render_feed_post_card(
    post: pd.Series,
    likes_df: pd.DataFrame,
    comments_df: pd.DataFrame,
    *,
    key_prefix: str = "feed",
    show_comments: bool = True,
):
    pid = str(post.get("id", ""))
    my_email = st.session_state.user_email.strip().lower()
    badge = _feed_post_badge(post.get("post_type", ""))
    created = format_local(post.get("created_at"), "%d/%m/%Y %H:%M")
    body_raw = str(post.get("body", ""))

    from feed_ui import render_feed_post_header

    render_feed_post_header(
        badge=badge,
        title=str(post.get("title", "")),
        author=str(post.get("author_name", "Integrante")),
        created=created,
    )
    if body_raw.strip():
        st.markdown(body_raw)

    img = str(post.get("image_url", "")).strip()
    img_path = feed_image_display_path(img, DATA_DIR) if img else None
    if img_path:
        try:
            if img_path.startswith("http"):
                st.image(img_path, use_container_width=True)
            else:
                st.image(img_path, use_container_width=True)
        except Exception:
            pass

    yt = str(post.get("youtube_url", "")).strip()
    cifra = str(post.get("cifra_url", "")).strip()
    link_cols = st.columns(4)
    with link_cols[0]:
        if yt.startswith("http"):
            st.link_button("▶ YouTube", yt, use_container_width=True)
    with link_cols[1]:
        if cifra.startswith("http"):
            st.link_button("🎸 Cifra", cifra, use_container_width=True)
    with link_cols[2]:
        share_txt = f"{str(post.get('title', ''))}\n{body_raw[:400]}"
        st.link_button(
            "📲 Compartilhar",
            whatsapp_share_url(share_txt, yt if yt.startswith("http") else ""),
            use_container_width=True,
            key=f"{key_prefix}_wa_{pid}",
        )
    with link_cols[3]:
        if st.button("🎶 Repertório", key=f"{key_prefix}_rep_{pid}", use_container_width=True):
            st.session_state.app_menu = "Repertório"
            st.rerun()

    likes_df = prepare_feed_likes(likes_df)
    comments_df = prepare_feed_comments(comments_df)
    likes_n = feed_likes_count(pid, likes_df)
    liked = user_liked_post(pid, my_email, likes_df)
    author_email = str(post.get("author_email", "")).strip().lower()
    lc1, lc2, lc3 = st.columns([1, 2, 1])
    with lc1:
        label = f"{'💔' if liked else '❤️'} Curtir ({likes_n})"
        if st.button(label, key=f"{key_prefix}_like_{pid}", use_container_width=True):
            toggle_feed_like(pid, my_email, likes_df)
            st.rerun()
    with lc3:
        if author_email == my_email and st.button(
            "🗑️ Apagar post", key=f"{key_prefix}_delpost_{pid}", use_container_width=True
        ):
            delete_feed_post(pid)
            st.rerun()

    if show_comments:
        post_comments = comments_df[comments_df["post_id"].astype(str) == pid]
        if not post_comments.empty:
            st.caption(f"💬 {len(post_comments)} comentário(s)")
            for _, c in post_comments.sort_values("created_at").iterrows():
                t = format_local(c.get("created_at"), "%d/%m %H:%M")
                st.markdown(
                    f'<div class="feed-comment"><b>{html.escape(str(c.get("name", "")))}</b> '
                    f'<time>· {html.escape(t)}</time><br>'
                    f'{html.escape(str(c.get("message", "")))}</div>',
                    unsafe_allow_html=True,
                )
                if str(c.get("email", "")).strip().lower() == my_email:
                    if st.button(
                        "Apagar comentário",
                        key=f"{key_prefix}_delcmt_{c['id']}",
                        use_container_width=True,
                    ):
                        delete_feed_comment(str(c["id"]))
                        st.rerun()
        cmt_key = f"{key_prefix}_cmt_msg_{pid}"
        msg = st.text_input(
            "Comentar",
            placeholder="Escreva um comentário...",
            key=cmt_key,
        )
        if st.button("Enviar", key=f"{key_prefix}_cmt_btn_{pid}", use_container_width=True):
            text = str(st.session_state.get(cmt_key, "")).strip()
            if not text:
                show_form_error("Escreva um comentário antes de enviar.")
            else:
                append_feed_comment(
                    pid,
                    my_email,
                    st.session_state.user_full_name or st.session_state.user_name,
                    text,
                    comments_df,
                )
                st.rerun()
    st.markdown("---")


def render_feed_preview(limit: int = 3):
    posts_df, likes_df, comments_df = load_feed_bundle()
    if posts_df.empty:
        return
    render_dashboard_section_start("Novidades do ministério", "📰", MENU_ACCENTS.get("Feed", "#f472b6"))
    df = posts_df.copy()
    df["_sort"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.sort_values("_sort", ascending=False).head(limit)
    for _, post in df.iterrows():
        render_feed_post_card(
            post, likes_df, comments_df, key_prefix=f"prev_{post['id']}", show_comments=False
        )
    if st.button("Ver feed completo", key="dash_go_feed", use_container_width=True):
        st.session_state.app_menu = "Feed"
        st.rerun()
    render_dashboard_section_end()


def show_feed_page(
    posts_df: pd.DataFrame,
    likes_df: pd.DataFrame,
    comments_df: pd.DataFrame,
):
    from feed_ui import (
        render_feed_empty_state,
        render_feed_header,
        render_feed_page_close,
        render_feed_page_open,
        render_feed_verse_card,
    )

    render_feed_page_open()
    render_feed_header()
    render_feed_verse_card()

    if is_scale_manager(st.session_state.user_roles):
        with st.expander("Manutenção do feed (líderes)", expanded=False, key="ig_feed_maint"):
            st.caption(
                "Apaga **todos** os posts, curtidas e comentários. Use se o feed estiver "
                "duplicado ou deixando o app lento."
            )
            if st.button("🗑️ Apagar todo o feed agora", key="feed_purge_all_btn"):
                n = purge_all_feed_data()
                st.success(f"Feed limpo ({n} publicação(ões) removida(s)).")
                st.rerun()

    with st.expander("Nova publicação", expanded=False, key="ig_feed_new"):
        with st.form(key="feed_post_form"):
            titulo = st.text_input("Título")
            corpo = st.text_area("Mensagem")
            tipo_opts = ["comunicado", "evento"]
            if is_scale_manager(st.session_state.user_roles):
                tipo_opts = ["comunicado", "evento"]
            tipo = st.selectbox(
                "Tipo",
                tipo_opts,
                format_func=lambda x: "📢 Comunicado" if x == "comunicado" else "📅 Evento",
            )
            yt = st.text_input("Link YouTube (opcional)")
            img_url = st.text_input("URL da imagem (opcional)")
            img_file = st.file_uploader(
                "Ou envie uma imagem",
                type=["jpg", "jpeg", "png", "webp"],
                key="feed_post_img_up",
            )
            pub = st.form_submit_button("Publicar no feed", type="primary")
            if pub:
                if not titulo.strip() or not corpo.strip():
                    show_form_error("Informe título e mensagem.")
                else:
                    image_ref = img_url.strip()
                    if img_file is not None:
                        image_ref = save_feed_image_file(img_file, DATA_DIR, FEED_IMAGES_DIR)
                    append_feed_post(
                        post_type=tipo,
                        title=titulo.strip(),
                        body=corpo.strip(),
                        youtube_url=yt.strip(),
                        author_email=st.session_state.user_email,
                        author_name=st.session_state.user_full_name
                        or st.session_state.user_name,
                        image_url=image_ref,
                    )
                    st.success("Publicado no feed!")
                    st.rerun()

    if posts_df.empty:
        render_feed_empty_state()
        render_feed_page_close()
        return

    st.markdown('<div class="ig-feed-refresh-wrap">', unsafe_allow_html=True)
    if st.button("Atualizar feed", key="ig_feed_refresh", use_container_width=False):
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    _render_feed_posts_live()
    render_feed_page_close()


def _render_feed_posts_live():
    posts_df, likes_df, comments_df = load_feed_bundle()
    if posts_df.empty:
        return
    df = posts_df.copy()
    df["_sort"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.sort_values("_sort", ascending=False)
    page_df = paginate_dataframe(df, 8, "feed_posts")
    for _, post in page_df.iterrows():
        render_feed_post_card(post, likes_df, comments_df, key_prefix=f"feed_{post['id']}")


def render_playlist_track_links(row: pd.Series, members_df: pd.DataFrame):
    from catalog_sanitize import sanitize_catalog_text

    titulo = sanitize_catalog_text(row.get("title", ""))
    artista = sanitize_catalog_text(row.get("artist", ""))
    yt = sanitize_catalog_text(row.get("youtube_url", ""))
    cifra = sanitize_catalog_text(row.get("cifra_url", ""))
    if cifra and not cifra.startswith("http"):
        cifra = ""
    if not cifra:
        cifra = cifra_search_url(titulo, artista)

    idx_me, row_me = get_current_member_row(members_df)
    roles_me = str(row_me.get("roles", "")) if row_me is not None else str(
        st.session_state.get("user_roles", "")
    )
    bio_me = str(row_me.get("bio", "")) if row_me is not None else ""
    kits = instrument_kits_from_roles(roles_me, bio=bio_me)

    cols = st.columns(min(4 + len(kits), 6))
    with cols[0]:
        if yt.startswith("http"):
            st.link_button("▶ YouTube", yt, use_container_width=True)
        else:
            st.caption("YouTube indisponível")
    for i, (kit_label, _, kit_prefix) in enumerate(kits[:3]):
        with cols[1 + i]:
            st.link_button(
                kit_label,
                kit_youtube_url(kit_prefix, titulo),
                use_container_width=True,
            )
    ci = min(1 + len(kits), len(cols) - 2)
    with cols[ci]:
        if cifra.startswith("http"):
            st.link_button("🎸 Cifra", cifra, use_container_width=True)
    with cols[-1]:
        st.link_button(
            "📲 WhatsApp",
            whatsapp_share_url(f"🎵 {titulo}", yt if yt.startswith("http") else cifra),
            use_container_width=True,
        )


def render_playlist_add_search(
    louvores_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    *,
    louvores_pool: pd.DataFrame | None = None,
    premium: bool = False,
):
    """Busca no repertório (mesmo padrão das escalas) e adiciona à playlist ao tocar ➕."""
    pool = louvores_pool if louvores_pool is not None else louvores_df
    if not premium:
        st.markdown("**🔍 Buscar no repertório**")
    if pool.empty:
        st.warning("Repertório ainda não carregado neste ambiente.")
        return

    key_prefix = "pl_add"
    qkey = f"{key_prefix}_lq"
    active_key = f"{key_prefix}_lq_active"
    if active_key not in st.session_state:
        st.session_state[active_key] = ""

    def commit_query():
        st.session_state[active_key] = str(st.session_state.get(qkey, "")).strip()

    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        input_kwargs = {
            "label": "Buscar louvor",
            "key": qkey,
            "placeholder": "Nome do louvor ou artista...",
            "label_visibility": "collapsed",
            "on_change": commit_query,
        }
        if _TEXT_INPUT_HAS_BIND:
            input_kwargs["bind"] = "query-params"
        st.text_input(**input_kwargs)
    with col_btn:
        if not premium:
            st.write("")
        btn_key = "ig_pl_buscar" if premium else f"{key_prefix}_go"
        if st.button("Buscar", key=btn_key, use_container_width=True):
            commit_query()

    query = str(st.session_state.get(active_key, "")).strip()
    if len(query) < 1:
        if not premium:
            st.info("Digite e busque para adicionar músicas à sua playlist.")
        return

    filtered = filter_louvores_for_picker(pool, query)
    catalog = louvores_catalog_options(filtered)
    opcoes = list(catalog.keys())[:15]
    if not opcoes:
        st.warning("Nenhum louvor encontrado.")
        return

    st.caption(f"**{len(catalog)}** encontrado(s) — toque em ➕ para incluir na sua playlist")
    for label in opcoes:
        data = catalog.get(label, {})
        from catalog_sanitize import sanitize_catalog_text

        titulo = sanitize_catalog_text(data.get("title", label.split(" — ")[0]))
        btn = f"➕ {titulo}"
        artista = sanitize_catalog_text(data.get("artist", ""))
        if artista:
            btn += f" — {artista}"
        if st.button(btn, key=f"{key_prefix}_pick_{_picker_key_slug(label)}", use_container_width=True):
            add_louvor_to_playlist(playlist_df, data)
            st.toast(f"Adicionado à playlist: {titulo}", icon="🎧")
            st.rerun()


def show_playlist_page(louvores_df: pd.DataFrame, playlist_df: pd.DataFrame, members_df: pd.DataFrame):
    from playlist_ui import (
        build_playlist_table_html,
        compute_playlist_stats,
        get_favorite_ids,
        render_add_music_card_close,
        render_add_music_card_open,
        render_playlist_banner,
        render_playlist_header,
        render_playlist_kpis,
        render_playlist_nova_button,
        render_playlist_page_close,
        render_playlist_page_open,
        render_playlist_sidebar,
        render_search_hint,
        render_sticky_player,
        render_tracks_empty_state,
        render_tracks_section_close,
        render_tracks_section_open,
        toggle_favorite,
    )

    my_email = st.session_state.user_email.strip().lower()
    playlist_df = prepare_playlist(playlist_df)
    mine = playlist_for_user(playlist_df, my_email)
    fav_ids = get_favorite_ids()
    if mine.empty:
        fav_ids = set()
    else:
        mine_ids = set(mine["id"].astype(str))
        fav_ids = fav_ids & mine_ids
        st.session_state["pl_favorite_ids"] = fav_ids

    from mobile_ui import mobile_hdr_close, mobile_hdr_open

    render_playlist_page_open()
    mobile_hdr_open()
    col_hdr, col_btn = st.columns([4, 1])
    with col_hdr:
        render_playlist_header()
    with col_btn:
        st.markdown('<div style="padding-top:0.5rem">', unsafe_allow_html=True)
        render_playlist_nova_button()
        st.markdown("</div>", unsafe_allow_html=True)
    mobile_hdr_close()

    render_playlist_banner()
    render_voice_kit_link()

    stats = compute_playlist_stats(mine, louvores_df, fav_ids)
    render_playlist_kpis(stats)

    if st.session_state.get("pl_nova_open"):
        with st.expander("Nova playlist", expanded=True):
            nome = st.text_input("Nome da playlist", placeholder="Ex.: Treino Domingo")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Criar", type="primary", use_container_width=True):
                    if nome.strip():
                        st.success(f'Playlist "{nome.strip()}" registrada para organização.')
                    st.session_state.pop("pl_nova_open", None)
                    st.rerun()
            with c2:
                if st.button("Fechar", use_container_width=True):
                    st.session_state.pop("pl_nova_open", None)
                    st.rerun()

    from mobile_ui import mobile_stack_close, mobile_stack_open

    mobile_stack_open()
    col_main, col_side = st.columns([3, 1])
    with col_main:
        render_add_music_card_open()
        pool = louvores_df.copy()
        if not pool.empty:
            f1, f2, f3, f4, f5 = st.columns(5)
            with f1:
                tema_f = st.multiselect(
                    "Tema", list(LOUVOR_THEMES), key="pl_f_tema", placeholder="Tema"
                )
            with f2:
                toms = sorted(
                    {
                        str(t).strip()
                        for t in pool["key"].dropna().astype(str)
                        if str(t).strip()
                    }
                )
                tom_f = st.selectbox("Tom", ["Todos"] + toms, key="pl_f_tom")
            with f3:
                ritmos = sorted(
                    {
                        str(r).strip()
                        for r in pool["ritmo"].dropna().astype(str)
                        if str(r).strip()
                    }
                )
                ritmo_f = st.selectbox("Ritmo", ["Todos"] + ritmos, key="pl_f_ritmo")
            with f4:
                minist_f = st.multiselect(
                    "Ministração",
                    list(LOUVOR_THEMES)[:10],
                    key="pl_f_minist",
                    placeholder="Ministração",
                )
            with f5:
                tag_f = st.multiselect(
                    "Tag bíblica",
                    list(LOUVOR_THEMES),
                    key="pl_f_tag",
                    placeholder="Tag bíblica",
                )
            fc1, fc2 = st.columns([4, 1])
            with fc2:
                if st.button("Limpar filtros", key="ig_pl_clear_filters", use_container_width=True):
                    for k in ("pl_f_tema", "pl_f_tom", "pl_f_ritmo", "pl_f_minist", "pl_f_tag"):
                        st.session_state.pop(k, None)
                    st.rerun()

            def _match_themes(row, tags: list[str]) -> bool:
                if not tags:
                    return True
                ts = themes_from_csv(str(row.get("temas", "")))
                return any(t in ts for t in tags)

            if tema_f:
                pool = pool[pool.apply(lambda r: _match_themes(r, tema_f), axis=1)]
            if tag_f:
                pool = pool[pool.apply(lambda r: _match_themes(r, tag_f), axis=1)]
            if minist_f:
                pool = pool[pool.apply(lambda r: _match_themes(r, minist_f), axis=1)]
            if tom_f != "Todos":
                pool = pool[pool["key"].astype(str) == tom_f]
            if ritmo_f != "Todos":
                pool = pool[pool["ritmo"].astype(str) == ritmo_f]

        render_playlist_add_search(
            louvores_df, playlist_df, louvores_pool=pool, premium=True
        )
        render_search_hint()
        render_add_music_card_close()

        render_tracks_section_open()
        if mine.empty:
            render_tracks_empty_state()
        else:
            mine = mine.copy()
            mine["_sort"] = pd.to_datetime(mine["added_at"], errors="coerce")
            mine = mine.sort_values("_sort", ascending=False)
            page_size = 10
            state_key = "page_my_playlist"
            total_pages = max(1, (len(mine) + page_size - 1) // page_size)
            page = min(st.session_state.get(state_key, 1), total_pages)
            st.session_state[state_key] = page
            start = (page - 1) * page_size
            page_mine = mine.iloc[start : start + page_size]
            st.markdown(build_playlist_table_html(page_mine), unsafe_allow_html=True)

            for _, track in page_mine.iterrows():
                tid = str(track["id"])
                c_rm, c_fav, c_links = st.columns([1, 1, 4])
                with c_fav:
                    is_fav = tid in get_favorite_ids()
                    label = "★ Favorita" if is_fav else "☆ Favoritar"
                    if st.button(label, key=f"pl_fav_{tid}", use_container_width=True):
                        toggle_favorite(tid)
                        st.rerun()
                with c_rm:
                    if st.button("🗑", key=f"pl_rm_{tid}", help="Remover"):
                        updated = playlist_df[
                            playlist_df["id"].astype(str) != tid
                        ]
                        save_data(updated, PLAYLIST_FILE)
                        st.rerun()
                with c_links:
                    render_playlist_track_links(track, members_df)

            c_prev, c_next = st.columns(2)
            with c_prev:
                if st.button(
                    "⏮ Anterior",
                    key="pl_pg_prev",
                    disabled=page <= 1,
                    use_container_width=True,
                ):
                    st.session_state[state_key] = page - 1
                    st.rerun()
            with c_next:
                if st.button(
                    "Próxima ⏭",
                    key="pl_pg_next",
                    disabled=page >= total_pages,
                    use_container_width=True,
                ):
                    st.session_state[state_key] = page + 1
                    st.rerun()
            st.caption(f"Página **{page}** de **{total_pages}** · **{len(mine)}** faixa(s)")

        render_tracks_section_close()

    with col_side:
        render_playlist_sidebar(mine)
    mobile_stack_close()

    first_track = None
    if not mine.empty:
        _sorted = mine.copy()
        _sorted["_s"] = pd.to_datetime(_sorted["added_at"], errors="coerce")
        first_track = _sorted.sort_values("_s", ascending=False).iloc[0]
    render_sticky_player(first_track)
    render_playlist_page_close()


def render_events_feed(eventos_df: pd.DataFrame, limit: int = 5):
    if eventos_df.empty:
        return
    render_dashboard_section_start(
        "Próximos eventos",
        "📅",
        MENU_ACCENTS.get("Eventos", "#38bdf8"),
    )
    df = eventos_df.copy()
    df["_d"] = pd.to_datetime(df["event_date"], errors="coerce")
    df = df.sort_values("_d").head(limit)
    for _, ev in df.iterrows():
        try:
            d = pd.to_datetime(ev["event_date"]).strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            d = str(ev.get("event_date", ""))
        titulo = event_plain_text(ev.get("title", "Evento"), max_len=120)
        desc = event_plain_text(ev.get("description", ""), max_len=280)
        img = str(ev.get("image_url", "")).strip()

        st.markdown(
            f'<div class="event-feed-card">'
            f"<h4>{html.escape(titulo)}</h4>"
            f'<p class="ev-date">📅 {html.escape(d)}</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
        if img.startswith("http"):
            try:
                st.image(img, use_container_width=True)
            except Exception:
                pass
        if desc:
            st.caption(desc)
    render_dashboard_section_end()


def show_dashboard(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
    eventos_df: pd.DataFrame,
    feed_posts_df: pd.DataFrame | None = None,
):
    from dashboard_ui import (
        inject_dashboard_ambient,
        render_dashboard_hero,
        render_ministry_tip,
        render_premium_metrics,
        render_quick_access_v3,
        render_right_panel,
        render_warning_card,
        render_week_culto_cards,
    )

    escalas_df, programa_df, equipe_df, trocas_df = get_escalas_bundle()
    feed_posts_df = feed_posts_df if feed_posts_df is not None else pd.DataFrame()

    inject_dashboard_ambient()

    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    nome = (
        str(st.session_state.get("user_full_name", "")).strip()
        or str(st.session_state.user_name)
    )
    is_mgr = is_scale_manager(st.session_state.user_roles)
    start, end = week_bounds(st.session_state.week_offset)
    my_email = st.session_state.user_email.strip().lower()
    minhas = user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)

    from mobile_ui import mobile_stack_open, mobile_stack_close

    mobile_stack_open()
    col_main, col_right = st.columns([2.2, 1], gap="large")

    with col_main:
        render_dashboard_hero(user_name=nome, group_name=GROUP_NAME)

        n_members = len(members_visible_to_group(members_df))
        render_premium_metrics(
            [
                ("members", "Integrantes", n_members, "Ver todos"),
                ("louvores", "Louvores", len(louvores_df), "Ver repertório"),
                ("escalas", "Escalas", len(escalas_df), "Ver escalas"),
            ]
        )

        if minhas:
            blocos = []
            for item in minhas:
                row = item["escala"]
                ev = str(row.get("event", "Culto"))
                dt = str(row.get("date", ""))
                try:
                    dtf = pd.to_datetime(dt).strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    dtf = dt
                funcao = html.escape(str(item.get("funcao", "")))
                ev_esc = html.escape(ev)
                blocos.append(
                    '<p class="escala-linha">'
                    f'<span class="escala-evento">{ev_esc}</span> '
                    f'<span class="escala-data">({html.escape(dtf)})</span> '
                    f'<span class="escala-funcao">— {funcao}</span>'
                    "</p>"
                    + ensaio_reminder_html(row, is_manager=is_mgr)
                )
            st.markdown(
                '<div class="status-escalado"><p>✅ <strong>Você está escalado(a) esta semana!</strong></p>'
                + "".join(blocos)
                + "</div>",
                unsafe_allow_html=True,
            )
        else:
            render_warning_card(escalado=False)

        items, _, icons = get_menu_items_for_user(st.session_state.user_roles)
        available = {name for name, _, _ in items}
        quick = [
            (n, icons.get(n, "🎵"))
            for n in DASHBOARD_QUICK_LINKS
            if n in available and n != "Dashboard"
        ]
        render_quick_access_v3(quick)

        week_label = f"Semana {start.strftime('%d/%m')} — {end.strftime('%d/%m/%Y')}"
        st.markdown(
            f'<h3 class="ig-section-title">Cultos da semana</h3>'
            f'<p class="ig-week-sub">{html.escape(week_label)}</p>',
            unsafe_allow_html=True,
        )
        from mobile_ui import mobile_row2_close, mobile_row2_open

        mobile_row2_open()
        w1, w2, w3 = st.columns([1, 1, 1])
        with w1:
            if st.button("◀ Semana anterior", key="ig_wk_prev", use_container_width=True):
                st.session_state.week_offset -= 1
                st.rerun()
        with w2:
            if st.button("Próxima semana ▶", key="ig_wk_next", use_container_width=True):
                st.session_state.week_offset += 1
                st.rerun()
        with w3:
            if st.session_state.week_offset != 0 and st.button(
                "Semana atual", key="ig_wk_now", use_container_width=True
            ):
                st.session_state.week_offset = 0
                st.rerun()
        mobile_row2_close()

        semana = escalas_na_semana(escalas_df, start, end)
        minhas_ids = {
            str(item["escala"]["id"])
            for item in user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)
        }
        render_week_culto_cards(
            semana,
            programa_df=programa_df,
            equipe_df=equipe_df,
            members_df=members_df,
            louvores_df=louvores_df,
            my_email=my_email,
            escalas_df=escalas_df,
            equipe_full=equipe_df,
            minhas_ids=minhas_ids,
        )

        render_ministry_tip()

    with col_right:
        render_right_panel(
            escalas_df=escalas_df,
            programa_df=programa_df,
            louvores_df=louvores_df,
            feed_posts_df=feed_posts_df,
            my_email=my_email,
            equipe_df=equipe_df,
        )
    mobile_stack_close()


def show_user_profile(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
):
    members_df = prepare_members(members_df)
    idx, row = get_current_member_row(members_df)
    if row is None:
        show_technical_error("Não foi possível carregar o perfil.")
        return

    st.markdown('<p class="music-panel-title">👤 Meu perfil</p>', unsafe_allow_html=True)
    st.caption("Atualize sua foto e informações cadastrais. O grupo verá suas alterações nas escalas.")
    render_voice_kit_link(str(row.get("roles", "")), bio=str(row.get("bio", "")))

    col_foto, col_dados = st.columns([1, 2])
    email = str(row["email"]).strip().lower()
    stored_photo = str(row.get("profile_photo", ""))
    photo_path = profile_photo_file(email, stored_photo)

    with col_foto:
        st.markdown('<div class="profile-card">', unsafe_allow_html=True)
        if photo_path:
            st.image(str(photo_path), width=160)
        else:
            st.markdown(
                f'<div class="profile-avatar-placeholder">🎤</div>',
                unsafe_allow_html=True,
            )
        uploaded = st.file_uploader(
            "Enviar foto (JPG, PNG ou WebP)",
            type=["jpg", "jpeg", "png", "webp"],
            key="profile_photo_upload",
        )
        if uploaded is not None:
            st.session_state["_pending_profile_photo"] = {
                "name": uploaded.name or "photo.jpg",
                "bytes": uploaded.getvalue(),
            }
        if st.button("💾 Salvar foto", use_container_width=True, key="save_profile_photo"):
            pending = st.session_state.pop("_pending_profile_photo", None)
            if pending is None and uploaded is not None:
                pending = {
                    "name": uploaded.name or "photo.jpg",
                    "bytes": uploaded.getvalue(),
                }
            if pending is None:
                st.warning("Escolha uma imagem antes de salvar.")
            else:
                try:
                    filename = save_profile_photo(email, pending)
                    members_df.at[idx, "profile_photo"] = str(filename).strip()
                    if save_data(members_df, MEMBERS_FILE):
                        st.session_state.user_profile_photo = filename
                        st.success("Foto atualizada!")
                        st.rerun()
                    else:
                        st.session_state["_pending_profile_photo"] = pending
                except ValueError as exc:
                    show_form_error(str(exc))
                    st.session_state["_pending_profile_photo"] = pending
                except Exception as exc:
                    show_exception_error(
                        exc,
                        context="Salvar foto do perfil",
                        user_hint="Não foi possível salvar a foto. Tente outra imagem (JPG ou PNG).",
                    )
                    st.session_state["_pending_profile_photo"] = pending
        if photo_path and st.button("🗑️ Remover foto", use_container_width=True, key="rm_profile_photo"):
            old_name = str(members_df.at[idx, "profile_photo"]).strip()
            photo_path.unlink(missing_ok=True)
            members_df.at[idx, "profile_photo"] = ""
            if save_data(members_df, MEMBERS_FILE):
                try:
                    from remote_store import delete_profile_photo_remote

                    if old_name:
                        delete_profile_photo_remote(old_name)
                except Exception:
                    pass
                st.session_state.user_profile_photo = ""
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_dados:
        leadership, musician = split_member_roles(row.get("roles", ""))
        with st.form(key="profile_data_form"):
            first_name = st.text_input("Nome", value=str(row.get("first_name", "")))
            last_name = st.text_input("Sobrenome", value=str(row.get("last_name", "")))
            st.text_input("Email", value=email, disabled=True)
            phone = st.text_input("Telefone / WhatsApp", value=str(row.get("phone", "")))
            bio = st.text_area(
                "Sobre você (opcional)",
                value=str(row.get("bio", "")),
                height=90,
                placeholder="Ex.: ministro há 3 anos, vocal tenor...",
            )
            if leadership:
                st.caption("Funções de liderança: " + ", ".join(leadership))
            role_label = (
                "Função(ões) no ministério (opcional para líderes)"
                if leadership
                else "Função(ões) no ministério"
            )
            new_musician = st.multiselect(
                role_label,
                MUSICIAN_ROLES,
                default=[r for r in musician if r in MUSICIAN_ROLES],
            )
            salvar = st.form_submit_button(
                "💾 Salvar informações", type="primary", use_container_width=True
            )

        if salvar:
            if not first_name.strip() or not last_name.strip():
                show_form_error("Nome e sobrenome são obrigatórios.")
            elif not leadership and not new_musician:
                show_form_error("Selecione pelo menos uma função (música ou técnico de som).")
            else:
                fn = first_name.strip().title()
                ln = last_name.strip().title()
                members_df.at[idx, "first_name"] = fn
                members_df.at[idx, "last_name"] = ln
                members_df.at[idx, "phone"] = phone.strip()
                members_df.at[idx, "bio"] = bio.strip()
                members_df.at[idx, "roles"] = merge_member_roles(leadership, new_musician)
                save_data(members_df, MEMBERS_FILE)

                full_name = f"{fn} {ln}".strip()
                escalas_df, equipe_df = sync_member_name_in_records(
                    email, full_name, escalas_df, equipe_df
                )
                save_data(escalas_df, ESCALAS_FILE)
                save_data(equipe_df, EQUIPE_FILE)

                updated = members_df.loc[idx]
                set_user_session(updated)
                st.success("Perfil atualizado!")
                st.rerun()

    st.markdown("---")
    st.subheader("🔒 Alterar senha")
    with st.form(key="profile_password_form"):
        senha_atual = st.text_input("Senha atual", type="password")
        senha_nova = st.text_input("Nova senha", type="password")
        senha_conf = st.text_input("Confirmar nova senha", type="password")
        trocar = st.form_submit_button("Atualizar senha", use_container_width=True)

    if trocar:
        if not senha_atual or not senha_nova:
            show_form_error("Preencha a senha atual e a nova senha.")
        elif len(senha_nova) < 6:
            show_form_error("A nova senha deve ter pelo menos 6 caracteres.")
        elif senha_nova != senha_conf:
            show_form_error("A confirmação não coincide com a nova senha.")
        elif hash_password(senha_atual) != str(row.get("password_hash", "")):
            show_form_error("Senha atual incorreta.")
        else:
            members_df.at[idx, "password_hash"] = hash_password(senha_nova)
            save_data(members_df, MEMBERS_FILE)
            st.success("Senha alterada com sucesso!")


def normalize_member_email(raw) -> str:
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    text = str(raw).strip().lower()
    if text in ("", "nan", "none"):
        return ""
    return text


def is_technical_dev_account(row) -> bool:
    """Conta só de manutenção — oculta em listas públicas do ministério."""
    email = normalize_member_email(row.get("email"))
    if email in TECHNICAL_DEV_EMAILS:
        return True
    if email and "@" not in email and email in get_developer_emails():
        return True
    fn = normalize_first_name(str(row.get("first_name", "")))
    ln = str(row.get("last_name", "")).strip().lower()
    if fn == "desenvolvedor" and ln == "admin":
        return True
    return False


def members_visible_to_group(members_df: pd.DataFrame) -> pd.DataFrame:
    """Integrantes do louvor (sem conta técnica de desenvolvedor)."""
    if members_df.empty:
        return members_df
    mask = ~members_df.apply(is_technical_dev_account, axis=1)
    return members_df.loc[mask].copy()


def reload_members_df() -> pd.DataFrame:
    """Recarrega members.csv do disco (evita lista desatualizada no painel dev)."""
    load_data.clear()
    df = load_data(MEMBERS_FILE, MEMBER_COLUMNS)
    df = sync_recognized_member_roles(df)
    return ensure_developer_access(df)


def build_password_reset_options(
    members_df: pd.DataFrame, *, include_all_accounts: bool
) -> dict[str, str]:
    """Rótulo na lista → referência (e-mail ou row:índice)."""
    options: dict[str, str] = {}
    for idx, row in members_df.iterrows():
        if is_technical_dev_account(row):
            continue
        em = normalize_member_email(row.get("email"))
        if not em and not include_all_accounts:
            continue
        name = member_display_name(row) or f"Integrante {idx}"
        if em:
            label = f"{name} ({em})"
            ref = em
        else:
            label = f"{name} (sem e-mail)"
            ref = f"row:{idx}"
        if label in options:
            label = f"{label} · #{idx}"
        options[label] = ref
    return options


def admin_set_member_password(
    members_df: pd.DataFrame, member_ref: str, new_password: str
) -> tuple[bool, str]:
    """Líder/organizador/desenvolvedor redefine senha sem e-mail."""
    if len(new_password) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."

    if str(member_ref).startswith("row:"):
        try:
            idx = int(str(member_ref).split(":", 1)[1])
        except (ValueError, IndexError):
            return False, "Referência de integrante inválida."
        if idx not in members_df.index:
            return False, "Integrante não encontrado."
        members_df.at[idx, "password_hash"] = hash_password(new_password)
        return True, ""

    email = str(member_ref).strip().lower()
    emails = members_df["email"].apply(normalize_member_email)
    idx_list = members_df.index[emails == email].tolist()
    if not idx_list:
        return False, "Integrante não encontrado."
    members_df.at[idx_list[0], "password_hash"] = hash_password(new_password)
    return True, ""


def render_password_reset_panel(
    members_df: pd.DataFrame, *, form_key_prefix: str = "admin"
):
    """Formulário de redefinição (líder ou desenvolvedor)."""
    show_all = is_current_developer()
    if show_all:
        members_df = reload_members_df()

    st.caption(
        "Escolha o integrante, defina uma senha nova e avise a pessoa. "
        "Não precisa configurar e-mail."
    )
    if show_all:
        n_vis = len(members_visible_to_group(members_df))
        st.caption(
            f"Modo desenvolvedor: **{n_vis}** integrante(s) do ministério "
            "(conta técnica de manutenção não aparece nas listas)."
        )

    if members_df.empty:
        st.info("Nenhum membro cadastrado.")
        return

    options = build_password_reset_options(
        members_df, include_all_accounts=show_all
    )

    if not options:
        st.warning("Nenhum integrante cadastrado.")
        return

    labels = sorted(options.keys(), key=str.casefold)
    if show_all and len(labels) > 6:
        busca = st.text_input(
            "Buscar por nome ou e-mail",
            key=f"{form_key_prefix}_pw_search",
            placeholder="Ex.: will ou @gmail.com",
        )
        if busca.strip():
            q = busca.strip().lower()
            labels = [lb for lb in labels if q in lb.lower()]

    with st.form(key=f"{form_key_prefix}_reset_password_form"):
        chosen = st.selectbox("Integrante", labels)
        nova = st.text_input("Nova senha", type="password")
        conf = st.text_input("Confirmar nova senha", type="password")
        submit = st.form_submit_button(
            "Salvar nova senha", type="primary", use_container_width=True
        )

    if submit:
        if nova != conf:
            show_form_error("As senhas não coincidem.")
        else:
            ok, err = admin_set_member_password(members_df, options[chosen], nova)
            if ok:
                save_data(members_df, MEMBERS_FILE)
                st.success(
                    f"Senha atualizada para **{chosen.split(' (')[0]}**. "
                    "Avise a pessoa para entrar com a nova senha."
                )
            else:
                show_form_error(str(err))


def render_admin_password_reset(members_df: pd.DataFrame):
    """Redefinição simples feita pelo líder ou desenvolvedor — sem SMTP."""
    with st.expander("🔑 Redefinir senha de integrante", expanded=False):
        render_password_reset_panel(members_df, form_key_prefix="admin")


ESCALA_MES_AVISO_KEY = "_escala_mes_aviso_pending"


@st.dialog("⚠️ Integrante já escalado no mês")
def _escala_mes_aviso_dialog():
    info = st.session_state.get(ESCALA_MES_AVISO_KEY) or {}
    nome = info.get("nome", "Integrante")
    count = int(info.get("count", 0))
    culto_ref = info.get("culto_ref", "")
    detalhes = info.get("detalhes", "")
    st.markdown(
        f"**{html.escape(nome)}** já consta em **{count}** escala(s) no mesmo mês"
        f"{f' (referência: {html.escape(culto_ref)})' if culto_ref else ''}."
    )
    if detalhes:
        st.caption(detalhes)
    st.info("Você pode continuar a montagem — este aviso é apenas para equilibrar as escalas.")
    if st.button("Entendi", type="primary", use_container_width=True):
        st.session_state.pop(ESCALA_MES_AVISO_KEY, None)
        st.rerun()


def maybe_show_escala_mes_aviso():
    if st.session_state.get(ESCALA_MES_AVISO_KEY):
        _escala_mes_aviso_dialog()


def _queue_escala_mes_aviso(
    nome: str,
    email: str,
    culto_date: date,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    exclude_escala_id: str | None = None,
):
    stats = member_escala_stats(
        email,
        escalas_df,
        equipe_df,
        ref=culto_date,
        exclude_escala_id=exclude_escala_id,
    )
    if stats.month_count <= 0:
        return
    linhas = [
        f"• {format_date_br(d)} — {html.escape(ev)}"
        for d, ev in stats.month_cultos[:5]
    ]
    detalhes = "Cultos no mês:\n" + "\n".join(linhas) if linhas else ""
    if len(stats.month_cultos) > 5:
        detalhes += f"\n… e mais {len(stats.month_cultos) - 5}."
    st.session_state[ESCALA_MES_AVISO_KEY] = {
        "nome": nome,
        "count": stats.month_count,
        "culto_ref": culto_date.strftime("%m/%Y"),
        "detalhes": detalhes,
    }


def _check_escala_selection_aviso(
    label: str,
    member_map: dict[str, str],
    culto_date: date,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    exclude_escala_id: str | None = None,
):
    if not label or label not in member_map:
        return
    email = member_map[label]
    nome = label.split(" (")[0] if " (" in label else label
    _queue_escala_mes_aviso(
        nome,
        email,
        culto_date,
        escalas_df,
        equipe_df,
        exclude_escala_id=exclude_escala_id,
    )


def render_members_leader_table(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
):
    """Tabela visual para líderes/organizadores com foto e estatísticas de escala."""
    visible = members_visible_to_group(members_df)
    if visible.empty:
        st.info("Nenhum integrante cadastrado.")
        return

    ref = date.today()
    rows_html = []
    for _, row in visible.sort_values(
        by=["first_name", "last_name"], key=lambda s: s.str.lower()
    ).iterrows():
        email = str(row["email"]).strip().lower()
        nome = html.escape(member_display_name(row))
        funcao = html.escape(roles_for_public_display(str(row.get("roles", ""))))
        foto = member_photo_html(email, members_df, size=44)
        stats = member_escala_stats(email, escalas_df, equipe_df, ref=ref)
        escalado_badge = (
            '<span class="badge-escalado-sim">Sim</span>'
            if stats.escalado_agora
            else '<span class="badge-escalado-nao">Não</span>'
        )
        mes_cls = "stat-pill" if stats.month_count else "stat-pill stat-pill-zero"
        ano_cls = "stat-pill" if stats.year_count else "stat-pill stat-pill-zero"
        ultima = html.escape(format_date_br(stats.last_date))
        rows_html.append(
            "<tr>"
            f'<td class="col-foto">{foto}</td>'
            f'<td class="mem-nome">{nome}</td>'
            f'<td class="mem-funcao">{funcao}</td>'
            f"<td>{escalado_badge}</td>"
            f'<td><span class="{mes_cls}">{stats.month_count}</span></td>'
            f'<td><span class="{ano_cls}">{stats.year_count}</span></td>'
            f"<td>{ultima}</td>"
            "</tr>"
        )

    table = (
        '<div class="members-leader-wrap"><table class="members-leader-table">'
        "<thead><tr>"
        "<th>Foto</th><th>Nome</th><th>Função</th><th>Escalado</th>"
        "<th>Este mês</th><th>Este ano</th><th>Última escala</th>"
        "</tr></thead><tbody>"
        + "".join(rows_html)
        + "</tbody></table></div>"
    )
    st.markdown(table, unsafe_allow_html=True)
    st.caption(
        "Escalado = culto futuro ou de hoje. Contagens consideram ministro e equipe. "
        "Use os números para distribuir melhor as escalas."
    )


def show_members_overview(
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    escalas_df: pd.DataFrame | None = None,
    equipe_df: pd.DataFrame | None = None,
):
    st.markdown('<p class="music-panel-title">👥 Todos os integrantes</p>', unsafe_allow_html=True)
    if members_df.empty:
        st.info("Nenhum membro cadastrado.")
        return

    if can_reset_member_passwords():
        render_admin_password_reset(members_df)

    leader_view = (
        can_reset_member_passwords()
        and escalas_df is not None
        and equipe_df is not None
    )
    if leader_view:
        render_members_leader_table(members_df, escalas_df, equipe_df)
    else:
        visible = members_visible_to_group(members_df)
        display = visible[["first_name", "last_name", "email", "roles", "created_at"]].copy()
        display["roles"] = display["roles"].apply(roles_for_public_display)
        display.columns = ["Nome", "Sobrenome", "Email", "Funções", "Cadastro"]
        st.dataframe(display, use_container_width=True, hide_index=True)
    st.caption(f"🎶 {len(louvores_df)} louvores disponíveis no repertório para montar o culto.")


def _picker_key_slug(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in str(text).lower())[:50]


def _picked_meta_key(key_prefix: str) -> str:
    return f"{key_prefix}_picked_meta"


def _default_parte_for_index(index: int) -> str:
    if index < len(CULTO_PARTES):
        return CULTO_PARTES[index]
    return f"Louvor {index + 1}"


def _init_picked_meta(key_prefix: str, label: str):
    meta_key = _picked_meta_key(key_prefix)
    if meta_key not in st.session_state:
        st.session_state[meta_key] = {}
    if label not in st.session_state[meta_key]:
        state_key = f"{key_prefix}_picked"
        idx = max(0, len(st.session_state.get(state_key, [])) - 1)
        st.session_state[meta_key][label] = {
            "parte": _default_parte_for_index(idx),
            "parte_outra": "",
        }


def _resolve_parte_from_meta(entry: dict) -> str:
    parte = str(entry.get("parte", CULTO_PARTES[0]))
    if parte == "Outra":
        custom = str(entry.get("parte_outra", "")).strip()
        return custom or "Outra"
    return parte


def get_picked_louvores_for_programa(
    key_prefix: str,
    full_catalog: dict,
    leader_email: str = "",
    leader_name: str = "",
) -> list[dict]:
    """Lista de louvores selecionados com parte do culto de cada um."""
    labels = list(st.session_state.get(f"{key_prefix}_picked", []))
    meta = st.session_state.get(_picked_meta_key(key_prefix), {})
    rows = []
    from catalog_sanitize import sanitize_catalog_text

    for label in labels:
        data = full_catalog.get(label, {})
        titulo = sanitize_catalog_text(data.get("title", label.split(" — ")[0]))
        entry = meta.get(label, {"parte": CULTO_PARTES[0], "parte_outra": ""})
        rows.append(
            {
                "label": label,
                "titulo": titulo,
                "artist": sanitize_catalog_text(data.get("artist", "")),
                "key": sanitize_catalog_text(data.get("key", "")),
                "youtube_url": str(data.get("youtube_url", "")),
                "cifra_url": str(data.get("cifra_url", "")),
                "parte": _resolve_parte_from_meta(entry),
                "leader_email": leader_email,
                "leader_name": leader_name,
            }
        )
    return rows


def _commit_louvor_search_query(key_prefix: str):
    qkey = f"{key_prefix}_lq"
    active_key = f"{key_prefix}_lq_active"
    st.session_state[active_key] = str(st.session_state.get(qkey, "")).strip()


def _louvor_search_panel(
    louvores_df: pd.DataFrame,
    key_prefix: str,
    state_key: str,
    max_results: int = 15,
) -> None:
    """Busca nativa: digita, Buscar/Enter, clica em ➕ para adicionar à seleção."""
    picked = list(st.session_state.get(state_key, []))
    qkey = f"{key_prefix}_lq"
    active_key = f"{key_prefix}_lq_active"
    if active_key not in st.session_state:
        st.session_state[active_key] = ""

    def commit_query():
        _commit_louvor_search_query(key_prefix)

    tema_key = f"{key_prefix}_tema_f"
    tema_sel = st.multiselect(
        "Filtrar por tema",
        list(LOUVOR_THEMES),
        key=tema_key,
        placeholder="Todos os temas",
    )
    if _TEXT_INPUT_HAS_BIND:
        input_kwargs = {
            "label": "Buscar louvor",
            "key": qkey,
            "placeholder": "Nome do louvor ou artista...",
            "label_visibility": "collapsed",
            "on_change": commit_query,
            "bind": "query-params",
        }
        st.text_input(**input_kwargs)
        st.session_state[active_key] = str(st.session_state.get(qkey, "")).strip()
        st.caption("A lista filtra enquanto você digita. Toque em **➕** para selecionar.")
    else:
        col_inp, col_btn = st.columns([6, 1])
        with col_inp:
            st.text_input(
                label="Buscar louvor",
                key=qkey,
                placeholder="Nome do louvor ou artista...",
                label_visibility="collapsed",
                on_change=commit_query,
            )
        with col_btn:
            st.markdown('<div class="louvor-search-btn-wrap">', unsafe_allow_html=True)
            if st.button("Buscar", key=f"{key_prefix}_lq_go", use_container_width=True):
                commit_query()
            st.markdown("</div>", unsafe_allow_html=True)
        st.caption(
            "Digite, pressione **Enter** ou **Buscar**, depois toque em **➕**."
        )

    query = str(st.session_state.get(active_key, "")).strip()
    if len(query) < 1 and not tema_sel:
        st.info("Digite pelo menos 1 letra ou escolha um tema para filtrar.")
        return

    filtered = (
        filter_louvores_for_picker(louvores_df, query)
        if query
        else louvores_df.copy()
    )
    if tema_sel:
        def _row_tema(r):
            ts = themes_from_csv(str(r.get("temas", "")))
            return any(t in ts for t in tema_sel)

        filtered = filtered[filtered.apply(_row_tema, axis=1)]
    catalog = louvores_catalog_options(filtered)
    opcoes = [k for k in catalog.keys() if k not in picked]
    total = len(opcoes)
    opcoes = opcoes[:max_results]

    if not opcoes:
        st.warning("Nenhum louvor encontrado. Tente outras letras.")
        return

    extra = f" (mostrando {len(opcoes)} de {total})" if total > len(opcoes) else ""
    st.caption(f"**{total}** encontrado(s){extra}")

    st.markdown('<div class="louvor-dropdown">', unsafe_allow_html=True)
    for label in opcoes:
        data = catalog.get(label, {})
        from catalog_sanitize import sanitize_catalog_text

        titulo = sanitize_catalog_text(data.get("title", label.split(" — ")[0]))
        artista = sanitize_catalog_text(data.get("artist", ""))
        tom = sanitize_catalog_text(data.get("key", ""))
        btn = f"➕ {titulo}"
        if artista:
            btn += f" — {artista}"
        if tom and tom.lower() not in ("nan", "none", ""):
            btn += f" · Tom {tom}"
        if st.button(
            btn,
            key=f"{key_prefix}_pick_{_picker_key_slug(label)}",
            use_container_width=True,
        ):
            current = list(st.session_state.get(state_key, []))
            if label not in current:
                st.session_state[state_key] = current + [label]
                _init_picked_meta(key_prefix, label)
                st.toast(f"Adicionado: {titulo}", icon="🎵")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_picked_louvores_panel(
    picked: list[str],
    full_catalog: dict,
    key_prefix: str,
    state_key: str,
    *,
    premium: bool = False,
):
    title = f"Selecionados ({len(picked)})" if premium else f"🎵 Selecionados ({len(picked)})"
    st.markdown(
        f'<p class="louvor-selected-title">{title}</p>',
        unsafe_allow_html=True,
    )
    if not picked:
        empty_msg = (
            "Nenhum louvor selecionado ainda. Busque e adicione usando o botão +."
            if premium
            else "Nenhum ainda — busque à esquerda e toque em ➕"
        )
        st.markdown(
            f'<div class="louvor-selected-box"><p style="color:#64748b;margin:0;font-size:0.88rem">'
            f"{empty_msg}</p></div>",
            unsafe_allow_html=True,
        )
        return

    meta_key = _picked_meta_key(key_prefix)
    parte_opts = CULTO_PARTES + ["Outra"]
    st.markdown('<div class="louvor-selected-box">', unsafe_allow_html=True)
    for i, label in enumerate(picked):
        if label not in st.session_state.get(meta_key, {}):
            _init_picked_meta(key_prefix, label)
        entry = st.session_state[meta_key][label]
        data = full_catalog.get(label, {})
        titulo = str(data.get("title", label.split(" — ")[0]))
        artista = str(data.get("artist", ""))
        slug = _picker_key_slug(label)

        cur_parte = str(entry.get("parte", _default_parte_for_index(i)))
        idx_parte = parte_opts.index(cur_parte) if cur_parte in parte_opts else 0
        parte_sel = st.selectbox(
            f"Parte — {titulo}",
            parte_opts,
            index=idx_parte,
            key=f"{key_prefix}_parte_{i}_{slug}",
        )
        entry["parte"] = parte_sel
        if parte_sel == "Outra":
            entry["parte_outra"] = st.text_input(
                "Nome da parte",
                value=str(entry.get("parte_outra", "")),
                key=f"{key_prefix}_parte_out_{i}_{slug}",
            )
        st.session_state[meta_key][label] = entry

        if artista:
            st.caption(artista)

        if st.button("✕ Remover", key=f"{key_prefix}_unpick_{i}_{slug}", use_container_width=True):
            st.session_state[state_key] = [p for p in picked if p != label]
            meta = st.session_state.get(meta_key, {})
            meta.pop(label, None)
            st.session_state[meta_key] = meta
            st.rerun()
        st.markdown("---")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("Limpar todos", key=f"{key_prefix}_clear_all", use_container_width=True):
        st.session_state[state_key] = []
        st.session_state[_picked_meta_key(key_prefix)] = {}
        st.rerun()

def render_louvor_search_picker(
    louvores_df: pd.DataFrame,
    key_prefix: str,
    max_results: int = 15,
    *,
    premium: bool = False,
) -> list[str]:
    """Busca à esquerda + lista de selecionados fixa à direita."""
    state_key = f"{key_prefix}_picked"
    if state_key not in st.session_state:
        st.session_state[state_key] = []

    picked: list[str] = list(st.session_state[state_key])
    full_catalog = louvores_catalog_options(louvores_df)

    col_busca, col_sel = st.columns([3, 2], gap="large")

    with col_busca:
        st.markdown(
            "**Buscar repertório**" if premium else "**🔍 Buscar no repertório**"
        )
        _louvor_search_panel(
            louvores_df, key_prefix, state_key, max_results=max_results
        )

    with col_sel:
        picked = list(st.session_state.get(state_key, []))
        _render_picked_louvores_panel(
            picked, full_catalog, key_prefix, state_key, premium=premium
        )

    return list(st.session_state.get(state_key, []))


def clear_louvor_picker_state(key_prefix: str):
    state_key = f"{key_prefix}_picked"
    if state_key in st.session_state:
        del st.session_state[state_key]
    meta_key = _picked_meta_key(key_prefix)
    if meta_key in st.session_state:
        del st.session_state[meta_key]
    for suffix in ("_lq", "_lq_active"):
        k = f"{key_prefix}{suffix}"
        if k in st.session_state:
            del st.session_state[k]


def show_louvores_picker(louvores_df: pd.DataFrame, key_prefix: str = "pick"):
    st.markdown('<p class="music-panel-title">🎶 Louvores disponíveis</p>', unsafe_allow_html=True)
    if louvores_df.empty:
        st.caption("O repertório ainda não foi carregado neste ambiente.")
        return
    search = st.text_input(
        "🔍 Digite as primeiras letras do louvor ou do artista",
        key=f"{key_prefix}_search",
    )
    filtered = filter_louvores_for_picker(louvores_df, search)
    show = filtered[["title", "artist", "key", "ritmo"]]
    show.columns = ["Louvor", "Artista", "Tom", "Ritmo"]
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.caption(f"{len(filtered)} louvor(es) no repertório (sem limite de exibição).")


def render_equipe_editor(
    escala_id: str,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    key_prefix: str,
):
    st.subheader("👥 Integrantes da escala")
    st.caption("Líderes e organizadores podem adicionar ou remover qualquer integrante.")

    eq = equipe_por_escala(equipe_df, escala_id)
    escala_row = escalas_df[escalas_df["id"].astype(str) == str(escala_id)]
    if not escala_row.empty:
        row0 = escala_row.iloc[0]
        st.markdown(
            f"**{FUNCAO_MINISTRADOR} do culto:** {row0.get('member_name', row0.get('responsible', '—'))}"
        )

    if not eq.empty:
        for _, erow in eq.iterrows():
            c1, c2, c3 = st.columns([4, 3, 1])
            c1.markdown(f"**{erow['member_name']}**")
            c2.caption(normalize_funcao_escala(str(erow.get("funcao", "Integrante"))))
            if c3.button("🗑️", key=f"{key_prefix}_eqdel_{erow['id']}", help="Remover da escala"):
                equipe_df = equipe_df[equipe_df["id"].astype(str) != str(erow["id"])]
                save_data(equipe_df, EQUIPE_FILE)
                st.success("Integrante removido da escala.")
                st.rerun()
    else:
        st.info("Nenhum integrante extra na equipe — use o campo abaixo para adicionar.")

    member_map = members_options_escala(members_df)
    principal_email = ""
    if not escala_row.empty:
        principal_email = str(escala_row.iloc[0].get("member_email", "")).strip().lower()
    in_team = set(eq["member_email"].astype(str).str.lower()) if not eq.empty else set()
    if principal_email:
        in_team.add(principal_email)
    available = [lbl for lbl, em in member_map.items() if em.lower() not in in_team]

    prev_eq_key = f"{key_prefix}_eq_add_prev"
    culto_ref = date.today()
    if not escala_row.empty:
        cd = pd.to_datetime(escala_row.iloc[0].get("date"), errors="coerce")
        if pd.notna(cd):
            culto_ref = cd.date()

    def _on_equipe_add_change():
        prev = set(st.session_state.get(prev_eq_key, []))
        curr = st.session_state.get(f"{key_prefix}_eq_add", [])
        st.session_state[prev_eq_key] = list(curr)
        for label in curr:
            if label not in prev:
                _check_escala_selection_aviso(
                    label,
                    member_map,
                    culto_ref,
                    escalas_df,
                    equipe_df,
                    exclude_escala_id=escala_id,
                )

    if prev_eq_key not in st.session_state:
        st.session_state[prev_eq_key] = list(st.session_state.get(f"{key_prefix}_eq_add", []))

    fmt_eq = lambda lbl: member_escala_select_format(
        lbl, member_map, escalas_df, equipe_df, culto_ref
    )
    novos = st.multiselect(
        "Adicionar integrantes à escala",
        available,
        key=f"{key_prefix}_eq_add",
        placeholder="Selecione um ou vários integrantes",
        on_change=_on_equipe_add_change,
        format_func=fmt_eq,
    )
    funcao_idx = default_funcao_escala_index(members_df, member_map, novos)
    funcao_nova = st.selectbox(
        "Função na escala",
        ESCALA_FUNCOES_EXIBICAO,
        index=funcao_idx,
        key=f"{key_prefix}_eq_fun",
        help="Ex.: Técnico de som para quem opera mesa/PA no culto.",
    )
    if st.button("➕ Adicionar à equipe", key=f"{key_prefix}_eq_btn", use_container_width=True):
        if not novos:
            st.warning("Selecione ao menos um integrante.")
        else:
            novas_rows = []
            for label in novos:
                email = member_map[label]
                if email.lower() in in_team:
                    continue
                mrow = members_df[members_df["email"].astype(str).str.lower() == email].iloc[0]
                novas_rows.append(
                    {
                        "id": new_id(),
                        "escala_id": escala_id,
                        "member_email": email,
                        "member_name": member_display_name(mrow),
                        "funcao": funcao_nova,
                    }
                )
            save_data(
                pd.concat([equipe_df, pd.DataFrame(novas_rows)], ignore_index=True),
                EQUIPE_FILE,
            )
            st.success(f"{len(novas_rows)} integrante(s) adicionado(s).")
            st.rerun()


def render_programa_louvores_editor(
    escala_id: str,
    programa_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    key_prefix: str,
):
    st.subheader("🎶 Louvores do culto")
    st.caption(
        "Busque à esquerda, toque em ➕ e defina a **parte do culto** de cada música em **Selecionados**."
    )

    prog = programa_por_escala(programa_df, escala_id)
    parte_opts = CULTO_PARTES + ["Outra"]
    if not prog.empty:
        st.markdown("**Programação atual** — edite a parte de cada louvor:")
        for _, prow in prog.iterrows():
            pid = str(prow["id"])
            titulo = str(prow.get("louvor_title", ""))
            parte_atual = str(prow.get("parte", ""))
            idx_p = parte_opts.index(parte_atual) if parte_atual in parte_opts else 0
            with st.expander(f"{prow.get('ordem', '')}. {parte_atual} — {titulo}", expanded=False):
                parte_sel = st.selectbox(
                    "Parte do culto",
                    parte_opts,
                    index=idx_p,
                    key=f"{key_prefix}_ep_{pid}",
                )
                parte_salvar = parte_sel
                if parte_sel == "Outra":
                    parte_salvar = st.text_input(
                        "Nome da parte",
                        value=parte_atual if parte_atual not in CULTO_PARTES else "",
                        key=f"{key_prefix}_epo_{pid}",
                    )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Salvar parte", key=f"{key_prefix}_savep_{pid}", use_container_width=True):
                        idx_row = programa_df.index[programa_df["id"].astype(str) == pid]
                        if len(idx_row):
                            programa_df.loc[idx_row[0], "parte"] = str(parte_salvar).strip()
                            save_data(programa_df, PROGRAMA_FILE)
                            st.success("Parte atualizada.")
                            st.rerun()
                with c2:
                    if st.button("🗑️ Remover louvor", key=f"{key_prefix}_pdel_{pid}", use_container_width=True):
                        programa_df = programa_df[programa_df["id"].astype(str) != pid]
                        save_data(programa_df, PROGRAMA_FILE)
                        st.success("Louvor removido.")
                        st.rerun()
    else:
        st.info("Nenhum louvor na programação deste culto ainda.")

    render_louvor_search_picker(louvores_df, key_prefix)

    member_map = members_options_escala(members_df)
    leader_opts = ["—"] + list(member_map.keys())
    leader_label = st.selectbox("Quem conduz (padrão nos novos)", leader_opts, key=f"{key_prefix}_lead")

    if st.button(
        "➕ Adicionar louvores selecionados",
        type="primary",
        key=f"{key_prefix}_ladd",
        use_container_width=True,
    ):
        picked_rows = get_picked_louvores_for_programa(key_prefix, louvores_catalog_options(louvores_df))
        if not picked_rows:
            st.warning("Selecione ao menos um louvor e defina a parte em **Selecionados**.")
        else:
            next_order = int(prog["ordem"].max() + 1) if not prog.empty else 1
            leader_email = ""
            leader_name = ""
            if leader_label and leader_label != "—":
                leader_email = member_map.get(leader_label, "")
                leader_name = leader_label.split(" (")[0]
            novas = []
            for i, row in enumerate(picked_rows):
                novas.append(
                    {
                        "id": new_id(),
                        "escala_id": escala_id,
                        "ordem": next_order + i,
                        "parte": row["parte"],
                        "louvor_title": row["titulo"],
                        "artist": row["artist"],
                        "key": row["key"],
                        "youtube_url": row["youtube_url"],
                        "cifra_url": row["cifra_url"],
                        "leader_email": leader_email or row["leader_email"],
                        "leader_name": leader_name or row["leader_name"],
                        "notes": "",
                    }
                )
            save_data(
                pd.concat([programa_df, pd.DataFrame(novas)], ignore_index=True),
                PROGRAMA_FILE,
            )
            programa_df = prepare_programa(load_data(PROGRAMA_FILE, PROGRAMA_COLUMNS))
            hydrate_escala_sequencia_content(escala_id, programa_df, louvores_df)
            st.success(f"{len(novas)} louvor(es) adicionado(s). O dashboard já está atualizado.")
            clear_louvor_picker_state(key_prefix)
            st.rerun()

    total_min = programa_duracao_total(programa_df, escala_id, louvores_df)
    if total_min > 0:
        st.markdown(
            f'<div class="prog-duracao-total">⏱ <b>Duração estimada do louvor:</b> '
            f"{html.escape(format_duracao_total(total_min))}</div>",
            unsafe_allow_html=True,
        )


def show_escala_completa_editor(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    chat_ensaio_df: pd.DataFrame | None = None,
    *,
    external_planner_panel: bool = False,
    premium_layout: bool = False,
):
    maybe_show_escala_mes_aviso()

    if members_df.empty:
        st.warning("Cadastre integrantes antes de montar escalas.")
        return

    member_map = members_options_escala(members_df)
    NOVA_ESCALA = "➕ Nova escala"
    todas = escalas_ordenadas(escalas_df)
    escala_labels = [NOVA_ESCALA] + [escala_label(r) for _, r in todas.iterrows()]
    if premium_layout:
        from gerenciar_escalas_ui import (
            render_gerenciar_culto_section_open,
            render_gerenciar_form_card_close,
            render_gerenciar_nova_escala_outline,
        )

        render_gerenciar_culto_section_open()
        c_sel, c_nova = st.columns([3, 1])
        with c_sel:
            escolha = st.selectbox(
                "Selecione o culto ou crie uma nova escala",
                escala_labels,
                key="editor_escala_sel",
                label_visibility="collapsed",
            )
        with c_nova:
            render_gerenciar_nova_escala_outline()
        render_gerenciar_form_card_close()
    else:
        st.markdown(
            '<div class="section-heading">'
            '<span class="section-heading-icon">📅</span>'
            "<h3>Culto / escala</h3></div>",
            unsafe_allow_html=True,
        )
        escolha = st.selectbox(
            "Selecione o culto ou crie uma nova escala",
            escala_labels,
            key="editor_escala_sel",
            label_visibility="collapsed",
        )
    is_nova = escolha == NOVA_ESCALA

    if is_nova:
        col_nova = st.container()
        col_painel = None
        if not external_planner_panel:
            col_nova, col_painel = st.columns([2, 1])

        def _on_nova_resp_change():
            cd = st.session_state.get("nova_esc_data", date.today())
            _check_escala_selection_aviso(
                st.session_state.get("nova_esc_resp", ""),
                member_map,
                cd,
                escalas_df,
                equipe_df,
            )

        def _on_nova_equipe_change():
            prev_key = "_nova_esc_equipe_prev"
            prev = set(st.session_state.get(prev_key, []))
            curr = st.session_state.get("nova_esc_equipe", [])
            st.session_state[prev_key] = list(curr)
            cd = st.session_state.get("nova_esc_data", date.today())
            for label in curr:
                if label not in prev:
                    _check_escala_selection_aviso(
                        label, member_map, cd, escalas_df, equipe_df
                    )

        if "_nova_esc_equipe_prev" not in st.session_state:
            st.session_state["_nova_esc_equipe_prev"] = list(
                st.session_state.get("nova_esc_equipe", [])
            )

        with col_nova:
            if premium_layout:
                from gerenciar_escalas_ui import (
                    render_gerenciar_form_card_close,
                    render_gerenciar_form_card_open,
                    render_gerenciar_louvores_section_header,
                    render_gerenciar_louvores_tip,
                )

                render_gerenciar_form_card_open("Novo Culto")
                r1c1, r1c2, r1c3 = st.columns(3)
                with r1c1:
                    culto_date = st.date_input("Data do culto", key="nova_esc_data")
                with r1c2:
                    culto_event = st.text_input("Evento / Culto", key="nova_esc_event")
                with r1c3:
                    data_ensaio = st.date_input("Data do ensaio", key="nova_esc_ensaio")
            else:
                st.markdown(
                    '<div class="section-heading">'
                    '<span class="section-heading-icon">📅</span>'
                    "<h3>Novo culto</h3></div>",
                    unsafe_allow_html=True,
                )
                culto_date = st.date_input("Data do culto", key="nova_esc_data")
                culto_event = st.text_input("Evento / Culto", key="nova_esc_event")
                data_ensaio = st.date_input("Data do ensaio", key="nova_esc_ensaio")

            culto_ref = st.session_state.get("nova_esc_data", date.today())
            fmt_nova = lambda lbl: member_escala_select_format(
                lbl, member_map, escalas_df, equipe_df, culto_ref
            )
            if premium_layout:
                r2c1, r2c2 = st.columns(2)
                with r2c1:
                    responsavel = st.selectbox(
                        "Ministrador principal",
                        list(member_map.keys()),
                        key="nova_esc_resp",
                        on_change=_on_nova_resp_change,
                        format_func=fmt_nova,
                    )
                with r2c2:
                    equipe_labels = st.multiselect(
                        "Demais integrantes",
                        [l for l in member_map.keys() if l != responsavel],
                        key="nova_esc_equipe",
                        on_change=_on_nova_equipe_change,
                        format_func=fmt_nova,
                    )
                notas = st.text_area(
                    "Notas",
                    key="nova_esc_notas",
                    placeholder=(
                        "Adicione observações sobre o culto, repertório e avisos."
                    ),
                )
                render_gerenciar_form_card_close()
                render_gerenciar_louvores_section_header()
            else:
                responsavel = st.selectbox(
                    f"{FUNCAO_MINISTRADOR} (todos os integrantes)",
                    list(member_map.keys()),
                    key="nova_esc_resp",
                    on_change=_on_nova_resp_change,
                    format_func=fmt_nova,
                )
                equipe_labels = st.multiselect(
                    "Demais integrantes da escala",
                    [l for l in member_map.keys() if l != responsavel],
                    key="nova_esc_equipe",
                    on_change=_on_nova_equipe_change,
                    format_func=fmt_nova,
                )
                notas = st.text_area("Notas", key="nova_esc_notas")
                st.markdown("---")
                st.markdown(
                    '<div class="section-heading">'
                    '<span class="section-heading-icon">🎵</span>'
                    "<h3>Louvores do culto</h3></div>",
                    unsafe_allow_html=True,
                )
                st.caption(
                    "Em **Selecionados**, escolha a ordem dos louvores e a **parte do culto** de cada música."
                )

            render_louvor_search_picker(
                louvores_df, "nova_esc", premium=premium_layout
            )
            if premium_layout:
                render_gerenciar_louvores_tip()
                render_gerenciar_form_card_close()

            save_label = "Salvar Escala Completa" if premium_layout else "💾 Salvar escala completa"
            if st.button(
                save_label,
                type="primary",
                use_container_width=True,
                key="nova_esc_save",
            ):
                if not culto_event.strip():
                    show_form_error("Informe o nome do culto/evento.")
                else:
                    email = member_map[responsavel]
                    row = members_df[
                        members_df["email"].astype(str).str.lower() == email
                    ].iloc[0]
                    name = member_display_name(row)
                    escala_id = new_id()
                    new_escala = {
                        "id": escala_id,
                        "date": culto_date.strftime("%Y-%m-%d"),
                        "event": culto_event.strip(),
                        "responsible": name,
                        "member_email": email,
                        "member_name": name,
                        "notes": notas.strip(),
                        "rehearsal_date": data_ensaio.strftime("%Y-%m-%d"),
                    }
                    escalas_df = pd.concat(
                        [escalas_df, pd.DataFrame([new_escala])], ignore_index=True
                    )
                    save_data(escalas_df, ESCALAS_FILE)

                    novas_eq = []
                    for label in equipe_labels:
                        em = member_map[label]
                        mrow = members_df[
                            members_df["email"].astype(str).str.lower() == em
                        ].iloc[0]
                        funcao = default_funcao_para_escala(mrow)
                        novas_eq.append(
                            {
                                "id": new_id(),
                                "escala_id": escala_id,
                                "member_email": em,
                                "member_name": member_display_name(mrow),
                                "funcao": funcao,
                            }
                        )
                    if novas_eq:
                        equipe_df = pd.concat(
                            [equipe_df, pd.DataFrame(novas_eq)], ignore_index=True
                        )
                        save_data(equipe_df, EQUIPE_FILE)

                    picked_rows = get_picked_louvores_for_programa(
                        "nova_esc", louvores_catalog_options(louvores_df), email, name
                    )
                    if picked_rows:
                        novas_prog = []
                        for i, row in enumerate(picked_rows):
                            novas_prog.append(
                                {
                                    "id": new_id(),
                                    "escala_id": escala_id,
                                    "ordem": i + 1,
                                    "parte": row["parte"],
                                    "louvor_title": row["titulo"],
                                    "artist": row["artist"],
                                    "key": row["key"],
                                    "youtube_url": row["youtube_url"],
                                    "cifra_url": row["cifra_url"],
                                    "leader_email": email,
                                    "leader_name": name,
                                    "notes": "",
                                }
                            )
                        save_data(
                            pd.concat(
                                [programa_df, pd.DataFrame(novas_prog)], ignore_index=True
                            ),
                            PROGRAMA_FILE,
                        )
                        programa_df = prepare_programa(
                            load_data(PROGRAMA_FILE, PROGRAMA_COLUMNS)
                        )
                        hydrate_escala_sequencia_content(
                            escala_id, programa_df, louvores_df
                        )

                    try:
                        queue_whatsapp_after_escala_save(
                            new_escala,
                            programa_df,
                            equipe_df,
                            members_df,
                            louvores_df,
                        )
                    except Exception:
                        pass
                    try:
                        schedule_feed_posts_for_escala(
                            escala_id,
                            new_escala,
                            equipe_df,
                            members_df,
                            programa_df,
                            louvores_df,
                        )
                    except Exception:
                        pass
                    st.success(
                        "Escala salva! Quem estiver no Dashboard ou em Escalas vê a atualização "
                        "em poucos segundos, sem precisar sair do app."
                    )
                    clear_louvor_picker_state("nova_esc")
                    st.rerun()

        if col_painel is not None:
            with col_painel:
                st.markdown('<div class="planner-column-wrap">', unsafe_allow_html=True)
                render_escala_planner_panel(
                    members_df,
                    escalas_df,
                    equipe_df,
                    st.session_state.get("nova_esc_data", date.today()),
                )
                st.markdown("</div>", unsafe_allow_html=True)
        return

    escala_id = None
    for _, r in todas.iterrows():
        if escala_label(r) == escolha:
            escala_id = str(r["id"])
            break
    if not escala_id:
        show_technical_error("Escala não encontrada.")
        return

    escala_row = escalas_df[escalas_df["id"].astype(str) == escala_id].iloc[0]
    culto_ref_edit = date.today()
    cd_edit = pd.to_datetime(escala_row.get("date"), errors="coerce")
    if pd.notna(cd_edit):
        culto_ref_edit = cd_edit.date()

    col_main_hdr = st.container()
    col_painel_edit = None
    if not external_planner_panel:
        col_main_hdr, col_painel_edit = st.columns([2, 1])
        with col_painel_edit:
            st.markdown('<div class="planner-column-wrap">', unsafe_allow_html=True)
            render_escala_planner_panel(
                members_df, escalas_df, equipe_df, culto_ref_edit
            )
            st.markdown("</div>", unsafe_allow_html=True)
    with col_main_hdr:
        st.markdown(
            '<div class="section-heading">'
            '<span class="section-heading-icon">✏️</span>'
            "<h3>Editar escala</h3></div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Líderes e organizadores podem alterar dados, equipe, louvores ou **excluir** esta escala."
        )

    confirm_key = f"confirm_del_esc_{escala_id}"
    if st.session_state.get(confirm_key):
        show_form_error("Confirma a exclusão permanente desta escala (equipe e louvores)?")
        c_del1, c_del2 = st.columns(2)
        with c_del1:
            if st.button("✅ Sim, excluir escala", type="primary", use_container_width=True):
                delete_escala_completa(escala_id, escalas_df, programa_df, equipe_df)
                st.session_state.pop(confirm_key, None)
                st.success("Escala excluída.")
                st.rerun()
        with c_del2:
            if st.button("Cancelar exclusão", use_container_width=True):
                st.session_state.pop(confirm_key, None)
                st.rerun()
    else:
        if st.button("🗑️ Excluir esta escala", use_container_width=True):
            st.session_state[confirm_key] = True
            st.rerun()

    st.markdown("#### 📋 Dados do culto")
    with st.form(key=f"meta_escala_{escala_id}"):
        dt_esc = pd.to_datetime(escala_row["date"], errors="coerce")
        nova_data = st.date_input(
            "Data",
            value=dt_esc.date() if pd.notna(dt_esc) else date.today(),
        )
        novo_evento = st.text_input("Evento / Culto", value=str(escala_row.get("event", "")))
        labels_resp = list(member_map.keys())
        resp_atual = str(escala_row.get("member_name", ""))
        idx_resp = next(
            (i for i, l in enumerate(labels_resp) if l.startswith(resp_atual)), 0
        )
        fmt_edit = lambda lbl: member_escala_select_format(
            lbl, member_map, escalas_df, equipe_df, culto_ref_edit
        )
        novo_resp = st.selectbox(
            f"{FUNCAO_MINISTRADOR} (todos os integrantes)",
            labels_resp,
            index=idx_resp,
            format_func=fmt_edit,
        )
        dt_ensaio = pd.to_datetime(escala_row.get("rehearsal_date", ""), errors="coerce")
        nova_data_ensaio = st.date_input(
            "Data do ensaio",
            value=dt_ensaio.date() if pd.notna(dt_ensaio) else date.today(),
        )
        novas_notas = st.text_area("Notas", value=str(escala_row.get("notes", "")))
        salvar_meta = st.form_submit_button("💾 Salvar dados do culto", use_container_width=True)

    if salvar_meta:
        _check_escala_selection_aviso(
            novo_resp,
            member_map,
            nova_data,
            escalas_df,
            equipe_df,
            exclude_escala_id=escala_id,
        )
        email = member_map[novo_resp]
        mrow = members_df[members_df["email"].astype(str).str.lower() == email].iloc[0]
        name = member_display_name(mrow)
        idx = escalas_df.index[escalas_df["id"].astype(str) == escala_id][0]
        escalas_df.loc[idx, "date"] = nova_data.strftime("%Y-%m-%d")
        escalas_df.loc[idx, "event"] = novo_evento.strip()
        escalas_df.loc[idx, "responsible"] = name
        escalas_df.loc[idx, "member_email"] = email
        escalas_df.loc[idx, "member_name"] = name
        escalas_df.loc[idx, "notes"] = novas_notas.strip()
        escalas_df.loc[idx, "rehearsal_date"] = nova_data_ensaio.strftime("%Y-%m-%d")
        save_data(escalas_df, ESCALAS_FILE)
        st.success("Dados do culto atualizados.")
        if st.session_state.get(ESCALA_MES_AVISO_KEY):
            st.rerun()
        st.rerun()

    st.markdown("---")
    render_equipe_editor(escala_id, equipe_df, members_df, escalas_df, f"ed_{escala_id}")

    st.markdown("---")
    if chat_ensaio_df is not None:
        render_ensaio_chat(escala_id, chat_ensaio_df, members_df)

    st.markdown("---")
    render_programa_louvores_editor(
        escala_id, programa_df, louvores_df, members_df, f"ed_{escala_id}"
    )


def list_ensaio_audio_files(escala_id: str) -> list[Path]:
    folder = ENSAIO_AUDIO_DIR / str(escala_id)
    if not folder.is_dir():
        return []
    exts = {".webm", ".ogg", ".mp3", ".m4a", ".wav", ".mp4"}
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts]
    return sorted(files, key=lambda p: p.stat().st_mtime)


def render_ensaio_chat(
    escala_id: str,
    chat_ensaio_df: pd.DataFrame,
    members_df: pd.DataFrame,
):
    st.subheader("💬 Chat do ensaio")
    st.caption(
        "Chat do ensaio · **+** galeria/câmera sob demanda · **segure** o mic para gravar."
    )
    saved = list_ensaio_audio_files(escala_id)
    if saved:
        with st.expander(f"🎧 Áudios de ensaio ({len(saved)})", expanded=False):
            for path in saved:
                st.caption(path.name)
                st.audio(str(path))

    def _append_ensaio(**kwargs):
        fresh = prepare_chat_ensaio(load_data(CHAT_ENSAIO_FILE, CHAT_ENSAIO_COLUMNS))
        base = {
            "timestamp": timestamp_now(),
            "escala_id": escala_id,
            "email": st.session_state.user_email,
            "name": st.session_state.user_full_name or st.session_state.user_name,
        }
        nova = {**base, **kwargs}
        subset_ids = fresh["escala_id"].astype(str) == str(escala_id)
        others = fresh[~subset_ids] if subset_ids.any() else fresh
        escala_rows = fresh[subset_ids] if subset_ids.any() else pd.DataFrame()
        updated = pd.concat(
            [others, escala_rows, pd.DataFrame([nova])], ignore_index=True
        )
        if save_data(updated, CHAT_ENSAIO_FILE):
            mark_chat_scroll_bottom()
            st.rerun()

    pending_key = pending_text_key(f"ensaio_{escala_id}")
    pending = st.session_state.pop(pending_key, None)
    if pending and str(pending).strip():
        _append_ensaio(message=str(pending).strip(), message_type="text", media_file="")
        return

    subset = prepare_chat_ensaio(load_data(CHAT_ENSAIO_FILE, CHAT_ENSAIO_COLUMNS))
    subset = subset[subset["escala_id"].astype(str) == str(escala_id)].copy()

    my_email = st.session_state.user_email.strip().lower()

    def _del_ensaio(ts, em):
        delete_own_ensaio_message(ts, escala_id, em)

    def _upd_ensaio(ts, em, txt):
        update_own_ensaio_message(ts, escala_id, em, txt)

    render_chat_messages(
        subset,
        members_df,
        delete_fn=_del_ensaio,
        update_fn=_upd_ensaio,
        key_prefix=f"ensaio_{escala_id}",
    )

    ensaio_dir = ENSAIO_AUDIO_DIR / str(escala_id)
    ensaio_dir.mkdir(parents=True, exist_ok=True)

    render_chat_composer(
        key_prefix=f"ensaio_{escala_id}",
        append_fn=_append_ensaio,
        audio_dir=ensaio_dir,
        audio_prefix=f"ensaio_{escala_id}",
        images_dir=CHAT_IMAGES_DIR,
        image_prefix=f"ensaio_{escala_id}",
    )


def render_escalas_pdf_export(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame | None = None,
    louvores_df: pd.DataFrame | None = None,
):
    members_df = members_df if members_df is not None else pd.DataFrame()
    """PDF em uma pagina para lideres/organizadores compartilharem no WhatsApp."""
    st.markdown(
        '<p class="music-panel-title">📄 PDF das escalas (WhatsApp)</p>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Selecione o periodo e os cultos. O PDF cabe em **uma folha** (paisagem) "
        "com equipe e programacao de cada escala."
    )

    if escalas_df.empty:
        st.info("Nenhuma escala cadastrada ainda. Monte uma escala na aba ao lado.")
        return

    today = date.today()
    default_end = today + timedelta(days=60)
    c1, c2, c3 = st.columns(3)
    with c1:
        date_start = st.date_input(
            "Data inicial",
            value=today,
            key="pdf_escala_date_start",
        )
    with c2:
        date_end = st.date_input(
            "Data final",
            value=default_end,
            key="pdf_escala_date_end",
        )
    with c3:
        preset = st.selectbox(
            "Atalho de periodo",
            ["Personalizado", "Proximos 7 dias", "Proximos 30 dias", "Este mes"],
            key="pdf_escala_preset",
        )

    if preset == "Proximos 7 dias":
        date_start, date_end = today, today + timedelta(days=7)
    elif preset == "Proximos 30 dias":
        date_start, date_end = today, today + timedelta(days=30)
    elif preset == "Este mes":
        date_start = today.replace(day=1)
        if today.month == 12:
            date_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            date_end = date(today.year, today.month + 1, 1) - timedelta(days=1)

    in_period = filter_escalas_by_period(
        escalas_df,
        date_start=date_start,
        date_end=date_end,
    )
    if in_period.empty:
        st.warning("Nenhuma escala nesse periodo. Ajuste as datas ou cadastre cultos.")
        return

    eventos = sorted(
        {str(e).strip() for e in in_period["event"].astype(str) if str(e).strip()}
    )
    filtro_evento = st.selectbox(
        "Filtrar por evento (opcional)",
        ["Todos os eventos"] + eventos,
        key="pdf_escala_event_filter",
    )
    event_filter = None if filtro_evento == "Todos os eventos" else filtro_evento

    pool = filter_escalas_by_period(
        in_period,
        date_start=None,
        date_end=None,
        event_filter=event_filter,
    )
    ordenadas = escalas_ordenadas(pool)
    if ordenadas.empty:
        st.warning("Nenhuma escala para o evento selecionado.")
        return

    options = {escala_label(r): str(r["id"]) for _, r in ordenadas.iterrows()}
    default_labels = list(options.keys())
    selected_labels = st.multiselect(
        "Escalas incluidas no PDF",
        options=list(options.keys()),
        default=default_labels,
        key="pdf_escala_multiselect",
        help="Marque os cultos que deseja compilar. Pode juntar varios do mesmo evento.",
    )

    if not selected_labels:
        st.info("Selecione ao menos uma escala.")
        return

    selected_ids = [options[lbl] for lbl in selected_labels]
    selected_df = filter_escalas_by_period(
        ordenadas,
        date_start=None,
        date_end=None,
        escala_ids=selected_ids,
    )
    period_label = format_period_label(date_start, date_end)
    if event_filter:
        period_label = f"{event_filter} · {period_label}"

    st.caption(f"**{len(selected_df)}** escala(s) no PDF · periodo: {period_label}")

    if len(selected_df) > 6:
        st.warning(
            "Mais de 6 escalas podem ficar apertadas na folha. "
            "Para melhor leitura no WhatsApp, prefira ate 4–6 cultos por PDF."
        )

    if st.button(
        "📄 Gerar PDF",
        type="primary",
        use_container_width=True,
        key="pdf_escala_generate",
    ):
        try:
            pdf_bytes = build_escalas_pdf(
                selected_df,
                programa_df,
                equipe_df,
                period_label=period_label,
                integrantes_escalados=integrantes_escalados,
                normalize_funcao_escala=normalize_funcao_escala,
                programa_por_escala=programa_por_escala,
                fix_louvor_display_title=fix_louvor_display_title,
                funcao_ministrador=FUNCAO_MINISTRADOR,
                rehearsal_date_is_set=rehearsal_date_is_set,
                format_rehearsal_date_pt=format_rehearsal_date_pt,
            )
            st.session_state["escala_pdf_bytes"] = pdf_bytes
            st.session_state["escala_pdf_filename"] = suggested_filename(
                period_label, len(selected_df)
            )
            st.success("PDF pronto! Use o botao abaixo para baixar e enviar no WhatsApp.")
        except ValueError as exc:
            show_form_error(str(exc))
        except Exception as exc:
            show_technical_error(f"Nao foi possivel gerar o PDF: {exc}")

    pdf_bytes = st.session_state.get("escala_pdf_bytes")
    if pdf_bytes:
        fname = st.session_state.get(
            "escala_pdf_filename",
            suggested_filename(period_label, len(selected_df)),
        )
        b64 = base64.b64encode(pdf_bytes).decode()
        st.markdown(
            f'<a href="data:application/pdf;base64,{b64}" target="_blank" rel="noopener" '
            f'style="display:inline-block;margin:0.5rem 0;padding:0.6rem 1rem;'
            f'background:#7c3aed;color:#fff;border-radius:10px;text-decoration:none;font-weight:600;">'
            f"📄 Abrir PDF em nova aba (não sai do app)</a>",
            unsafe_allow_html=True,
        )
        with st.expander("👁️ Pré-visualizar PDF aqui", expanded=False):
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{b64}" '
                f'width="100%" height="480" style="border:1px solid #4c3a6a;border-radius:8px;"></iframe>',
                unsafe_allow_html=True,
            )
        c_dl, c_cls = st.columns(2)
        with c_dl:
            st.download_button(
                "⬇️ Baixar PDF",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
                key="pdf_escala_download",
            )
        with c_cls:
            if st.button("← Voltar ao painel (fechar PDF)", use_container_width=True, key="pdf_close"):
                st.session_state.pop("escala_pdf_bytes", None)
                st.session_state.pop("escala_pdf_filename", None)
                st.rerun()
        wa_parts = []
        for _, er in selected_df.iterrows():
            wa_parts.append(
                collect_escala_whatsapp_message(
                    er, programa_df, equipe_df, members_df
                )
            )
            wa_parts.append("—" * 12)
        wa_txt = "\n".join(wa_parts)
        render_escala_whatsapp_actions(
            wa_txt,
            pdf_bytes=pdf_bytes,
            pdf_filename=fname,
            key_prefix="wa_pdf_export",
        )


def show_gerenciar_escalas(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    chat_ensaio_df: pd.DataFrame,
):
    from gerenciar_escalas_ui import (
        GERENCIAR_TAB_LABELS,
        culto_ref_for_planner,
        cultos_esta_semana,
        render_gerenciar_header,
        render_gerenciar_kpis,
        render_gerenciar_nova_escala_button,
        render_gerenciar_page_close,
        render_gerenciar_page_open,
        render_gerenciar_sidebar,
    )

    escalas_df, programa_df, equipe_df, _ = get_escalas_bundle()
    render_pending_whatsapp_share_banner()

    from mobile_ui import mobile_hdr_close, mobile_hdr_open, mobile_stack_close, mobile_stack_open

    render_gerenciar_page_open()
    mobile_hdr_open()
    col_hdr, col_btn = st.columns([4, 1])
    with col_hdr:
        render_gerenciar_header()
    with col_btn:
        st.markdown('<div style="padding-top:0.5rem">', unsafe_allow_html=True)
        render_gerenciar_nova_escala_button()
        st.markdown("</div>", unsafe_allow_html=True)
    mobile_hdr_close()

    n_cultos = cultos_esta_semana(escalas_df)

    render_gerenciar_kpis(
        n_members=len(members_visible_to_group(members_df)),
        n_louvores=len(louvores_df),
        n_escalas=len(escalas_df),
        n_cultos=n_cultos,
    )

    tab_montar, tab_sugestoes, tab_sequencia, tab_pdf, tab_whatsapp = st.tabs(
        list(GERENCIAR_TAB_LABELS)
    )

    with tab_montar:
        mobile_stack_open()
        col_main, col_side = st.columns([3, 1])
        with col_main:
            show_escala_completa_editor(
                escalas_df,
                programa_df,
                equipe_df,
                louvores_df,
                members_df,
                chat_ensaio_df,
                external_planner_panel=True,
                premium_layout=True,
            )
        with col_side:
            render_gerenciar_sidebar(
                members_df,
                escalas_df,
                equipe_df,
                programa_df,
                louvores_df,
                culto_ref=culto_ref_for_planner(),
            )
        mobile_stack_close()

    with tab_sugestoes:
        from escala_suggester_ui import render_escala_suggestions_panel

        render_escala_suggestions_panel(
            members_df,
            escalas_df,
            equipe_df,
            programa_df,
            louvores_df,
        )

    with tab_sequencia:
        pref = st.session_state.pop("focus_sequencia_escala_id", None)
        show_sequencia_culto_page(
            escalas_df,
            programa_df,
            equipe_df,
            louvores_df,
            members_df,
            escala_id_pref=pref,
        )

    with tab_pdf:
        render_escalas_pdf_export(
            escalas_df, programa_df, equipe_df, members_df, louvores_df
        )

    with tab_whatsapp:
        st.markdown(
            '<p class="music-panel-title">💬 WhatsApp · integrantes</p>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Telefones cadastrados e gestão de integrantes. "
            "Para enviar a escala ao grupo, use **Exportar PDF** após gerar o PDF."
        )
        show_members_overview(members_df, louvores_df, escalas_df, equipe_df)

    render_gerenciar_page_close()


def show_sequencia_culto_page(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame | None = None,
    *,
    escala_id_pref: str | None = None,
):
    """Sequência do Culto: letras completas, marcações vocais e cifras por trecho."""
    from catalog_sanitize import format_louvor_display, sanitize_catalog_text

    seq_df = load_programa_sequencia_df()
    can_edit = is_scale_manager(st.session_state.get("user_roles", []))
    members_df = members_df if members_df is not None else pd.DataFrame()

    st.markdown(
        '<p class="music-panel-title">🎼 Sequência do Culto</p>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Ordem: **repertório local** (banco) → sequência salva → **internet** se faltar. "
        "Marque «Salvar na base do Repertório» para alimentar o banco do ministério."
    )

    todas = escalas_ordenadas(escalas_df)
    if todas.empty:
        st.info("Nenhuma escala cadastrada ainda.")
        return

    labels = [escala_label(r) for _, r in todas.iterrows()]
    id_by_label = {escala_label(r): str(r["id"]) for _, r in todas.iterrows()}

    pref = escala_id_pref or st.session_state.get("focus_sequencia_escala_id")
    default_idx = 0
    if pref:
        for i, lb in enumerate(labels):
            if id_by_label.get(lb) == str(pref):
                default_idx = i
                break

    escolha = st.selectbox("Culto", labels, index=default_idx, key="seq_culto_sel")
    escala_id = id_by_label[escolha]
    row_esc = todas[todas["id"].astype(str) == escala_id].iloc[0]

    prog = programa_por_escala(programa_df, escala_id)
    if prog.empty:
        st.warning(
            "Esta escala ainda não tem louvores na programação. "
            "Monte em **Gerenciar Escalas → Montar / editar escala**."
        )
        return

    with st.spinner("Preparando letras e cifras do culto…"):
        n_sync, n_web = hydrate_escala_sequencia_content(
            escala_id, programa_df, louvores_df
        )
    seq_df = load_programa_sequencia_df()
    if n_web:
        st.success(
            f"{n_web} música(s) com letra/cifra importadas da internet e salvas no culto."
        )
        louvores_df = prepare_louvores_with_meta(
            load_data(
                LOUVORES_FILE,
                (
                    "title",
                    "artist",
                    "key",
                    "youtube_url",
                    "cifra_url",
                    "ritmo",
                    "letter",
                    "source",
                    *LOUVOR_EXTRA_COLUMNS,
                    *LOUVOR_SEQUENCIA_COLUMNS,
                ),
            )
        )
    elif n_sync and not n_web:
        st.caption(f"{n_sync} música(s) carregada(s) do repertório.")

    team = integrantes_escalados(row_esc, equipe_df, members_df)
    vocal_opts = integrantes_marcacao_opts(team)
    banda_opts = banda_escala(team) or integrantes_marcacao_opts(team)
    if not vocal_opts:
        st.caption("Nenhum integrante na equipe deste culto — cadastre a escala em Gerenciar Escalas.")
    if not banda_opts:
        st.caption("Nenhum instrumentista escalado — cadastre Baixo, Guitarra, Teclado, etc. na equipe.")

    try:
        dt = pd.to_datetime(str(row_esc.get("date", "")))
        date_fmt = f"{_DIAS_SEMANA_PT[dt.weekday()]}, {dt.strftime('%d/%m/%Y')}"
    except (ValueError, TypeError):
        date_fmt = str(row_esc.get("date", ""))
    st.markdown(
        f"**{row_esc.get('event', 'Culto')}** · {date_fmt} · "
        f"{len(prog)} música(s) na sequência"
    )

    song_labels = []
    prog_by_label: dict[str, pd.Series] = {}
    for _, item in prog.iterrows():
        louvor = fix_louvor_display_title(sanitize_catalog_text(item.get("louvor_title", "")))
        artist = sanitize_catalog_text(item.get("artist", ""))
        lbl = f"{item['ordem']}. {format_louvor_display(louvor, artist)} ({item.get('parte', '')})"
        song_labels.append(lbl)
        prog_by_label[lbl] = item

    musica = st.selectbox("Música na sequência", song_labels, key="seq_musica_sel")
    item = prog_by_label[musica]
    programa_id = str(item.get("id", ""))
    louvor_t = sanitize_catalog_text(item.get("louvor_title", ""))
    artist_t = sanitize_catalog_text(item.get("artist", ""))
    tom_base = sanitize_catalog_text(item.get("key", "")) or "C"

    seq_row = get_sequencia_row(seq_df, programa_id)
    lyrics_stored = str(seq_row.get("lyrics_text", "")).strip()
    cifra_stored = str(seq_row.get("cifra_text", "")).strip()
    lyrics_default = lyrics_stored or default_lyrics_from_louvor(louvores_df, louvor_t, artist_t)
    cifra_default = cifra_stored or default_cifra_from_louvor(louvores_df, louvor_t, artist_t)
    cifra_url_item = sanitize_catalog_text(item.get("cifra_url", ""))

    if not lyrics_default.strip() or not cifra_default.strip():
        from louvor_content import ensure_sequencia_louvor_content

        with st.spinner("Buscando letra e cifra na internet para esta música…"):
            seq_df, louvores_df, msg, _web = ensure_sequencia_louvor_content(
                seq_df,
                programa_id,
                louvor_t,
                artist_t,
                cifra_url_item,
                tom_base,
                louvores_df,
                use_web=True,
                save_to_catalog=can_edit,
            )
        if _web and can_edit:
            save_data(louvores_df, LOUVORES_FILE)
            save_programa_sequencia_df(seq_df)
        elif _web:
            save_programa_sequencia_df(seq_df)
        if msg:
            if _web:
                st.success(msg)
            else:
                st.warning(msg)
        seq_row = get_sequencia_row(seq_df, programa_id)
        lyrics_default = str(seq_row.get("lyrics_text", "")).strip() or lyrics_default
        cifra_default = str(seq_row.get("cifra_text", "")).strip() or cifra_default

    if can_edit and st.button(
        "🔄 Atualizar letra/cifra da internet",
        key=f"seq_refetch_{programa_id}",
    ):
        from louvor_content import ensure_sequencia_louvor_content

        with st.spinner("Atualizando da internet…"):
            seq_df, louvores_df, msg, _web = ensure_sequencia_louvor_content(
                seq_df,
                programa_id,
                louvor_t,
                artist_t,
                cifra_url_item,
                tom_base,
                louvores_df,
                use_web=True,
                save_to_catalog=True,
                force_web_refresh=True,
            )
        if _web:
            save_programa_sequencia_df(seq_df)
            save_data(louvores_df, LOUVORES_FILE)
            st.success(msg or "Atualizado.")
            st.rerun()
        else:
            st.warning(msg or "Não foi possível buscar.")

    tom_prog = str(seq_row.get("tom_programa", "")).strip() or tom_base
    capo_val = int(pd.to_numeric(seq_row.get("capo", 0), errors="coerce") or 0)

    paragraphs = split_lyrics_paragraphs(lyrics_default)
    n_para = max(len(paragraphs), 1)
    trechos_v = trechos_from_markup(str(seq_row.get("lyrics_markup", "")), n_para)
    trechos_b = trechos_banda_from_markup(str(seq_row.get("cifra_markup", "")), n_para)

    lyrics_edit = lyrics_default
    cifra_edit = cifra_default
    tom_new = tom_prog if tom_prog in TOM_OPCOES else (tom_base if tom_base in TOM_OPCOES else "C")
    capo_new = capo_val
    trechos_v_new = trechos_v
    trechos_b_new = trechos_b
    paragraphs_edit = paragraphs

    idx_tom = list(TOM_OPCOES).index(tom_prog) if tom_prog in TOM_OPCOES else 0
    c1, c2, c3, c4 = st.columns([1.2, 1, 1, 2])
    with c1:
        tom_view = st.selectbox(
            "Tom do culto",
            TOM_OPCOES,
            index=idx_tom,
            key=f"seq_tom_view_{programa_id}",
            disabled=not can_edit,
        )
    with c2:
        capo_view = st.number_input(
            "Capotraste",
            min_value=0,
            max_value=11,
            value=capo_val,
            key=f"seq_capo_view_{programa_id}",
            disabled=not can_edit,
        )
    with c3:
        st.caption(f"Tom no repertório: **{tom_base or '—'}**")
    with c4:
        if not cifra_default.strip():
            st.warning("Cifra ainda não carregada — use o botão acima para buscar na internet.")

    tom_show = tom_view if can_edit else tom_prog
    capo_show = int(capo_view) if can_edit else capo_val
    cifra_show = display_cifra_transposed(cifra_default, tom_base, tom_show) or cifra_default

    direcoes_html = render_cifra_direcoes_html(paragraphs, trechos_v, trechos_b)
    st.markdown('<div class="seq-cifra-panel">', unsafe_allow_html=True)
    st.markdown("#### 🎸 Cifra")
    if direcoes_html:
        st.markdown(direcoes_html, unsafe_allow_html=True)
    if cifra_show:
        st.markdown(
            render_cifra_html(cifra_show, effective_tom(tom_base, tom_show), capo_show),
            unsafe_allow_html=True,
        )
    else:
        st.info(
            "Cifra indisponível. Clique em **Atualizar letra/cifra da internet** "
            "ou cole manualmente abaixo (líderes)."
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### 📝 Letra com marcações (vocal e banda)")
    lyrics_edit = lyrics_default
    cifra_edit = cifra_default
    tom_new = tom_prog if tom_prog in TOM_OPCOES else (tom_base if tom_base in TOM_OPCOES else "C")
    capo_new = capo_val
    if paragraphs:
        st.markdown(
            render_lyrics_annotated_html(paragraphs, trechos_v, trechos_b),
            unsafe_allow_html=True,
        )
    if can_edit:
        with st.expander("✏️ Editar texto da letra", expanded=not paragraphs):
            lyrics_edit = st.text_area(
                "Letra completa — estrofes separadas por linha em branco",
                value=lyrics_default,
                height=180,
                key=f"seq_ly_{programa_id}",
                label_visibility="collapsed",
            )
        paragraphs_edit = split_lyrics_paragraphs(lyrics_edit)
        if not paragraphs_edit and lyrics_edit.strip():
            paragraphs_edit = [lyrics_edit.strip()]
        if paragraphs_edit:
            st.markdown("#### 🎤 Marcações vocais")
            trechos_v_new = build_trechos_vocal_ui(
                st,
                paragraphs_edit,
                vocal_opts,
                trechos_v,
                f"seqv_{programa_id}",
            )
            st.markdown("#### 🎹 Marcações da banda")
            trechos_b_new = build_trechos_banda_ui(
                st,
                paragraphs_edit,
                banda_opts,
                trechos_b,
                f"seqb_{programa_id}",
            )
        else:
            st.caption("Cole a letra no expander acima para marcar os trechos.")
        st.markdown("---")
        with st.expander("🎸 Editar cifra (texto)", expanded=False):
            cifra_edit = st.text_area(
                "Cifra (acordes por linha)",
                value=cifra_default,
                height=240,
                key=f"seq_cf_{programa_id}",
            )
            tom_new = tom_view
            capo_new = int(capo_view)
            cifra_trans = display_cifra_transposed(cifra_edit, tom_base, tom_new)
            if cifra_trans:
                st.markdown("**Prévia transposta**")
                st.markdown(
                    render_cifra_html(cifra_trans, tom_new, capo_new),
                    unsafe_allow_html=True,
                )
        if paragraphs_edit:
            from cifra_fetch import normalize_cifra_text

            cifra_draft = normalize_cifra_text(cifra_edit)
            tom_draft = (
                str(tom_view)
                if str(tom_view) in TOM_OPCOES
                else str(tom_new)
            )
            seq_df, autosaved = autosave_sequencia_trabalho(
                seq_df,
                programa_id,
                lyrics_text=lyrics_edit,
                cifra_text=cifra_draft,
                trechos_v=trechos_v_new,
                trechos_b=trechos_b_new,
                tom_programa=tom_draft,
                capo=int(capo_view),
            )
            if autosaved:
                save_programa_sequencia_df(seq_df)
            autosave_at = st.session_state.get(f"seq_autosave_at_{programa_id}", "")
            st.caption(
                "💾 Letra, cifra e **marcações vocais/banda** são salvas automaticamente"
                + (f" (última: {autosave_at})" if autosave_at else "")
                + " — você não perde ao sair do app ou atualizar a página."
            )
    elif not paragraphs:
        st.info("Letra indisponível para esta música.")

    if can_edit:
        salvar_rep = st.checkbox(
            "Salvar letra e cifra na **base do Repertório** (banco local do ministério)",
            value=True,
            key=f"seq_rep_{programa_id}",
        )
        if st.button(
            "💾 Salvar sequência desta música",
            type="primary",
            key=f"seq_save_{programa_id}",
        ):
            from cifra_fetch import normalize_cifra_text
            from louvor_content import apply_content_to_louvores_df

            cifra_save = normalize_cifra_text(cifra_edit)
            seq_df = upsert_sequencia_row(
                seq_df,
                programa_id,
                lyrics_text=lyrics_edit.strip(),
                lyrics_markup=markup_to_json(trechos_v_new),
                cifra_text=cifra_save,
                tom_programa=str(tom_new),
                capo=int(capo_new),
                cifra_markup=markup_to_json(trechos_b_new),
            )
            save_programa_sequencia_df(seq_df)
            if salvar_rep and louvor_t:
                louvores_df = apply_content_to_louvores_df(
                    louvores_df,
                    louvor_t,
                    artist_t,
                    lyrics_edit,
                    cifra_save,
                    source_tag="sequencia_culto",
                )
                if tom_new:
                    mask_l = (
                        louvores_df["title"].astype(str).str.strip().str.lower()
                        == louvor_t.lower()
                    )
                    if artist_t:
                        mask_l &= (
                            louvores_df["artist"].astype(str).str.strip().str.lower()
                            == artist_t.lower()
                        )
                    if mask_l.any():
                        louvores_df.at[louvores_df[mask_l].index[0], "key"] = str(tom_new)
                save_data(louvores_df, LOUVORES_FILE)
            msg_ok = "Sequência salva para este louvor."
            if salvar_rep and louvor_t:
                msg_ok += " Letra e cifra gravadas no repertório local."
            st.success(msg_ok)
            st.rerun()


def show_programa_culto_editor(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
):
    show_escala_completa_editor(
        escalas_df, programa_df, equipe_df, louvores_df, members_df
    )


def show_escalas_page(
    escalas_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
    members_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    chat_ensaio_df: pd.DataFrame,
):
    from escalas_ui import (
        ESCALAS_TAB_LABELS,
        render_escalas_gerenciar_button,
        render_escalas_header,
        render_escalas_info_banner,
        render_escalas_not_scheduled_warning,
        render_escalas_page_close,
        render_escalas_page_open,
        render_escalas_tabs_spacer,
    )

    escalas_df, programa_df, equipe_df, trocas_df = get_escalas_bundle()

    render_escalas_page_open()
    render_escalas_header()
    render_escalas_info_banner()
    if is_scale_manager(st.session_state.user_roles):
        render_escalas_gerenciar_button()
    render_escalas_tabs_spacer()

    tab_equipe, tab_todas, tab_sequencia, tab_trocar, tab_pedidos, tab_ensaio = st.tabs(
        list(ESCALAS_TAB_LABELS)
    )

    member_map = members_options_escala(members_df)
    my_email = st.session_state.user_email.strip().lower()
    start, end = week_bounds(st.session_state.get("week_offset", 0))

    focus_id = st.session_state.pop("focus_escala_id", None)

    with tab_equipe:
        minhas = user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)
        if focus_id:
            row_f = escalas_df[escalas_df["id"].astype(str) == str(focus_id)]
            if not row_f.empty:
                st.success("Programação do culto selecionado no painel:")
                render_culto_programa(
                    row_f.iloc[0],
                    programa_df,
                    equipe_df,
                    members_df,
                    louvores_df,
                    ensaio_notice=True,
                    widget_key_prefix=f"eq_focus_{focus_id}",
                )
                st.markdown("---")
        if not minhas and not focus_id:
            render_escalas_not_scheduled_warning()
        for item in minhas:
            if focus_id and str(item["escala"].get("id", "")) == str(focus_id):
                continue
            eid_item = str(item["escala"].get("id", ""))
            render_culto_programa(
                item["escala"],
                programa_df,
                equipe_df,
                members_df,
                louvores_df,
                ensaio_notice=True,
                widget_key_prefix=f"eq_{eid_item}",
            )

    with tab_todas:
        occ = member_escala_occurrences(my_email, escalas_df, equipe_df)
        if not occ:
            st.info("Você ainda não aparece em nenhuma escala registrada.")
        else:
            st.caption(f"{len(occ)} culto(s) no seu histórico de escalas.")
            for i, (culto_d, eid, ev) in enumerate(occ):
                row_match = escalas_df[escalas_df["id"].astype(str) == str(eid)]
                if row_match.empty:
                    continue
                render_culto_programa(
                    row_match.iloc[0],
                    programa_df,
                    equipe_df,
                    members_df,
                    louvores_df,
                    ensaio_notice=True,
                    widget_key_prefix=f"todas_{i}_{eid}",
                )

    with tab_sequencia:
        pref = None
        if st.session_state.get("_open_sequencia_tab"):
            pref = st.session_state.pop("focus_sequencia_escala_id", None)
            st.session_state.pop("_open_sequencia_tab", None)
        if not pref:
            pref = st.session_state.pop("focus_sequencia_escala_id", None)
        show_sequencia_culto_page(
            escalas_df,
            programa_df,
            equipe_df,
            louvores_df,
            members_df,
            escala_id_pref=pref,
        )

    with tab_trocar:
        st.write(
            "Divulgue para o grupo ou peça a um integrante específico. "
            "A escala atualiza após aceite ou quando alguém assumir."
        )
        minhas = user_escalas(escalas_df, my_email, equipe_df)
        if minhas.empty:
            st.warning(
                "Não encontramos culto vinculado ao seu e-mail. "
                "Confira se você está escalado em **Minha equipe** com o mesmo login."
            )
        else:
            minhas_opts = {
                escala_label_for_user(r, my_email, equipe_df): str(r["id"])
                for _, r in minhas.iterrows()
            }
            with st.form(key="troca_form_v2"):
                minha = st.selectbox("Minha escala", list(minhas_opts.keys()))
                modo = st.radio(
                    "Tipo de troca",
                    [
                        "Divulgar para qualquer integrante assumir",
                        "Pedir que integrante específico assuma",
                    ],
                )
                target_email = ""
                target_name = ""
                tipo = "aberta"
                outros = [l for l, e in member_map.items() if e != my_email]
                if modo.startswith("Pedir que integrante"):
                    tipo = "direcionada"
                    outro = st.selectbox("Integrante que deve assumir", outros)
                    target_email = member_map[outro]
                    tr = members_df[
                        members_df["email"].astype(str).str.lower() == target_email
                    ].iloc[0]
                    target_name = member_display_name(tr)
                msg = st.text_input("Mensagem (opcional)")
                go = st.form_submit_button("📨 Enviar solicitação", type="primary")
            if go:
                oid = minhas_opts[minha]
                if not trocas_df[
                    (trocas_df["status"] == "pendente")
                    & (trocas_df["escala_id_origem"].astype(str) == str(oid))
                ].empty:
                    st.warning("Já existe solicitação pendente para esta escala.")
                else:
                    nova = {
                        "id": new_id(),
                        "escala_id_origem": oid,
                        "escala_id_destino": "",
                        "requester_email": my_email,
                        "requester_name": st.session_state.user_full_name
                        or st.session_state.user_name,
                        "target_email": target_email,
                        "target_name": target_name,
                        "status": "pendente",
                        "message": msg.strip(),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "responded_at": "",
                        "tipo": tipo,
                        "accepter_email": "",
                        "accepter_name": "",
                    }
                    save_data(
                        pd.concat([trocas_df, pd.DataFrame([nova])], ignore_index=True),
                        TROCAS_FILE,
                    )
                    st.success(
                        "Solicitação enviada! Ela aparece em destaque no Dashboard e em Escalas."
                    )
                    st.rerun()

    with tab_pedidos:
        _, rec, env = swap_alerts_for_user(
            trocas_df, my_email, escalas_df=escalas_df, equipe_df=equipe_df
        )
        st.subheader("📥 Recebidos")
        if rec.empty:
            st.info("Nenhum pedido direcionado a você.")
        for _, t in rec.iterrows():
            o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
            ot = escala_label(o.iloc[0]) if not o.empty else "—"
            if str(t["escala_id_destino"]).strip():
                d = escalas_df[escalas_df["id"] == t["escala_id_destino"]]
                dt = escala_label(d.iloc[0]) if not d.empty else "—"
                txt = f"Troca: {ot} ↔ {dt}"
            else:
                txt = f"Assumir: {ot}"
            st.markdown(
                f'<div class="swap-card"><b>{t["requester_name"]}</b><br>{txt}</div>',
                unsafe_allow_html=True,
            )
            if t["message"]:
                st.caption(t["message"])
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Aceitar", key=f"a{t['id']}", use_container_width=True):
                    name = st.session_state.user_full_name or st.session_state.user_name
                    escalas_df, equipe_df, trocas_df, ok = accept_open_swap(
                        t, my_email, name, escalas_df, equipe_df, trocas_df
                    )
                    if ok:
                        save_data(escalas_df, ESCALAS_FILE)
                        save_data(equipe_df, EQUIPE_FILE)
                        save_data(trocas_df, TROCAS_FILE)
                        st.rerun()
                    else:
                        st.error(
                            "Você já está escalado neste culto — não é possível aceitar esta troca."
                        )
            with c2:
                if st.button("❌ Recusar", key=f"r{t['id']}", use_container_width=True):
                    trocas_df = prepare_trocas(trocas_df)
                    trocas_df.loc[trocas_df["id"].astype(str) == str(t["id"]), "status"] = (
                        "recusada"
                    )
                    trocas_df.loc[
                        trocas_df["id"].astype(str) == str(t["id"]), "responded_at"
                    ] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_data(trocas_df, TROCAS_FILE)
                    st.rerun()
        st.subheader("📤 Enviados")
        if env.empty:
            st.info("Nenhum pedido enviado pendente.")
        for _, t in env.iterrows():
            o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
            alvo = t.get("target_name") or "o grupo"
            st.caption(
                f"Aguardando {alvo} · {escala_label(o.iloc[0]) if not o.empty else '—'}"
            )
            if st.button("Cancelar", key=f"c{t['id']}"):
                trocas_df.loc[trocas_df["id"] == t["id"], "status"] = "cancelada"
                save_data(trocas_df, TROCAS_FILE)
                st.rerun()

    with tab_ensaio:
        minhas_ids = {
            str(item["escala"]["id"])
            for item in user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)
        }
        if not minhas_ids:
            st.info("Participe de uma escala desta semana para acessar o chat do ensaio.")
        else:
            labels = {}
            for eid in minhas_ids:
                row = escalas_df[escalas_df["id"].astype(str) == eid]
                if not row.empty:
                    labels[escala_label(row.iloc[0])] = eid
            escolha = st.selectbox("Escala / culto", list(labels.keys()))
            escala_row = escalas_df[
                escalas_df["id"].astype(str) == str(labels[escolha])
            ].iloc[0]
            is_mgr_ensaio = is_scale_manager(st.session_state.user_roles)
            if rehearsal_date_is_set(escala_row):
                st.success(f"📅 Ensaio: {format_rehearsal_date_pt(escala_row)}")
            elif is_mgr_ensaio:
                st.warning(
                    "⚠️ **Definir data do ensaio** — cadastre em **Gerenciar Escalas** "
                    "para avisar quem está escalado."
                )
            else:
                st.warning(
                    "⏳ **Definir data do ensaio** — aguardando o líder confirmar. "
                    "Fique atento(a)!"
                )
            render_ensaio_chat(labels[escolha], chat_ensaio_df, members_df)

    render_escalas_page_close()


def _render_louvor_validation_search(louvores_df: pd.DataFrame):
    """Busca ao digitar (mesmo padrão do culto) + analisar ao tocar no louvor."""
    key_prefix = "val_rep"
    qkey = f"{key_prefix}_lq"
    active_key = f"{key_prefix}_lq_active"
    if active_key not in st.session_state:
        st.session_state[active_key] = ""

    def commit_query():
        st.session_state[active_key] = str(st.session_state.get(qkey, "")).strip()

    if _TEXT_INPUT_HAS_BIND:
        st.text_input(
            label="Buscar",
            key=qkey,
            placeholder="Nome do louvor ou artista...",
            label_visibility="collapsed",
            on_change=commit_query,
            bind="query-params",
        )
        st.session_state[active_key] = str(st.session_state.get(qkey, "")).strip()
        st.caption("A lista filtra enquanto você digita.")
    else:
        col_inp, col_btn = st.columns([6, 1])
        with col_inp:
            st.text_input(
                label="Buscar",
                key=qkey,
                placeholder="Nome do louvor ou artista...",
                label_visibility="collapsed",
                on_change=commit_query,
            )
        with col_btn:
            st.markdown('<div class="louvor-search-btn-wrap">', unsafe_allow_html=True)
            if st.button("Buscar", key=f"{key_prefix}_go", use_container_width=True):
                commit_query()
            st.markdown("</div>", unsafe_allow_html=True)

    query = str(st.session_state.get(active_key, "")).strip()
    if len(query) < 1:
        st.info("Digite para buscar um louvor a validar.")
        return

    filtered = filter_louvores_for_picker(louvores_df, query)
    catalog = louvores_catalog_options(filtered)
    opcoes = list(catalog.keys())[:12]
    if not opcoes:
        st.warning("Nenhum louvor encontrado.")
        return

    st.caption(f"**{len(catalog)}** encontrado(s) — toque para analisar")
    for label in opcoes:
        data = catalog.get(label, {})
        from catalog_sanitize import sanitize_catalog_text

        titulo = sanitize_catalog_text(data.get("title", label.split(" — ")[0]))
        artista = sanitize_catalog_text(data.get("artist", ""))
        btn = f"🔍 Analisar — {titulo}"
        if artista:
            btn += f" ({artista})"
        if st.button(btn, key=f"{key_prefix}_v_{_picker_key_slug(label)}", use_container_width=True):
            themes_v = themes_from_csv(str(data.get("temas", "")))
            if not themes_v:
                themes_v = classify_themes(titulo, artista)
            res = validate_louvor(titulo, artista, themes_v)
            st.session_state[f"{key_prefix}_last"] = res
            st.rerun()

    res = st.session_state.get(f"{key_prefix}_last")
    if res:
        st.markdown("---")
        st.markdown(f"**{res['summary']}**")
        for p in res["positives"]:
            st.success(p)
        for i in res["issues"]:
            st.warning(i)
        st.caption(f"Temas: {', '.join(res['themes'])}")
        st.caption(f"Referências: {res['refs']}")
        st.info(res["guidance"])


def _render_louvores_edit_manager(louvores_df: pd.DataFrame):
    key_prefix = "edit_rep"
    qkey = f"{key_prefix}_lq"
    active_key = f"{key_prefix}_lq_active"
    if active_key not in st.session_state:
        st.session_state[active_key] = ""
    sel_key = f"{key_prefix}_selected"

    def commit_query():
        st.session_state[active_key] = str(st.session_state.get(qkey, "")).strip()

    if _TEXT_INPUT_HAS_BIND:
        st.text_input(
            "Buscar louvor para editar",
            key=qkey,
            placeholder="Nome ou artista...",
            on_change=commit_query,
            bind="query-params",
        )
        st.session_state[active_key] = str(st.session_state.get(qkey, "")).strip()
    else:
        st.text_input(
            "Buscar louvor para editar",
            key=qkey,
            placeholder="Nome ou artista...",
            on_change=commit_query,
        )

    query = str(st.session_state.get(active_key, "")).strip()
    if len(query) < 1:
        st.caption("Busque o louvor que deseja editar ou excluir.")
        return

    filtered = filter_louvores_for_picker(louvores_df, query)
    catalog = louvores_catalog_options(filtered)
    labels = list(catalog.keys())[:15]
    pick = st.selectbox("Selecione o louvor", labels, key=sel_key) if labels else None
    if not pick:
        return
    data = catalog[pick]
    titulo_orig = str(data.get("title", ""))
    idx_mask = louvores_df["title"].astype(str).str.strip() == titulo_orig.strip()
    if not idx_mask.any():
        st.warning("Louvor não encontrado no arquivo.")
        return
    idx = louvores_df[idx_mask].index[0]
    with st.form(key=f"{key_prefix}_form"):
        nt = st.text_input("Título", value=str(louvores_df.at[idx, "title"]))
        na = st.text_input("Artista", value=str(louvores_df.at[idx, "artist"]))
        nk = st.text_input("Tom", value=str(louvores_df.at[idx, "key"]))
        nr = st.text_input("Ritmo", value=str(louvores_df.at[idx, "ritmo"]))
        nyt = st.text_input("YouTube", value=str(louvores_df.at[idx, "youtube_url"]))
        ncif = st.text_input("Link Cifra Club", value=str(louvores_df.at[idx, "cifra_url"]))
        ntemas = st.text_input(
            "Temas (separados por ;)",
            value=str(louvores_df.at[idx, "temas"]),
        )
        st.caption(
            "Letra e cifra abaixo ficam no **banco do repertório** e alimentam a "
            "**Sequência do Culto** (antes da busca na internet)."
        )
        nly = st.text_area(
            "Letra completa (repertório)",
            value=str(louvores_df.at[idx, "lyrics_text"]),
            height=140,
        )
        ncf = st.text_area(
            "Cifra completa (repertório)",
            value=str(louvores_df.at[idx, "cifra_text"]),
            height=140,
        )
        c1, c2 = st.columns(2)
        with c1:
            salvar = st.form_submit_button("💾 Salvar", type="primary", use_container_width=True)
        with c2:
            excluir = st.form_submit_button("🗑️ Excluir", use_container_width=True)
    if salvar:
        from louvor_content import apply_content_to_louvores_df
        from louvor_sync import apply_repertoire_save_side_effects

        old_title = titulo_orig.strip()
        old_artist = str(louvores_df.at[idx, "artist"]).strip()
        meta = ensure_louvor_row_metadata(nt, na, ntemas, "", "")
        louvores_df.at[idx, "title"] = nt.strip()
        louvores_df.at[idx, "artist"] = na.strip()
        louvores_df.at[idx, "key"] = nk.strip()
        louvores_df.at[idx, "ritmo"] = nr.strip()
        louvores_df.at[idx, "youtube_url"] = nyt.strip()
        louvores_df.at[idx, "cifra_url"] = ncif.strip()
        louvores_df.at[idx, "temas"] = ntemas.strip() or meta["temas"]
        louvores_df.at[idx, "ref_biblica"] = meta["ref_biblica"]
        louvores_df.at[idx, "duracao_min"] = meta["duracao_min"]
        louvores_df.at[idx, "letter"] = nt.strip()[0].upper() if nt.strip() else "A"
        louvores_df = apply_content_to_louvores_df(
            louvores_df,
            nt.strip(),
            na.strip(),
            nly,
            ncf,
            source_tag="repertorio_editado",
        )
        save_data(louvores_df, LOUVORES_FILE)
        programa_df = prepare_programa(load_data(PROGRAMA_FILE, PROGRAMA_COLUMNS))
        seq_df = load_programa_sequencia_df()
        programa_df, seq_df, stats = apply_repertoire_save_side_effects(
            programa_df,
            seq_df,
            louvores_df,
            old_title,
            old_artist,
            nt.strip(),
            na.strip(),
            refresh_sequencia=True,
        )
        if stats["programa"]:
            save_data(programa_df, PROGRAMA_FILE)
        if stats["sequencia"]:
            save_programa_sequencia_df(seq_df)
        extra = ""
        if stats["programa"] or stats["sequencia"]:
            extra = (
                f" Atualizado em **{stats['programa']}** culto(s) na programação "
                f"e **{stats['sequencia']}** sequência(s) com letra/cifra do repertório."
            )
        st.success(f"Louvor atualizado.{extra}")
        st.rerun()
    if excluir:
        louvores_df = louvores_df.drop(index=idx)
        save_data(louvores_df, LOUVORES_FILE)
        st.success("Louvor removido do repertório.")
        st.rerun()


def show_louvores_catalog(
    louvores_df: pd.DataFrame,
    programa_df: pd.DataFrame | None = None,
    sugestoes_df: pd.DataFrame | None = None,
    playlist_df: pd.DataFrame | None = None,
):
    from louvor_content import (
        count_louvores_missing_content,
        count_louvores_with_full_content,
        enrich_louvores_letras_cifras,
        ensure_louvor_content_columns,
    )
    from repertorio_ui import (
        build_repertorio_table_html,
        compute_repertorio_stats,
        count_added_this_month,
        render_repertorio_add_button,
        render_repertorio_banner,
        render_repertorio_filter_card_close,
        render_repertorio_filter_card_open,
        render_repertorio_header,
        render_repertorio_kpis,
        render_repertorio_page_close,
        render_repertorio_page_open,
        render_repertorio_pagination,
        render_repertorio_sidebar,
        render_repertorio_toolbar,
    )

    louvores_df = ensure_louvor_content_columns(louvores_df.copy())
    programa_df = programa_df if programa_df is not None else pd.DataFrame()
    mgr = is_scale_manager(st.session_state.user_roles)
    my_email = str(st.session_state.get("user_email", "")).strip().lower()

    from mobile_ui import mobile_hdr_close, mobile_hdr_open, mobile_stack_close, mobile_stack_open

    render_repertorio_page_open()
    mobile_hdr_open()
    col_hdr, col_btn = st.columns([4, 1])
    with col_hdr:
        render_repertorio_header()
    with col_btn:
        st.markdown('<div style="padding-top:0.5rem">', unsafe_allow_html=True)
        render_repertorio_add_button()
        st.markdown("</div>", unsafe_allow_html=True)
    mobile_hdr_close()

    render_repertorio_banner()
    render_voice_kit_link()

    stats = compute_repertorio_stats(louvores_df)
    added_month = count_added_this_month(sugestoes_df)
    render_repertorio_kpis(stats, added_month=added_month)

    if louvores_df.empty:
        st.warning(
            "Repertório ainda não gerado. Execute: `python build_louvores_db.py`"
        )
        render_repertorio_page_close()
        return

    if st.session_state.get("rep_add_open"):
        with st.expander("➕ Adicionar música ao repertório", expanded=True):
            if mgr:
                _render_louvores_edit_manager(louvores_df)
            else:
                st.info(
                    "Envie sugestões em **Sugestão de louvor** — a liderança analisa e "
                    "inclui no repertório."
                )
                if st.button("Ir para Sugestão de louvor", key="rep_go_sugestao"):
                    st.session_state.app_menu = "Sugestão de louvor"
                    st.session_state.pop("rep_add_open", None)
                    st.rerun()

    mobile_stack_open()
    col_main, col_side = st.columns([3, 1])
    with col_main:
        render_repertorio_filter_card_open()
        search = st.text_input(
            "Buscar música ou artista...",
            key="rep_search_q",
            placeholder="Buscar música ou artista...",
        )
        letters = sorted(
            {letter for letter in louvores_df["letter"].dropna().astype(str) if letter}
        )
        ritmos = sorted(
            {
                ritmo
                for ritmo in louvores_df["ritmo"].dropna().astype(str)
                if ritmo.strip()
            }
        )
        toms = sorted(
            {str(t).strip() for t in louvores_df["key"].dropna().astype(str) if str(t).strip()}
        )
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            letter_filter = st.selectbox("Letra", ["Todas"] + letters, key="rep_f_letter")
        with f2:
            tom_filter = st.selectbox("Tom", ["Todos"] + toms, key="rep_f_tom")
        with f3:
            ritmo_filter = st.selectbox("Ritmo", ["Todos"] + ritmos, key="rep_f_ritmo")
        with f4:
            tema_filter = st.multiselect(
                "Tema", list(LOUVOR_THEMES), key="rep_f_tema", placeholder="Todos"
            )
        tag_filter = st.multiselect(
            "Tag bíblica",
            list(LOUVOR_THEMES),
            key="rep_f_tag",
            placeholder="Filtrar por tag bíblica",
        )
        minist_filter = st.multiselect(
            "Ministração",
            list(LOUVOR_THEMES)[:12],
            key="rep_f_minist",
            placeholder="Todas",
        )
        fc1, fc2, fc3 = st.columns([2, 2, 1])
        with fc1:
            apenas_fav = st.toggle("⭐ Apenas favoritas", key="rep_f_fav")
        with fc3:
            if st.button("Limpar filtros", key="ig_rep_clear_filters", use_container_width=True):
                for k in (
                    "rep_search_q",
                    "rep_f_letter",
                    "rep_f_tom",
                    "rep_f_ritmo",
                    "rep_f_tema",
                    "rep_f_tag",
                    "rep_f_minist",
                ):
                    st.session_state.pop(k, None)
                st.session_state["rep_f_fav"] = False
                st.session_state["page_repertorio"] = 1
                st.rerun()
        render_repertorio_filter_card_close()

        fav_titles: set[str] = set()
        if playlist_df is not None and not playlist_df.empty and my_email:
            mine = playlist_for_user(playlist_df, my_email)
            fav_titles = {
                str(t).strip().lower()
                for t in mine.get("title", pd.Series(dtype=str)).astype(str)
            }

        filtered = louvores_df.copy()
        if search.strip():
            term = search.strip().lower()
            mask = (
                filtered["title"].astype(str).str.lower().str.contains(term, na=False)
                | filtered["artist"].astype(str).str.lower().str.contains(term, na=False)
            )
            filtered = filtered[mask]
        if letter_filter != "Todas":
            filtered = filtered[filtered["letter"].astype(str) == letter_filter]
        if tom_filter != "Todos":
            filtered = filtered[filtered["key"].astype(str) == tom_filter]
        if ritmo_filter != "Todos":
            filtered = filtered[filtered["ritmo"].astype(str) == ritmo_filter]

        def _match_themes(row, tags: list[str]) -> bool:
            if not tags:
                return True
            ts = themes_from_csv(str(row.get("temas", "")))
            return any(t in ts for t in tags)

        if tema_filter:
            filtered = filtered[filtered.apply(lambda r: _match_themes(r, tema_filter), axis=1)]
        if tag_filter:
            filtered = filtered[filtered.apply(lambda r: _match_themes(r, tag_filter), axis=1)]
        if minist_filter:
            filtered = filtered[filtered.apply(lambda r: _match_themes(r, minist_filter), axis=1)]
        if apenas_fav and fav_titles:
            filtered = filtered[
                filtered["title"].astype(str).str.strip().str.lower().isin(fav_titles)
            ]
        elif apenas_fav and not fav_titles:
            filtered = filtered.iloc[0:0]

        if any(
            [
                search.strip(),
                letter_filter != "Todas",
                tom_filter != "Todos",
                ritmo_filter != "Todos",
                tema_filter,
                tag_filter,
                minist_filter,
                apenas_fav,
            ]
        ):
            st.session_state["page_repertorio"] = 1

        page_size = st.selectbox(
            "Itens por página",
            [25, 50, 100],
            index=0,
            key="rep_page_size",
            label_visibility="collapsed",
        )
        total_pages = max(
            1, (len(filtered) + page_size - 1) // page_size
        ) if len(filtered) else 1
        page = min(
            st.session_state.get("page_repertorio", 1),
            total_pages,
        )
        st.session_state["page_repertorio"] = page
        start = (page - 1) * page_size
        end = start + page_size
        render_repertorio_toolbar(len(filtered), len(louvores_df), page, total_pages)

        page_df = filtered.iloc[start:end]
        st.markdown(build_repertorio_table_html(page_df), unsafe_allow_html=True)
        render_repertorio_pagination(len(filtered), page_size, "repertorio")

        if mgr:
            with st.expander("🛠️ Ferramentas do repertório (líderes)", expanded=False):
                faltam_texto = count_louvores_missing_content(louvores_df)
                completas = count_louvores_with_full_content(louvores_df)
                st.caption(
                    f"Banco local: **{completas}** de **{len(louvores_df)}** com letra e cifra · "
                    f"**{faltam_texto}** pendente(s)."
                )
                from enrich_louvores_links import enrich_dataframe

                col_l0, col_l0b = st.columns(2)
                with col_l0:
                    batch_letras = st.number_input(
                        "Importar letras/cifras (por vez)",
                        min_value=3,
                        max_value=50,
                        value=10,
                        step=1,
                        key="batch_letras_n",
                    )
                    if st.button("📜 Importar lote no repertório", use_container_width=True):
                        try:
                            with st.spinner(
                                f"Importando até {int(batch_letras)} música(s)…"
                            ):
                                df = louvores_df.copy()
                                df, n = enrich_louvores_letras_cifras(
                                    df, use_web=True, limit=int(batch_letras)
                                )
                            save_data(df, LOUVORES_FILE)
                            st.success(f"{n} música(s) salvas no banco.")
                            st.rerun()
                        except Exception as exc:
                            show_exception_error(exc, context="Importar letras e cifras")
                with col_l0b:
                    if st.button("🔍 Links de pesquisa (rápido)", use_container_width=True):
                        try:
                            df = louvores_df.copy()
                            df, n = enrich_dataframe(df, use_web=False)
                            save_data(df, LOUVORES_FILE)
                            st.success(f"{n} música(s) com links de pesquisa.")
                            st.rerun()
                        except Exception as exc:
                            show_exception_error(exc)
                with st.expander(
                    "✅ Validação bíblica de louvor",
                    expanded=st.session_state.pop("rep_show_validation", False),
                ):
                    _render_louvor_validation_search(louvores_df)
                with st.expander("✏️ Editar / excluir louvor", expanded=False):
                    _render_louvores_edit_manager(louvores_df)

    with col_side:
        render_repertorio_sidebar(louvores_df, programa_df, is_manager=mgr)
        if st.session_state.pop("rep_show_categories", False):
            st.info("Use os filtros **Tema** e **Tag bíblica** na área principal.")
    mobile_stack_close()

    render_repertorio_page_close()



def show_eventos_page(eventos_df: pd.DataFrame, members_df: pd.DataFrame):
    st.markdown('<p class="music-panel-title">📅 Eventos do ministério</p>', unsafe_allow_html=True)
    mgr = is_scale_manager(st.session_state.user_roles)

    if mgr:
        with st.expander("➕ Cadastrar / editar evento", expanded=False):
            with st.form(key="evento_form"):
                titulo = st.text_input("Título do evento")
                desc = st.text_area("Descrição")
                d1 = st.date_input("Data do evento")
                d2 = st.date_input("Data final (opcional)", value=None)
                img = st.text_input("URL da imagem (opcional)", placeholder="https://...")
                salvar = st.form_submit_button("Publicar evento", type="primary")
            if salvar:
                if not titulo.strip():
                    show_form_error("Informe o título.")
                else:
                    end = d2.strftime("%Y-%m-%d") if d2 else ""
                    nova = {
                        "id": new_id(),
                        "title": event_plain_text(titulo, max_len=200),
                        "description": event_plain_text(desc, max_len=2000),
                        "event_date": d1.strftime("%Y-%m-%d"),
                        "end_date": end,
                        "image_url": img.strip(),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "created_by_email": st.session_state.user_email,
                        "created_by_name": st.session_state.user_full_name
                        or st.session_state.user_name,
                    }
                    save_data(
                        pd.concat([eventos_df, pd.DataFrame([nova])], ignore_index=True),
                        EVENTOS_FILE,
                    )
                    st.success("Evento publicado!")
                    st.rerun()

    if eventos_df.empty:
        st.info("Nenhum evento cadastrado ainda.")
        return

    df = eventos_df.copy()
    df["_d"] = pd.to_datetime(df["event_date"], errors="coerce")
    df = df.sort_values("_d", ascending=False)
    for _, ev in df.iterrows():
        try:
            d = pd.to_datetime(ev["event_date"]).strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            d = str(ev.get("event_date", ""))
        img = str(ev.get("image_url", "")).strip()
        if img.startswith("http"):
            st.image(img, use_container_width=True)
        st.subheader(event_plain_text(ev.get("title", "Evento"), max_len=200))
        st.caption(f"📅 {d}")
        desc_plain = event_plain_text(ev.get("description", ""), max_len=2000)
        if desc_plain:
            st.write(desc_plain)
        if mgr and st.button("🗑️ Remover", key=f"del_ev_{ev['id']}"):
            eventos_df = eventos_df[eventos_df["id"].astype(str) != str(ev["id"])]
            save_data(eventos_df, EVENTOS_FILE)
            st.rerun()
        st.markdown("---")


def _render_minhas_sugestoes_louvor(sugestoes_df: pd.DataFrame):
    """Lista de sugestões do usuário logado com status atual."""
    email = str(st.session_state.get("user_email", "")).strip().lower()
    if not email or sugestoes_df.empty:
        return
    mine = sugestoes_df[
        sugestoes_df["suggester_email"].astype(str).str.strip().str.lower() == email
    ].copy()
    if mine.empty:
        return
    mine["_ord"] = pd.to_datetime(mine["created_at"], errors="coerce")
    mine = mine.sort_values("_ord", ascending=False).drop(columns=["_ord"])

    st.markdown("---")
    st.subheader("📬 Acompanhe suas sugestões")
    st.caption(
        "Status: **Pendente** (enviada) → **Em análise** (liderança recebeu) → "
        "**Aprovada** ou **Recusada**."
    )
    for _, s in mine.iterrows():
        status = normalize_sugestao_status(str(s.get("status", "")))
        nota = csv_cell_text(s.get("review_notes", ""))
        nota_html = (
            f'<p class="sugestao-track-meta">💬 {html.escape(nota)}</p>' if nota else ""
        )
        st.markdown(
            f'<div class="sugestao-track-card">'
            f'<p class="sugestao-track-title">{html.escape(str(s["title"]))}</p>'
            f'<p class="sugestao-track-meta">Enviada em {html.escape(str(s.get("created_at", "")))} '
            f"· {sugestao_status_badge_html(status)}</p>"
            f"{nota_html}</div>",
            unsafe_allow_html=True,
        )
        yt = str(s.get("youtube_url", "")).strip()
        if yt.startswith("http"):
            st.link_button("▶ YouTube", yt, key=f"yt_mine_{s['id']}")


def _gestao_salvar_nota(sugestoes_df: pd.DataFrame, sid: str, nota: str) -> pd.DataFrame:
    sugestoes_df = prepare_sugestoes(sugestoes_df)
    mask = sugestoes_df["id"].astype(str) == sid
    if nota:
        sugestoes_df.loc[mask, "review_notes"] = nota
    return sugestoes_df


def _gestao_receber(sid: str, sugestoes_df: pd.DataFrame, nota: str) -> None:
    sugestoes_df = _gestao_salvar_nota(sugestoes_df, sid, csv_cell_text(nota))
    mask = sugestoes_df["id"].astype(str) == sid
    sugestoes_df.loc[mask, "status"] = SUGESTAO_STATUS_EM_ANALISE
    save_data(sugestoes_df, SUGESTOES_FILE)
    st.success("Sugestão marcada como **em análise**.")


def _gestao_aprovar(
    s: pd.Series,
    sid: str,
    sugestoes_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    nota: str,
) -> None:
    sugestoes_df = _gestao_salvar_nota(sugestoes_df, sid, csv_cell_text(nota))
    _aprovar_sugestao_louvor(s, sugestoes_df, louvores_df)
    st.success("Aprovada! Publicada no Feed e no repertório.")


def _gestao_recusar(sid: str, sugestoes_df: pd.DataFrame, nota: str) -> None:
    sugestoes_df = _gestao_salvar_nota(sugestoes_df, sid, csv_cell_text(nota))
    mask = sugestoes_df["id"].astype(str) == sid
    sugestoes_df.loc[mask, "status"] = SUGESTAO_STATUS_RECUSADA
    save_data(sugestoes_df, SUGESTOES_FILE)
    st.success("Sugestão **recusada**.")


def _gestao_acoes_botoes(
    c_recv,
    c_ap,
    c_rj,
    status: str,
    sid: str,
    s: pd.Series,
    sugestoes_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    motivo: str,
    kp: str,
    i: int,
) -> None:
    if c_recv is not None:
        with c_recv:
            if status == SUGESTAO_STATUS_PENDENTE and st.button(
                "📥 Receber (em análise)",
                key=f"recv_{kp}_{i}_{sid}",
                use_container_width=True,
            ):
                _gestao_receber(sid, sugestoes_df, motivo)
                st.rerun()
    with c_ap:
        if st.button("✅ Aprovar", key=f"ap_{kp}_{i}_{sid}", use_container_width=True):
            _gestao_aprovar(s, sid, sugestoes_df, louvores_df, motivo)
            st.rerun()
    with c_rj:
        if st.button("❌ Recusar", key=f"rj_{kp}_{i}_{sid}", use_container_width=True):
            _gestao_recusar(sid, sugestoes_df, motivo)
            st.rerun()


def _render_gestao_sugestoes_lideranca(
    sugestoes_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    *,
    premium: bool = False,
    tab_filter: str | None = None,
    key_prefix: str = "gest",
):
    """Painel da liderança: receber (em análise), aprovar ou recusar."""
    from sugestao_louvor_ui import (
        build_suggestion_row_html,
        parse_extra_from_notes,
        render_gestao_card_close,
        render_gestao_card_open,
    )
    from ui_html import inject_ui_html

    df = prepare_sugestoes(sugestoes_df).copy()
    df["_st"] = df["status"].astype(str).map(normalize_sugestao_status)

    if tab_filter and tab_filter != "todas":
        df = df[df["_st"] == tab_filter]
    elif not premium:
        df = df[df["_st"].isin((SUGESTAO_STATUS_PENDENTE, SUGESTAO_STATUS_EM_ANALISE))]

    if df.empty:
        st.info("Nenhuma sugestão neste filtro.")
        return

    df["_ord"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.sort_values("_ord", ascending=False).drop(columns=["_ord"])

    from sugestao_louvor_ui import user_facing_review_note

    kp = f"{key_prefix}_{tab_filter or 'fila'}"
    for i, (_, s) in enumerate(df.iterrows()):
        sid = str(s["id"])
        status = normalize_sugestao_status(str(s.get("status", "")))
        artista = parse_extra_from_notes(str(s.get("review_notes", "")))
        yt_url = str(s.get("youtube_url", "")).strip()
        can_act = status in (SUGESTAO_STATUS_PENDENTE, SUGESTAO_STATUS_EM_ANALISE)
        msg_usuario = user_facing_review_note(str(s.get("review_notes", "")))

        if not premium:
            with st.expander(
                f"{s['title']} — {s['suggester_name']} · "
                f"{SUGESTAO_STATUS_LABELS.get(status, status)}",
                expanded=status == SUGESTAO_STATUS_PENDENTE,
            ):
                if yt_url.startswith("http"):
                    st.link_button("YouTube", yt_url, key=f"yt_ld_{kp}_{i}_{sid}")
                st.markdown(sugestao_status_badge_html(status), unsafe_allow_html=True)
                motivo = st.text_input(
                    "Observação para quem sugeriu (opcional)",
                    value=csv_cell_text(s.get("review_notes", "")),
                    key=f"nota_ld_{kp}_{i}_{sid}",
                )
                c1, c2, c3 = st.columns(3)
                _gestao_acoes_botoes(
                    c1, c2, c3, status, sid, s, sugestoes_df, louvores_df, motivo, kp, i
                )
            continue

        inject_ui_html('<div class="ig-sug-item">')
        c_info, c_yt = st.columns([5.2, 1])
        with c_info:
            st.markdown(
                build_suggestion_row_html(
                    str(s["title"]),
                    artista,
                    str(s.get("suggester_name", "")),
                    str(s.get("created_at", "")),
                    status,
                    SUGESTAO_STATUS_LABELS.get(status, status),
                ),
                unsafe_allow_html=True,
            )
        with c_yt:
            if yt_url.startswith("http"):
                st.link_button(
                    "▶ YouTube",
                    yt_url,
                    key=f"yt_ld_{kp}_{i}_{sid}",
                    use_container_width=True,
                )
            else:
                st.caption("—")

        if can_act:
            motivo = st.text_input(
                "Observação (opcional)",
                value=msg_usuario or csv_cell_text(s.get("review_notes", "")),
                key=f"nota_ld_{kp}_{i}_{sid}",
                label_visibility="collapsed",
                placeholder="Observação para quem sugeriu (opcional)",
            )
            if status == SUGESTAO_STATUS_PENDENTE:
                c_recv, c_ap, c_rj = st.columns(3)
            else:
                c_recv = None
                c_ap, c_rj = st.columns(2)
            _gestao_acoes_botoes(
                c_recv,
                c_ap,
                c_rj,
                status,
                sid,
                s,
                sugestoes_df,
                louvores_df,
                motivo,
                kp,
                i,
            )
        elif msg_usuario:
            inject_ui_html(
                f'<p class="ig-sug-item-note">{html.escape(msg_usuario)}</p>'
            )
        inject_ui_html("</div>")


def show_sugestao_louvor(sugestoes_df: pd.DataFrame, louvores_df: pd.DataFrame):
    from sugestao_louvor_ui import (
        SUGESTAO_TAB_LABELS,
        compute_sugestao_stats,
        pack_extra_notes,
        parse_extra_from_notes,
        render_footer_banner,
        render_form_card_checks_hint,
        render_form_card_close,
        render_form_card_open,
        render_sugestao_banner,
        render_sugestao_header,
        render_sugestao_kpis,
        render_sugestao_nova_button,
        render_sugestao_page_close,
        render_sugestao_page_open,
        render_sugestao_sidebar,
        build_suggestion_row_html,
        render_gestao_card_open,
        render_gestao_card_close,
    )

    mark_user_sugestoes_seen(
        sugestoes_df, str(st.session_state.get("user_email", ""))
    )
    sugestoes_df = prepare_sugestoes(sugestoes_df)
    mgr = is_scale_manager(st.session_state.user_roles)
    my_email = str(st.session_state.get("user_email", "")).strip().lower()

    from mobile_ui import mobile_hdr_close, mobile_hdr_open, mobile_stack_close, mobile_stack_open

    render_sugestao_page_open()
    mobile_hdr_open()
    col_hdr, col_btn = st.columns([4, 1])
    with col_hdr:
        render_sugestao_header()
    with col_btn:
        st.markdown('<div style="padding-top:0.5rem">', unsafe_allow_html=True)
        render_sugestao_nova_button()
        st.markdown("</div>", unsafe_allow_html=True)
    mobile_hdr_close()

    render_sugestao_banner()
    counts = compute_sugestao_stats(sugestoes_df, normalize_sugestao_status)
    render_sugestao_kpis(counts, SUGESTAO_STATUS_LABELS)

    mobile_stack_open()
    col_main, col_side = st.columns([3, 1])

    with col_main:
        render_form_card_open()
        with st.form(key="sugestao_form"):
            r1a, r1b = st.columns(2)
            with r1a:
                titulo = st.text_input("Nome da música *", placeholder="Nome da música")
            with r1b:
                artista = st.text_input("Artista / Ministério", placeholder="Artista ou ministério")
            yt = st.text_input("Link YouTube *", placeholder="https://youtube.com/...")
            r2a, r2b, r2c = st.columns(3)
            with r2a:
                tema = st.text_input("Tema bíblico", placeholder="Ex.: Adoração")
            with r2b:
                categoria = st.selectbox(
                    "Categoria",
                    ["", "Adoração", "Louvor", "Missões", "Comunhão", "Outra"],
                )
            with r2c:
                ministracao = st.text_input("Ministração sugerida", placeholder="Ex.: Abertura")
            r3a, r3b = st.columns(2)
            with r3a:
                tom = st.selectbox("Tom original", ["", "C", "D", "E", "F", "G", "A", "Bb"])
            with r3b:
                observacoes = st.text_area(
                    "Observações (opcional)",
                    placeholder="Adicione contexto para a liderança.",
                    height=80,
                )
            cc1, cc2, cc3, cc4 = st.columns(4)
            with cc1:
                tem_cifra = st.checkbox("Tem cifra")
            with cc2:
                tem_playback = st.checkbox("Tem playback")
            with cc3:
                tem_kit = st.checkbox("Tem kit voz")
            with cc4:
                tem_cong = st.checkbox("Versão congregacional")
            render_form_card_checks_hint()
            enviar = st.form_submit_button(
                "✈ Enviar sugestão",
                type="primary",
                use_container_width=True,
            )
        render_form_card_close()

        if enviar:
            if not titulo.strip() or not yt.strip():
                show_form_error("Informe nome e link do YouTube.")
            elif "youtube" not in yt.lower() and "youtu.be" not in yt.lower():
                st.warning("Use um link válido do YouTube.")
            else:
                extra = pack_extra_notes(
                    artista=artista,
                    tema=tema,
                    categoria=categoria,
                    ministracao=ministracao,
                    tom=tom,
                    observacoes=observacoes,
                    tem_cifra=tem_cifra,
                    tem_playback=tem_playback,
                    tem_kit=tem_kit,
                    tem_cong=tem_cong,
                )
                nova = {
                    "id": new_id(),
                    "title": titulo.strip().title(),
                    "youtube_url": yt.strip(),
                    "suggester_email": st.session_state.user_email,
                    "suggester_name": st.session_state.user_full_name
                    or st.session_state.user_name,
                    "status": SUGESTAO_STATUS_PENDENTE,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "review_notes": extra,
                }
                save_data(
                    prepare_sugestoes(
                        pd.concat([sugestoes_df, pd.DataFrame([nova])], ignore_index=True)
                    ),
                    SUGESTOES_FILE,
                )
                st.success("Sugestão enviada! Acompanhe o status no painel à direita.")
                st.rerun()

        if not sugestoes_df.empty and my_email:
            mine = sugestoes_df[
                sugestoes_df["suggester_email"].astype(str).str.strip().str.lower()
                == my_email
            ].copy()
            if not mine.empty:
                mine["_ord"] = pd.to_datetime(mine["created_at"], errors="coerce")
                mine = mine.sort_values("_ord", ascending=False).head(8)
                from ui_html import inject_ui_html as _inject

                _inject(
                    '<div class="ig-sug-card"><div class="ig-sug-card-title">Acompanhe suas sugestões</div>'
                )
                from sugestao_louvor_ui import user_facing_review_note

                for mi, (_, s) in enumerate(mine.iterrows()):
                    status = normalize_sugestao_status(str(s.get("status", "")))
                    sid_m = str(s["id"])
                    yt = str(s.get("youtube_url", "")).strip()
                    msg = user_facing_review_note(str(s.get("review_notes", "")))
                    _inject('<div class="ig-sug-item">')
                    c_row, c_yt = st.columns([5.2, 1])
                    with c_row:
                        st.markdown(
                            build_suggestion_row_html(
                                str(s["title"]),
                                parse_extra_from_notes(str(s.get("review_notes", ""))),
                                "Você",
                                str(s.get("created_at", "")),
                                status,
                                SUGESTAO_STATUS_LABELS.get(status, status),
                            ),
                            unsafe_allow_html=True,
                        )
                    with c_yt:
                        if yt.startswith("http"):
                            st.link_button(
                                "▶ YouTube",
                                yt,
                                key=f"yt_mine_{mi}_{sid_m}",
                                use_container_width=True,
                            )
                        else:
                            st.caption("—")
                    if msg:
                        _inject(
                            f'<p class="ig-sug-item-note">{html.escape(msg)}</p>'
                        )
                    _inject("</div>")
                _inject("</div>")

        if mgr:
            render_gestao_card_open()
            tab_map = {
                SUGESTAO_TAB_LABELS[0]: "todas",
                SUGESTAO_TAB_LABELS[1]: SUGESTAO_STATUS_PENDENTE,
                SUGESTAO_TAB_LABELS[2]: SUGESTAO_STATUS_EM_ANALISE,
                SUGESTAO_TAB_LABELS[3]: SUGESTAO_STATUS_APROVADA,
                SUGESTAO_TAB_LABELS[4]: SUGESTAO_STATUS_RECUSADA,
            }
            tabs = st.tabs(list(SUGESTAO_TAB_LABELS))
            for tab, label in zip(tabs, SUGESTAO_TAB_LABELS):
                with tab:
                    tf = tab_map[label]
                    _render_gestao_sugestoes_lideranca(
                        sugestoes_df,
                        louvores_df,
                        premium=True,
                        tab_filter=tf,
                        key_prefix=f"gest_tab_{tf}",
                    )
            render_gestao_card_close()

        render_footer_banner()

    with col_side:
        render_sugestao_sidebar(
            sugestoes_df,
            normalize_status=normalize_sugestao_status,
            status_labels=SUGESTAO_STATUS_LABELS,
        )
    mobile_stack_close()

    render_sugestao_page_close()


def _run_app() -> None:
    st.set_page_config(
        page_title=GROUP_NAME,
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_music_theme()
    ensure_session_state()

    if st.session_state.get("_feed_purge_v") != FEED_ONE_TIME_PURGE_VERSION:
        try:
            purge_all_feed_data()
        except Exception:
            pass
        st.session_state._feed_purge_v = FEED_ONE_TIME_PURGE_VERSION

    if "data_guard_initialized" not in st.session_state:
        snapshot_data_folder(DATA_DIR)
        st.session_state.data_guard_initialized = True

    members_df = load_data(MEMBERS_FILE, MEMBER_COLUMNS)
    members_df = ensure_developer_access(members_df)
    members_df = prepare_members(members_df)
    ensure_local_profile_photos(members_df)
    members_df = sync_recognized_member_roles(members_df)

    if try_restore_device_session(members_df):
        st.rerun()

    chat_df = prepare_chat(load_data(CHAT_FILE, CHAT_COLUMNS))
    escalas_df = prepare_escalas(load_data(ESCALAS_FILE, ESCALA_COLUMNS))
    trocas_df = prepare_trocas(load_data(TROCAS_FILE, TROCA_COLUMNS))
    programa_df = prepare_programa(load_data(PROGRAMA_FILE, PROGRAMA_COLUMNS))
    equipe_df = prepare_equipe(load_data(EQUIPE_FILE, EQUIPE_COLUMNS))
    playlist_df = prepare_playlist(load_data(PLAYLIST_FILE, PLAYLIST_COLUMNS))
    feed_posts_df, feed_likes_df, feed_comments_df = load_feed_bundle()
    louvores_df = prepare_louvores_with_meta(
        load_data(
            LOUVORES_FILE,
            (
                "title",
                "artist",
                "key",
                "youtube_url",
                "cifra_url",
                "ritmo",
                "letter",
                "source",
                *LOUVOR_EXTRA_COLUMNS,
                *LOUVOR_SEQUENCIA_COLUMNS,
            ),
        )
    )
    louvores_df["title"] = louvores_df["title"].astype(str).apply(fix_louvor_display_title)
    eventos_df = prepare_eventos(load_data(EVENTOS_FILE, EVENTO_COLUMNS))
    sugestoes_df = prepare_sugestoes(load_data(SUGESTOES_FILE, SUGESTAO_COLUMNS))
    chat_ensaio_df = prepare_chat_ensaio(load_data(CHAT_ENSAIO_FILE, CHAT_ENSAIO_COLUMNS))

    inject_mobile_app_shell()
    ensure_media_dirs()
    update_chat_latest_ts(chat_df)
    st.session_state["_chat_df_cache"] = chat_df
    _initial_unread = count_unread_chat_messages(chat_df)
    st.session_state.chat_unread_count = _initial_unread
    st.session_state._chat_unread_prev = _initial_unread

    if not st.session_state.authenticated:
        show_login_page(members_df)
        return

    if not session_is_valid(st.session_state):
        logout_user()
        st.warning(session_expired_user_message(st.session_state))
        show_login_page(members_df)
        return

    if handle_app_resume_query_params():
        if not st.session_state.get("authenticated"):
            try_restore_device_session(members_df)
        st.rerun()

    session_touch(st.session_state)

    dev_tok = str(st.session_state.get("device_session_token", "")).strip()
    if dev_tok and not st.session_state.get("_device_auth_injected"):
        inject_device_auth_token(dev_tok)
        st.session_state._device_auth_injected = True

    render_sidebar_profile(members_df)
    if "_escalas_bundle" not in st.session_state:
        try:
            refresh_escalas_bundle()
        except Exception:
            pass
    menu = render_sidebar_navigation()
    chat_unread = int(st.session_state.get("chat_unread_count", 0))
    user_email = str(st.session_state.get("user_email", ""))
    if is_scale_manager(st.session_state.user_roles):
        sug_badge = count_pending_sugestoes(sugestoes_df)
    else:
        sug_badge = count_sugestoes_news_for_user(sugestoes_df, user_email)
    try:
        escalas_b, _, equipe_b, trocas_alert_df = get_escalas_bundle()
        swap_alert_count = count_swap_alerts_for_user(
            trocas_alert_df,
            st.session_state.user_email,
            escalas_df=escalas_b,
            equipe_df=equipe_b,
        )
    except Exception:
        swap_alert_count = 0
    _escalas_global_sync()
    _feed_global_sync()
    _chat_global_sync()
    render_sidebar_footer(
        members_df=members_df,
        chat_unread=chat_unread,
        sug_badge=sug_badge,
        swap_alert_count=swap_alert_count,
    )
    render_data_loss_warning(members_df)

    email_hdr = str(st.session_state.get("user_email", "")).strip().lower()
    photo_hdr = profile_photo_to_data_uri(
        email_hdr, str(st.session_state.get("user_profile_photo", "")).strip()
    )
    notif_hdr = int(chat_unread) + int(sug_badge) + int(swap_alert_count)
    from dashboard_ui import render_global_header

    render_global_header(
        user_name=str(st.session_state.get("user_full_name", "")).strip()
        or str(st.session_state.user_name),
        photo_uri=photo_hdr,
        notif_count=notif_hdr,
    )

    if menu not in (
        "Dashboard",
        "Feed",
        "Avisos",
        "Escalas",
        "Gerenciar Escalas",
        "Repertório",
        "Playlist",
        "Sugestão de louvor",
        "Chat",
    ):
        page_header(menu)

    wa_open = st.session_state.pop("wa_auto_open_url", None)
    if wa_open:
        import json as _json

        inject_page_html(
            f'<script>window.open({_json.dumps(wa_open)}, "_blank", "noopener");</script>',
            height=0,
        )
        st.info(
            "O WhatsApp deve ter aberto em outra aba com a escala completa. "
            "Confirme o envio no grupo e anexe o PDF pelo botão verde no celular."
        )

    if menu in SWAP_ALERT_MENUS:
        escalas_alert, programa_alert, equipe_alert, trocas_alert = get_escalas_bundle()
        render_swap_alerts_panel(
            trocas_alert,
            escalas_alert,
            equipe_alert,
            key_prefix=f"alert_{menu}",
        )

    if menu == "Gerenciar Escalas":
        show_gerenciar_escalas(
            escalas_df, programa_df, equipe_df, louvores_df, members_df, chat_ensaio_df
        )

    elif menu == "Dashboard":
        show_dashboard(
            escalas_df,
            programa_df,
            equipe_df,
            louvores_df,
            members_df,
            playlist_df,
            trocas_df,
            eventos_df,
            feed_posts_df=feed_posts_df,
        )

    elif menu == "Avisos":
        show_feed_page(feed_posts_df, feed_likes_df, feed_comments_df)

    elif menu == "Repertório":
        show_louvores_catalog(
            louvores_df,
            programa_df=programa_df,
            sugestoes_df=sugestoes_df,
            playlist_df=playlist_df,
        )

    elif menu == "Feed":
        show_feed_page(feed_posts_df, feed_likes_df, feed_comments_df)

    elif menu == "Escalas":
        show_escalas_page(
            escalas_df,
            trocas_df,
            members_df,
            programa_df,
            equipe_df,
            louvores_df,
            chat_ensaio_df,
        )

    elif menu == "Eventos":
        show_eventos_page(eventos_df, members_df)

    elif menu == "Sugestão de louvor":
        show_sugestao_louvor(sugestoes_df, louvores_df)

    elif menu == "Playlist":
        show_playlist_page(louvores_df, playlist_df, members_df)

    elif menu == "Chat":
        show_group_chat(chat_df, members_df)

    elif menu == "Perfil":
        show_user_profile(members_df, escalas_df, equipe_df)

    elif menu == "Membros":
        if can_reset_member_passwords():
            show_members_overview(members_df, louvores_df, escalas_df, equipe_df)
        else:
            st.markdown('<p class="music-panel-title">🎹 Equipe de louvor</p>', unsafe_allow_html=True)
            st.write("Integrantes do ministério.")
            visible = members_visible_to_group(members_df)
            if not visible.empty:
                display_df = visible.drop(
                    columns=["password_hash", "profile_photo"], errors="ignore"
                )
                page_members = paginate_dataframe(display_df, 15, "membros")
                st.dataframe(page_members, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum membro cadastrado ainda.")

    from app_time import now_local

    year = now_local().year
    st.markdown(
        f'<p class="ig-footer">© {year} IGREJA · Gestão Ministerial — {html.escape(GROUP_NAME)}</p>',
        unsafe_allow_html=True,
    )

    pending = st.session_state.pop("_pending_menu_refresh", None)
    if pending and pending == menu:
        st.rerun()


def main() -> None:
    try:
        _run_app()
    except Exception as exc:
        try:
            st.set_page_config(page_title=GROUP_NAME, page_icon="🎵", layout="wide")
        except Exception:
            pass
        try:
            apply_music_theme()
        except Exception:
            pass
        from user_feedback import is_dev_viewer

        if is_dev_viewer():
            show_exception_error(exc, context="Falha na aplicação")
        else:
            st.info(MSG_IMPROVEMENTS)


if __name__ == "__main__":
    main()
