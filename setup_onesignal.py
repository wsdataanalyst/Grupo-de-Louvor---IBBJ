#!/usr/bin/env python3
"""
Assistente para configurar OneSignal e gerar .streamlit/secrets.toml

Uso:
  python setup_onesignal.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SECRETS_DIR = ROOT / ".streamlit"
SECRETS_FILE = SECRETS_DIR / "secrets.toml"
EXAMPLE_FILE = SECRETS_DIR / "secrets.toml.example"


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


def valid_url(url: str) -> bool:
    return bool(re.match(r"^https://.+", url, re.I))


def main() -> int:
    print()
    print("=" * 60)
    print("  Configuração OneSignal — Grupo de Louvor IBBJ")
    print("=" * 60)
    print()
    print("Antes de continuar, no site https://onesignal.com:")
    print("  1. Crie conta (grátis)")
    print("  2. New App → nome: Grupo de Louvor IBBJ")
    print("  3. Plataforma: Web / Web Push")
    print("  4. Em Settings → Keys & IDs copie:")
    print("     - OneSignal App ID")
    print("     - REST API Key")
    print("  5. Em Settings → Platforms → Web:")
    print("     - Site URL = URL HTTPS do app (ex.: Streamlit Cloud)")
    print()
    if not ask_yes("Já criou o app no OneSignal?", default=False):
        print()
        print("Abra o guia: CONFIGURAR_ONESIGNAL.md")
        print("Depois execute de novo: python setup_onesignal.py")
        return 1

    print()
    public_url = ask(
        "URL pública HTTPS do app",
        "https://seu-app.streamlit.app",
    )
    while not valid_url(public_url):
        print("  ⚠ Use HTTPS (obrigatório para push). Ex.: https://xxx.streamlit.app")
        public_url = ask("URL pública HTTPS do app")

    app_id = ask("OneSignal App ID")
    while len(app_id) < 8:
        print("  ⚠ App ID inválido (copie em Keys & IDs no OneSignal)")
        app_id = ask("OneSignal App ID")

    api_key = ask("OneSignal REST API Key")
    while len(api_key) < 10:
        print("  ⚠ REST API Key inválida")
        api_key = ask("OneSignal REST API Key")

    dev_emails = ask(
        "E-mails de desenvolvedor (separados por vírgula)",
        "wsdataanalyst, willsousaa7x@gmail.com",
    )
    dev_list = ", ".join(f'"{e.strip()}"' for e in dev_emails.split(",") if e.strip())
    dev_password = ask("Senha padrão da conta desenvolvedor", "IbbjDev2024")

    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    content = f'''# Gerado por setup_onesignal.py — não commite este arquivo

public_url = "{public_url}"

push_notifications_enabled = true
onesignal_app_id = "{app_id}"
onesignal_rest_api_key = "{api_key}"

developer_emails = [{dev_list}]
dev_default_password = "{dev_password}"
'''
    SECRETS_FILE.write_text(content, encoding="utf-8")
    print()
    print(f"✅ Arquivo salvo: {SECRETS_FILE}")
    print()

    if ask_yes("Enviar notificação de teste agora?", default=True):
        import json
        import urllib.error
        import urllib.request

        payload = {
            "app_id": app_id,
            "included_segments": ["Subscribed Users"],
            "headings": {"en": "Teste IBBJ", "pt": "Teste IBBJ"},
            "contents": {
                "en": "Se você recebeu isto, o servidor está OK!",
                "pt": "Se você recebeu isto, o servidor está OK!",
            },
            "url": public_url,
        }
        req = urllib.request.Request(
            "https://onesignal.com/api/v1/notifications",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read().decode()
                print("✅ API OneSignal respondeu OK.")
                print("   (Só chega no celular quem já ativou notificações no app.)")
                if body.strip():
                    print(f"   Resposta: {body[:200]}")
        except urllib.error.HTTPError as exc:
            print("❌ Erro na API OneSignal:")
            print(exc.read().decode())
            print()
            print("Confira: Site URL no painel = mesma public_url acima.")
            return 1

    print()
    print("Próximos passos:")
    print("  1. python scripts/generate_pwa_icons.py   (se ainda não rodou)")
    print("  2. streamlit run app.py")
    print("  3. No app: expander 📲 → Ativar notificações")
    print("  4. Se for Streamlit Cloud: cole o mesmo TOML em Settings → Secrets")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
