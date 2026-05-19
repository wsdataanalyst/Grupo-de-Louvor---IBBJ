"""Recuperação de senha por e-mail (SMTP) com token de uso único."""

from __future__ import annotations

import hashlib
import os
import secrets
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

import pandas as pd

TOKEN_TTL_HOURS = 1
MAX_REQUESTS_PER_EMAIL_PER_HOUR = 3
TOKEN_COLUMNS = ("token_hash", "email", "created_at", "expires_at", "used_at")


def _secret_get(key: str, default: str = "") -> str:
    try:
        import streamlit as st

        if key in st.secrets:
            return str(st.secrets[key]).strip()
        smtp = st.secrets.get("smtp")
        if smtp and key in smtp:
            return str(smtp[key]).strip()
    except Exception:
        pass
    env_key = f"SMTP_{key.upper()}"
    return os.environ.get(env_key, default).strip()


def smtp_is_configured() -> bool:
    host = _secret_get("host")
    user = _secret_get("user")
    password = _secret_get("password")
    from_email = _secret_get("from_email") or user
    enabled = _secret_get("enabled", "true").lower()
    if enabled in ("0", "false", "nao", "no", "off"):
        return False
    return bool(host and user and password and from_email)


def smtp_config_status() -> dict[str, Any]:
    return {
        "configured": smtp_is_configured(),
        "host": _secret_get("host"),
        "port": _secret_get("port", "587"),
        "from_email": _secret_get("from_email") or _secret_get("user"),
        "user": _secret_get("user"),
        "has_password": bool(_secret_get("password")),
    }


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def tokens_file_path(data_dir: Path) -> Path:
    return data_dir / "password_reset_tokens.csv"


def load_tokens(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=list(TOKEN_COLUMNS))
    try:
        df = pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=list(TOKEN_COLUMNS))
    for col in TOKEN_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[list(TOKEN_COLUMNS)].copy()


