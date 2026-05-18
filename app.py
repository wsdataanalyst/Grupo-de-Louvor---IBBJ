import hashlib
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
MEMBERS_FILE = DATA_DIR / "members.csv"
CHAT_FILE = DATA_DIR / "chat.csv"
ESCALAS_FILE = DATA_DIR / "escalas.csv"
PLAYLIST_FILE = DATA_DIR / "playlist.csv"

ROLES = [
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


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@st.cache_data
def load_data(file_path: Path, columns):
    if not file_path.exists():
        return pd.DataFrame(columns=columns)
    df = pd.read_csv(file_path)
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    return df[columns]


def save_data(df: pd.DataFrame, file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)


def authenticate(email: str, password: str, users_df: pd.DataFrame):
    email = email.strip().lower()
    hashed = hash_password(password)
    match = users_df[(users_df["email"] == email) & (users_df["password_hash"] == hashed)]
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
    if email in members_df["email"].astype(str).str.lower().values:
        return None, "Este email já está cadastrado."

    new_member = {
        "first_name": first_name.strip().title(),
        "last_name": last_name.strip().title(),
        "email": email,
        "roles": ", ".join(roles),
        "password_hash": hash_password(password),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    members_df = pd.concat([members_df, pd.DataFrame([new_member])], ignore_index=True)
    save_data(members_df, MEMBERS_FILE)
    return new_member, None


def ensure_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.session_state.user_roles = ""


def show_login_page(members_df: pd.DataFrame):
    st.header("Acesso ao sistema")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        with st.form(key="login_form"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Senha", type="password", key="login_password")
            login_button = st.form_submit_button("Entrar")

        if login_button:
            user = authenticate(login_email, login_password, members_df)
            if user is not None:
                st.session_state.authenticated = True
                st.session_state.user_name = user["first_name"]
                st.session_state.user_email = user["email"]
                st.session_state.user_roles = user["roles"]
                st.success(f"Olá {user['first_name']}, seja bem-vindo!")
                st.experimental_rerun()
            else:
                st.error("Email ou senha incorretos.")

    with col2:
        st.subheader("Cadastro de novo membro")
        with st.form(key="register_form"):
            first_name = st.text_input("Nome", key="reg_first_name")
            last_name = st.text_input("Sobrenome", key="reg_last_name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Senha", type="password", key="reg_password")
            confirm_password = st.text_input(
                "Confirme a senha", type="password", key="reg_confirm_password"
            )
            roles = st.multiselect("Função(s) no grupo", ROLES, key="reg_roles")
            register_button = st.form_submit_button("Cadastrar")

        if register_button:
            if not first_name or not last_name or not email or not password or not roles:
                st.error("Preencha todos os campos obrigatórios e escolha pelo menos uma função.")
            elif password != confirm_password:
                st.error("As senhas não coincidem.")
            else:
                new_member, error = register_user(
                    first_name, last_name, email, password, roles, members_df
                )
                if error:
                    st.error(error)
                else:
                    st.success(f"Olá {new_member['first_name']}, seu cadastro foi criado!")
                    st.info(
                        "Use o email e a senha para entrar no sistema. Compartilhe o link do app com outros membros."
                    )

    st.markdown("---")
    st.write(
        "Depois de fazer login, você poderá acessar as áreas de Escalas, Playlist, Chat e Membros."
    )


def main():
    st.set_page_config(page_title="Organização Grupo de Louvor", layout="wide")
    ensure_session_state()

    members_df = load_data(
        MEMBERS_FILE,
        ["first_name", "last_name", "email", "roles", "password_hash", "created_at"],
    )
    chat_df = load_data(CHAT_FILE, ["timestamp", "name", "message"])
    escalas_df = load_data(
        ESCALAS_FILE, ["date", "event", "responsible", "notes"]
    )
    playlist_df = load_data(
        PLAYLIST_FILE, ["title", "artist", "url", "notes", "added_at"]
    )

    st.title("Organização do Grupo de Louvor")
    st.write(
        "Este app ajuda a organizar membros, escalas, playlist e interação do grupo de louvor."
    )

    if not st.session_state.authenticated:
        show_login_page(members_df)
        return

    st.sidebar.write(f"Usuário: {st.session_state.user_name}")
    if st.sidebar.button("Sair"):
        st.session_state.authenticated = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.session_state.user_roles = ""
        st.experimental_rerun()

    menu = st.sidebar.selectbox(
        "Navegação",
        ["Dashboard", "Escalas", "Playlist", "Chat", "Membros"],
    )

    st.success(f"Bem vindo, {st.session_state.user_name}! Você faz parte como {st.session_state.user_roles}.")

    if menu == "Dashboard":
        st.header("Painel inicial")
        st.write(
            "Use o menu lateral para navegar entre Escalas, Playlist, Chat e Membros."
        )
        st.metric("Membros cadastrados", len(members_df))
        st.metric("Mensagens no chat", len(chat_df))
        st.metric("Músicas na playlist", len(playlist_df))

    elif menu == "Escalas":
        st.header("Escalas do grupo")
        st.write(
            "Registre aqui as escalas de fim de semana, cultos e eventos especiais."
        )
        with st.form(key="escala_form"):
            date = st.date_input("Data do evento")
            event = st.text_input("Evento / Descrição")
            responsible = st.text_input("Responsável / Equipe")
            notes = st.text_area("Notas adicionais")
            submit = st.form_submit_button("Adicionar escala")

        if submit:
            if not event:
                st.error("Informe o nome do evento ou descrição.")
            else:
                new_row = {
                    "date": date.strftime("%Y-%m-%d"),
                    "event": event.strip(),
                    "responsible": responsible.strip(),
                    "notes": notes.strip(),
                }
                escalas_df = pd.concat([escalas_df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(escalas_df, ESCALAS_FILE)
                st.success("Escala adicionada com sucesso.")

        if not escalas_df.empty:
            st.subheader("Escalas registradas")
            st.dataframe(escalas_df.sort_values("date", ascending=False))
        else:
            st.info("Nenhuma escala registrada ainda.")

    elif menu == "Playlist":
        st.header("Playlist do grupo")
        st.write(
            "Adicione músicas que serão usadas nas reuniões, com título, artista e link opcional."
        )
        with st.form(key="playlist_form"):
            title = st.text_input("Nome da música")
            artist = st.text_input("Artista / Banda")
            url = st.text_input("Link da música (YouTube, Spotify, etc.)")
            notes = st.text_area("Observações")
            submit = st.form_submit_button("Adicionar música")

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

        if not playlist_df.empty:
            st.subheader("Playlist registrada")
            st.dataframe(
                playlist_df["title artist url notes added_at".split()].sort_values(
                    "added_at", ascending=False
                )
            )
        else:
            st.info("Nenhuma música adicionada ainda.")

    elif menu == "Chat":
        st.header("Chat do grupo")
        st.write(
            "Use este espaço para interagir com outros membros do grupo."
        )
        with st.form(key="chat_form"):
            name = st.text_input("Seu nome", value=st.session_state.user_name)
            message = st.text_area("Mensagem")
            send = st.form_submit_button("Enviar mensagem")

        if send:
            if not name or not message:
                st.error("Informe seu nome e a mensagem.")
            else:
                new_message = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": name.strip().title(),
                    "message": message.strip(),
                }
                chat_df = pd.concat([chat_df, pd.DataFrame([new_message])], ignore_index=True)
                save_data(chat_df, CHAT_FILE)
                st.success("Mensagem enviada.")

        if not chat_df.empty:
            chat_display = chat_df.sort_values("timestamp", ascending=False)
            chat_display["timestamp"] = pd.to_datetime(chat_display["timestamp"]).dt.strftime("%d/%m %H:%M")
            st.dataframe(chat_display)
        else:
            st.info("Ainda não há mensagens no chat.")

    elif menu == "Membros":
        st.header("Base de membros")
        if not members_df.empty:
            display_df = members_df.drop(columns=["password_hash"], errors="ignore")
            st.dataframe(display_df)
        else:
            st.info("Nenhum membro cadastrado ainda.")

    st.sidebar.markdown("---")
    st.sidebar.write(
        "Próximos passos: deploy no Streamlit Cloud e envio de e-mail para convite de membros."
    )


if __name__ == "__main__":
    main()
