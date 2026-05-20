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
    SESSION_MINUTES,
    format_local,
    now_local,
    parse_timestamp,
    to_local_timestamps,
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
    load_csv_preserve_rows,
    members_save_allowed,
    snapshot_data_folder,
)
from password_reset import (
    apply_password_reset,
    create_password_reset_request,
    email_is_configured,
    validate_reset_token,
)
from escala_member_stats import format_date_br, member_escala_stats
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
EQUIPE_FILE = DATA_DIR / "escala_equipe.csv"
PLAYLIST_FILE = DATA_DIR / "playlist.csv"
LOUVORES_FILE = DATA_DIR / "louvores.csv"
EVENTOS_FILE = DATA_DIR / "eventos.csv"
SUGESTOES_FILE = DATA_DIR / "sugestoes_louvor.csv"
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
FUNCAO_MINISTRADOR = "Ministrador"

MENU_ITEMS_BASE = [
    ("Dashboard", "🎼", "Sua semana, equipe e novidades"),
    ("Gerenciar Escalas", "🎯", "Montar cultos, equipe e louvores"),
    ("Catálogo", "🎶", "Repertório de louvores"),
    ("Escalas", "🎤", "Escalas, ensaio e trocas"),
    ("Eventos", "📅", "Próximos eventos do ministério"),
    ("Sugestão de louvor", "💡", "Sugerir música para o catálogo"),
    ("Playlist", "🎧", "Músicas do grupo"),
    ("Chat", "💬", "Comunicação"),
    ("Membros", "🎹", "Integrantes do ministério"),
    ("Perfil", "👤", "Sua foto e dados cadastrais"),
]
MENU_HEADERS = {
    "Dashboard": "Sua semana no ministério",
    "Gerenciar Escalas": "Painel de gestão de escalas",
    "Catálogo": "Catálogo de louvores",
    "Escalas": "Escalas, ensaio e trocas",
    "Eventos": "Eventos e novidades",
    "Sugestão de louvor": "Sugerir música ao catálogo",
    "Playlist": "Playlist do grupo",
    "Chat": "Chat do grupo",
    "Membros": "Integrantes do grupo",
    "Perfil": "Sua foto e dados cadastrais",
}
MENU_ACCENTS = {
    "Dashboard": "#a78bfa",
    "Gerenciar Escalas": "#f59e0b",
    "Catálogo": "#fbbf24",
    "Escalas": "#60a5fa",
    "Eventos": "#38bdf8",
    "Sugestão de louvor": "#4ade80",
    "Playlist": "#f472b6",
    "Chat": "#34d399",
    "Membros": "#fb923c",
    "Perfil": "#c084fc",
}

# Organização do menu por áreas (sidebar)
NAV_GROUP_ORDER = (
    ("Início", ("Dashboard",)),
    ("Culto & escalas", ("Escalas", "Gerenciar Escalas")),
    ("Repertório", ("Catálogo", "Playlist", "Sugestão de louvor")),
    ("Comunidade", ("Chat", "Eventos", "Membros")),
    ("Conta", ("Perfil",)),
)

DASHBOARD_QUICK_LINKS = (
    "Escalas",
    "Chat",
    "Eventos",
    "Playlist",
    "Catálogo",
    "Perfil",
)

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
        save_data(members_df, MEMBERS_FILE)
    return members_df


def get_menu_items_for_user(roles: str) -> list:
    hidden_for_members = {"Gerenciar Escalas", "Catálogo", "Membros"}
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
        section = [by_name[n] for n in names if n in by_name]
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
            "Função(s) musicais (opcional para Líder e organizadores)",
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
            show_form_error("Escolha pelo menos uma função musical.")
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
    return members_df


@st.cache_data
def load_data(file_path: Path, columns: tuple):
    df = load_csv_preserve_rows(file_path, columns)
    if file_path == MEMBERS_FILE and not df.empty and "email" in df.columns:
        df["email"] = df["email"].astype(str).str.strip().str.lower()
    return df


def save_data(df: pd.DataFrame, file_path: Path, *, force: bool = False) -> bool:
    """Grava CSV com backup prévio. Retorna False se proteção bloquear members."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_path == MEMBERS_FILE:
        ok, msg = members_save_allowed(df, file_path, force=force)
        if not ok:
            show_technical_error(msg)
            return False

    backup_csv_if_exists(file_path, DATA_DIR)
    df.to_csv(file_path, index=False)
    load_data.clear()
    return True


def new_id() -> str:
    return str(uuid.uuid4())[:8]


def email_to_photo_slug(email: str) -> str:
    return email.strip().lower().replace("@", "_at_").replace(".", "_")


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


def save_profile_photo(email: str, uploaded_file) -> str:
    PROFILE_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    raw = uploaded_file.getvalue()
    if not raw:
        raise ValueError("Arquivo de imagem vazio.")
    if len(raw) > 5 * 1024 * 1024:
        raise ValueError("Imagem muito grande (máx. 5 MB).")
    ext = Path(uploaded_file.name).suffix.lower()
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


# Na montagem de escalas: só Integrante ou Banda (papéis de liderança ficam no perfil)
ESCALA_FUNCOES_EXIBICAO = ["Integrante", "Banda"]


def roles_for_public_display(roles_str: str) -> str:
    """Oculta Líder/Organizador/Desenvolvedor — mostra funções musicais ou Integrante."""
    _, musician = split_member_roles(roles_str)
    if musician:
        return ", ".join(musician)
    return "Integrante"


def normalize_funcao_escala(funcao: str) -> str:
    """Converte função salva antiga (ex.: Desenvolvedor) para Integrante ou Banda."""
    f = str(funcao).strip()
    if f in ("Integrante", "Banda", "Responsável", FUNCAO_MINISTRADOR):
        if f == "Responsável":
            return FUNCAO_MINISTRADOR
        return f
    if f in LEADERSHIP_ROLES:
        return "Integrante"
    if f in MUSICIAN_ROLES:
        return "Banda"
    fl = f.lower()
    if any(k in fl for k in ("vocal", "guitar", "baix", "bater", "teclad", "violon")):
        return "Banda"
    return "Integrante"


def default_funcao_para_escala(row) -> str:
    _, musician = split_member_roles(str(row.get("roles", "")))
    return "Banda" if musician else "Integrante"


def members_options_escala(members_df: pd.DataFrame) -> dict[str, str]:
    """Lista de integrantes para escalas — apenas nome, sem cargos de liderança."""
    options = {}
    for _, row in members_visible_to_group(members_df).iterrows():
        email = str(row["email"]).strip().lower()
        if email:
            options[member_display_name(row)] = email
    return options


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
    return df[list(TROCA_COLUMNS)].copy()


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


def prepare_sugestoes(df: pd.DataFrame) -> pd.DataFrame:
    for column in SUGESTAO_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[list(SUGESTAO_COLUMNS)].copy()


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


def accept_open_swap(
    troca_row,
    accepter_email: str,
    accepter_name: str,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Aceita troca aberta ou assume vaga — atualiza escala e encerra pedidos relacionados."""
    escala_id = str(troca_row["escala_id_origem"])
    dest_id = str(troca_row.get("escala_id_destino", "")).strip()
    tipo = str(troca_row.get("tipo", "")).lower()

    if dest_id and tipo in ("direta", "com_escala", ""):
        escalas_df = execute_swap(escalas_df, escala_id, dest_id)
    else:
        idx = escalas_df.index[escalas_df["id"].astype(str) == escala_id]
        if len(idx):
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
    return escalas_df, equipe_df, trocas_df


def enrich_programa_from_catalog(
    programa_df: pd.DataFrame, louvores_df: pd.DataFrame
) -> pd.DataFrame:
    """Preenche youtube/cifra do catálogo quando ausentes na programação."""
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


def fix_louvor_display_title(title: str) -> str:
    """Correções ortográficas leves para exibição."""
    from catalog_sanitize import sanitize_catalog_text

    t = sanitize_catalog_text(title)
    fixes = {
        "Aclame ao senhor": "Aclame ao Senhor",
        "a alegria esta no coracao": "A alegria está no coração",
        "A alegria esta no coracao": "A alegria está no coração",
        "Autor da,nha fé": "Autor da minha fé",
        "Autor da minha fé": "Autor da minha fé",
        "a começar em": "A começar em mim",
        "A começar em": "A começar em mim",
    }
    tl = t.lower()
    for wrong, right in fixes.items():
        if tl == wrong.lower():
            return right
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    return t


def cifra_search_url(title: str, artist: str = "") -> str:
    from catalog_sanitize import sanitize_catalog_text

    q = f"{sanitize_catalog_text(title)} {sanitize_catalog_text(artist)}".strip()
    return f"https://www.cifraclub.com.br/?q={q.replace(' ', '+')}"


def escala_label(row) -> str:
    date = str(row.get("date", ""))
    event = str(row.get("event", ""))
    name = str(row.get("member_name") or row.get("responsible", ""))
    return f"{date} · {event} · {name}"


def user_escalas(escalas_df: pd.DataFrame, email: str) -> pd.DataFrame:
    email = email.strip().lower()
    mask = escalas_df["member_email"].astype(str).str.strip().str.lower() == email
    if not mask.any():
        name = st.session_state.user_name.strip().lower()
        mask = escalas_df["responsible"].astype(str).str.lower().str.contains(name, na=False)
    return escalas_df[mask].copy()


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

    principal = {
        "nome": str(escala_row.get("member_name") or escala_row.get("responsible", "")),
        "funcao": FUNCAO_MINISTRADOR,
        "email": str(escala_row.get("member_email", "")),
    }
    if principal["nome"]:
        team.append(principal)

    for _, row in equipe_por_escala(equipe_df, escala_id).iterrows():
        team.append(
            {
                "nome": str(row.get("member_name", "")),
                "funcao": normalize_funcao_escala(str(row.get("funcao", "Integrante"))),
                "email": str(row.get("member_email", "")),
            }
        )

    return team


