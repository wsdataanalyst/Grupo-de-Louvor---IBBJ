"""Geração de PDF compacto das escalas para compartilhar (ex.: WhatsApp)."""

from __future__ import annotations

import unicodedata
from datetime import date, datetime
from io import BytesIO

import pandas as pd
from fpdf import FPDF

GROUP_NAME = "Grupo de Louvor - IBBJ"
_DIAS = ("Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom")

# Helvetica (PDF core) nao suporta pontuacao Unicode comum em textos PT-BR.
_UNICODE_TO_ASCII = str.maketrans(
    {
        "\u2026": "...",  # reticencias
        "\u2014": "-",  # travessao
        "\u2013": "-",  # meia-risca
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00a0": " ",
        "\u2212": "-",
    }
)


def pdf_safe(text: str, max_len: int = 0) -> str:
    """Texto compativel com Helvetica (Latin-1, sem acentos)."""
    s = unicodedata.normalize("NFKD", str(text or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.translate(_UNICODE_TO_ASCII)
    s = "".join(c if ord(c) < 256 else "?" for c in s)
    s = s.replace("\n", " ").strip()
    if max_len and len(s) > max_len:
        s = s[: max(0, max_len - 3)].rstrip() + "..."
    return s


def format_culto_date(value) -> str:
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return pdf_safe(str(value or "-"))
    d = dt.date()
    return f"{_DIAS[d.weekday()]}, {d.strftime('%d/%m/%Y')}"


def format_period_label(start: date | None, end: date | None) -> str:
    if start and end:
        return f"{start.strftime('%d/%m/%Y')} a {end.strftime('%d/%m/%Y')}"
    if start:
        return f"a partir de {start.strftime('%d/%m/%Y')}"
    if end:
        return f"ate {end.strftime('%d/%m/%Y')}"
    return "Periodo selecionado"


def filter_escalas_by_period(
    escalas_df: pd.DataFrame,
    *,
    date_start: date | None,
    date_end: date | None,
    event_filter: str | None = None,
    escala_ids: list[str] | None = None,
) -> pd.DataFrame:
    if escalas_df.empty:
        return escalas_df
    df = escalas_df.copy()
    df["_d"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    if date_start:
        df = df[df["_d"].notna() & (df["_d"] >= date_start)]
    if date_end:
        df = df[df["_d"].notna() & (df["_d"] <= date_end)]
    if event_filter and str(event_filter).strip():
        ev = str(event_filter).strip().lower()
        df = df[df["event"].astype(str).str.strip().str.lower() == ev]
    if escala_ids:
        ids = {str(i) for i in escala_ids}
        df = df[df["id"].astype(str).isin(ids)]
    return df.sort_values("_d").drop(columns=["_d"], errors="ignore")


def _team_lines(
    escala_row,
    equipe_df: pd.DataFrame,
    *,
    integrantes_escalados,
    normalize_funcao_escala,
    funcao_ministrador: str,
) -> list[str]:
    team = integrantes_escalados(escala_row, equipe_df, pd.DataFrame())
    lines = []
    for p in team:
        nome = pdf_safe(p.get("nome", ""), 32)
        funcao = pdf_safe(normalize_funcao_escala(str(p.get("funcao", "Integrante"))), 18)
        if nome:
            lines.append(f"{nome} ({funcao})")
    if not lines:
        resp = pdf_safe(
            escala_row.get("member_name") or escala_row.get("responsible", ""),
            32,
        )
        if resp:
            lines.append(f"{resp} ({pdf_safe(funcao_ministrador)})")
    return lines


def _programa_lines(
    escala_id: str,
    programa_df: pd.DataFrame,
    *,
    programa_por_escala,
    fix_louvor_display_title,
) -> list[str]:
    prog = programa_por_escala(programa_df, escala_id)
    if prog.empty:
        return []
    lines = []
    for _, item in prog.iterrows():
        ordem = str(item.get("ordem", "")).strip()
        parte = pdf_safe(item.get("parte", ""), 28)
        louvor = pdf_safe(fix_louvor_display_title(str(item.get("louvor_title", ""))), 36)
        artist = pdf_safe(str(item.get("artist", "")).strip(), 24)
        tom = pdf_safe(str(item.get("key", "")).strip(), 8)
        leader = pdf_safe(str(item.get("leader_name", "")).strip(), 20)
        titulo = louvor
        if artist:
            titulo = f"{louvor} - {artist}" if louvor else artist
        meta = []
        if tom:
            meta.append(f"Tom {tom}")
        if leader:
            meta.append(leader)
        extra = f" ({', '.join(meta)})" if meta else ""
        lines.append(f"{ordem}. {parte}: {titulo}{extra}")
    return lines


def _estimate_blocks(n_escalas: int, total_prog: int) -> int:
    return n_escalas * 3 + total_prog


def _font_sizes(n_escalas: int, blocks: int) -> tuple[int, int, int, int]:
    if n_escalas <= 1 and blocks <= 12:
        return 16, 11, 9, 8
    if n_escalas <= 2 and blocks <= 20:
        return 14, 10, 8, 7
    if n_escalas <= 4 and blocks <= 35:
        return 13, 9, 8, 7
    return 12, 8, 7, 6


def build_escalas_pdf(
    escalas_df: pd.DataFrame,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    *,
    period_label: str,
    integrantes_escalados,
    normalize_funcao_escala,
    programa_por_escala,
    fix_louvor_display_title,
    funcao_ministrador: str,
    rehearsal_date_is_set,
    format_rehearsal_date_pt,
) -> bytes:
    """PDF em uma pagina (paisagem), escalas ordenadas por data."""
    if escalas_df.empty:
        raise ValueError("Nenhuma escala selecionada para o PDF.")

    escala_ids = escalas_df["id"].astype(str).tolist()
    prog_counts = sum(
        len(programa_por_escala(programa_df, eid)) for eid in escala_ids
    )
    n = len(escalas_df)
    blocks = _estimate_blocks(n, prog_counts)
    title_sz, head_sz, body_sz, small_sz = _font_sizes(n, blocks)

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(10, 10, 10)
    pdf.add_page()

    page_w = pdf.w - pdf.l_margin - pdf.r_margin

    # Cabecalho
    pdf.set_fill_color(18, 12, 28)
    pdf.set_text_color(245, 200, 66)
    pdf.set_font("Helvetica", "B", title_sz)
    pdf.cell(page_w, 9, pdf_safe(GROUP_NAME), fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(60, 50, 90)
    pdf.set_font("Helvetica", "", body_sz)
    pdf.cell(
        page_w,
        6,
        pdf_safe(f"Escalas do ministerio  |  {period_label}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("Helvetica", "I", small_sz)
    pdf.set_text_color(100, 95, 120)
    pdf.cell(
        page_w,
        5,
        pdf_safe(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    events_seen: dict[str, list] = {}
    for _, row in escalas_df.iterrows():
        ev = pdf_safe(str(row.get("event", "Culto")), 40)
        events_seen.setdefault(ev, []).append(row)

    y_max = pdf.h - pdf.b_margin - 6
    col_gap = 4
    use_two_cols = n >= 3 and n <= 6
    col_w = (page_w - col_gap) / 2 if use_two_cols else page_w

    items = list(escalas_df.iterrows())
    if use_two_cols:
        mid = (len(items) + 1) // 2
        columns = [items[:mid], items[mid:]]
    else:
        columns = [items]

    for col_idx, col_items in enumerate(columns):
        x0 = pdf.l_margin + col_idx * (col_w + col_gap)
        pdf.set_xy(x0, pdf.get_y() if col_idx == 0 else 32)

        for _, row in col_items:
            escala_id = str(row.get("id", ""))
            event = pdf_safe(str(row.get("event", "Culto")), 50)
            culto_dt = format_culto_date(row.get("date", ""))
            notes = pdf_safe(str(row.get("notes", "")).strip(), 120)

            ensaio = ""
            if rehearsal_date_is_set(row):
                ensaio = pdf_safe(format_rehearsal_date_pt(row), 60)

            if pdf.get_y() > y_max - 14:
                break

            # Bloco da escala
            pdf.set_x(x0)
            pdf.set_fill_color(139, 92, 246)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", head_sz)
            pdf.cell(col_w, 7, f" {event}", fill=True, new_x="LMARGIN", new_y="NEXT")

            pdf.set_x(x0)
            pdf.set_text_color(30, 25, 45)
            pdf.set_font("Helvetica", "B", body_sz)
            pdf.cell(col_w, 5, f"Data: {culto_dt}", new_x="LMARGIN", new_y="NEXT")

            if ensaio:
                pdf.set_x(x0)
                pdf.set_font("Helvetica", "", body_sz)
                pdf.set_text_color(80, 70, 110)
                pdf.cell(col_w, 4, f"Ensaio: {ensaio}", new_x="LMARGIN", new_y="NEXT")

            team = _team_lines(
                row,
                equipe_df,
                integrantes_escalados=integrantes_escalados,
                normalize_funcao_escala=normalize_funcao_escala,
                funcao_ministrador=funcao_ministrador,
            )
            pdf.set_x(x0)
            pdf.set_font("Helvetica", "B", small_sz)
            pdf.set_text_color(30, 25, 45)
            pdf.cell(col_w, 4, "Equipe:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", small_sz)
            team_text = "  |  ".join(team) if team else "A definir"
            pdf.set_x(x0)
            pdf.multi_cell(col_w, 3.5, team_text, new_x="LMARGIN", new_y="NEXT")

            prog_lines = _programa_lines(
                escala_id,
                programa_df,
                programa_por_escala=programa_por_escala,
                fix_louvor_display_title=fix_louvor_display_title,
            )
            if prog_lines:
                pdf.set_x(x0)
                pdf.set_font("Helvetica", "B", small_sz)
                pdf.cell(col_w, 4, "Programacao:", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", small_sz)
                prog_text = "  ".join(prog_lines[:8])
                if len(prog_lines) > 8:
                    prog_text += f"  (+{len(prog_lines) - 8} itens)"
                pdf.set_x(x0)
                pdf.multi_cell(col_w, 3.2, prog_text, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.set_x(x0)
                pdf.set_font("Helvetica", "I", small_sz)
                pdf.set_text_color(120, 115, 140)
                pdf.cell(col_w, 4, "Programacao ainda nao montada.", new_x="LMARGIN", new_y="NEXT")

            if notes:
                pdf.set_x(x0)
                pdf.set_font("Helvetica", "I", small_sz)
                pdf.set_text_color(100, 95, 120)
                pdf.multi_cell(col_w, 3, f"Obs: {notes}", new_x="LMARGIN", new_y="NEXT")

            pdf.set_x(x0)
            pdf.ln(1.5)
            pdf.set_draw_color(220, 215, 235)
            pdf.line(x0, pdf.get_y(), x0 + col_w, pdf.get_y())
            pdf.ln(2)

    # Rodape
    pdf.set_y(-8)
    pdf.set_font("Helvetica", "I", 6)
    pdf.set_text_color(140, 135, 160)
    pdf.cell(0, 4, pdf_safe("Compartilhe no WhatsApp com a equipe do louvor."), align="C")

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def suggested_filename(period_label: str, n: int) -> str:
    stamp = datetime.now().strftime("%Y%m%d")
    safe = pdf_safe(period_label, 24).replace(" ", "_").replace("/", "-")
    return f"escalas_ibbj_{safe}_{n}cultos_{stamp}.pdf"