def save_tokens(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def purge_expired_tokens(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    now = datetime.now()
    keep = []
    for _, row in df.iterrows():
        used = str(row.get("used_at", "")).strip()
        if used:
            continue
        try:
            exp = pd.to_datetime(row["expires_at"])
            if pd.notna(exp) and exp.to_pydatetime() < now:
                continue
        except (ValueError, TypeError):
            pass
        keep.append(row)
    if not keep:
        return pd.DataFrame(columns=list(TOKEN_COLUMNS))
    return pd.DataFrame(keep).reset_index(drop=True)


def count_recent_requests(df: pd.DataFrame, email: str) -> int:
    email = email.strip().lower()
    since = datetime.now() - timedelta(hours=1)
    if df.empty:
        return 0
    n = 0
    for _, row in df.iterrows():
        if str(row.get("email", "")).strip().lower() != email:
            continue
        if str(row.get("used_at", "")).strip():
            continue
        try:
            created = pd.to_datetime(row["created_at"])
            if pd.notna(created) and created.to_pydatetime() >= since:
                n += 1
        except (ValueError, TypeError):
            pass
    return n


def member_exists(members_df: pd.DataFrame, email: str) -> bool:
    email = email.strip().lower()
    if members_df.empty or "email" not in members_df.columns:
        return False
    emails = members_df["email"].astype(str).str.strip().str.lower()
    return email in emails.values


def member_first_name(members_df: pd.DataFrame, email: str) -> str:
    email = email.strip().lower()
    match = members_df[members_df["email"].astype(str).str.lower() == email]
    if match.empty:
        return "integrante"
    return str(match.iloc[0].get("first_name", "integrante")).strip() or "integrante"


def build_reset_email_html(name: str, reset_url: str, group_name: str) -> str:
    return f"""\
<html><body style="font-family:Segoe UI,sans-serif;background:#f4f2fa;padding:24px">
  <div style="max-width:520px;margin:0 auto;background:#fff;border-radius:12px;padding:28px;border:1px solid #e8e4f0">
    <h2 style="color:#1a1530;margin:0 0 12px">Redefinição de senha</h2>
    <p style="color:#4a4560;line-height:1.6">Olá, <strong>{name}</strong>!</p>
    <p style="color:#4a4560;line-height:1.6">
      Recebemos um pedido para redefinir sua senha no <strong>{group_name}</strong>.
      O link abaixo vale por <strong>1 hora</strong> e só pode ser usado uma vez.
    </p>
    <p style="margin:24px 0">
      <a href="{reset_url}" style="display:inline-block;background:#7c3aed;color:#fff;
         text-decoration:none;padding:12px 22px;border-radius:8px;font-weight:600">
        Redefinir minha senha
      </a>
    </p>
    <p style="color:#888;font-size:13px;line-height:1.5">
      Se você não pediu isso, ignore este e-mail. Sua senha atual continua válida.
    </p>
    <p style="color:#aaa;font-size:12px;word-break:break-all">{reset_url}</p>
  </div>
</body></html>"""


def build_reset_email_text(name: str, reset_url: str, group_name: str) -> str:
    return (
        f"Olá, {name}!\n\n"
        f"Pedido de redefinição de senha no {group_name}.\n"
        f"Acesse o link (válido por 1 hora):\n{reset_url}\n\n"
        "Se você não pediu isso, ignore este e-mail.\n"
    )


def send_reset_email(
    to_email: str,
    reset_url: str,
    *,
    member_name: str,
    group_name: str,
) -> tuple[bool, str]:
    if not smtp_is_configured():
        return False, "SMTP não configurado no servidor."

    host = _secret_get("host")
    port = int(_secret_get("port", "587") or "587")
    user = _secret_get("user")
    password = _secret_get("password")
    from_email = _secret_get("from_email") or user
    use_tls = _secret_get("use_tls", "true").lower() not in ("0", "false", "no", "off")

    subject = f"{group_name} — redefinir sua senha"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    text = build_reset_email_text(member_name, reset_url, group_name)
    html = build_reset_email_html(member_name, reset_url, group_name)
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        if use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port, timeout=30) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(user, password)
                server.sendmail(from_email, [to_email], msg.as_string())
        else:
            with smtplib.SMTP_SSL(host, port, timeout=30) as server:
                server.login(user, password)
                server.sendmail(from_email, [to_email], msg.as_string())
        return True, "E-mail enviado."
    except smtplib.SMTPAuthenticationError:
        return False, "Falha de autenticação SMTP. Verifique usuário e senha do e-mail."
    except Exception as exc:
        return False, f"Erro ao enviar e-mail: {exc}"


def create_password_reset_request(
    email: str,
    members_df: pd.DataFrame,
    tokens_path: Path,
    *,
    reset_url_base: str,
    reset_query_param: str,
    group_name: str,
) -> tuple[bool, str, str]:
    """
    Cria token e envia e-mail se o endereço estiver cadastrado.
    Retorna (enviou_email_real, mensagem_usuario, link_dev_vazio_ou_url).
    """
    email = email.strip().lower()
    generic_ok = (
        "Se este e-mail estiver cadastrado, você receberá um link para redefinir a senha "
        f"em alguns minutos. Verifique também a pasta de spam."
    )

    if "@" not in email or len(email) < 5:
        return False, "Informe um e-mail válido.", ""

    if not member_exists(members_df, email):
        return True, generic_ok, ""

    if not smtp_is_configured():
        return (
            False,
            "O envio de e-mail ainda não está configurado no servidor. "
            "Peça ao líder ou desenvolvedor para configurar o SMTP em secrets.toml.",
            "",
        )

    df = purge_expired_tokens(load_tokens(tokens_path))
    if count_recent_requests(df, email) >= MAX_REQUESTS_PER_EMAIL_PER_HOUR:
        return (
            True,
            "Já enviamos um link recentemente para este e-mail. "
            "Aguarde alguns minutos antes de tentar de novo.",
            "",
        )

    token = secrets.token_urlsafe(32)
    now = datetime.now()
    expires = now + timedelta(hours=TOKEN_TTL_HOURS)
    new_row = {
        "token_hash": hash_token(token),
        "email": email,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires.strftime("%Y-%m-%d %H:%M:%S"),
        "used_at": "",
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_tokens(df, tokens_path)

    sep = "&" if "?" in reset_url_base else "?"
    reset_url = f"{reset_url_base}{sep}{reset_query_param}={token}"
    name = member_first_name(members_df, email)
    ok, detail = send_reset_email(
        email, reset_url, member_name=name, group_name=group_name
    )
    if not ok:
        return False, detail, ""
    return True, generic_ok, ""


def validate_reset_token(token: str, tokens_path: Path) -> tuple[str | None, str]:
    token = token.strip()
    if not token or len(token) < 20:
        return None, "Link inválido."

    df = purge_expired_tokens(load_tokens(tokens_path))
    th = hash_token(token)
    match = df[df["token_hash"].astype(str) == th]
    if match.empty:
        return None, "Este link não é válido ou já foi utilizado."

    row = match.iloc[0]
    if str(row.get("used_at", "")).strip():
        return None, "Este link já foi utilizado. Solicite um novo e-mail."

    try:
        exp = pd.to_datetime(row["expires_at"])
        if pd.notna(exp) and exp.to_pydatetime() < datetime.now():
            return None, "Este link expirou. Solicite um novo e-mail de recuperação."
    except (ValueError, TypeError):
        return None, "Link inválido."

    return str(row["email"]).strip().lower(), ""


def apply_password_reset(
    token: str,
    new_password: str,
    members_df: pd.DataFrame,
    tokens_path: Path,
    *,
    hash_password_fn,
) -> tuple[bool, str]:
    email, err = validate_reset_token(token, tokens_path)
    if not email:
        return False, err

    if len(new_password) < 6:
        return False, "A nova senha deve ter pelo menos 6 caracteres."

    emails = members_df["email"].astype(str).str.strip().str.lower()
    idx_list = members_df.index[emails == email].tolist()
    if not idx_list:
        return False, "Conta não encontrada."

    idx = idx_list[0]
    members_df.at[idx, "password_hash"] = hash_password_fn(new_password)

    df = load_tokens(tokens_path)
    th = hash_token(token.strip())
    mask = df["token_hash"].astype(str) == th
    if mask.any():
        df.loc[mask, "used_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_tokens(df, tokens_path)

    return True, ""