def execute_swap(escalas_df: pd.DataFrame, escala_a: str, escala_b: str) -> pd.DataFrame:
    idx_a = escalas_df.index[escalas_df["id"] == escala_a]
    idx_b = escalas_df.index[escalas_df["id"] == escala_b]
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
        save_data(members_df, MEMBERS_FILE)
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


def set_user_session(user_row):
    st.session_state.authenticated = True
    st.session_state.user_name = user_row["first_name"]
    st.session_state.user_full_name = member_display_name(user_row)
    st.session_state.user_email = user_row["email"]
    st.session_state.user_roles = user_row["roles"]
    st.session_state.user_primary_role = parse_primary_role(user_row["roles"])
    st.session_state.user_profile_photo = str(user_row.get("profile_photo", ""))
    session_touch(st.session_state)


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
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        :root {
            --bg-deep: #07060d;
            --bg-surface: #12101c;
            --bg-elevated: #1a1728;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-accent: rgba(167, 139, 250, 0.35);
            --text-primary: #f4f2fa;
            --text-secondary: #a8a3b8;
            --accent-gold: #f5c842;
            --accent-violet: #8b5cf6;
            --radius-lg: 18px;
            --radius-md: 12px;
            --shadow-card: 0 12px 40px rgba(0, 0, 0, 0.35);
        }

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(ellipse 80% 50% at 0% 0%, rgba(139, 92, 246, 0.14) 0%, transparent 50%),
                radial-gradient(ellipse 60% 40% at 100% 100%, rgba(245, 200, 66, 0.08) 0%, transparent 45%),
                linear-gradient(180deg, var(--bg-deep) 0%, #0e0c16 50%, #14121f 100%);
        }
        [data-testid="stAppViewContainer"]::before { display: none; }
        [data-testid="stHeader"] { background: transparent !important; }
        .block-container {
            padding-top: 1rem;
            max-width: 1080px;
            position: relative;
            z-index: 1;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0c0a14 0%, #14111f 55%, #0a0810 100%) !important;
            border-right: 1px solid var(--border-subtle);
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 0.75rem;
        }
        .sidebar-brand {
            padding: 0.5rem 0.25rem 0.75rem;
            margin-bottom: 0.25rem;
        }
        .sidebar-brand h3 {
            color: var(--text-primary) !important;
            font-size: 1.05rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
            letter-spacing: -0.02em;
        }
        .sidebar-brand p {
            color: var(--text-secondary) !important;
            font-size: 0.78rem !important;
            margin: 0.2rem 0 0 !important;
        }
        .nav-group-label {
            color: var(--text-secondary);
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin: 1rem 0 0.35rem 0.15rem;
            padding: 0;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
            padding: 0.55rem 0.75rem !important;
            border-radius: var(--radius-md) !important;
            margin-bottom: 0.15rem !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            color: var(--text-secondary) !important;
            border: 1px solid transparent !important;
            transition: background 0.15s, border-color 0.15s, color 0.15s !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label:hover {
            background: rgba(139, 92, 246, 0.12) !important;
            color: var(--text-primary) !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-checked="true"],
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
            background: rgba(139, 92, 246, 0.22) !important;
            border-color: var(--border-accent) !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
            color: #fbbf24 !important;
            font-weight: 700;
            letter-spacing: 0.03em;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
            color: #e9e4f5 !important;
        }
        section[data-testid="stSidebar"] .stCaption {
            color: #a89bc4 !important;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
            padding: 0.6rem 0.85rem;
            border-radius: 10px;
            margin-bottom: 0.2rem;
            font-weight: 500;
            color: #d4cce8 !important;
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }
        section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
            background: rgba(139, 92, 246, 0.2);
            border-color: rgba(167, 139, 250, 0.35);
        }
        section[data-testid="stSidebar"] button {
            border-radius: 10px !important;
            font-weight: 600 !important;
        }

        /* Cabeçalho de página */
        .music-hero {
            background: rgba(26, 23, 40, 0.65);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.15rem 1.35rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-card);
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        }
        .music-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, var(--accent, #8b5cf6) 0%, transparent 55%);
            opacity: 0.12;
            pointer-events: none;
        }
        .music-hero::after {
            content: "";
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 4px;
            background: var(--accent, var(--accent-gold));
            border-radius: 4px 0 0 4px;
        }
        .music-hero h2 {
            margin: 0;
            color: var(--text-primary);
            font-size: 1.45rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            position: relative;
        }
        .music-hero p {
            margin: 0.3rem 0 0;
            color: var(--text-secondary);
            font-size: 0.88rem;
            position: relative;
        }
        .music-hero .notes-deco { display: none; }

        /* Atalhos do dashboard */
        .quick-nav-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 0.65rem;
            margin: 0.5rem 0 1.25rem;
        }
        .quick-nav-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 0.85rem 0.5rem;
            text-align: center;
            transition: transform 0.15s, border-color 0.15s, background 0.15s;
        }
        .quick-nav-card:hover {
            transform: translateY(-2px);
            border-color: var(--border-accent);
            background: rgba(139, 92, 246, 0.1);
        }
        .quick-nav-card .qn-icon { font-size: 1.5rem; display: block; margin-bottom: 0.35rem; }
        .quick-nav-card .qn-label {
            color: var(--text-primary);
            font-size: 0.72rem;
            font-weight: 600;
            line-height: 1.2;
        }

        /* Cards e painéis */
        .music-panel {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(167, 139, 250, 0.25);
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(8px);
        }
        .music-panel-title {
            color: #fbbf24;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin: 0 0 0.75rem;
        }

        /* Métricas estilo player */
        .music-stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin: 1rem 0 1.5rem;
        }
        @media (max-width: 900px) {
            .music-stats { grid-template-columns: repeat(2, 1fr); }
        }
        .music-stat {
            background: linear-gradient(145deg, rgba(30, 25, 55, 0.9), rgba(20, 16, 38, 0.95));
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 14px;
            padding: 1.1rem 1rem;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .music-stat:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(139, 92, 246, 0.25);
        }
        .music-stat-icon { font-size: 1.75rem; display: block; margin-bottom: 0.35rem; }
        .music-stat-value {
            display: block;
            font-size: 1.85rem;
            font-weight: 700;
            color: #faf8ff;
            line-height: 1.2;
        }
        .music-stat-label {
            display: block;
            font-size: 0.78rem;
            color: #a89bc4;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-top: 0.25rem;
        }

        /* Paginação */
        .music-pagination {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
            background: rgba(18, 14, 31, 0.8);
            border: 1px solid rgba(251, 191, 36, 0.35);
            border-radius: 12px;
            padding: 0.75rem 1.25rem;
            margin: 0.75rem 0 1rem;
        }
        .music-pagination span {
            color: #d4cce8;
            font-size: 0.9rem;
        }
        .music-pagination strong { color: #fbbf24; }

        /* Alertas e textos principais */
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li {
            color: #d4cce8;
        }
        h1, h2, h3 { color: #faf8ff !important; }
        div[data-testid="stMetric"] {
            background: rgba(26, 21, 48, 0.6);
            border: 1px solid rgba(167, 139, 250, 0.2);
            border-radius: 12px;
            padding: 0.75rem;
        }
        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(167, 139, 250, 0.2);
            border-radius: 14px;
            padding: 1rem;
        }
        div[data-testid="stTabs"] {
            background: rgba(18, 14, 31, 0.85) !important;
            border: 1px solid rgba(212, 175, 55, 0.25) !important;
            border-radius: 16px !important;
        }
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 10px;
        }

        /* Login */
        .login-wrap { max-width: 980px; margin: 0 auto; padding: 1rem 0 2rem; }
        .login-hero {
            background: linear-gradient(165deg, #1a1435 0%, #2d1f4e 40%, #120e1f 100%);
            border: 1px solid rgba(212, 175, 55, 0.4);
            border-radius: 20px;
            padding: 2.5rem 1.5rem;
            text-align: center;
            min-height: 420px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.45);
            position: relative;
            overflow: hidden;
        }
        .login-hero::before {
            content: "♫ ♪ ♩ ♬";
            position: absolute;
            font-size: 5rem;
            opacity: 0.06;
            top: 10%;
            letter-spacing: 1rem;
        }
        .login-hero img {
            width: 120px;
            filter: drop-shadow(0 4px 16px rgba(251, 191, 36, 0.4));
        }
        .login-hero h1 {
            color: #faf8ff;
            font-size: 1.6rem;
            font-weight: 700;
            margin: 1rem 0 0.4rem;
        }
        .login-hero .tagline { color: #c4b5fd; font-size: 0.95rem; }
        .login-hero .features { color: #a89bc4; font-size: 0.85rem; line-height: 1.9; }
        .login-panel-title {
            color: #faf8ff !important;
            font-size: 1.35rem;
            font-weight: 600;
        }
        .login-panel-sub { color: #a89bc4 !important; font-size: 0.9rem; }

        /* Chat entre integrantes */
        #chat-scroll-box {
            max-height: min(56vh, 540px);
            overflow-y: auto;
            overflow-x: hidden;
            padding: 0.5rem 0.35rem 0.75rem;
            margin-bottom: 0.5rem;
            border: 1px solid rgba(52, 211, 153, 0.25);
            border-radius: 14px;
            background: rgba(12, 10, 20, 0.55);
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
        }
        .chat-feed { min-height: 80px; }
        .chat-row-head {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.35rem;
        }
        .chat-row-name { font-weight: 600; color: #e9e4ff; font-size: 0.88rem; }
        .chat-row-time { color: #a89bc4; font-size: 0.78rem; }
        .chat-bubble {
            max-width: 82%;
            padding: 0.55rem 0.85rem;
            border-radius: 14px;
            margin: 0 0 0.5rem 0;
            line-height: 1.45;
            clear: both;
        }
        .chat-bubble audio, .chat-bubble img {
            max-width: 100%;
            display: block;
            margin-top: 0.35rem;
            border-radius: 8px;
        }
        .chat-compose-bar {
            margin-top: 0.25rem;
            padding-top: 0.35rem;
            border-top: 1px solid rgba(134, 150, 160, 0.15);
        }
        .chat-bubble.me {
            margin-left: auto;
            background: linear-gradient(135deg, #5b3fa6, #7c5cbf);
            border: 1px solid rgba(167, 139, 250, 0.5);
            border-bottom-right-radius: 4px;
        }
        .chat-bubble.other {
            margin-right: auto;
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(52, 211, 153, 0.35);
            border-bottom-left-radius: 4px;
        }
        .chat-meta {
            font-size: 0.72rem;
            color: #a89bc4;
            margin-bottom: 0.2rem;
        }
        .chat-text { color: #f3f0ff; font-size: 0.92rem; margin: 0; }

        /* Compositor estilo WhatsApp — abaixo das mensagens (fluxo natural) */
        .wa-composer-shell {
            position: relative;
            margin-top: 0.5rem;
            padding: 0.35rem 0 0.25rem;
            border-top: 1px solid rgba(134, 150, 160, 0.2);
        }
        .wa-composer-shell iframe {
            border-radius: 16px !important;
            border: 1px solid rgba(0, 168, 132, 0.25) !important;
        }
        [data-testid="stChatMessage"] {
            max-width: 85%;
        }
        [data-testid="stChatMessageContent"] {
            background: #2a3942 !important;
            border-radius: 12px !important;
            border: 1px solid rgba(134, 150, 160, 0.2) !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
            background: linear-gradient(135deg, #005c4b, #00a884) !important;
            border-color: rgba(0, 168, 132, 0.35) !important;
        }
        .swap-card {
            background: rgba(96, 165, 250, 0.1);
            border: 1px solid rgba(96, 165, 250, 0.35);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }
        .culto-week-card {
            background: linear-gradient(145deg, rgba(30, 25, 55, 0.95), rgba(18, 14, 31, 0.98));
            border: 1px solid rgba(167, 139, 250, 0.35);
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.25rem;
        }
        .culto-week-card h3 {
            color: #fbbf24;
            margin: 0 0 0.5rem;
            font-size: 1.2rem;
        }
        .culto-week-card .culto-date {
            color: #a89bc4;
            font-size: 0.88rem;
            margin-bottom: 0.75rem;
        }
        .team-chip {
            display: inline-block;
            background: rgba(139, 92, 246, 0.25);
            border: 1px solid rgba(167, 139, 250, 0.4);
            border-radius: 20px;
            padding: 0.35rem 0.75rem;
            margin: 0.2rem 0.35rem 0.2rem 0;
            font-size: 0.82rem;
            color: #e9e4f5;
        }
        .team-chip strong { color: #fbbf24; }
        .seq-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.6rem;
            height: 1.6rem;
            background: #fbbf24;
            color: #1a1435;
            border-radius: 50%;
            font-weight: 700;
            font-size: 0.8rem;
            margin-right: 0.5rem;
        }

        /* Cards de programa (mobile-friendly) */
        .prog-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(167, 139, 250, 0.3);
            border-radius: 12px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.6rem;
        }
        .prog-card .prog-parte {
            color: #fbbf24;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .prog-card .prog-louvor {
            color: #faf8ff;
            font-size: 1rem;
            font-weight: 600;
            margin: 0.35rem 0 0.2rem;
        }
        .prog-card .prog-meta {
            color: #a89bc4;
            font-size: 0.82rem;
            margin: 0;
            line-height: 1.5;
        }
        .prog-card a { color: #34d399; word-break: break-all; }

        .mobile-user-bar { display: none; }

        /* Botões de atalho (Streamlit) */
        div[data-testid="column"] button[kind="secondary"] {
            border-radius: var(--radius-md) !important;
        }
        .quick-nav-btn > button {
            min-height: 4.25rem !important;
            flex-direction: column !important;
            font-size: 0.78rem !important;
            line-height: 1.25 !important;
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid var(--border-subtle) !important;
        }
        .quick-nav-btn > button:hover {
            border-color: var(--border-accent) !important;
            background: rgba(139, 92, 246, 0.12) !important;
        }

        /* Botões com área de toque confortável */
        .stButton > button, .stFormSubmitButton > button {
            min-height: 2.75rem !important;
            font-size: 1rem !important;
        }

        /* Tabelas: rolagem horizontal no celular */
        div[data-testid="stDataFrame"] {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
        }

        /* ========== SMARTPHONE (até 768px) ========== */
        @media (max-width: 768px) {
            [data-testid="stAppViewContainer"]::before { display: none; }

            .block-container {
                max-width: 100% !important;
                padding: 0.35rem 0.65rem 5rem !important;
            }

            /* Colunas Streamlit empilham */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }

            .music-hero {
                padding: 1rem 1.1rem;
                margin-bottom: 0.85rem;
            }
            .music-hero h2 { font-size: 1.25rem; }
            .music-hero p { font-size: 0.85rem; }
            .music-hero .notes-deco { display: none; }

            .music-stats {
                grid-template-columns: repeat(2, 1fr);
                gap: 0.55rem;
                margin: 0.75rem 0 1rem;
            }
            .music-stat { padding: 0.75rem 0.5rem; }
            .music-stat-value { font-size: 1.45rem; }
            .music-stat-label { font-size: 0.68rem; }

            .login-wrap { padding: 0.25rem 0 1rem; }
            .login-hero {
                min-height: auto;
                padding: 1.5rem 1rem;
                margin-bottom: 1rem;
            }
            .login-hero h1 { font-size: 1.25rem; }
            .login-hero img { width: 90px; }

            .chat-feed { max-height: 55vh; padding: 0.75rem; }
            .chat-bubble { max-width: 92%; font-size: 0.95rem; }

            .culto-week-card { padding: 1rem; }
            .culto-week-card h3 { font-size: 1.05rem; }
            .team-chip {
                display: block;
                margin: 0.35rem 0;
                text-align: center;
            }

            .music-pagination {
                flex-direction: column;
                text-align: center;
                padding: 0.65rem;
            }

            div[data-testid="stTabs"] [data-baseweb="tab-list"] {
                flex-wrap: wrap;
            }
            div[data-testid="stTabs"] button[data-baseweb="tab"] {
                font-size: 0.78rem !important;
                padding: 0.5rem 0.65rem !important;
            }

            section[data-testid="stSidebar"] {
                min-width: min(88vw, 320px) !important;
            }

            h1 { font-size: 1.35rem !important; }
            h2, h3 { font-size: 1.1rem !important; }

            input, textarea, select {
                font-size: 16px !important; /* evita zoom automático no iOS */
            }
        }

        @media (max-width: 380px) {
            .music-stats { grid-template-columns: 1fr 1fr; }
            .music-stat-icon { font-size: 1.4rem; }
        }

        .profile-card {
            background: linear-gradient(145deg, rgba(45, 27, 78, 0.95), rgba(30, 20, 50, 0.98));
            border: 1px solid rgba(251, 191, 36, 0.25);
            border-radius: 16px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }
        .profile-avatar-placeholder {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: rgba(167, 139, 250, 0.2);
            border: 2px dashed rgba(251, 191, 36, 0.45);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3.5rem;
            margin: 0 auto 0.75rem;
        }
        .louvor-dropdown {
            background: rgba(28, 18, 48, 0.98);
            border: 1px solid rgba(251, 191, 36, 0.4);
            border-radius: 12px;
            padding: 0.35rem 0.5rem;
            margin: 0.35rem 0 0.75rem;
            max-height: 260px;
            overflow-y: auto;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
        }
        .louvor-dropdown .stButton > button {
            text-align: left !important;
            justify-content: flex-start !important;
            background: rgba(139, 92, 246, 0.15) !important;
            border: 1px solid rgba(167, 139, 250, 0.25) !important;
            margin-bottom: 0.35rem !important;
        }
        .louvor-selected-box {
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(167, 139, 250, 0.35);
            border-radius: 12px;
            padding: 0.65rem 0.85rem;
            margin-top: 0.5rem;
            min-height: 120px;
            max-height: 320px;
            overflow-y: auto;
        }
        .louvor-selected-title {
            color: #fbbf24;
            font-weight: 600;
            font-size: 0.95rem;
            margin: 0 0 0.5rem;
        }

        /* Dashboard moderno */
        .welcome-card {
            background: rgba(26, 23, 40, 0.75);
            border: 1px solid var(--border-accent);
            border-radius: var(--radius-lg);
            padding: 1.25rem 1.35rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-card);
            backdrop-filter: blur(10px);
        }
        .welcome-card h3 {
            color: var(--text-primary);
            margin: 0 0 0.35rem;
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        .welcome-card p { color: var(--text-secondary); margin: 0; font-size: 0.9rem; }
        .verse-of-day {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.14), rgba(139, 92, 246, 0.1));
            border: 1px solid rgba(212, 175, 55, 0.4);
            border-radius: 14px;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
        }
        .verse-of-day .verse-label {
            margin: 0 0 0.5rem;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #fbbf24;
        }
        .verse-of-day .verse-text {
            margin: 0;
            font-size: 1rem;
            line-height: 1.55;
            font-style: italic;
            color: #f3f0ff;
        }
        .verse-of-day .verse-ref {
            margin: 0.65rem 0 0;
            font-size: 0.88rem;
            font-weight: 600;
            color: #c4b5fd;
        }
        .status-escalado {
            background: rgba(52, 211, 153, 0.12);
            border: 1px solid rgba(52, 211, 153, 0.45);
            border-radius: 14px;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
            color: #d4cce8;
            line-height: 1.55;
        }
        .status-escalado .escala-linha {
            margin: 0.5rem 0 0;
            padding: 0.45rem 0 0;
            border-top: 1px solid rgba(52, 211, 153, 0.2);
        }
        .status-escalado .escala-linha:first-of-type {
            border-top: none;
            padding-top: 0.15rem;
        }
        .status-escalado .escala-evento {
            color: #faf8ff;
            font-weight: 600;
        }
        .status-escalado .escala-data {
            color: #a7f3d0;
            font-weight: 500;
        }
        .status-escalado .escala-funcao {
            color: #86efac;
        }
        .status-escalado .escala-ensaio {
            margin: 0.2rem 0 0.65rem;
            padding: 0.35rem 0 0.35rem 0.65rem;
            font-size: 0.92rem;
            border-left: 3px solid rgba(251, 191, 36, 0.55);
            line-height: 1.45;
        }
        .status-escalado .ensaio-ok {
            border-left-color: rgba(96, 165, 250, 0.65);
            color: #93c5fd;
        }
        .status-escalado .ensaio-pendente {
            color: #fde68a;
        }
        .ensaio-aviso-banner {
            background: rgba(251, 191, 36, 0.14);
            border: 1px solid rgba(251, 191, 36, 0.5);
            border-radius: 12px;
            padding: 0.85rem 1.1rem;
            margin: 0 0 0.85rem;
            color: #fef3c7;
            line-height: 1.5;
        }
        .ensaio-aviso-banner .ensaio-aviso-titulo {
            margin: 0;
            font-weight: 700;
            color: #fde68a;
        }
        .ensaio-aviso-banner .ensaio-aviso-sub {
            margin: 0.35rem 0 0;
            font-size: 0.9rem;
            color: #fcd34d;
        }
        .members-leader-wrap {
            overflow-x: auto;
            margin: 0.5rem 0 1rem;
            border-radius: 14px;
            border: 1px solid rgba(139, 92, 246, 0.35);
            background: rgba(15, 10, 30, 0.55);
        }
        .members-leader-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            color: #e8e4f5;
        }
        .members-leader-table th {
            text-align: left;
            padding: 0.75rem 0.85rem;
            font-size: 0.72rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #c4b5fd;
            background: rgba(139, 92, 246, 0.18);
            border-bottom: 1px solid rgba(139, 92, 246, 0.35);
            white-space: nowrap;
        }
        .members-leader-table td {
            padding: 0.65rem 0.85rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            vertical-align: middle;
        }
        .members-leader-table tr:hover td {
            background: rgba(139, 92, 246, 0.08);
        }
        .members-leader-table .col-foto {
            width: 56px;
        }
        .members-leader-table .mem-nome {
            font-weight: 600;
            color: #faf8ff;
        }
        .members-leader-table .mem-funcao {
            color: #c4b5fd;
            font-size: 0.85rem;
            max-width: 220px;
        }
        .badge-escalado-sim {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: rgba(52, 211, 153, 0.2);
            color: #6ee7b7;
            border: 1px solid rgba(52, 211, 153, 0.45);
        }
        .badge-escalado-nao {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            background: rgba(148, 163, 184, 0.15);
            color: #94a3b8;
            border: 1px solid rgba(148, 163, 184, 0.3);
        }
        .stat-pill {
            display: inline-block;
            min-width: 1.6rem;
            text-align: center;
            padding: 0.15rem 0.45rem;
            border-radius: 8px;
            font-weight: 700;
            background: rgba(251, 191, 36, 0.15);
            color: #fde68a;
        }
        .stat-pill-zero {
            background: rgba(148, 163, 184, 0.12);
            color: #94a3b8;
        }
        .status-nao-escalado {
            background: rgba(251, 191, 36, 0.08);
            border: 1px solid rgba(251, 191, 36, 0.35);
            border-radius: 14px;
            padding: 1rem 1.25rem;
            margin-bottom: 1rem;
        }
        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 0.85rem;
            margin: 0.75rem 0 1rem;
        }
        .team-member-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(167, 139, 250, 0.3);
            border-radius: 14px;
            padding: 0.85rem 0.65rem;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .team-member-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px rgba(139, 92, 246, 0.25);
        }
        .team-member-card .tm-name {
            color: #faf8ff;
            font-weight: 600;
            font-size: 0.88rem;
            margin: 0.45rem 0 0.15rem;
        }
        .team-member-card .tm-role {
            color: #a89bc4;
            font-size: 0.75rem;
        }
        .event-feed-card {
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 14px;
            padding: 1rem 1.15rem;
            margin-bottom: 0.75rem;
        }
        .event-feed-card h4 { color: #7dd3fc; margin: 0 0 0.35rem; }
        .event-feed-card .ev-date { color: #fbbf24; font-size: 0.82rem; }
        .swap-banner {
            background: rgba(96, 165, 250, 0.12);
            border: 1px solid rgba(96, 165, 250, 0.4);
            border-radius: 12px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.65rem;
        }
        .prog-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        .prog-btn {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            text-decoration: none !important;
        }
        .prog-btn-yt { background: #dc2626; color: #fff !important; }
        .prog-btn-kit { background: #b45309; color: #fff !important; }
        .prog-btn-cifra { background: #059669; color: #fff !important; }
        .prog-btn-letra { background: #7c3aed; color: #fff !important; }
        .voice-kit-banner {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.65rem 1rem;
            margin: 0.5rem 0 1rem;
            padding: 0.75rem 1rem;
            border-radius: 12px;
            border: 1px solid rgba(220, 38, 38, 0.45);
            background: rgba(220, 38, 38, 0.12);
        }
        .voice-kit-banner a {
            color: #fecaca !important;
            font-weight: 600;
            text-decoration: none;
        }
        .voice-kit-banner a:hover { text-decoration: underline; }
        .voice-kit-banner span {
            color: #c4b5fd;
            font-size: 0.85rem;
        }
        .catalog-table-wrap {
            overflow-x: auto;
            border-radius: 14px;
            border: 1px solid rgba(167, 139, 250, 0.35);
            margin: 0.75rem 0;
        }
        table.catalog-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }
        table.catalog-table th {
            background: rgba(139, 92, 246, 0.35);
            color: #faf8ff;
            padding: 0.65rem 0.75rem;
            text-align: center;
            font-weight: 600;
        }
        table.catalog-table td {
            padding: 0.55rem 0.75rem;
            text-align: center;
            border-bottom: 1px solid rgba(167, 139, 250, 0.15);
            color: #e9e4f5;
        }
        table.catalog-table tr:nth-child(even) td {
            background: rgba(255, 255, 255, 0.03);
        }
        table.catalog-table tr:hover td {
            background: rgba(139, 92, 246, 0.12);
        }
        table.catalog-table td:first-child { text-align: left; font-weight: 500; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_page_html(html_fragment: str, height: int = 0):
    """Injeta HTML/JS — components.html (compatível com Streamlit Cloud)."""
    body = html_fragment.strip()
    if not body:
        return
    import streamlit.components.v1 as components

    # height=0 em st.html quebra em algumas versões do Streamlit Cloud
    iframe_h = 0 if height <= 0 else height
    components.html(body, height=iframe_h, scrolling=False)


def inject_mobile_app_shell():
    """PWA (instalar pelo link) + service worker + OneSignal (se configurado)."""
    st.markdown(
        """
        <link rel="manifest" href="/manifest.webmanifest">
        <meta name="theme-color" content="#07060d">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Louvor IBBJ">
        <link rel="apple-touch-icon" href="/icon-192.png">
        """,
        unsafe_allow_html=True,
    )
    inject_page_html(
        """
        <script>
        if ("serviceWorker" in navigator) {
          navigator.serviceWorker.register("/sw.js").catch(function () {});
        }
        </script>
        """,
        height=0,
    )
    app_id = onesignal_app_id()
    if push_is_enabled() and app_id:
        inject_page_html(
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
            """,
            height=0,
        )


def render_mobile_and_push_panel():
    """Instalação no celular + ativar notificações."""
    with st.sidebar.expander("📲 App no celular e notificações", expanded=False):
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
        with st.sidebar.expander("🔑 Redefinir senhas (dev)", expanded=False):
            render_password_reset_panel(members_df, form_key_prefix="dev_sidebar")

    with st.sidebar.expander("🔔 Configurar push (admin)", expanded=False):
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


def render_sidebar_profile():
    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            <h3>🎵 {GROUP_NAME}</h3>
            <p>Ministério de louvor · IBBJ</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    photo_path = profile_photo_file(
        st.session_state.user_email,
        st.session_state.get("user_profile_photo", ""),
    )
    col_photo, col_info = st.sidebar.columns([1, 2])
    with col_photo:
        if photo_path:
            st.image(str(photo_path), width=72)
        else:
            st.markdown('<div style="font-size:2.2rem;text-align:center">👤</div>', unsafe_allow_html=True)
    with col_info:
        st.markdown(f"**{st.session_state.user_name}**")
        roles = str(st.session_state.user_roles).strip()
        if roles:
            st.caption(roles_for_public_display(roles))
    st.sidebar.markdown("---")
    if is_scale_manager(st.session_state.user_roles):
        render_registration_link_box(compact=True)
        st.sidebar.markdown("---")


def render_sidebar_navigation() -> str:
    """Menu lateral com seções visuais e seleção única."""
    groups = build_nav_groups_for_user(st.session_state.user_roles)
    flat: list[tuple[str, str, str]] = []
    for _, section in groups:
        flat.extend(section)
    names = [name for name, _, _ in flat]
    icons = {name: icon for name, icon, _ in flat}

    if "app_menu" not in st.session_state or st.session_state.app_menu not in names:
        st.session_state.app_menu = names[0] if names else "Dashboard"

    st.sidebar.markdown(
        '<p class="nav-group-label">Navegação</p>',
        unsafe_allow_html=True,
    )
    group_legend = " · ".join(g for g, _ in groups)
    st.sidebar.caption(group_legend)

    try:
        idx = names.index(st.session_state.app_menu)
    except ValueError:
        idx = 0

    # Sem key no widget: navegação só via app_menu (compatível com atalhos do Dashboard)
    picked = st.sidebar.radio(
        "Ir para",
        names,
        index=idx,
        format_func=lambda n, ic=icons: f"{ic.get(n, '🎵')}  {n}",
        label_visibility="collapsed",
    )
    if picked != st.session_state.app_menu:
        st.session_state.app_menu = picked
        st.rerun()
    return picked


def render_dashboard_quick_actions(roles: str):
    """Atalhos visuais na home para as telas mais usadas."""
    icons = menu_icons_map(roles)
    items, _, _ = get_menu_items_for_user(roles)
    available_names = {name for name, _, _ in items}
    links = [n for n in DASHBOARD_QUICK_LINKS if n in available_names and n != "Dashboard"]
    if not links:
        return

    st.markdown('<p class="music-panel-title">⚡ Acesso rápido</p>', unsafe_allow_html=True)
    cols = st.columns(min(len(links), 4))
    for col, name in zip(cols, links[:4]):
        with col:
            extra = " quick-nav-btn--chat" if name == "Chat" else ""
            st.markdown(f'<div class="quick-nav-btn{extra}">', unsafe_allow_html=True)
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
                extra = " quick-nav-btn--chat" if name == "Chat" else ""
                st.markdown(f'<div class="quick-nav-btn{extra}">', unsafe_allow_html=True)
                if st.button(
                    f"{icons.get(name, '🎵')}\n{name}",
                    key=f"quick_nav2_{name}",
                    use_container_width=True,
                ):
                    st.session_state.app_menu = name
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar_footer():
    render_mobile_and_push_panel()
    if st.sidebar.button("🚪  Sair", use_container_width=True, type="secondary"):
        session_logout(st.session_state)
        st.rerun()


def page_header(menu: str):
    from verse_of_day import render_verse_of_day

    render_verse_of_day()
    items, _, icons = get_menu_items_for_user(st.session_state.user_roles)
    icon = icons.get(menu, "🎵")
    title = MENU_HEADERS.get(menu, menu)
    subtitle = next((desc for name, _, desc in items if name == menu), "")
    accent = MENU_ACCENTS.get(menu, "#fbbf24")
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
        return "—", "Catálogo disponível no menu"
    if "escala" in label_l:
        return "—", "Nenhuma escala registrada"
    return "—", "Sem informações no momento"


def render_music_stats(stats: list[tuple[str, str, int]]):
    if not stats:
        st.caption("Resumo indisponível no momento.")
        return
    cols = st.columns(len(stats))
    for col, (icon, label, value) in zip(cols, stats):
        display_val, display_label = humanize_stat(value, label)
        with col:
            st.metric(label=f"{icon} {display_label}", value=display_val)


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


def render_login_brand():
    if CROSS_IMAGE.exists():
        cross_b64 = base64.b64encode(CROSS_IMAGE.read_bytes()).decode()
        cross_img = f'<img src="data:image/svg+xml;base64,{cross_b64}" alt="Cruz"/>'
    else:
        cross_img = '<div style="font-size:4rem;color:#d4af37;">✝</div>'

    st.markdown(
        f"""
        <div class="login-hero">
            {cross_img}
            <h1>{GROUP_NAME}</h1>
            <p class="tagline">Sistema de organização do ministério de louvor</p>
            <p class="features">
                🎶 Catálogo de louvores &nbsp;·&nbsp; 🎧 Playlist<br>
                🎤 Escalas &nbsp;·&nbsp; 🎼 Painel do ministério
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

    if st.button("← Voltar ao login", use_container_width=True):
        st.query_params.clear()
        st.rerun()


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

    if st.button("← Voltar ao login", use_container_width=True):
        st.query_params.clear()
        st.rerun()


def show_login_page(members_df: pd.DataFrame):
    apply_music_theme()
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)

    render_login_brand()

    st.markdown("---")

    if is_reset_password_page():
        render_reset_password_form(members_df)
    elif is_forgot_password_page():
        render_forgot_password_form(members_df)
    elif is_register_page():
        st.markdown(
            '<p class="login-panel-title">Cadastro de novo membro</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="login-panel-sub">Preencha seus dados para entrar no ministério de louvor.</p>',
            unsafe_allow_html=True,
        )
        render_register_form(members_df)
        if st.button("← Já tenho conta — ir para o login", use_container_width=True):
            st.query_params.clear()
            st.rerun()
    else:
        st.markdown('<p class="login-panel-title">Acesso ao sistema</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="login-panel-sub">Entre com sua conta ou cadastre-se como novo membro.</p>',
            unsafe_allow_html=True,
        )
        render_registration_link_box()

        tab_login, tab_register = st.tabs(["🎵 Entrar", "🎤 Cadastrar"])

        with tab_login:
            inject_login_restore_fields()
            with st.form(key="login_form"):
                login_email = st.text_input("Email")
                login_password = st.text_input("Senha", type="password")
                remember_me = st.checkbox(
                    "Lembrar login e senha neste dispositivo",
                    help="Salva no navegador deste aparelho. Use só em celular ou PC pessoal.",
                )
                login_button = st.form_submit_button(
                    "Entrar", type="primary", use_container_width=True
                )

            if st.button("🔑  Esqueci minha senha", use_container_width=True):
                st.query_params.clear()
                st.query_params[FORGOT_PASSWORD_QUERY_PARAM] = "1"
                st.rerun()

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
                    set_user_session(user)
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

        with tab_register:
            render_register_form(members_df)

    st.markdown("</div>", unsafe_allow_html=True)


def load_chat_df() -> pd.DataFrame:
    """Recarrega o chat do disco (evita DataFrame desatualizado na sessão)."""
    load_data.clear()
    return prepare_chat(load_data(CHAT_FILE, CHAT_COLUMNS))


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


def render_chat_messages(chat_df: pd.DataFrame, members_df: pd.DataFrame):
    if chat_df.empty:
        st.caption("💬 Nenhuma mensagem ainda — use o campo abaixo.")
        return

    my_email = st.session_state.user_email.strip().lower()
    chat_sorted = sort_chat_messages(chat_df)

    parts = ['<div id="chat-scroll-box" class="chat-feed">']
    for _, row in chat_sorted.iterrows():
        is_me = str(row.get("email", "")).strip().lower() == my_email
        display_name = "Você" if is_me else str(row.get("name", "Integrante"))
        time_str = format_local(row.get("timestamp"), "%d/%m %H:%M")
        email = str(row.get("email", "")).strip().lower()
        foto = member_photo_html(email, members_df, 32)
        css = "me" if is_me else "other"
        mtype = str(row.get("message_type", "text") or "text").strip().lower()
        if mtype == "audio":
            body = _chat_media_html("audio", str(row.get("media_file", "")))
        elif mtype == "image":
            body = _chat_media_html("image", str(row.get("media_file", "")))
        else:
            body = f'<p class="chat-text">{_escape_chat_html(row.get("message", ""))}</p>'
        parts.append(
            f'<div class="chat-bubble {css}">'
            f'<div class="chat-row-head">{foto}'
            f'<span class="chat-row-name">{_escape_chat_html(display_name)}</span>'
            f'<span class="chat-row-time"> · {time_str}</span></div>'
            f"{body}</div>"
        )
    parts.append('<div id="chat-scroll-end" style="height:1px;"></div>')
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)
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
    pending_key = pending_text_key("group_chat")
    pending = st.session_state.pop(pending_key, None)
    if pending and str(pending).strip():
        append_chat_message(message=str(pending).strip(), message_type="text", media_file="")

    mark_chat_seen(load_chat_df())
    st.markdown('<p class="music-panel-title">💬 Conversa do grupo</p>', unsafe_allow_html=True)
    _chat_group_live(members_df)


@st.fragment(run_every=timedelta(seconds=4))
def _chat_group_live(members_df: pd.DataFrame):
    """Atualiza o histórico a cada poucos segundos para refletir mensagens de outros integrantes."""
    chat_df = load_chat_df()
    st.session_state["_chat_df_cache"] = chat_df
    st.session_state.chat_unread_count = 0

    def _append(**kwargs):
        append_chat_message(**kwargs)

    render_chat_messages(chat_df, members_df)
    render_chat_composer(
        key_prefix="group_chat",
        append_fn=_append,
        audio_dir=CHAT_AUDIO_DIR,
        audio_prefix="chat",
        images_dir=CHAT_IMAGES_DIR,
        image_prefix="chat",
    )


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


def render_culto_programa(
    escala_row,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame | None = None,
    *,
    ensaio_notice: bool = False,
):
    escala_id = str(escala_row.get("id", ""))
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
    nipe_me = vocal_nipe_from_roles(roles_me, bio=bio_me)
    if nipe_me:
        st.caption(
            f"Use **Kit Voz** em cada música — busca: "
            f"*Kit Voz {nipe_me.lower()} - [nome do louvor]* "
            f"(ex.: Kit Voz {nipe_me.lower()} - Santo pra Sempre)."
        )
    else:
        st.caption(
            "Para ver o kit de voz no YouTube, cadastre sua função vocal "
            "(ex.: Vocalista - Tenor) em **Perfil**."
        )

    for _, item in prog.iterrows():
        artist = sanitize_catalog_text(item.get("artist", ""))
        louvor = fix_louvor_display_title(sanitize_catalog_text(item.get("louvor_title", "")))
        titulo = format_louvor_display(louvor, artist)
        tom = sanitize_catalog_text(item.get("key", ""))
        leader = sanitize_catalog_text(item.get("leader_name", ""))
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
        if nipe_me and louvor:
            kit_url = voice_kit_youtube_url(nipe_me, louvor)
            kit_label = html.escape(voice_kit_search_query(nipe_me, louvor))
            btns.append(
                f'<a class="prog-btn prog-btn-kit" href="{kit_url}" target="_blank" rel="noopener" '
                f'title="{kit_label}">🎤 Kit Voz</a>'
            )
        btns.append(
            f'<a class="prog-btn prog-btn-letra" href="{cifra}" target="_blank" rel="noopener">📜 Letra / Cifra</a>'
        )
        btns_html = f'<div class="prog-actions">{"".join(btns)}</div>' if btns else ""
        meta = " · ".join(x for x in [f"Tom: {tom}" if tom else "", f"🎤 {leader}" if leader else ""] if x)
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


def render_dashboard_swap_alerts(
    trocas_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
):
    abertas = trocas_abertas_pendentes(trocas_df)
    if abertas.empty:
        return
    my_email = st.session_state.user_email.strip().lower()
    st.markdown('<p class="music-panel-title">🔄 Trocas disponíveis</p>', unsafe_allow_html=True)
    for _, t in abertas.iterrows():
        if str(t.get("requester_email", "")).strip().lower() == my_email:
            continue
        o = escalas_df[escalas_df["id"].astype(str) == str(t["escala_id_origem"])]
        label = escala_label(o.iloc[0]) if not o.empty else "Escala"
        st.markdown(
            f'<div class="swap-banner"><strong>{t["requester_name"]}</strong> '
            f"solicitou troca · <em>{label}</em></div>",
            unsafe_allow_html=True,
        )
        if t.get("message"):
            st.caption(str(t["message"]))
        if st.button(
            "✅ Assumir esta troca",
            key=f"dash_swap_{t['id']}",
            use_container_width=True,
        ):
            name = st.session_state.user_full_name or st.session_state.user_name
            escalas_df, _, trocas_df = accept_open_swap(
                t, my_email, name, escalas_df, pd.DataFrame(), trocas_df
            )
            save_data(escalas_df, ESCALAS_FILE)
            save_data(trocas_df, TROCAS_FILE)
            st.success("Troca realizada! A solicitação saiu do painel de todos.")
            st.rerun()


def render_events_feed(eventos_df: pd.DataFrame, limit: int = 5):
    if eventos_df.empty:
        return
    st.markdown('<p class="music-panel-title">📰 Próximos eventos</p>', unsafe_allow_html=True)
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


def show_dashboard(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
    trocas_df: pd.DataFrame,
    eventos_df: pd.DataFrame,
):
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    nome = st.session_state.user_name
    is_mgr = is_scale_manager(st.session_state.user_roles)
    st.markdown(
        f"""
        <div class="welcome-card">
            <h3>Olá, {nome}! 👋</h3>
            <p>Bem-vindo(a) ao painel do {GROUP_NAME}. Aqui você acompanha sua escala e o ministério.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    start, end = week_bounds(st.session_state.week_offset)
    my_email = st.session_state.user_email.strip().lower()
    minhas = user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)

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
        st.markdown(
            '<div class="status-nao-escalado">ℹ️ <strong>Você não está escalado(a) nesta semana.</strong> '
            "Quando for escalado, a informação aparecerá aqui no início do painel.</div>",
            unsafe_allow_html=True,
        )

    render_dashboard_swap_alerts(trocas_df, escalas_df)
    render_events_feed(eventos_df)
    render_dashboard_quick_actions(st.session_state.user_roles)

    st.markdown('<p class="music-panel-title">📅 Cultos da semana</p>', unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center;color:#fbbf24;font-weight:600;margin:0.25rem 0 0.75rem'>"
        f"Semana {start.strftime('%d/%m')} — {end.strftime('%d/%m/%Y')}</p>",
        unsafe_allow_html=True,
    )
    w1, w2 = st.columns(2)
    with w1:
        if st.button("◀ Semana anterior", use_container_width=True):
            st.session_state.week_offset -= 1
            st.rerun()
    with w2:
        if st.button("Próxima semana ▶", use_container_width=True):
            st.session_state.week_offset += 1
            st.rerun()

    if st.session_state.week_offset != 0 and st.button("📍 Voltar para semana atual", use_container_width=True):
        st.session_state.week_offset = 0
        st.rerun()

    semana = escalas_na_semana(escalas_df, start, end)

    if is_mgr:
        render_music_stats(
            [
                ("🎤", "Cultos na semana", len(semana)),
                ("🎹", "Integrantes", len(members_visible_to_group(members_df))),
                ("🎶", "Louvores catálogo", len(louvores_df)),
            ]
        )
    else:
        render_music_stats(
            [
                ("🎧", "Playlist", len(playlist_df)),
            ]
        )

    if semana.empty:
        st.info(
            "Nenhum culto nesta semana por enquanto. Quando houver escala, ela aparecerá aqui para todos."
        )
        return

    minhas_ids = {
        str(item["escala"]["id"])
        for item in user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)
    }
    for _, escala in semana.iterrows():
        render_culto_programa(
            escala,
            programa_df,
            equipe_df,
            members_df,
            louvores_df,
            ensaio_notice=str(escala.get("id", "")) in minhas_ids,
        )


def show_user_profile(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
):
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
            st.session_state["_pending_profile_photo"] = uploaded
        if st.button("💾 Salvar foto", use_container_width=True, key="save_profile_photo"):
            pending = st.session_state.pop("_pending_profile_photo", None) or uploaded
            if pending is None:
                st.warning("Escolha uma imagem antes de salvar.")
            else:
                try:
                    filename = save_profile_photo(email, pending)
                    members_df.at[idx, "profile_photo"] = filename
                    save_data(members_df, MEMBERS_FILE)
                    st.session_state.user_profile_photo = filename
                    st.success("Foto atualizada!")
                    st.rerun()
                except ValueError as exc:
                    show_form_error(str(exc))
                except Exception:
                    show_technical_error("Não foi possível salvar a foto.")
        if photo_path and st.button("🗑️ Remover foto", use_container_width=True, key="rm_profile_photo"):
            photo_path.unlink(missing_ok=True)
            members_df.at[idx, "profile_photo"] = ""
            save_data(members_df, MEMBERS_FILE)
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
                "Função(ões) musicais (opcional para líderes)"
                if leadership
                else "Função(ões) musicais"
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
                show_form_error("Selecione pelo menos uma função musical.")
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
    st.caption(f"🎶 {len(louvores_df)} louvores disponíveis no catálogo para montar o culto.")


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
        st.write("")
        if st.button("Buscar", key=f"{key_prefix}_lq_go", use_container_width=True):
            commit_query()

    if _TEXT_INPUT_HAS_BIND:
        st.session_state[active_key] = str(st.session_state.get(qkey, "")).strip()
        st.caption("A lista filtra enquanto você digita. Toque em ➕ para selecionar.")
    else:
        st.caption(
            "Digite, pressione **Enter** ou **Buscar**, depois toque em **➕** "
            "(pode adicionar vários sem buscar de novo)."
        )

    query = str(st.session_state.get(active_key, "")).strip()
    if len(query) < 1:
        st.info("Digite pelo menos 1 letra e use **Buscar** ou **Enter**.")
        return

    filtered = filter_louvores_for_picker(louvores_df, query)
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
):
    st.markdown(
        f'<p class="louvor-selected-title">🎵 Selecionados ({len(picked)})</p>',
        unsafe_allow_html=True,
    )
    if not picked:
        st.markdown(
            '<div class="louvor-selected-box"><p style="color:#a89bc4;margin:0;font-size:0.88rem">'
            "Nenhum ainda — busque à esquerda e toque em ➕</p></div>",
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
) -> list[str]:
    """Busca à esquerda + lista de selecionados fixa à direita."""
    state_key = f"{key_prefix}_picked"
    if state_key not in st.session_state:
        st.session_state[state_key] = []

    picked: list[str] = list(st.session_state[state_key])
    full_catalog = louvores_catalog_options(louvores_df)

    col_busca, col_sel = st.columns([3, 2], gap="large")

    with col_busca:
        st.markdown("**🔍 Buscar no catálogo**")
        _louvor_search_panel(
            louvores_df, key_prefix, state_key, max_results=max_results
        )

    with col_sel:
        picked = list(st.session_state.get(state_key, []))
        _render_picked_louvores_panel(picked, full_catalog, key_prefix, state_key)

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
        st.caption("O catálogo de louvores ainda não foi carregado neste ambiente.")
        return
    search = st.text_input(
        "🔍 Digite as primeiras letras do louvor ou do artista",
        key=f"{key_prefix}_search",
    )
    filtered = filter_louvores_for_picker(louvores_df, search)
    show = filtered[["title", "artist", "key", "ritmo"]]
    show.columns = ["Louvor", "Artista", "Tom", "Ritmo"]
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.caption(f"{len(filtered)} louvor(es) no catálogo (sem limite de exibição).")


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

    novos = st.multiselect(
        "Adicionar integrantes à escala",
        available,
        key=f"{key_prefix}_eq_add",
        placeholder="Selecione um ou vários integrantes",
        on_change=_on_equipe_add_change,
    )
    funcao_nova = st.selectbox(
        "Função na escala", ESCALA_FUNCOES_EXIBICAO, key=f"{key_prefix}_eq_fun"
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
            st.success(f"{len(novas)} louvor(es) adicionado(s). O dashboard já está atualizado.")
            clear_louvor_picker_state(key_prefix)
            st.rerun()


def show_escala_completa_editor(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    chat_ensaio_df: pd.DataFrame | None = None,
):
    maybe_show_escala_mes_aviso()

    st.write(
        "Monte a escala completa: integrantes, louvores e salve. "
        "As alterações aparecem no **Dashboard** de todos os integrantes."
    )

    if members_df.empty:
        st.warning("Cadastre integrantes antes de montar escalas.")
        return

    member_map = members_options_escala(members_df)
    NOVA_ESCALA = "➕ Nova escala"
    todas = escalas_ordenadas(escalas_df)
    escala_labels = [NOVA_ESCALA] + [escala_label(r) for _, r in todas.iterrows()]
    escolha = st.selectbox("Culto / escala", escala_labels, key="editor_escala_sel")
    is_nova = escolha == NOVA_ESCALA

    if is_nova:
        st.markdown("#### 📅 Novo culto")
        culto_date = st.date_input("Data do culto", key="nova_esc_data")
        culto_event = st.text_input("Evento / Culto", key="nova_esc_event")
        data_ensaio = st.date_input("Data do ensaio", key="nova_esc_ensaio")

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

        responsavel = st.selectbox(
            f"{FUNCAO_MINISTRADOR} (todos os integrantes)",
            list(member_map.keys()),
            key="nova_esc_resp",
            on_change=_on_nova_resp_change,
        )
        equipe_labels = st.multiselect(
            "Demais integrantes da escala",
            [l for l in member_map.keys() if l != responsavel],
            key="nova_esc_equipe",
            on_change=_on_nova_equipe_change,
        )
        notas = st.text_area("Notas", key="nova_esc_notas")

        st.markdown("---")
        st.subheader("🎶 Louvores do culto")
        st.caption("Em **Selecionados**, escolha a **parte do culto** de cada música.")
        render_louvor_search_picker(louvores_df, "nova_esc")

        if st.button(
            "💾 Salvar escala completa",
            type="primary",
            use_container_width=True,
            key="nova_esc_save",
        ):
            if not culto_event.strip():
                show_form_error("Informe o nome do culto/evento.")
            else:
                email = member_map[responsavel]
                row = members_df[members_df["email"].astype(str).str.lower() == email].iloc[0]
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
                    mrow = members_df[members_df["email"].astype(str).str.lower() == em].iloc[0]
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
                    equipe_df = pd.concat([equipe_df, pd.DataFrame(novas_eq)], ignore_index=True)
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
                        pd.concat([programa_df, pd.DataFrame(novas_prog)], ignore_index=True),
                        PROGRAMA_FILE,
                    )

                notify_new_escala(
                    new_escala["event"],
                    new_escala["date"],
                    new_escala["responsible"],
                )
                st.success(
                    "Escala salva! Equipe e louvores já estão visíveis no Dashboard de todos."
                )
                clear_louvor_picker_state("nova_esc")
                st.rerun()
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

    st.markdown("#### ✏️ Editar escala")
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
        novo_resp = st.selectbox(
            f"{FUNCAO_MINISTRADOR} (todos os integrantes)", labels_resp, index=idx_resp
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

    render_chat_messages(subset, members_df)

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


def show_gerenciar_escalas(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    chat_ensaio_df: pd.DataFrame,
):
    primary = st.session_state.get("user_primary_role", "membro")
    if is_leader(st.session_state.user_roles):
        st.success(
            "👑 Painel do **Líder** — adicione, remova e edite qualquer escala, integrante e louvor."
        )
    else:
        st.info(
            f"🎼 Painel de **{primary}** — mesmas permissões: montar, alterar e excluir escalas."
        )

    render_music_stats(
        [
            ("👥", "Integrantes", len(members_visible_to_group(members_df))),
            ("🎶", "Louvores", len(louvores_df)),
            ("📅", "Escalas", len(escalas_df)),
            ("🎤", "Cultos c/ programação", programa_df["escala_id"].nunique() if not programa_df.empty else 0),
        ]
    )

    tab_montar, tab_membros = st.tabs(["🎯 Montar / editar escala", "👥 Integrantes"])

    with tab_montar:
        show_escala_completa_editor(
            escalas_df,
            programa_df,
            equipe_df,
            louvores_df,
            members_df,
            chat_ensaio_df,
        )

    with tab_membros:
        show_members_overview(members_df, louvores_df, escalas_df, equipe_df)


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
    if is_scale_manager(st.session_state.user_roles):
        st.info(
            "🎯 Líderes e organizadores montam escalas em **Gerenciar Escalas**. "
            "Aqui você solicita trocas e acompanha o chat do ensaio."
        )

    tab_equipe, tab_trocar, tab_pedidos, tab_ensaio = st.tabs(
        ["👥 Minha equipe", "🔄 Trocar escala", "📬 Solicitações", "💬 Chat do ensaio"]
    )

    member_map = members_options_escala(members_df)
    my_email = st.session_state.user_email.strip().lower()
    start, end = week_bounds(st.session_state.get("week_offset", 0))

    with tab_equipe:
        minhas = user_on_escala_semana(escalas_df, equipe_df, my_email, start, end)
        if not minhas:
            st.info("Você não está escalado(a) nesta semana ou a escala ainda não foi publicada.")
        for item in minhas:
            render_culto_programa(
                item["escala"],
                programa_df,
                equipe_df,
                members_df,
                louvores_df,
                ensaio_notice=True,
            )

    with tab_trocar:
        st.write("Escolha como deseja solicitar a troca. A escala atualiza após aceite ou quando alguém assumir.")
        minhas = user_escalas(escalas_df, my_email)
        if minhas.empty:
            st.warning("Você não tem escala vinculada ao seu login.")
        else:
            minhas_opts = {escala_label(r): r["id"] for _, r in minhas.iterrows()}
            with st.form(key="troca_form_v2"):
                minha = st.selectbox("Minha escala", list(minhas_opts.keys()))
                modo = st.radio(
                    "Tipo de troca",
                    [
                        "Divulgar para qualquer integrante assumir",
                        "Trocar diretamente com outro integrante",
                        "Pedir que integrante específico assuma",
                    ],
                )
                target_email = ""
                target_name = ""
                dest_id = ""
                tipo = "aberta"
                outros = [l for l, e in member_map.items() if e != my_email]
                if modo.startswith("Trocar diretamente"):
                    tipo = "direta"
                    outro = st.selectbox("Integrante", outros)
                    target_email = member_map[outro]
                    tr = members_df[
                        members_df["email"].astype(str).str.lower() == target_email
                    ].iloc[0]
                    target_name = member_display_name(tr)
                    outras = escalas_df[
                        escalas_df["member_email"].astype(str).str.lower() == target_email
                    ]
                    if not outras.empty:
                        oopts = {escala_label(r): r["id"] for _, r in outras.iterrows()}
                        dest_id = oopts[
                            st.selectbox("Escala do integrante", list(oopts.keys()))
                        ]
                elif modo.startswith("Pedir que integrante"):
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
                if tipo == "direta" and not dest_id:
                    show_form_error("Escolha a escala do integrante para troca direta.")
                elif not trocas_df[
                    (trocas_df["status"] == "pendente")
                    & (trocas_df["escala_id_origem"].astype(str) == str(oid))
                ].empty:
                    st.warning("Já existe solicitação pendente para esta escala.")
                else:
                    nova = {
                        "id": new_id(),
                        "escala_id_origem": oid,
                        "escala_id_destino": dest_id,
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
                    st.success("Solicitação enviada! Todos verão no Dashboard se for divulgação aberta.")
                    st.rerun()

    with tab_pedidos:
        pend = trocas_df[trocas_df["status"] == "pendente"]
        rec = pend[pend["target_email"].astype(str).str.lower() == my_email]
        env = pend[pend["requester_email"].astype(str).str.lower() == my_email]
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
                    escalas_df, _, trocas_df = accept_open_swap(
                        t, my_email, name, escalas_df, equipe_df, trocas_df
                    )
                    save_data(escalas_df, ESCALAS_FILE)
                    save_data(trocas_df, TROCAS_FILE)
                    st.rerun()
            with c2:
                if st.button("❌ Recusar", key=f"r{t['id']}", use_container_width=True):
                    trocas_df.loc[trocas_df["id"] == t["id"], "status"] = "recusada"
                    trocas_df.loc[trocas_df["id"] == t["id"], "responded_at"] = (
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
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


def show_louvores_catalog(louvores_df: pd.DataFrame):
    st.markdown(
        '<p class="music-panel-title">🎶 Repertório completo</p>',
        unsafe_allow_html=True,
    )
    st.write(
        "Navegue pelo repertório com busca, filtros e paginação — como um catálogo musical."
    )
    render_voice_kit_link()
    st.caption(
        "▶ link direto · 🔍 busca no YouTube ou Cifra Club quando ainda não há URL cadastrada."
    )
    from enrich_louvores_links import enrich_dataframe
    from link_finder import is_direct_url

    missing = 0
    if not louvores_df.empty:
        for _, row in louvores_df.iterrows():
            if not is_direct_url(str(row.get("youtube_url", ""))) or not is_direct_url(
                str(row.get("cifra_url", ""))
            ):
                missing += 1
    if missing:
        st.info(f"**{missing}** música(s) ainda sem link direto de YouTube ou Cifra.")

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        if st.button("🔍 Links de pesquisa (rápido)", use_container_width=True):
            try:
                df = louvores_df.copy()
                df, n = enrich_dataframe(df, use_web=False)
                save_data(df, LOUVORES_FILE)
                st.success(f"{n} música(s) com links de pesquisa.")
                st.rerun()
            except Exception as exc:
                show_exception_error(exc)
    with col_l2:
        batch = st.number_input(
            "Buscar na internet (por vez)",
            min_value=3,
            max_value=25,
            value=8,
            step=1,
            help="Evita timeout no servidor. Clique várias vezes até completar.",
        )
        if st.button("🌐 Buscar links reais na internet", use_container_width=True):
            try:
                with st.spinner(
                    f"Buscando YouTube e Cifra Club para {int(batch)} música(s)..."
                ):
                    df = louvores_df.copy()
                    df, n = enrich_dataframe(df, use_web=True, limit=int(batch))
                save_data(df, LOUVORES_FILE)
                st.success(f"{n} música(s) atualizada(s) com links da internet.")
                st.rerun()
            except Exception as exc:
                show_exception_error(exc, context="Busca de links")

    if louvores_df.empty:
        st.warning(
            "Catálogo ainda não gerado. Execute: `python build_louvores_db.py`"
        )
        return

    search = st.text_input("🔍 Buscar música ou artista", "")
    letters = sorted(
        {letter for letter in louvores_df["letter"].dropna().astype(str) if letter}
    )
    letter_filter = st.selectbox("🅰 Letra", ["Todas"] + letters)
    ritmos = sorted(
        {
            ritmo
            for ritmo in louvores_df["ritmo"].dropna().astype(str)
            if ritmo.strip()
        }
    )
    ritmo_filter = st.selectbox("🥁 Ritmo", ["Todos"] + ritmos)

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
    if ritmo_filter != "Todos":
        filtered = filtered[filtered["ritmo"].astype(str) == ritmo_filter]

    if search.strip() or letter_filter != "Todas" or ritmo_filter != "Todos":
        st.session_state["page_catalogo"] = 1

    st.markdown(
        f"**🎵 {len(filtered)}** faixa(s) encontrada(s) · catálogo com **{len(louvores_df)}** louvores",
        unsafe_allow_html=True,
    )

    display = filtered[
        ["title", "artist", "key", "ritmo", "youtube_url", "cifra_url", "source"]
    ].copy()
    display.columns = [
        "Música",
        "Artista",
        "Tom",
        "Ritmo",
        "YouTube",
        "Cifra",
        "Fonte",
    ]
    page_df = paginate_dataframe(display, CATALOG_PAGE_SIZE, "catalogo")
    rows_html = []
    for _, r in page_df.iterrows():
        yt = str(r.get("YouTube", "")).strip()
        cif = str(r.get("Cifra", "")).strip()
        yt_l = (
            f'<a href="{yt}" target="_blank" title="YouTube">{catalog_link_label(yt)}</a>'
            if yt.startswith("http")
            else "—"
        )
        cif_l = (
            f'<a href="{cif}" target="_blank" title="Cifra">{catalog_link_label(cif) or "🎸"}</a>'
            if cif.startswith("http")
            else "—"
        )
        rows_html.append(
            "<tr>"
            f"<td>{r['Música']}</td><td>{r['Artista']}</td><td>{r['Tom']}</td>"
            f"<td>{r['Ritmo']}</td><td>{yt_l}</td><td>{cif_l}</td><td>{r['Fonte']}</td>"
            "</tr>"
        )
    table = (
        '<div class="catalog-table-wrap"><table class="catalog-table">'
        "<thead><tr><th>Música</th><th>Artista</th><th>Tom</th><th>Ritmo</th>"
        "<th>YouTube</th><th>Cifra</th><th>Fonte</th></tr></thead><tbody>"
        + "".join(rows_html)
        + "</tbody></table></div>"
    )
    st.markdown(table, unsafe_allow_html=True)



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


def show_sugestao_louvor(sugestoes_df: pd.DataFrame, louvores_df: pd.DataFrame):
    st.markdown('<p class="music-panel-title">💡 Sugerir louvor</p>', unsafe_allow_html=True)
    st.write(
        "Envie o link do YouTube e o nome da música. Líderes e organizadores analisam para incluir no catálogo."
    )

    with st.form(key="sugestao_form"):
        titulo = st.text_input("Nome da música")
        yt = st.text_input("Link do YouTube")
        enviar = st.form_submit_button("Enviar sugestão", type="primary")
    if enviar:
        if not titulo.strip() or not yt.strip():
            show_form_error("Informe nome e link do YouTube.")
        elif "youtube" not in yt.lower() and "youtu.be" not in yt.lower():
            st.warning("Use um link válido do YouTube.")
        else:
            nova = {
                "id": new_id(),
                "title": titulo.strip().title(),
                "youtube_url": yt.strip(),
                "suggester_email": st.session_state.user_email,
                "suggester_name": st.session_state.user_full_name
                or st.session_state.user_name,
                "status": "pendente",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "review_notes": "",
            }
            save_data(
                pd.concat([sugestoes_df, pd.DataFrame([nova])], ignore_index=True),
                SUGESTOES_FILE,
            )
            st.success("Sugestão enviada! Aguarde análise da liderança.")
            st.rerun()

    if is_scale_manager(st.session_state.user_roles):
        st.markdown("---")
        st.subheader("📋 Sugestões pendentes (liderança)")
        pend = sugestoes_df[sugestoes_df["status"].astype(str).str.lower() == "pendente"]
        if pend.empty:
            st.caption("Nenhuma sugestão pendente.")
        for _, s in pend.iterrows():
            st.markdown(f"**{s['title']}** — {s['suggester_name']}")
            st.link_button("YouTube", str(s["youtube_url"]))
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Aprovar", key=f"ap_{s['id']}", use_container_width=True):
                    row = {
                        "title": s["title"],
                        "artist": "",
                        "key": "",
                        "youtube_url": s["youtube_url"],
                        "cifra_url": "",
                        "ritmo": "",
                        "letter": s["title"][0].upper() if s["title"] else "A",
                        "source": "sugestao",
                    }
                    save_data(
                        pd.concat([louvores_df, pd.DataFrame([row])], ignore_index=True),
                        LOUVORES_FILE,
                    )
                    sugestoes_df.loc[sugestoes_df["id"] == s["id"], "status"] = "aprovada"
                    save_data(sugestoes_df, SUGESTOES_FILE)
                    st.rerun()
            with c2:
                if st.button("❌ Recusar", key=f"rj_{s['id']}", use_container_width=True):
                    sugestoes_df.loc[sugestoes_df["id"] == s["id"], "status"] = "recusada"
                    save_data(sugestoes_df, SUGESTOES_FILE)
                    st.rerun()


def _run_app() -> None:
    st.set_page_config(
        page_title=GROUP_NAME,
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_music_theme()
    ensure_session_state()

    if "data_guard_initialized" not in st.session_state:
        snapshot_data_folder(DATA_DIR)
        st.session_state.data_guard_initialized = True

    members_df = load_data(MEMBERS_FILE, MEMBER_COLUMNS)
    members_df = ensure_developer_access(members_df)
    members_df = sync_recognized_member_roles(members_df)
    chat_df = prepare_chat(load_data(CHAT_FILE, CHAT_COLUMNS))
    escalas_df = prepare_escalas(load_data(ESCALAS_FILE, ESCALA_COLUMNS))
    trocas_df = prepare_trocas(load_data(TROCAS_FILE, TROCA_COLUMNS))
    programa_df = prepare_programa(load_data(PROGRAMA_FILE, PROGRAMA_COLUMNS))
    equipe_df = prepare_equipe(load_data(EQUIPE_FILE, EQUIPE_COLUMNS))
    playlist_df = load_data(
        PLAYLIST_FILE, ("title", "artist", "url", "notes", "added_at")
    )
    from catalog_sanitize import prepare_louvores_df

    louvores_df = prepare_louvores_df(
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
    st.session_state.chat_unread_count = count_unread_chat_messages(chat_df)

    if not st.session_state.authenticated:
        show_login_page(members_df)
        return

    if not session_is_valid(st.session_state):
        session_logout(st.session_state)
        st.warning(
            f"Sessão encerrada após {SESSION_MINUTES} minutos sem uso. Entre novamente."
        )
        show_login_page(members_df)
        return

    render_sidebar_profile()
    menu = render_sidebar_navigation()
    inject_chat_unread_badges(int(st.session_state.get("chat_unread_count", 0)))
    render_sidebar_footer()
    render_push_admin_sidebar(members_df)

    page_header(menu)

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
        )

    elif menu == "Catálogo":
        show_louvores_catalog(louvores_df)

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
        st.markdown('<p class="music-panel-title">🎧 Sua playlist</p>', unsafe_allow_html=True)
        st.write("Monte a setlist com links de referência para ensaio e culto.")
        with st.form(key="playlist_form"):
            title = st.text_input("🎵 Nome da música")
            artist = st.text_input("🎤 Artista / Banda")
            url = st.text_input("🔗 Link (YouTube, Spotify, etc.)")
            notes = st.text_area("Observações")
            submit = st.form_submit_button("🎵 Adicionar música")

        if submit:
            if not title or not artist:
                show_form_error("Informe pelo menos título e artista.")
            else:
                new_row = {
                    "title": title.strip().title(),
                    "artist": artist.strip().title(),
                    "url": url.strip(),
                    "notes": notes.strip(),
                    "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                playlist_df = pd.concat(
                    [playlist_df, pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                save_data(playlist_df, PLAYLIST_FILE)
                st.success("Música adicionada à playlist.")
                st.rerun()

        if not playlist_df.empty:
            st.subheader("🎧 Faixas na playlist")
            playlist_display = playlist_df[
                ["title", "artist", "url", "notes", "added_at"]
            ].copy()
            playlist_display.columns = ["Música", "Artista", "Link", "Notas", "Adicionada em"]
            playlist_display["_sort_at"] = pd.to_datetime(
                playlist_display["Adicionada em"], errors="coerce"
            )
            playlist_display = playlist_display.sort_values(
                "_sort_at", ascending=False
            ).drop(columns=["_sort_at"])
            page_playlist = paginate_dataframe(playlist_display, 15, "playlist")
            st.dataframe(page_playlist, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma música adicionada ainda.")

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
