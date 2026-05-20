"""Integração do compositor estilo WhatsApp com o chat Streamlit."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Callable

import streamlit as st

from chat_media import save_audio_upload, save_image_upload

try:
    from wa_composer import whatsapp_composer

    _WA_COMPONENT_OK = True
except Exception:
    whatsapp_composer = None
    _WA_COMPONENT_OK = False


def _payload_id(payload: dict[str, Any]) -> str:
    return str(payload.get("id", "")).strip()


def _already_handled(key_prefix: str, payload: dict[str, Any]) -> bool:
    pid = _payload_id(payload)
    if not pid:
        return True
    state_key = f"{key_prefix}_wa_last_id"
    if st.session_state.get(state_key) == pid:
        return True
    st.session_state[state_key] = pid
    return False


class _BytesUpload:
    def __init__(self, raw: bytes, name: str):
        self._raw = raw
        self.name = name

    def getvalue(self) -> bytes:
        return self._raw


def process_whatsapp_payload(
    payload: dict[str, Any] | None,
    *,
    key_prefix: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
) -> bool:
    if not payload or not isinstance(payload, dict):
        return False
    if _already_handled(key_prefix, payload):
        return False

    action = str(payload.get("action", "")).strip().lower()
    b64 = str(payload.get("b64", "")).strip()
    text = str(payload.get("text", "")).strip()

    try:
        if action == "text" and text:
            append_fn(message=text, message_type="text", media_file="")
            return True

        if action in ("audio", "audio_file") and b64:
            raw = base64.b64decode(b64)
            ext = str(payload.get("ext", ".webm")).strip() or ".webm"
            if not ext.startswith("."):
                ext = f".{ext}"
            upload = _BytesUpload(raw, f"gravacao{ext}")
            rel = save_audio_upload(
                upload, audio_dir, prefix=audio_prefix, data_dir=data_dir
            )
            append_fn(
                message="🎤 Áudio",
                message_type="audio",
                media_file=rel,
            )
            return True

        if action == "image" and b64:
            raw = base64.b64decode(b64)
            fname = str(payload.get("filename", "foto.jpg"))
            upload = _BytesUpload(raw, fname)
            rel = save_image_upload(
                upload, images_dir, prefix=image_prefix, data_dir=data_dir
            )
            append_fn(
                message="📷 Foto",
                message_type="image",
                media_file=rel,
            )
            return True
    except Exception as exc:
        st.error(f"Não foi possível enviar: {exc}")
        return False

    return False


def _use_compat_mode(key_prefix: str) -> bool:
    return bool(st.session_state.get(f"{key_prefix}_wa_compat", False))


def render_whatsapp_compat_composer(
    *,
    key_prefix: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
) -> None:
    """Fallback com widgets nativos do Streamlit (sempre funciona no Cloud)."""
    st.caption("Modo compatível — anexos pelo menu **+** · áudio por arquivo.")

    attach = st.session_state.get(f"{key_prefix}_attach_mode")

    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        if st.button("➕ Anexos", key=f"{key_prefix}_open_attach", use_container_width=True):
            st.session_state[f"{key_prefix}_attach_open"] = not st.session_state.get(
                f"{key_prefix}_attach_open", False
            )
    with ac2:
        if st.button("🖼️ Galeria", key=f"{key_prefix}_pick_gal", use_container_width=True):
            st.session_state[f"{key_prefix}_attach_mode"] = "gallery"
    with ac3:
        if st.button("📷 Câmera", key=f"{key_prefix}_pick_cam", use_container_width=True):
            st.session_state[f"{key_prefix}_attach_mode"] = "camera"

    attach = st.session_state.get(f"{key_prefix}_attach_mode")

    if attach == "gallery":
        photo = st.file_uploader(
            "Escolha da galeria",
            type=["jpg", "jpeg", "png", "webp", "heic"],
            key=f"{key_prefix}_gal_file",
            label_visibility="collapsed",
        )
        if st.button("Enviar foto", key=f"{key_prefix}_gal_send", type="primary"):
            if photo is not None:
                rel = save_image_upload(
                    photo, images_dir, prefix=image_prefix, data_dir=data_dir
                )
                append_fn(
                    message="📷 Foto",
                    message_type="image",
                    media_file=rel,
                )
                st.session_state[f"{key_prefix}_attach_mode"] = None
                st.rerun()
            else:
                st.warning("Selecione uma foto.")

    elif attach == "camera":
        cam = st.camera_input("Tirar foto", key=f"{key_prefix}_cam_only")
        if st.button("Enviar foto da câmera", key=f"{key_prefix}_cam_send", type="primary"):
            if cam is not None:
                rel = save_image_upload(
                    cam, images_dir, prefix=image_prefix, data_dir=data_dir
                )
                append_fn(
                    message="📷 Foto",
                    message_type="image",
                    media_file=rel,
                )
                st.session_state[f"{key_prefix}_attach_mode"] = None
                st.rerun()
            else:
                st.warning("Tire uma foto primeiro.")

    audio_file = st.file_uploader(
        "Áudio (arquivo ou gravação do celular)",
        type=["webm", "ogg", "mp3", "m4a", "wav", "mp4", "aac"],
        key=f"{key_prefix}_audio_compat",
        label_visibility="collapsed",
    )
    if audio_file is not None and st.button(
        "Enviar áudio", key=f"{key_prefix}_audio_send", use_container_width=True
    ):
        rel = save_audio_upload(
            audio_file, audio_dir, prefix=audio_prefix, data_dir=data_dir
        )
        append_fn(message="🎤 Áudio", message_type="audio", media_file=rel)
        st.rerun()

    prompt = st.chat_input("Mensagem", key=f"{key_prefix}_chat_input")
    if prompt and prompt.strip():
        append_fn(message=prompt.strip(), message_type="text", media_file="")
        st.rerun()


def render_whatsapp_chat_composer(
    *,
    key_prefix: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
) -> None:
    st.markdown('<div class="wa-composer-shell">', unsafe_allow_html=True)

    if _use_compat_mode(key_prefix) or not _WA_COMPONENT_OK:
        render_whatsapp_compat_composer(
            key_prefix=key_prefix,
            append_fn=append_fn,
            audio_dir=audio_dir,
            audio_prefix=audio_prefix,
            images_dir=images_dir,
            image_prefix=image_prefix,
            data_dir=data_dir,
        )
        if _WA_COMPONENT_OK:
            if st.button(
                "Tentar interface WhatsApp novamente",
                key=f"{key_prefix}_wa_retry",
                use_container_width=True,
            ):
                st.session_state[f"{key_prefix}_wa_compat"] = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    payload = whatsapp_composer(key=key_prefix, default=None)
    if process_whatsapp_payload(
        payload,
        key_prefix=key_prefix,
        append_fn=append_fn,
        audio_dir=audio_dir,
        audio_prefix=audio_prefix,
        images_dir=images_dir,
        image_prefix=image_prefix,
        data_dir=data_dir,
    ):
        st.rerun()

    if st.button(
        "Problemas ao carregar? Usar modo compatível",
        key=f"{key_prefix}_wa_compat_btn",
        use_container_width=True,
    ):
        st.session_state[f"{key_prefix}_wa_compat"] = True
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
