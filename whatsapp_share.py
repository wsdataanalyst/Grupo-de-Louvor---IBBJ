"""Compartilhamento de escalas no WhatsApp (texto, PDF e configuração)."""

from __future__ import annotations

import base64
import hashlib
import json
from urllib.parse import quote_plus


def _pdf_b64_signature(pdf_bytes: bytes) -> str:
    return hashlib.md5(pdf_bytes).hexdigest()


def pdf_bytes_to_b64_cached(pdf_bytes: bytes, cache_key: str) -> str:
    """Evita re-encodar o mesmo PDF a cada rerun (Fase 4)."""
    import streamlit as st

    sig = _pdf_b64_signature(pdf_bytes)
    bucket = st.session_state.get(cache_key)
    if isinstance(bucket, dict) and bucket.get("sig") == sig and bucket.get("b64"):
        return str(bucket["b64"])
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    st.session_state[cache_key] = {"sig": sig, "b64": b64}
    return b64


def clear_pdf_b64_cache(cache_key: str) -> None:
    import streamlit as st

    st.session_state.pop(cache_key, None)


def _secret_whatsapp(key: str, default: str = "") -> str:
    try:
        import streamlit as st

        if "whatsapp" in st.secrets and key in st.secrets["whatsapp"]:
            return str(st.secrets["whatsapp"][key]).strip()
        wkey = f"whatsapp_{key}"
        if wkey in st.secrets:
            return str(st.secrets[wkey]).strip()
    except Exception:
        pass
    return default


def whatsapp_group_phone() -> str:
    """Número do grupo ou do líder (DDI+DDD+número, só dígitos). Ex.: 5511999999999"""
    return "".join(c for c in _secret_whatsapp("group_phone") if c.isdigit())


def whatsapp_auto_prompt_enabled() -> bool:
    v = _secret_whatsapp("auto_prompt_on_save", "true").lower()
    return v in ("1", "true", "sim", "yes", "on")


def whatsapp_share_url(text: str, url: str = "", phone: str = "") -> str:
    parts = [str(text).strip()]
    u = str(url).strip()
    if u:
        parts.append(u)
    msg = "\n".join(p for p in parts if p)
    encoded = quote_plus(msg)
    digits = "".join(c for c in str(phone) if c.isdigit())
    if digits:
        return f"https://wa.me/{digits}?text={encoded}"
    return f"https://wa.me/?text={encoded}"


def build_escala_share_message(
    *,
    event: str,
    culto_date: str,
    ensaio_date: str = "",
    ministrador: str = "",
    equipe: list[tuple[str, str]] | None = None,
    programa: list[tuple[str, str, str, str]] | None = None,
    notas: str = "",
) -> str:
    """
    Mensagem completa para WhatsApp.
    programa: lista (ordem, parte, louvor, tom).
    equipe: lista (nome, função) — ministrador pode estar duplicado; será destacado.
    """
    lines = [
        "🎤 *ESCALA — Grupo de Louvor IBBJ*",
        "",
        f"📅 *Culto:* {culto_date}",
        f"🎪 *Evento:* {event}",
    ]
    if ensaio_date:
        lines.append(f"🎹 *Ensaio:* {ensaio_date}")
    else:
        lines.append("🎹 *Ensaio:* a confirmar")
    if ministrador:
        lines.append(f"✝️ *Ministrador:* {ministrador}")
    lines.append("")

    if equipe:
        lines.append("👥 *Equipe escalada:*")
        for nome, funcao in equipe:
            if not nome:
                continue
            lines.append(f"• {nome} — {funcao}")
        lines.append("")

    if programa:
        lines.append("🎶 *Louvores (sequência):*")
        for ordem, parte, louvor, tom in programa:
            tom_s = f" (Tom {tom})" if tom and str(tom).lower() not in ("nan", "") else ""
            parte_s = f"[{parte}] " if parte else ""
            lines.append(f"{ordem}. {parte_s}{louvor}{tom_s}")
        lines.append("")

    if notas and str(notas).strip():
        lines.append(f"📝 *Notas:* {notas.strip()}")
        lines.append("")

    lines.append("_Gerado pelo app GDL — confira sempre no painel oficial._")
    return "\n".join(lines)


