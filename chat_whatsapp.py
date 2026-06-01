"""Compositor de chat simplificado (estilo WhatsApp leve)."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import streamlit as st

from chat_media import save_audio_upload, save_image_upload


def mark_chat_scroll_bottom() -> None:
    st.session_state["_chat_scroll_bottom"] = True


class _BytesUpload:
    def __init__(self, raw: bytes, name: str):
        self._raw = raw
        self.name = name

    def getvalue(self) -> bytes:
        return self._raw


def _att_key(key_prefix: str) -> str:
    return f"{key_prefix}_attach_mode"


def _emoji_open_key(key_prefix: str) -> str:
    return f"{key_prefix}_emoji_open"


def _attach_menu_key(key_prefix: str) -> str:
    return f"{key_prefix}_attach_menu"


def _close_mobile_panels(key_prefix: str) -> None:
    st.session_state[_attach_menu_key(key_prefix)] = False
    st.session_state[_emoji_open_key(key_prefix)] = False


def _render_attach_mode_mobile(
    *,
    key_prefix: str,
    mode: str,
    ak: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
) -> None:
    """Painel curto para anexo (sem ocupar meia tela)."""
    st.caption({"gallery": "📷 Foto da galeria", "camera": "📷 Câmera", "record": "🎤 Gravar áudio", "audio": "🎤 Arquivo de áudio"}.get(mode, ""))
    if mode == "gallery":
        photo = st.file_uploader(
            "Foto",
            type=["jpg", "jpeg", "png", "webp", "heic"],
            key=f"{key_prefix}_gal",
            label_visibility="collapsed",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enviar", type="primary", use_container_width=True, key=f"{key_prefix}_gal_ok"):
                if photo is not None:
                    rel = save_image_upload(photo, images_dir, prefix=image_prefix, data_dir=data_dir)
                    append_fn(message="📷 Foto", message_type="image", media_file=rel)
                    st.session_state[ak] = None
                    _close_mobile_panels(key_prefix)
                    mark_chat_scroll_bottom()
                    st.rerun()
                else:
                    st.warning("Escolha uma foto.")
        with c2:
            if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_gal_no"):
                st.session_state[ak] = None
                st.rerun()
    elif mode == "camera":
        cam = st.camera_input("Câmera", key=f"{key_prefix}_cam", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enviar", type="primary", use_container_width=True, key=f"{key_prefix}_cam_ok"):
                if cam is not None:
                    rel = save_image_upload(cam, images_dir, prefix=image_prefix, data_dir=data_dir)
                    append_fn(message="📷 Foto", message_type="image", media_file=rel)
                    st.session_state[ak] = None
                    _close_mobile_panels(key_prefix)
                    mark_chat_scroll_bottom()
                    st.rerun()
                else:
                    st.warning("Tire a foto primeiro.")
        with c2:
            if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_cam_no"):
                st.session_state[ak] = None
                st.rerun()
    elif mode == "record":
        rec = st.audio_input("Gravar", key=f"{key_prefix}_rec", label_visibility="collapsed")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enviar", type="primary", use_container_width=True, key=f"{key_prefix}_rec_ok"):
                if rec is not None:
                    rel = save_audio_upload(rec, audio_dir, prefix=audio_prefix, data_dir=data_dir)
                    append_fn(message="🎤 Áudio", message_type="audio", media_file=rel)
                    st.session_state[ak] = None
                    _close_mobile_panels(key_prefix)
                    mark_chat_scroll_bottom()
                    st.rerun()
                else:
                    st.warning("Grave o áudio antes de enviar.")
        with c2:
            if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_rec_no"):
                st.session_state[ak] = None
                st.rerun()
    elif mode == "audio":
        aud = st.file_uploader(
            "Áudio",
            type=["webm", "ogg", "mp3", "m4a", "wav", "mp4", "aac"],
            key=f"{key_prefix}_aud",
            label_visibility="collapsed",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enviar", type="primary", use_container_width=True, key=f"{key_prefix}_aud_ok"):
                if aud is not None:
                    rel = save_audio_upload(aud, audio_dir, prefix=audio_prefix, data_dir=data_dir)
                    append_fn(message="🎤 Áudio", message_type="audio", media_file=rel)
                    st.session_state[ak] = None
                    _close_mobile_panels(key_prefix)
                    mark_chat_scroll_bottom()
                    st.rerun()
                else:
                    st.warning("Selecione um áudio.")
        with c2:
            if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_aud_no"):
                st.session_state[ak] = None
                st.rerun()


def render_simple_chat_composer(
    *,
    key_prefix: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
) -> None:
    """Envio compacto: campo de mensagem + popover de anexos."""
    ak = _att_key(key_prefix)
    mode = st.session_state.get(ak)

    if mode == "gallery":
        photo = st.file_uploader(
            "Foto",
            type=["jpg", "jpeg", "png", "webp", "heic"],
            key=f"{key_prefix}_gal",
            label_visibility="collapsed",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enviar", type="primary", use_container_width=True, key=f"{key_prefix}_gal_ok"):
                if photo is not None:
                    rel = save_image_upload(
                        photo, images_dir, prefix=image_prefix, data_dir=data_dir
                    )
                    append_fn(message="📷 Foto", message_type="image", media_file=rel)
                    st.session_state[ak] = None
                    mark_chat_scroll_bottom()
                    st.rerun()
                else:
                    st.warning("Escolha uma foto.")
        with c2:
            if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_gal_no"):
                st.session_state[ak] = None
                st.rerun()

    elif mode == "camera":
        cam = st.camera_input("Câmera", key=f"{key_prefix}_cam")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enviar", type="primary", use_container_width=True, key=f"{key_prefix}_cam_ok"):
                if cam is not None:
                    rel = save_image_upload(
                        cam, images_dir, prefix=image_prefix, data_dir=data_dir
                    )
                    append_fn(message="📷 Foto", message_type="image", media_file=rel)
                    st.session_state[ak] = None
                    mark_chat_scroll_bottom()
                    st.rerun()
                else:
                    st.warning("Tire a foto primeiro.")
        with c2:
            if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_cam_no"):
                st.session_state[ak] = None
                st.rerun()

    elif mode == "record":
        rec = st.audio_input(
            "Gravar mensagem de voz",
            key=f"{key_prefix}_rec",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enviar", type="primary", use_container_width=True, key=f"{key_prefix}_rec_ok"):
                if rec is not None:
                    rel = save_audio_upload(
                        rec, audio_dir, prefix=audio_prefix, data_dir=data_dir
                    )
                    append_fn(message="🎤 Áudio", message_type="audio", media_file=rel)
                    st.session_state[ak] = None
                    mark_chat_scroll_bottom()
                    st.rerun()
                else:
                    st.warning("Grave o áudio antes de enviar.")
        with c2:
            if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_rec_no"):
                st.session_state[ak] = None
                st.rerun()

    elif mode == "audio":
        aud = st.file_uploader(
            "Áudio",
            type=["webm", "ogg", "mp3", "m4a", "wav", "mp4", "aac"],
            key=f"{key_prefix}_aud",
            label_visibility="collapsed",
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Enviar", type="primary", use_container_width=True, key=f"{key_prefix}_aud_ok"):
                if aud is not None:
                    rel = save_audio_upload(
                        aud, audio_dir, prefix=audio_prefix, data_dir=data_dir
                    )
                    append_fn(message="🎤 Áudio", message_type="audio", media_file=rel)
                    st.session_state[ak] = None
                    mark_chat_scroll_bottom()
                    st.rerun()
                else:
                    st.warning("Selecione um áudio.")
        with c2:
            if st.button("Cancelar", use_container_width=True, key=f"{key_prefix}_aud_no"):
                st.session_state[ak] = None
                st.rerun()

    row = st.columns([1, 1, 10, 1])
    with row[0]:
        with st.popover("➕", use_container_width=True):
            if st.button("🖼️ Galeria", use_container_width=True, key=f"{key_prefix}_m_gal"):
                st.session_state[ak] = "gallery"
                st.rerun()
            if st.button("📷 Câmera", use_container_width=True, key=f"{key_prefix}_m_cam"):
                st.session_state[ak] = "camera"
                st.rerun()
            if st.button("🎤 Áudio", use_container_width=True, key=f"{key_prefix}_m_aud"):
                st.session_state[ak] = "audio"
                st.rerun()
            if st.button("🔴 Gravar", use_container_width=True, key=f"{key_prefix}_m_rec"):
                st.session_state[ak] = "record"
                st.rerun()

    with row[1]:
        with st.popover("😊", use_container_width=True):
            emojis = ("👍", "🙏", "✅", "❤️", "🎵", "⛪", "😊", "🎤")
            ec = st.columns(len(emojis))
            for i, (col, em) in enumerate(zip(ec, emojis)):
                with col:
                    if st.button(em, key=f"{key_prefix}_em_{i}"):
                        prev = st.session_state.get(f"{key_prefix}_pending_text", "")
                        st.session_state[f"{key_prefix}_pending_text"] = f"{prev}{em}".strip()
                        mark_chat_scroll_bottom()
                        st.rerun()

    with row[3]:
        if st.button("🎤", key=f"{key_prefix}_mic_short", help="Gravar áudio"):
            st.session_state[ak] = "record"
            st.rerun()

    placeholder = "Mensagem"
    with row[2]:
        prompt = st.chat_input(placeholder, key=f"{key_prefix}_input")
    if prompt and prompt.strip():
        st.session_state[f"{key_prefix}_pending_text"] = prompt.strip()
        st.rerun()


def render_mobile_wa_composer(
    *,
    key_prefix: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
) -> None:
    """
    Barra de composição mobile — uma linha (+ mensagem mic), sem popovers expansivos.
    """
    ak = _att_key(key_prefix)
    menu_key = _attach_menu_key(key_prefix)
    emoji_key = _emoji_open_key(key_prefix)
    mode = st.session_state.get(ak)

    st.markdown('<div class="chat-compose-bar wa-compose-bar wa-compose-mobile">', unsafe_allow_html=True)

    if mode:
        with st.container(key="ml_chat_attach_panel"):
            _render_attach_mode_mobile(
            key_prefix=key_prefix,
            mode=mode,
            ak=ak,
            append_fn=append_fn,
            audio_dir=audio_dir,
            audio_prefix=audio_prefix,
            images_dir=images_dir,
            image_prefix=image_prefix,
            data_dir=data_dir,
            )

    if st.session_state.get(menu_key):
        with st.container(key="ml_chat_attach_sheet"):
            cols = st.columns(6)
            actions = (
                ("🖼️", "Galeria", "gallery"),
                ("📷", "Câmera", "camera"),
                ("🎤", "Áudio", "audio"),
                ("🔴", "Gravar", "record"),
                ("😊", "Emoji", "_emoji"),
                ("✕", "Fechar", "_close"),
            )
            for col, (icon, label, act) in zip(cols, actions):
                with col:
                    if st.button(
                        icon,
                        key=f"{key_prefix}_sheet_{act}",
                        help=label,
                        use_container_width=True,
                    ):
                        if act == "_close":
                            st.session_state[menu_key] = False
                        elif act == "_emoji":
                            st.session_state[menu_key] = False
                            st.session_state[emoji_key] = True
                        else:
                            st.session_state[ak] = act
                            st.session_state[menu_key] = False
                        st.rerun()

    if st.session_state.get(emoji_key):
        with st.container(key="ml_chat_emoji_strip"):
            emojis = ("👍", "🙏", "✅", "❤️", "🎵", "⛪", "😊", "🎤", "✝️", "🙌")
            ec = st.columns(len(emojis))
            for i, (col, em) in enumerate(zip(ec, emojis)):
                with col:
                    if st.button(em, key=f"{key_prefix}_em_{i}", use_container_width=True):
                        prev = st.session_state.get(f"{key_prefix}_pending_text", "")
                        st.session_state[f"{key_prefix}_pending_text"] = f"{prev}{em}".strip()
                        st.session_state[emoji_key] = False
                        mark_chat_scroll_bottom()
                        st.rerun()

    prompt = None
    with st.container(key="ml_chat_compose_main"):
        row = st.columns([1, 1, 10, 1], gap="small")
        with row[0]:
            if st.button("➕", key=f"{key_prefix}_plus", help="Anexos", use_container_width=True):
                st.session_state[menu_key] = not st.session_state.get(menu_key, False)
                st.session_state[emoji_key] = False
                if st.session_state[menu_key]:
                    st.session_state[ak] = None
                st.rerun()
        with row[1]:
            if st.button("😊", key=f"{key_prefix}_em_btn", help="Emojis", use_container_width=True):
                st.session_state[emoji_key] = not st.session_state.get(emoji_key, False)
                st.session_state[menu_key] = False
                st.rerun()
        with row[2]:
            prompt = st.chat_input("Mensagem", key=f"{key_prefix}_input")
        with row[3]:
            if st.button("🎤", key=f"{key_prefix}_mic", help="Áudio", use_container_width=True):
                st.session_state[ak] = "record"
                _close_mobile_panels(key_prefix)
                st.rerun()

    if prompt and prompt.strip():
        st.session_state[f"{key_prefix}_pending_text"] = prompt.strip()
        _close_mobile_panels(key_prefix)
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div id="chat-page-end" style="height:1px;"></div>', unsafe_allow_html=True)


def render_whatsapp_chat_composer(
    *,
    key_prefix: str,
    append_fn: Callable,
    audio_dir: Path,
    audio_prefix: str,
    images_dir: Path,
    image_prefix: str,
    data_dir: Path,
    mobile: bool = False,
) -> None:
    if mobile:
        render_mobile_wa_composer(
            key_prefix=key_prefix,
            append_fn=append_fn,
            audio_dir=audio_dir,
            audio_prefix=audio_prefix,
            images_dir=images_dir,
            image_prefix=image_prefix,
            data_dir=data_dir,
        )
        return
    st.markdown('<div class="chat-compose-bar wa-compose-bar">', unsafe_allow_html=True)
    render_simple_chat_composer(
        key_prefix=key_prefix,
        append_fn=append_fn,
        audio_dir=audio_dir,
        audio_prefix=audio_prefix,
        images_dir=images_dir,
        image_prefix=image_prefix,
        data_dir=data_dir,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div id="chat-page-end" style="height:1px;"></div>', unsafe_allow_html=True)
