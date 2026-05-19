#!/usr/bin/env python3
"""
Assistente para configurar SMTP (Esqueci minha senha).

Uso:
  python setup_smtp.py

Atualiza .streamlit/secrets.toml sem apagar OneSignal/outras chaves.
No Streamlit Cloud: cole o bloco [smtp] em Settings → Secrets.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SECRETS_DIR = ROOT / ".streamlit"
SECRETS_FILE = SECRETS_DIR / "secrets.toml"


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def ask_yes(prompt: str, default: bool = True) -> bool:
    d = "S" if default else "n"
    value = input(f"{prompt} (s/n) [{d}]: ").strip().lower()
    if not value:
        return default
    return value in ("s", "sim", "y", "yes", "1")


def read_public_url_from_secrets() -> str:
    if not SECRETS_FILE.exists():
        return ""
    text = SECRETS_FILE.read_text(encoding="utf-8")
    match = re.search(r'^public_url\s*=\s*"(.*?)"', text, re.M)
    return match.group(1).strip() if match else ""


def build_smtp_block(
    host: str,
    port: int,
    user: str,
    password: str,
    from_email: str,
    use_tls: bool,
) -> str:
    tls = "true" if use_tls else "false"
    return f"""[smtp]
enabled = true
host = "{host}"
port = {port}
user = "{user}"
password = "{password}"
from_email = "{from_email}"
use_tls = {tls}"""


def merge_smtp_into_secrets(smtp_block: str) -> None:
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    if not SECRETS_FILE.exists():
        public_url = ask(
            "URL pública do app (HTTPS, para links no e-mail)",
            "https://seu-app.streamlit.app",
        )
        SECRETS_FILE.write_text(
            f'# Gerado por setup_smtp.py\n\npublic_url = "{public_url}"\n\n{smtp_block}\n',
            encoding="utf-8",
        )
        return

    text = SECRETS_FILE.read_text(encoding="utf-8")
    text = re.sub(r"\n*\[smtp\][\s\S]*?(?=\n\[|\Z)", "\n", text)
    text = text.rstrip() + "\n\n" + smtp_block.strip() + "\n"
    SECRETS_FILE.write_text(text, encoding="utf-8")


def main() -> int:
    print()
    print("=" * 60)
    print("  Configuração SMTP — Esqueci minha senha")
    print("=" * 60)
    print()
    print("Gmail (recomendado):")
    print("  1. Ative verificação em 2 etapas na conta Google")
    print("  2. Crie Senha de app: https://myaccount.google.com/apppasswords")
    print("  3. Use essa senha (16 caracteres) no campo abaixo — NÃO a senha normal")
    print()
    print("Outros provedores: Outlook, Hostinger, Zoho — veja CONFIGURAR_EMAIL.md")
    print()

    provider = ask("Provedor (gmail/outlook/outro)", "gmail").lower()
    if provider == "gmail":
        host, port, use_tls = "smtp.gmail.com", 587, True
    elif provider == "outlook":
        host, port, use_tls = "smtp.office365.com", 587, True
    else:
        host = ask("Servidor SMTP (host)", "smtp.gmail.com")
        port = int(ask("Porta", "587") or "587")
        use_tls = ask_yes("Usar TLS (STARTTLS)?", default=True)

    user = ask("E-mail de envio (login SMTP)", "seu-email@gmail.com")
    password = ask("Senha de app / senha SMTP")
    while len(password) < 8:
        print("  ⚠ Senha muito curta.")
        password = ask("Senha de app / senha SMTP")

    default_from = f"Grupo de Louvor IBBJ <{user}>"
    from_email = ask("Remetente (From)", default_from)

    smtp_block = build_smtp_block(host, port, user, password, from_email, use_tls)
    merge_smtp_into_secrets(smtp_block)

    print()
    print(f"✅ SMTP salvo em: {SECRETS_FILE}")
    print()

    if ask_yes("Enviar e-mail de teste agora?", default=True):
        test_to = ask("Enviar teste para qual e-mail?", user)
        from password_reset import send_email_message

        ok, msg = send_email_message(
            host=host,
            port=port,
            user=user,
            password=password,
            from_email=from_email,
            to_email=test_to,
            subject="Grupo de Louvor IBBJ — teste SMTP",
            text_body="Se você recebeu isto, o Esqueci minha senha está pronto.",
            html_body="<p>Se você recebeu isto, o <strong>Esqueci minha senha</strong> está pronto.</p>",
            use_tls=use_tls,
        )
        if ok:
            print(f"✅ {msg} Verifique a caixa de entrada de {test_to}")
        else:
            print(f"❌ {msg}")
            print("   Gmail: confira se usou Senha de app, não a senha da conta.")
            return 1

    print()
    print("Próximos passos:")
    print("  1. Reinicie o app: streamlit run app.py")
    print("  2. Teste: login → Esqueci minha senha")
    print("  3. Streamlit Cloud: Settings → Secrets")
    print("     Cole o bloco [smtp] (e public_url) do arquivo secrets.toml")
    print()
    print("Bloco para copiar no Cloud:")
    print("-" * 40)
    print(smtp_block)
    print("-" * 40)
    existing_url = read_public_url_from_secrets()
    if existing_url:
        print(f'public_url = "{existing_url}"  (já no secrets.toml)')
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