def _inject_html(html_fragment: str, height: int = 0) -> None:
    import streamlit.components.v1 as components

    components.html(html_fragment, height=height or None, scrolling=False)


def inject_copy_whatsapp_message(message: str, element_id: str = "wa-copy-msg") -> None:
    """Botão via HTML/JS para copiar texto (útil antes de colar no grupo)."""
    safe = json.dumps(message)
    _inject_html(
        f"""
        <button id="{element_id}" type="button" style="
            width:100%;padding:0.55rem 1rem;margin:0.25rem 0;
            background:#25D366;color:#fff;border:none;border-radius:10px;
            font-weight:700;cursor:pointer;font-size:0.9rem;">
            📋 Copiar texto da escala
        </button>
        <script>
        (function() {{
          var btn = window.parent.document.getElementById("{element_id}");
          if (!btn) return;
          var msg = {safe};
          btn.onclick = function() {{
            navigator.clipboard.writeText(msg).then(function() {{
              btn.textContent = "✓ Copiado! Cole no WhatsApp do grupo";
              setTimeout(function() {{ btn.textContent = "📋 Copiar texto da escala"; }}, 2500);
            }}).catch(function() {{
              prompt("Copie a mensagem:", msg);
            }});
          }};
        }})();
        </script>
        """,
        height=52,
    )


def inject_share_pdf_whatsapp(
    pdf_bytes: bytes,
    filename: str,
    share_text: str,
    element_id: str = "wa-share-pdf",
) -> None:
    """
    Tenta compartilhar PDF via Web Share API (celular: costuma abrir WhatsApp com anexo).
    No desktop pode só baixar — o usuário envia manualmente.
    """
    b64 = pdf_bytes_to_b64_cached(pdf_bytes, f"wa_pdf_b64_{element_id}")
    safe_name = json.dumps(filename)
    safe_text = json.dumps(share_text[:500])
    _inject_html(
        f"""
        <button id="{element_id}" type="button" style="
            width:100%;padding:0.55rem 1rem;margin:0.25rem 0;
            background:#128C7E;color:#fff;border:none;border-radius:10px;
            font-weight:700;cursor:pointer;font-size:0.9rem;">
            📎 Enviar PDF no WhatsApp (celular)
        </button>
        <p style="color:#a89bc4;font-size:0.75rem;margin:0.2rem 0 0;">
            No iPhone/Android abre o menu de compartilhar com o PDF. No PC use Baixar PDF.
        </p>
        <script>
        (function() {{
          var btn = window.parent.document.getElementById("{element_id}");
          if (!btn) return;
          var b64 = "{b64}";
          var fname = {safe_name};
          var text = {safe_text};
          btn.onclick = async function() {{
            try {{
              var raw = atob(b64);
              var arr = new Uint8Array(raw.length);
              for (var i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
              var blob = new Blob([arr], {{ type: "application/pdf" }});
              var file = new File([blob], fname, {{ type: "application/pdf" }});
              if (navigator.share && navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                await navigator.share({{ files: [file], title: fname, text: text }});
                btn.textContent = "✓ Compartilhado";
              }} else {{
                var a = document.createElement("a");
                a.href = "data:application/pdf;base64," + b64;
                a.download = fname;
                a.click();
                alert("Seu navegador não envia PDF direto ao WhatsApp. Baixe o arquivo e anexe no grupo.");
              }}
            }} catch (e) {{
              alert("Não foi possível compartilhar o PDF: " + e);
            }}
          }};
        }})();
        </script>
        """,
        height=88,
    )


def _render_pdf_preview(
    pdf_bytes: bytes,
    b64: str,
    *,
    mobile: bool,
    height: int,
) -> None:
    """Preview in-app; st.pdf no mobile (iOS) com fallback para iframe."""
    import streamlit as st

    try:
        st.pdf(pdf_bytes, height=height)
        return
    except Exception:
        pass
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="{height}" '
        f'style="border:1px solid #334155;border-radius:12px;background:#fff;"></iframe>',
        unsafe_allow_html=True,
    )


