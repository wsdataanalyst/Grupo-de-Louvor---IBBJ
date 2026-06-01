"""Componentes reutilizáveis de badge de notificação (chat e menus)."""

from __future__ import annotations

import html


def format_unread_count(count: int) -> str:
    """Formata contador para exibição (máx. 99+)."""
    n = max(0, int(count))
    if n <= 0:
        return ""
    return "99+" if n > 99 else str(n)


def notification_badge_html(
    count: int,
    *,
    css_class: str = "ig-unread-badge",
    pulse: bool = False,
    title: str = "",
) -> str:
    """
    Badge circular vermelho (estilo WhatsApp).
    Retorna string vazia se count <= 0.
    """
    label = format_unread_count(count)
    if not label:
        return ""
    pulse_cls = " ig-unread-badge--pulse" if pulse else ""
    title_attr = f' title="{html.escape(title)}"' if title else ""
    return (
        f'<span class="{css_class}{pulse_cls}"{title_attr} '
        f'aria-label="{html.escape(label)} mensagens não lidas">{label}</span>'
    )


def unread_message_badge_html(count: int, *, pulse: bool = False) -> str:
    """Alias para badge de mensagens não lidas."""
    return notification_badge_html(
        count,
        css_class="ig-unread-badge ig-unread-badge--msg",
        pulse=pulse,
        title="Mensagens não lidas",
    )


def chat_notification_counter_html(count: int, *, pulse: bool = False) -> str:
    """Badge para ícone do Chat na navegação."""
    return notification_badge_html(
        count,
        css_class="ig-unread-badge ig-unread-badge--nav",
        pulse=pulse,
        title="Chat — não lidas",
    )


def notification_badge_css() -> str:
    """Estilos globais para badges (nav, lista de conversas, sidebar)."""
    return """
    .ig-unread-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 1.125rem;
      height: 1.125rem;
      padding: 0 0.35rem;
      border-radius: 999px;
      background: #ef4444;
      color: #fff !important;
      font-size: 0.62rem;
      font-weight: 800;
      line-height: 1;
      box-shadow: 0 2px 10px rgba(239, 68, 68, 0.55);
      border: 2px solid rgba(15, 23, 42, 0.95);
      pointer-events: none;
      box-sizing: border-box;
    }
    .ig-unread-badge--nav {
      position: absolute;
      top: 0.05rem;
      right: 0.15rem;
      z-index: 12;
      min-width: 1.2rem;
      height: 1.2rem;
      font-size: 0.65rem;
    }
    .ig-unread-badge--conv {
      position: static;
      margin-left: auto;
      flex-shrink: 0;
    }
  .ig-chat-conv.is-unread {
      background: rgba(239, 68, 68, 0.08) !important;
      border: 1px solid rgba(239, 68, 68, 0.22) !important;
    }
    .ig-chat-conv.is-unread .ig-chat-conv-name {
      color: #fecaca !important;
      font-weight: 800 !important;
    }
    .ig-unread-badge--pulse {
      animation: ig-badge-pulse 0.85s ease-out 2;
    }
    @keyframes ig-badge-pulse {
      0% { transform: scale(1); }
      35% { transform: scale(1.22); box-shadow: 0 0 0 6px rgba(239, 68, 68, 0.35); }
      70% { transform: scale(1.05); }
      100% { transform: scale(1); box-shadow: 0 2px 10px rgba(239, 68, 68, 0.55); }
    }
    """
