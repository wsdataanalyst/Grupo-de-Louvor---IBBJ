import base64
import hashlib
import inspect
import os
import unicodedata
import uuid
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime, timedelta

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

DATA_DIR = Path("data")
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
)
CHAT_COLUMNS = ("timestamp", "email", "name", "message")

MENU_ITEMS_BASE = [
    ("Dashboard", "🎼", "Escalados, louvores e programação do culto"),
    ("Gerenciar Escalas", "🎯", "Montar cultos, equipe e louvores"),
    ("Catálogo", "🎶", "Repertório de louvores"),
    ("Escalas", "🎤", "Eventos e trocas"),
    ("Playlist", "🎧", "Músicas do grupo"),
    ("Chat", "💬", "Comunicação"),
    ("Membros", "🎹", "Integrantes do ministério"),
    ("Perfil", "👤", "Sua foto e dados cadastrais"),
]
MENU_HEADERS = {
    "Dashboard": "Escala e programação da semana",
    "Gerenciar Escalas": "Painel de gestão de escalas",
    "Catálogo": "Catálogo de louvores",
    "Escalas": "Escalas de louvor",
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
    "Playlist": "#f472b6",
    "Chat": "#34d399",
    "Membros": "#fb923c",
    "Perfil": "#c084fc",
}

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
    items = [item for item in MENU_ITEMS_BASE if item[0] != "Gerenciar Escalas"]
    if is_scale_manager(roles):
        items.insert(1, ("Gerenciar Escalas", "🎯", "Montar cultos, equipe e louvores"))
    labels = {f"{icon}  {name}": name for name, icon, _ in items}
    icons = {name: icon for name, icon, _ in items}
    return items, labels, icons


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
            st.error("Preencha nome, sobrenome, email e senha.")
        elif not special_hint and not roles:
            st.error("Escolha pelo menos uma função musical.")
        elif not is_valid_email(email):
            st.error("Informe um email válido.")
        elif len(password) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
        elif password != confirm_password:
            st.error("As senhas não coincidem.")
        else:
            new_member, error = register_user(
                first_name, last_name, email, password, roles, members_df
            )
            if error:
                st.error(error)
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
    if not file_path.exists():
        return pd.DataFrame(columns=list(columns))
    try:
        df = pd.read_csv(file_path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=list(columns))
    if df.empty:
        return pd.DataFrame(columns=list(columns))
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    df = df[list(columns)].copy()
    if file_path == MEMBERS_FILE and "email" in df.columns:
        df["email"] = df["email"].astype(str).str.strip().str.lower()
    return df


def save_data(df: pd.DataFrame, file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)
    load_data.clear()


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
    ext = Path(uploaded_file.name).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    slug = email_to_photo_slug(email)
    for old in PROFILE_PHOTOS_DIR.glob(f"{slug}.*"):
        old.unlink(missing_ok=True)
    filename = f"{slug}{ext}"
    (PROFILE_PHOTOS_DIR / filename).write_bytes(uploaded_file.getvalue())
    return filename


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
    if f in ("Integrante", "Banda", "Responsável"):
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
    for _, row in members_df.iterrows():
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
    for _, row in members_df.iterrows():
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


def prepare_chat(df: pd.DataFrame) -> pd.DataFrame:
    for column in CHAT_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[list(CHAT_COLUMNS)].copy()


def prepare_trocas(df: pd.DataFrame) -> pd.DataFrame:
    for column in TROCA_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[list(TROCA_COLUMNS)].copy()


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
    for column in PROGRAMA_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[list(PROGRAMA_COLUMNS)].copy()
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
    title = str(row.get("title", "")).strip()
    if not title:
        return ""
    artist = str(row.get("artist", "")).strip()
    return f"{title} — {artist}" if artist else title


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
        "funcao": "Responsável",
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