def render_pdf_delivery_panel(
    pdf_bytes: bytes,
    filename: str,
    *,
    b64_cache_key: str,
    download_key: str,
    back_key: str,
    on_back,
    share_text: str = "",
    share_element_id: str = "",
    success_message: str = "PDF pronto! Baixe ou compartilhe abaixo.",
    back_label: str = "← Voltar ao app",
    preview_label: str = "👁️ Ver PDF aqui",
) -> None:
    """Painel de entrega de PDF — preview no app (mobile), download e WhatsApp."""
    import streamlit as st

    from mobile_lab import is_mobile_lab_enabled

    mobile = is_mobile_lab_enabled()
    b64 = pdf_bytes_to_b64_cached(pdf_bytes, b64_cache_key)
    st.success(success_message)

    def _go_back() -> None:
        on_back()
        st.rerun()

    if mobile:
        if st.button(back_label, use_container_width=True, key=f"{back_key}_top"):
            _go_back()
        st.caption(
            "Veja o PDF abaixo sem sair do app. Para salvar ou enviar, use os botões "
            "desta tela — no iPhone, **não** abra em nova aba."
        )
        with st.expander(preview_label, expanded=True):
            _render_pdf_preview(pdf_bytes, b64, mobile=True, height=420)
    else:
        with st.expander(preview_label, expanded=False):
            _render_pdf_preview(pdf_bytes, b64, mobile=False, height=480)

    if mobile and share_text and share_element_id and len(pdf_bytes) <= 2_500_000:
        inject_share_pdf_whatsapp(
            pdf_bytes,
            filename,
            share_text[:300],
            element_id=share_element_id,
        )

    c_dl, c_back = st.columns(2, gap="small")
    with c_dl:
        st.download_button(
            "⬇️ Baixar PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
            key=download_key,
        )
    with c_back:
        if st.button(
            back_label if not mobile else "← Voltar ao app",
            use_container_width=True,
            key=back_key,
        ):
            _go_back()

    if (
        not mobile
        and share_text
        and share_element_id
        and len(pdf_bytes) <= 2_500_000
    ):
        inject_share_pdf_whatsapp(
            pdf_bytes,
            filename,
            share_text[:300],
            element_id=share_element_id,
        )
    elif len(pdf_bytes) > 2_500_000:
        st.caption(
            "PDF grande — use **Baixar PDF** e anexe manualmente no grupo do WhatsApp."
        )


def share_escala_text(
    event: str,
    culto_date: str,
    ensaio: str = "",
    team_lines: list[str] | None = None,
) -> str:
    equipe = None
    if team_lines:
        equipe = []
        for line in team_lines:
            s = str(line).strip().lstrip("•").strip()
            if "—" in s:
                nome, func = s.split("—", 1)
                equipe.append((nome.strip(), func.strip()))
            else:
                equipe.append((s, "Integrante"))
    return build_escala_share_message(
        event=event,
        culto_date=culto_date,
        ensaio_date=ensaio,
        equipe=equipe,
    )


def whatsapp_automation_status() -> str:
    """
    Envio automático ao grupo exige WhatsApp Business Cloud API (Meta).
    O app usa: push OneSignal + abrir WhatsApp com texto pronto + PDF no celular.
    """
    phone = whatsapp_group_phone()
    if phone:
        return (
            f"Modo assistido: ao salvar a escala, o app abre o WhatsApp ({phone}) "
            "com a mensagem completa — confirme o envio no grupo. "
            "PDF: use o botão verde no celular."
        )
    return (
        "Para abrir o WhatsApp já com a mensagem ao salvar, configure em "
        "`.streamlit/secrets.toml`: `[whatsapp]` → `group_phone = \"5511...\"` (número do grupo ou líder). "
        "Envio 100% automático ao grupo sem clicar exige API oficial do WhatsApp Business (Meta)."
    )
