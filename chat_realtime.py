"""Supabase Realtime para o chat — push instantâneo sem polling no Streamlit."""

from __future__ import annotations

import json


def inject_chat_realtime_listener(
    supabase_url: str,
    supabase_anon_key: str,
    *,
    watch_names: tuple[str, ...] = ("chat.csv",),
) -> None:
    """Inscreve em sync_signals; ao mudar chat.csv, clica no botão oculto ig_chat_rt_sync."""
    from app import inject_page_html

    url = supabase_url.rstrip("/")
    key = supabase_anon_key.strip()
    if not url or not key:
        return

    names_js = json.dumps(list(watch_names), ensure_ascii=False)
    inject_page_html(
        f"""
        <style>
        [class*="st-key-ig_chat_rt_sync"] {{
          position: fixed !important;
          width: 1px !important;
          height: 1px !important;
          opacity: 0 !important;
          pointer-events: none !important;
          overflow: hidden !important;
          z-index: -1 !important;
        }}
        </style>
        <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
        <script>
        (function () {{
          if (window.__igbjChatRt) return;
          window.__igbjChatRt = true;
          var watch = new Set({names_js});
          var doc = window.parent.document;
          var lastClick = 0;

          function clickSync() {{
            var now = Date.now();
            if (now - lastClick < 600) return;
            lastClick = now;
            var btn = doc.querySelector('[class*="st-key-ig_chat_rt_sync"] button');
            if (btn && !btn.disabled) btn.click();
          }}

          function start() {{
            if (!window.supabase || !window.supabase.createClient) {{
              setTimeout(start, 400);
              return;
            }}
            var client = window.supabase.createClient({json.dumps(url)}, {json.dumps(key)});
            client
              .channel("igbj-chat-sync")
              .on(
                "postgres_changes",
                {{ event: "*", schema: "public", table: "sync_signals" }},
                function (payload) {{
                  var row = payload.new || payload.old || {{}};
                  if (row.name && watch.has(row.name)) clickSync();
                }}
              )
              .subscribe(function (status) {{
                if (status === "CHANNEL_ERROR" || status === "TIMED_OUT") {{
                  window.__igbjChatRt = false;
                }}
              }});
          }}
          start();
        }})();
        </script>
        """,
        height=0,
    )
