"""Links para compartilhar no WhatsApp (wa.me)."""

from __future__ import annotations

from urllib.parse import quote_plus


def whatsapp_share_url(text: str, url: str = "") -> str:
    parts = [str(text).strip()]
    u = str(url).strip()
    if u:
        parts.append(u)
    msg = "\n".join(p for p in parts if p)
    return f"https://wa.me/?text={quote_plus(msg)}"


def share_escala_text(
    event: str,
    culto_date: str,
    ensaio: str = "",
    team_lines: list[str] | None = None,
) -> str:
    lines = [
        f"🎤 *Escala — {event}*",
        f"📅 Culto: {culto_date}",
    ]
    if ensaio:
        lines.append(f"🎹 Ensaio: {ensaio}")
    if team_lines:
        lines.append("")
        lines.append("*Equipe:*")
        lines.extend(team_lines[:20])
    lines.append("")
    lines.append("Grupo de Louvor IBBJ")
    return "\n".join(lines)
