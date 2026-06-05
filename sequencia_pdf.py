"""PDF oficial da Sequência do Culto — letras, marcações coloridas e reflexões."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO

import pandas as pd
from fpdf import FPDF

from escala_pdf import GROUP_NAME, format_culto_date, pdf_safe
from louvor_meta import build_song_biblical_reflection, themes_from_csv
from sequencia_culto import (
    TIPO_BANDA_COLORS,
    TIPO_CORE_COLORS,
    _marcacoes_for_paragraph,
    get_sequencia_row,
    split_lyrics_paragraphs,
    trechos_banda_from_markup,
    trechos_from_markup,
)


def _hex_rgb(hex_color: str) -> tuple[int, int, int]:
    h = str(hex_color or "").strip().lstrip("#")
    if len(h) != 6:
        return 120, 120, 140
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return 120, 120, 140


def _border_for_trecho(tv: dict, tb: dict) -> str:
    tipo_v = str(tv.get("tipo", "")).strip()
    tipo_b = str(tb.get("tipo", "")).strip()
    return TIPO_CORE_COLORS.get(tipo_v) or TIPO_BANDA_COLORS.get(tipo_b, "#6b7280")


class SequenciaCultoPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(130, 125, 150)
        self.cell(0, 5, pdf_safe(f"{GROUP_NAME}  |  Sequencia do Culto  |  Pag. {self.page_no()}"), align="C")


def _reflection_plain(md_text: str) -> str:
    s = str(md_text or "")
    for tok in ("**", "*", "__", "_"):
        s = s.replace(tok, "")
    return pdf_safe(s)


def _draw_section_title(pdf: SequenciaCultoPDF, text: str, *, rgb: tuple[int, int, int] = (139, 92, 246)) -> None:
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_fill_color(*rgb)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(w, 7, pdf_safe(text, 90), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


def _draw_reflection_box(pdf: SequenciaCultoPDF, reflection_md: str) -> None:
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_fill_color(30, 25, 50)
    pdf.set_draw_color(139, 92, 246)
    y0 = pdf.get_y()
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(196, 181, 253)
    pdf.cell(w, 5, pdf_safe("Reflexao biblica"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(220, 215, 235)
    body = _reflection_plain(reflection_md)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(w, 4.2, body, new_x="LMARGIN", new_y="NEXT")
    y1 = pdf.get_y()
    pdf.set_line_width(0.4)
    pdf.rect(pdf.l_margin, y0, w, max(12, y1 - y0 + 1.5), style="D")
    pdf.ln(2.5)


def _draw_marcacao_line(pdf: SequenciaCultoPDF, marcacoes: list[tuple[str, str]]) -> None:
    if not marcacoes:
        return
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_font("Helvetica", "B", 8)
    x = pdf.l_margin
    for lbl, color in marcacoes:
        rgb = _hex_rgb(color)
        pdf.set_text_color(*rgb)
        chunk = pdf_safe(lbl, 48)
        pdf.set_x(x)
        pdf.cell(min(w, pdf.get_string_width(chunk) + 3), 4, chunk, new_x="END")
        x = pdf.get_x() + 2
        if x > pdf.l_margin + w - 20:
            pdf.ln(4)
            x = pdf.l_margin
    pdf.ln(4.5)


def _draw_trecho_block(
    pdf: SequenciaCultoPDF,
    *,
    num: int,
    para: str,
    marcacoes: list[tuple[str, str]],
    border_hex: str,
) -> None:
    w = pdf.w - pdf.l_margin - pdf.r_margin
    br, bg, bb = _hex_rgb(border_hex)
    y0 = pdf.get_y()
    pdf.set_fill_color(br, bg, bb)
    pdf.rect(pdf.l_margin, y0, 2.2, 8, style="F")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(br, bg, bb)
    pdf.cell(0, 4, pdf_safe(f"Trecho {num}"), new_x="LMARGIN", new_y="NEXT")
    _draw_marcacao_line(pdf, marcacoes)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(235, 230, 245)
    pdf.set_x(pdf.l_margin + 3)
    for line in str(para or "").splitlines():
        ln = line.strip()
        if not ln:
            pdf.ln(2)
            continue
        pdf.set_x(pdf.l_margin + 3)
        pdf.multi_cell(w - 3, 5.2, pdf_safe(ln), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2.5)


def build_sequencia_culto_pdf(
    escala_row,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame | None = None,
) -> bytes:
    """Documento oficial: capa + cada louvor com reflexão e letra marcada."""
    from app import (
        default_lyrics_from_louvor,
        enrich_programa_from_catalog,
        fix_louvor_display_title,
        format_rehearsal_date_pt,
        hydrate_escala_sequencia_content,
        integrantes_escalados,
        load_programa_sequencia_df,
        lookup_louvor_meta,
        programa_por_escala,
        rehearsal_date_is_set,
    )
    from catalog_sanitize import format_louvor_display, sanitize_catalog_text

    row = escala_row if isinstance(escala_row, pd.Series) else pd.Series(escala_row)
    escala_id = str(row.get("id", ""))
    event = str(row.get("event", "Culto"))
    culto_notes = str(row.get("notes", "")).strip()

    louvores_safe = louvores_df if louvores_df is not None else pd.DataFrame()
    hydrate_escala_sequencia_content(
        escala_id, programa_df, louvores_safe, use_web=False
    )
    seq_df = load_programa_sequencia_df()
    prog = programa_por_escala(programa_df, escala_id)
    if louvores_safe is not None and not louvores_safe.empty:
        prog = enrich_programa_from_catalog(prog, louvores_safe)
    if prog.empty:
        raise ValueError("Programacao vazia — monte a sequencia antes de gerar o PDF.")

    pdf = SequenciaCultoPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(14, 14, 14)
    pdf.add_page()

    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    culto_dt = format_culto_date(row.get("date", ""))

    pdf.set_fill_color(18, 12, 28)
    pdf.set_text_color(245, 200, 66)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(page_w, 10, pdf_safe(GROUP_NAME), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_text_color(30, 25, 45)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(page_w, 7, pdf_safe(f"Sequencia do Culto — {event}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(70, 65, 95)
    pdf.cell(page_w, 5, pdf_safe(f"Data: {culto_dt}"), new_x="LMARGIN", new_y="NEXT")
    if rehearsal_date_is_set(row):
        pdf.cell(
            page_w,
            5,
            pdf_safe(f"Ensaio: {format_rehearsal_date_pt(row)}"),
            new_x="LMARGIN",
            new_y="NEXT",
        )
    if culto_notes:
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(page_w, 4.5, pdf_safe(f"Tema / notas: {culto_notes}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(110, 105, 130)
    pdf.cell(
        page_w,
        4,
        pdf_safe(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(3)

    team = integrantes_escalados(row, equipe_df, members_df)
    if team:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 25, 45)
        pdf.cell(page_w, 5, pdf_safe("Equipe escalada"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(60, 55, 80)
        for person in team[:14]:
            nome = pdf_safe(str(person.get("nome", "")), 40)
            func = pdf_safe(str(person.get("funcao", "")), 22)
            if nome:
                pdf.cell(page_w, 4.2, f"  - {nome} ({func})", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(139, 92, 246)
    pdf.cell(page_w, 5, pdf_safe("Legenda vocal: Solo | Harmonia | Unissono | Todos"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(96, 165, 250)
    pdf.cell(page_w, 5, pdf_safe("Legenda banda: Solo inst. | Entrada | Harmonia | Todos"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    for _, item in prog.iterrows():
        artist = sanitize_catalog_text(item.get("artist", ""))
        louvor = fix_louvor_display_title(sanitize_catalog_text(item.get("louvor_title", "")))
        titulo = format_louvor_display(louvor, artist)
        parte = sanitize_catalog_text(item.get("parte", "")) or "Louvor"
        tom = sanitize_catalog_text(item.get("key", ""))
        leader = sanitize_catalog_text(item.get("leader_name", ""))
        ordem = str(item.get("ordem", "")).strip()
        pid = str(item.get("id", ""))

        seq_row = get_sequencia_row(seq_df, pid)
        lyrics = str(seq_row.get("lyrics_text", "")).strip() or default_lyrics_from_louvor(
            louvores_safe, louvor, artist
        )
        tom_prog = str(seq_row.get("tom_programa", "") or tom).strip()
        capo = int(pd.to_numeric(seq_row.get("capo", 0), errors="coerce") or 0)

        meta = (
            lookup_louvor_meta(louvores_safe, louvor, artist)
            if louvores_safe is not None and not louvores_safe.empty
            else {}
        )
        themes = themes_from_csv(str(meta.get("temas", "")))
        refs = str(meta.get("ref_biblica", "")).strip()

        reflection = build_song_biblical_reflection(
            title=louvor or titulo,
            artist=artist,
            evento=event,
            culto_notes=culto_notes,
            themes=themes,
            refs=refs,
            lyrics=lyrics,
            parte=parte,
        )

        if pdf.get_y() > pdf.h - 50:
            pdf.add_page()

        _draw_section_title(pdf, f"{ordem}. {parte} — {titulo}")

        meta_bits = []
        if tom_prog:
            meta_bits.append(f"Tom {tom_prog}")
        if capo:
            meta_bits.append(f"Capo {capo}")
        if leader:
            meta_bits.append(f"Lider: {leader}")
        if meta_bits:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(100, 95, 120)
            pdf.cell(page_w, 4.5, pdf_safe("  |  ".join(meta_bits)), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        _draw_reflection_box(pdf, reflection)

        paragraphs = split_lyrics_paragraphs(lyrics)
        trechos_v = trechos_from_markup(str(seq_row.get("lyrics_markup", "")), max(len(paragraphs), 1))
        trechos_b = trechos_banda_from_markup(
            str(seq_row.get("cifra_markup", "")), max(len(paragraphs), 1)
        )

        if not paragraphs:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(140, 135, 160)
            pdf.multi_cell(
                page_w,
                5,
                pdf_safe("Letra ainda nao cadastrada. Use Sequencia > Editar ou busque na internet."),
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.ln(3)
            continue

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(226, 232, 240)
        pdf.cell(page_w, 5, pdf_safe("Letra com marcacoes"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        for i, para in enumerate(paragraphs):
            if pdf.get_y() > pdf.h - 35:
                pdf.add_page()
            tv = next((x for x in trechos_v if int(x.get("paragrafo", -1)) == i), {})
            tb = next((x for x in trechos_b if int(x.get("paragrafo", -1)) == i), {})
            marcacoes = _marcacoes_for_paragraph(tv, tb)
            border = _border_for_trecho(tv, tb)
            _draw_trecho_block(pdf, num=i + 1, para=para, marcacoes=marcacoes, border_hex=border)

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def suggested_sequencia_filename(escala_row) -> str:
    row = escala_row if isinstance(escala_row, pd.Series) else pd.Series(escala_row)
    event = pdf_safe(str(row.get("event", "culto")), 24).replace(" ", "_")
    dt = pd.to_datetime(row.get("date"), errors="coerce")
    stamp = dt.strftime("%Y%m%d") if pd.notna(dt) else datetime.now().strftime("%Y%m%d")
    return f"sequencia_ibbj_{event}_{stamp}.pdf"