def get_developer_emails() -> list[str]:
    """Emails com acesso total de Desenvolvedor (menu Gerenciar Escalas, etc.)."""
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
    """Garante conta técnica e papel Desenvolvedor nos emails configurados."""
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
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Outfit', 'Segoe UI', sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 8% 12%, rgba(139, 92, 246, 0.18) 0%, transparent 42%),
                radial-gradient(circle at 92% 88%, rgba(251, 191, 36, 0.12) 0%, transparent 40%),
                linear-gradient(165deg, #0a0812 0%, #12101f 40%, #1a1530 100%);
        }
        [data-testid="stAppViewContainer"]::before {
            content: "♪  ♫  ♩  ♬  ♪  ♫  ♩  ♬";
            position: fixed;
            top: 0; left: 0; right: 0;
            font-size: 1.1rem;
            letter-spacing: 2.5rem;
            color: rgba(212, 175, 55, 0.06);
            padding: 1.5rem 2rem;
            pointer-events: none;
            z-index: 0;
            white-space: nowrap;
            overflow: hidden;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        .block-container {
            padding-top: 1.5rem;
            max-width: 1100px;
            position: relative;
            z-index: 1;
        }

        /* Sidebar — estúdio / palco */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #120e1f 0%, #1a1435 50%, #0d0a16 100%) !important;
            border-right: 1px solid rgba(212, 175, 55, 0.2);
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
            background: linear-gradient(135deg, rgba(26, 21, 48, 0.95) 0%, rgba(18, 14, 31, 0.98) 100%);
            border: 1px solid rgba(212, 175, 55, 0.35);
            border-radius: 16px;
            padding: 1.35rem 1.75rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
            position: relative;
            overflow: hidden;
        }
        .music-hero::after {
            content: "";
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent, #fbbf24), transparent);
        }
        .music-hero h2 {
            margin: 0;
            color: #faf8ff;
            font-size: 1.65rem;
            font-weight: 700;
        }
        .music-hero p {
            margin: 0.35rem 0 0;
            color: #a89bc4;
            font-size: 0.92rem;
        }
        .music-hero .notes-deco {
            position: absolute;
            right: 1.25rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 2.5rem;
            opacity: 0.15;
            color: #fbbf24;
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
        .chat-feed {
            max-height: 420px;
            overflow-y: auto;
            padding: 1rem;
            background: rgba(12, 10, 20, 0.6);
            border: 1px solid rgba(52, 211, 153, 0.3);
            border-radius: 14px;
            margin-bottom: 1rem;
        }
        .chat-bubble {
            max-width: 78%;
            padding: 0.65rem 0.9rem;
            border-radius: 14px;
            margin-bottom: 0.65rem;
            line-height: 1.45;
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

        .mobile-user-bar {
            background: rgba(139, 92, 246, 0.15);
            border-left: 4px solid #fbbf24;
            padding: 0.65rem 0.85rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: #e9e4f5;
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_page_html(html_fragment: str, height: int = 0):
    """Injeta HTML/JS na página (st.html se disponível, senão componente iframe)."""
    body = html_fragment.strip()
    if not body:
        return
    if hasattr(st, "html"):
        st.html(body, height=height)
        return
    import streamlit.components.v1 as components

    components.html(body, height=height)


def inject_mobile_app_shell():
    """PWA (instalar pelo link) + service worker + OneSignal (se configurado)."""
    st.markdown(
        """
        <link rel="manifest" href="/manifest.webmanifest">
        <meta name="theme-color" content="#1a1530">
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
    with st.expander("📲 App no celular e notificações", expanded=False):
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
    email = str(st.session_state.get("user_email", "")).strip().lower()
    if email and email in get_developer_emails():
        return True
    roles = str(st.session_state.get("user_roles", "")).lower()
    return ROLE_DESENVOLVEDOR.lower() in roles


def render_push_admin_sidebar():
    """Painel do desenvolvedor para testar e conferir OneSignal."""
    if not is_current_developer():
        return
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
    st.sidebar.markdown(f"### 🎵 {GROUP_NAME}")
    st.sidebar.markdown("---")
    photo_path = profile_photo_file(
        st.session_state.user_email,
        st.session_state.get("user_profile_photo", ""),
    )
    if photo_path:
        st.sidebar.image(str(photo_path), width=88)
    st.sidebar.markdown(f"👤 **{st.session_state.user_name}**")
    roles = str(st.session_state.user_roles).strip()
    if roles:
        st.sidebar.caption(roles_for_public_display(roles))
    st.sidebar.markdown("---")
    if is_scale_manager(st.session_state.user_roles):
        render_registration_link_box(compact=True)
        st.sidebar.markdown("---")
    if st.sidebar.button("🚪  Sair", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_name = ""
        st.session_state.user_full_name = ""
        st.session_state.user_email = ""
        st.session_state.user_roles = ""
        st.session_state.user_primary_role = "membro"
        st.session_state.user_profile_photo = ""
        st.rerun()


def render_navigation() -> str:
    """Menu principal no topo — otimizado para uso com o polegar no celular."""
    _, labels, _ = get_menu_items_for_user(st.session_state.user_roles)
    choice = st.selectbox(
        "🎼 Ir para",
        list(labels.keys()),
        key="app_navigation",
    )
    return labels[choice]


def page_header(menu: str):
    items, _, icons = get_menu_items_for_user(st.session_state.user_roles)
    icon = icons.get(menu, "🎵")
    title = MENU_HEADERS.get(menu, menu)
    subtitle = next((desc for name, _, desc in items if name == menu), "")
    accent = MENU_ACCENTS.get(menu, "#fbbf24")
    st.markdown(
        f"""
        <div class="music-hero" style="--accent: {accent}">
            <span class="notes-deco">♪♫♩</span>
            <h2>{icon} {title}</h2>
            <p>{subtitle}</p>
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


def show_login_page(members_df: pd.DataFrame):
    apply_music_theme()
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)

    render_login_brand()

    st.markdown("---")

    if is_register_page():
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
            with st.form(key="login_form"):
                login_email = st.text_input("Email")
                login_password = st.text_input("Senha", type="password")
                login_button = st.form_submit_button(
                    "Entrar", type="primary", use_container_width=True
                )

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
                    special = recognized_leadership_role(user["first_name"])
                    if special:
                        st.success(f"Bem-vindo! Você está como **{special}**.")
                    st.rerun()
                else:
                    st.error("Email ou senha incorretos.")

        with tab_register:
            render_register_form(members_df)

    st.markdown("</div>", unsafe_allow_html=True)


def render_chat_messages(chat_df: pd.DataFrame):
    if chat_df.empty:
        st.caption("💬 O chat está quieto por enquanto — envie a primeira mensagem quando quiser.")
        return

    my_email = st.session_state.user_email.strip().lower()
    chat_sorted = chat_df.copy()
    chat_sorted["_ts"] = pd.to_datetime(chat_sorted["timestamp"], errors="coerce")
    chat_sorted = chat_sorted.sort_values("_ts", ascending=True)

    bubbles = ['<div class="chat-feed">']
    for _, row in chat_sorted.iterrows():
        is_me = str(row.get("email", "")).strip().lower() == my_email
        css_class = "me" if is_me else "other"
        name = str(row.get("name", "Integrante"))
        time_str = row["_ts"].strftime("%d/%m %H:%M") if pd.notna(row.get("_ts")) else ""
        message = str(row.get("message", "")).replace("<", "&lt;").replace(">", "&gt;")
        bubbles.append(
            f'<div class="chat-bubble {css_class}">'
            f'<div class="chat-meta">{"Você" if is_me else name} · {time_str}</div>'
            f'<p class="chat-text">{message}</p></div>'
        )
    bubbles.append("</div>")
    st.markdown("".join(bubbles), unsafe_allow_html=True)


def show_group_chat(chat_df: pd.DataFrame, members_df: pd.DataFrame):
    st.markdown('<p class="music-panel-title">💬 Conversa do grupo</p>', unsafe_allow_html=True)
    st.write("Chat para integrantes logados — todos do grupo veem as mensagens.")
    st.caption(f"🟢 {len(members_df)} integrante(s) cadastrado(s)")
    render_chat_messages(chat_df)
    with st.form(key="chat_form", clear_on_submit=True):
        message = st.text_area("Sua mensagem", height=100, placeholder="Escreva para o grupo...")
        send = st.form_submit_button("💬 Enviar", type="primary", use_container_width=True)
    if send:
        if not message.strip():
            st.error("Digite uma mensagem.")
        else:
            new_message = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "email": st.session_state.user_email,
                "name": st.session_state.user_full_name or st.session_state.user_name,
                "message": message.strip(),
            }
            save_data(pd.concat([chat_df, pd.DataFrame([new_message])], ignore_index=True), CHAT_FILE)
            notify_chat_message(new_message["name"], new_message["message"])
            st.rerun()
    if st.button("🔄 Atualizar conversa", use_container_width=True):
        st.rerun()


def render_culto_programa(
    escala_row,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
):
    escala_id = str(escala_row.get("id", ""))
    event = str(escala_row.get("event", "Culto"))
    culto_date = str(escala_row.get("date", ""))
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    try:
        dt = pd.to_datetime(culto_date)
        date_fmt = f"{dias[dt.weekday()]}, {dt.strftime('%d/%m/%Y')}"
    except (ValueError, TypeError):
        date_fmt = culto_date

    team = integrantes_escalados(escala_row, equipe_df, members_df)
    chips = "".join(
        f'<span class="team-chip"><strong>{p["nome"]}</strong> · {p["funcao"]}</span>'
        for p in team
    )

    st.markdown(
        f"""
        <div class="culto-week-card">
            <h3>🎤 {event}</h3>
            <p class="culto-date">📅 {date_fmt}</p>
            <p style="color:#a89bc4;margin:0 0 0.5rem;">👥 Escalados:</p>
            {chips or '<span class="team-chip">Equipe a definir</span>'}
        </div>
        """,
        unsafe_allow_html=True,
    )

    prog = programa_por_escala(programa_df, escala_id)
    if prog.empty:
        st.caption(
            "🎶 Programação do culto ainda não montada — configure em **Gerenciar Escalas**."
        )
        return

    st.markdown("**🎶 Sequência do culto**")
    for _, item in prog.iterrows():
        artist = str(item.get("artist", "")).strip()
        louvor = str(item.get("louvor_title", ""))
        titulo = f"{louvor} — {artist}" if artist else louvor
        tom = str(item.get("key", "")).strip()
        leader = str(item.get("leader_name", "")).strip()
        yt = str(item.get("youtube_url", "")).strip()
        cifra = str(item.get("cifra_url", "")).strip()
        links = []
        if yt:
            links.append(f'<a href="{yt}" target="_blank">▶ YouTube</a>')
        if cifra and cifra.startswith("http"):
            links.append(f'<a href="{cifra}" target="_blank">🎸 Cifra</a>')
        links_html = " · ".join(links) if links else ""
        meta = " · ".join(x for x in [f"Tom: {tom}" if tom else "", f"🎤 {leader}" if leader else ""] if x)
        st.markdown(
            f"""
            <div class="prog-card">
                <span class="seq-badge">{item['ordem']}</span>
                <span class="prog-parte">{item['parte']}</span>
                <p class="prog-louvor">{titulo}</p>
                <p class="prog-meta">{meta}</p>
                {f'<p class="prog-meta">{links_html}</p>' if links_html else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_dashboard(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
    chat_df: pd.DataFrame,
    playlist_df: pd.DataFrame,
):
    if "week_offset" not in st.session_state:
        st.session_state.week_offset = 0

    st.markdown('<p class="music-panel-title">📅 Escala da semana</p>', unsafe_allow_html=True)

    start, end = week_bounds(st.session_state.week_offset)
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

    render_music_stats(
        [
            ("🎤", "Cultos na semana", len(semana)),
            ("🎹", "Integrantes", len(members_df)),
            ("🎶", "Louvores catálogo", len(louvores_df)),
            ("💬", "Mensagens chat", len(chat_df)),
        ]
    )

    if semana.empty:
        st.info(
            "Nenhum culto nesta semana por enquanto. Quando houver escala, ela aparecerá aqui para todos."
        )
        return

    for _, escala in semana.iterrows():
        render_culto_programa(escala, programa_df, equipe_df, members_df)


def show_user_profile(
    members_df: pd.DataFrame,
    escalas_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
):
    idx, row = get_current_member_row(members_df)
    if row is None:
        st.error("Não foi possível carregar seu perfil.")
        return

    st.markdown('<p class="music-panel-title">👤 Meu perfil</p>', unsafe_allow_html=True)
    st.caption("Atualize sua foto e informações cadastrais. O grupo verá suas alterações nas escalas.")

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
        if st.button("💾 Salvar foto", use_container_width=True, key="save_profile_photo"):
            if not uploaded:
                st.warning("Escolha uma imagem antes de salvar.")
            else:
                filename = save_profile_photo(email, uploaded)
                members_df.at[idx, "profile_photo"] = filename
                save_data(members_df, MEMBERS_FILE)
                st.session_state.user_profile_photo = filename
                st.success("Foto atualizada!")
                st.rerun()
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
                st.error("Nome e sobrenome são obrigatórios.")
            elif not leadership and not new_musician:
                st.error("Selecione pelo menos uma função musical.")
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
            st.error("Preencha a senha atual e a nova senha.")
        elif len(senha_nova) < 6:
            st.error("A nova senha deve ter pelo menos 6 caracteres.")
        elif senha_nova != senha_conf:
            st.error("A confirmação não coincide com a nova senha.")
        elif hash_password(senha_atual) != str(row.get("password_hash", "")):
            st.error("Senha atual incorreta.")
        else:
            members_df.at[idx, "password_hash"] = hash_password(senha_nova)
            save_data(members_df, MEMBERS_FILE)
            st.success("Senha alterada com sucesso!")


def show_members_overview(members_df: pd.DataFrame, louvores_df: pd.DataFrame):
    st.markdown('<p class="music-panel-title">👥 Todos os integrantes</p>', unsafe_allow_html=True)
    if members_df.empty:
        st.info("Nenhum membro cadastrado.")
        return
    display = members_df[["first_name", "last_name", "email", "roles", "created_at"]].copy()
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
    for label in labels:
        data = full_catalog.get(label, {})
        titulo = str(data.get("title", label.split(" — ")[0])).strip()
        entry = meta.get(label, {"parte": CULTO_PARTES[0], "parte_outra": ""})
        rows.append(
            {
                "label": label,
                "titulo": titulo,
                "artist": str(data.get("artist", "")),
                "key": str(data.get("key", "")),
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
        titulo = str(data.get("title", label.split(" — ")[0]))
        artista = str(data.get("artist", ""))
        tom = str(data.get("key", "")).strip()
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
            f"**Responsável do culto:** {row0.get('member_name', row0.get('responsible', '—'))}"
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

    novos = st.multiselect(
        "Adicionar integrantes à escala",
        available,
        key=f"{key_prefix}_eq_add",
        placeholder="Selecione um ou vários integrantes",
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
):
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
        responsavel = st.selectbox(
            "Responsável principal",
            list(member_map.keys()),
            key="nova_esc_resp",
        )
        equipe_labels = st.multiselect(
            "Demais integrantes da escala",
            [l for l in member_map.keys() if l != responsavel],
            key="nova_esc_equipe",
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
                st.error("Informe o nome do culto/evento.")
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
        st.error("Escala não encontrada.")
        return

    escala_row = escalas_df[escalas_df["id"].astype(str) == escala_id].iloc[0]

    st.markdown("#### ✏️ Editar escala")
    st.caption(
        "Líderes e organizadores podem alterar dados, equipe, louvores ou **excluir** esta escala."
    )
    confirm_key = f"confirm_del_esc_{escala_id}"
    if st.session_state.get(confirm_key):
        st.error("Confirma a exclusão permanente desta escala (equipe e louvores)?")
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
        novo_resp = st.selectbox("Responsável principal", labels_resp, index=idx_resp)
        novas_notas = st.text_area("Notas", value=str(escala_row.get("notes", "")))
        salvar_meta = st.form_submit_button("💾 Salvar dados do culto", use_container_width=True)

    if salvar_meta:
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
        save_data(escalas_df, ESCALAS_FILE)
        st.success("Dados do culto atualizados.")
        st.rerun()

    st.markdown("---")
    render_equipe_editor(escala_id, equipe_df, members_df, escalas_df, f"ed_{escala_id}")

    st.markdown("---")
    render_programa_louvores_editor(
        escala_id, programa_df, louvores_df, members_df, f"ed_{escala_id}"
    )


def show_gerenciar_escalas(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    louvores_df: pd.DataFrame,
    members_df: pd.DataFrame,
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
            ("👥", "Integrantes", len(members_df)),
            ("🎶", "Louvores", len(louvores_df)),
            ("📅", "Escalas", len(escalas_df)),
            ("🎤", "Cultos c/ programação", programa_df["escala_id"].nunique() if not programa_df.empty else 0),
        ]
    )

    tab_montar, tab_membros = st.tabs(["🎯 Montar / editar escala", "👥 Integrantes"])

    with tab_montar:
        show_escala_completa_editor(
            escalas_df, programa_df, equipe_df, louvores_df, members_df
        )

    with tab_membros:
        show_members_overview(members_df, louvores_df)


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
):
    if is_scale_manager(st.session_state.user_roles):
        st.info(
            "🎯 Use **Gerenciar Escalas** para montar cultos, equipe, louvores e alterações em qualquer escala."
        )

    if is_scale_manager(st.session_state.user_roles):
        tab_trocar, tab_pedidos = st.tabs(["🔄 Trocar escala", "📬 Solicitações"])
    else:
        tab_escalas, tab_trocar, tab_pedidos = st.tabs(
            ["📅 Escalas", "🔄 Trocar escala", "📬 Solicitações"]
        )

    member_map = members_options_escala(members_df)
    my_email = st.session_state.user_email.strip().lower()

    if not is_scale_manager(st.session_state.user_roles):
        with tab_escalas:
            st.write("Cadastre cultos e ensaios vinculando o integrante responsável.")
            with st.form(key="escala_form"):
                date = st.date_input("Data do evento")
                event = st.text_input("Evento / Descrição")
                labels = list(member_map.keys())
                idx = next((i for i, e in enumerate(member_map.values()) if e == my_email), 0)
                assign_label = st.selectbox("Integrante escalado", labels, index=idx)
                notes = st.text_area("Notas adicionais")
                submit = st.form_submit_button("📅 Adicionar escala", type="primary")
            if submit:
                if not event:
                    st.error("Informe o evento.")
                else:
                    email = member_map[assign_label]
                    row = members_df[members_df["email"].astype(str).str.lower() == email].iloc[0]
                    name = member_display_name(row)
                    new_row = {
                        "id": new_id(),
                        "date": date.strftime("%Y-%m-%d"),
                        "event": event.strip(),
                        "responsible": name,
                        "member_email": email,
                        "member_name": name,
                        "notes": notes.strip(),
                    }
                    save_data(
                        pd.concat([escalas_df, pd.DataFrame([new_row])], ignore_index=True),
                        ESCALAS_FILE,
                    )
                    st.success("Escala adicionada.")
                    st.rerun()
            if not escalas_df.empty:
                disp = escalas_df.copy()
                disp["_d"] = pd.to_datetime(disp["date"], errors="coerce")
                disp = disp.sort_values("_d")[["date", "event", "member_name", "notes"]]
                disp.columns = ["Data", "Evento", "Integrante", "Notas"]
                st.dataframe(disp, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma escala registrada.")

    with tab_trocar:
        st.write("Solicite troca com outro integrante. A troca só vale após **aceite**.")
        minhas = user_escalas(escalas_df, my_email)
        if minhas.empty:
            st.warning("Você não tem escala vinculada ao seu login.")
        elif len(member_map) < 2:
            st.warning("Cadastre pelo menos 2 integrantes.")
        else:
            minhas_opts = {escala_label(r): r["id"] for _, r in minhas.iterrows()}
            with st.form(key="troca_form"):
                minha = st.selectbox("Minha escala", list(minhas_opts.keys()))
                outros = [l for l, e in member_map.items() if e != my_email]
                outro = st.selectbox("Integrante", outros)
                target_email = member_map[outro]
                outras = escalas_df[escalas_df["member_email"].astype(str).str.lower() == target_email]
                tipo = st.radio("Tipo", ["Trocar com escala do integrante", "Pedir para assumir minha vaga"])
                dest_id = ""
                if tipo.startswith("Trocar") and not outras.empty:
                    oopts = {escala_label(r): r["id"] for _, r in outras.iterrows()}
                    dest_id = oopts[st.selectbox("Escala do integrante", list(oopts.keys()))]
                msg = st.text_input("Mensagem (opcional)")
                go = st.form_submit_button("📨 Enviar solicitação", type="primary")
            if go:
                oid = minhas_opts[minha]
                if tipo.startswith("Trocar") and not dest_id:
                    st.error("Escolha a escala do integrante ou 'assumir minha vaga'.")
                elif not trocas_df[(trocas_df["status"] == "pendente") & (trocas_df["escala_id_origem"] == oid)].empty:
                    st.warning("Já existe solicitação pendente para esta escala.")
                else:
                    tr = members_df[members_df["email"].astype(str).str.lower() == target_email].iloc[0]
                    nova = {
                        "id": new_id(), "escala_id_origem": oid, "escala_id_destino": dest_id,
                        "requester_email": my_email,
                        "requester_name": st.session_state.user_full_name or st.session_state.user_name,
                        "target_email": target_email, "target_name": member_display_name(tr),
                        "status": "pendente", "message": msg.strip(),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "responded_at": "",
                    }
                    save_data(pd.concat([trocas_df, pd.DataFrame([nova])], ignore_index=True), TROCAS_FILE)
                    st.success("Solicitação enviada!"); st.rerun()

    with tab_pedidos:
        pend = trocas_df[trocas_df["status"] == "pendente"]
        rec = pend[pend["target_email"].astype(str).str.lower() == my_email]
        env = pend[pend["requester_email"].astype(str).str.lower() == my_email]
        st.subheader("📥 Recebidos")
        if rec.empty:
            st.info("Nenhum pedido para você.")
        for _, t in rec.iterrows():
            o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
            ot = escala_label(o.iloc[0]) if not o.empty else "—"
            if str(t["escala_id_destino"]).strip():
                d = escalas_df[escalas_df["id"] == t["escala_id_destino"]]
                dt = escala_label(d.iloc[0]) if not d.empty else "—"
                txt = f"Troca: {ot} ↔ {dt}"
            else:
                txt = f"Assumir: {ot}"
            st.markdown(f'<div class="swap-card"><b>{t["requester_name"]}</b><br>{txt}</div>', unsafe_allow_html=True)
            if t["message"]: st.caption(t["message"])
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Aceitar", key=f"a{t['id']}", use_container_width=True):
                    eu = escalas_df.copy()
                    if str(t["escala_id_destino"]).strip():
                        eu = execute_swap(eu, t["escala_id_origem"], t["escala_id_destino"])
                    else:
                        ix = eu.index[eu["id"] == t["escala_id_origem"]]
                        if len(ix):
                            eu.loc[ix[0], ["member_email", "member_name", "responsible"]] = [
                                t["target_email"], t["target_name"], t["target_name"]
                            ]
                    trocas_df.loc[trocas_df["id"] == t["id"], "status"] = "aceita"
                    trocas_df.loc[trocas_df["id"] == t["id"], "responded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_data(eu, ESCALAS_FILE); save_data(trocas_df, TROCAS_FILE); st.rerun()
            with c2:
                if st.button("❌ Recusar", key=f"r{t['id']}", use_container_width=True):
                    trocas_df.loc[trocas_df["id"] == t["id"], "status"] = "recusada"
                    trocas_df.loc[trocas_df["id"] == t["id"], "responded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_data(trocas_df, TROCAS_FILE); st.rerun()
        st.subheader("📤 Enviados")
        if env.empty:
            st.info("Nenhum pedido enviado pendente.")
        for _, t in env.iterrows():
            o = escalas_df[escalas_df["id"] == t["escala_id_origem"]]
            st.caption(f"Aguardando {t['target_name']} · {escala_label(o.iloc[0]) if not o.empty else '—'}")
            if st.button("Cancelar", key=f"c{t['id']}"):
                trocas_df.loc[trocas_df["id"] == t["id"], "status"] = "cancelada"
                save_data(trocas_df, TROCAS_FILE); st.rerun()


def show_louvores_catalog(louvores_df: pd.DataFrame):
    st.markdown(
        '<p class="music-panel-title">🎶 Repertório completo</p>',
        unsafe_allow_html=True,
    )
    st.write(
        "Navegue pelo repertório com busca, filtros e paginação — como um catálogo musical."
    )

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
    st.dataframe(page_df, use_container_width=True, hide_index=True)


def main():
    st.set_page_config(
        page_title=GROUP_NAME,
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_music_theme()
    ensure_session_state()

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
    louvores_df = load_data(
        LOUVORES_FILE,
        ("title", "artist", "key", "youtube_url", "cifra_url", "ritmo", "letter", "source"),
    )

    inject_mobile_app_shell()

    if not st.session_state.authenticated:
        show_login_page(members_df)
        return

    render_sidebar_profile()
    render_push_admin_sidebar()
    render_mobile_and_push_panel()
    menu = render_navigation()

    primary = st.session_state.get("user_primary_role", "membro")
    badge = "👑" if primary == ROLE_LIDER else ("🎯" if is_scale_manager(st.session_state.user_roles) else "🎤")
    st.markdown(
        f'<div class="mobile-user-bar">{badge} <strong>{st.session_state.user_name}</strong><br>'
        f'<span style="font-size:0.82rem;color:#a89bc4">{roles_for_public_display(st.session_state.user_roles)}</span></div>',
        unsafe_allow_html=True,
    )
    page_header(menu)

    if menu == "Gerenciar Escalas":
        show_gerenciar_escalas(
            escalas_df, programa_df, equipe_df, louvores_df, members_df
        )

    elif menu == "Dashboard":
        show_dashboard(
            escalas_df, programa_df, equipe_df, louvores_df, members_df, chat_df, playlist_df
        )

    elif menu == "Catálogo":
        show_louvores_catalog(louvores_df)

    elif menu == "Escalas":
        show_escalas_page(
            escalas_df, trocas_df, members_df, programa_df, equipe_df, louvores_df
        )

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
                st.error("Informe pelo menos título e artista.")
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
        if is_scale_manager(st.session_state.user_roles):
            show_members_overview(members_df, louvores_df)
        else:
            st.markdown('<p class="music-panel-title">🎹 Equipe de louvor</p>', unsafe_allow_html=True)
            st.write("Integrantes do ministério.")
            if not members_df.empty:
                display_df = members_df.drop(
                    columns=["password_hash", "profile_photo"], errors="ignore"
                )
                page_members = paginate_dataframe(display_df, 15, "membros")
                st.dataframe(page_members, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum membro cadastrado ainda.")

if __name__ == "__main__":
    main()
