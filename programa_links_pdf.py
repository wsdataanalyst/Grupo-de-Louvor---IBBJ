"""PDF da programação do culto — louvores e links (personalizado por função do integrante)."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO

import pandas as pd
from fpdf import FPDF

from escala_pdf import GROUP_NAME, format_culto_date, pdf_safe


class ProgramaLinksPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-10)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(130, 125, 150)
        self.cell(
            0,
            5,
            pdf_safe(f"{GROUP_NAME}  |  Programacao do Culto  |  Pag. {self.page_no()}"),
            align="C",
        )


def _draw_section_title(pdf: ProgramaLinksPDF, text: str) -> None:
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_fill_color(139, 92, 246)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(w, 7, pdf_safe(text, 95), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1.5)


def _draw_link_line(pdf: ProgramaLinksPDF, label: str, url: str) -> None:
    if not url or not str(url).startswith("http"):
        return
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(37, 99, 235)
    line = pdf_safe(f"  • {label}")
    pdf.set_x(pdf.l_margin)
    pdf.cell(w, 4.5, line, link=str(url), new_x="LMARGIN", new_y="NEXT")


def _song_links_for_viewer(
    item: pd.Series,
    *,
    louvores_df: pd.DataFrame | None,
    kits_me: list[tuple[str, str, str]],
) -> list[tuple[str, str]]:
    from app import cifra_search_url, fix_louvor_display_title, lookup_louvor_meta
    from catalog_sanitize import sanitize_catalog_text
    from cifra_fetch import resolve_letra_url
    from instrument_kit_links import kit_youtube_url

    louvor = fix_louvor_display_title(sanitize_catalog_text(item.get("louvor_title", "")))
    artist = sanitize_catalog_text(item.get("artist", ""))
    yt = sanitize_catalog_text(item.get("youtube_url", ""))
    cifra_stored = sanitize_catalog_text(item.get("cifra_url", ""))
    cifra = cifra_stored if cifra_stored.startswith("http") else ""
    if not cifra:
        cifra = cifra_search_url(louvor, artist)
    letra = resolve_letra_url(louvor, artist, cifra_club_url=cifra_stored)

    links: list[tuple[str, str]] = []
    if yt:
        links.append(("YouTube", yt))
    for kit_label, _kit_key, kit_prefix in kits_me:
        links.append((kit_label, kit_youtube_url(kit_prefix, louvor)))
    if cifra:
        links.append(("Cifra", cifra))
    if letra:
        links.append(("Letra", letra))
    meta = (
        lookup_louvor_meta(louvores_df, louvor, artist)
        if louvores_df is not None and not louvores_df.empty
        else {}
    )
    ref_b = str(meta.get("ref_biblica", "")).strip()
    if ref_b:
        links.append((f"Ref. biblica: {ref_b[:80]}", ""))
    return links


def build_programa_culto_links_pdf(
    escala_row,
    programa_df: pd.DataFrame,
    equipe_df: pd.DataFrame,
    members_df: pd.DataFrame,
    louvores_df: pd.DataFrame | None,
    *,
    viewer_roles: str = "",
    viewer_bio: str = "",
) -> bytes:
    from app import (
        enrich_programa_from_catalog,
        format_rehearsal_date_pt,
        integrantes_escalados,
        programa_por_escala,
        rehearsal_date_is_set,
    )
    from app import fix_louvor_display_title
    from catalog_sanitize import format_louvor_display, sanitize_catalog_text
    from instrument_kit_links import instrument_kits_from_roles

    row = escala_row if isinstance(escala_row, pd.Series) else pd.Series(escala_row)
    escala_id = str(row.get("id", ""))
    event = str(row.get("event", "Culto"))
    culto_notes = str(row.get("notes", "")).strip()

    louvores_safe = louvores_df if louvores_df is not None else pd.DataFrame()
    prog = programa_por_escala(programa_df, escala_id)
    if not louvores_safe.empty:
        prog = enrich_programa_from_catalog(prog, louvores_safe)
    if prog.empty:
        raise ValueError("Programacao vazia — monte os louvores antes de gerar o PDF.")

    kits_me = instrument_kits_from_roles(viewer_roles, bio=viewer_bio)

    pdf = ProgramaLinksPDF(orientation="P", unit="mm", format="A4")
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
    pdf.cell(page_w, 7, pdf_safe(f"Programacao — {event}"), new_x="LMARGIN", new_y="NEXT")
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
        pdf.multi_cell(page_w, 4.5, pdf_safe(f"Notas: {culto_notes}"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(110, 105, 130)
    pdf.cell(
        page_w,
        4,
        pdf_safe(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    if kits_me:
        kit_names = ", ".join(k[0] for k in kits_me)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(
            page_w,
            4,
            pdf_safe(f"Links personalizados: {kit_names}"),
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

    for _, item in prog.iterrows():
        if pdf.get_y() > pdf.h - 45:
            pdf.add_page()

        artist = sanitize_catalog_text(item.get("artist", ""))
        louvor = fix_louvor_display_title(sanitize_catalog_text(item.get("louvor_title", "")))
        titulo = format_louvor_display(louvor, artist)
        parte = sanitize_catalog_text(item.get("parte", "")) or "Louvor"
        tom = sanitize_catalog_text(item.get("key", ""))
        leader = sanitize_catalog_text(item.get("leader_name", ""))
        ordem = str(item.get("ordem", "")).strip()

        _draw_section_title(pdf, f"{ordem}. {parte} — {titulo}")

        meta_bits = []
        if tom:
            meta_bits.append(f"Tom {tom}")
        if leader:
            meta_bits.append(f"Lider: {leader}")
        if meta_bits:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(100, 95, 120)
            pdf.cell(page_w, 4.5, pdf_safe("  |  ".join(meta_bits)), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 25, 45)
        pdf.cell(page_w, 4.5, pdf_safe("Links"), new_x="LMARGIN", new_y="NEXT")

        links = _song_links_for_viewer(item, louvores_df=louvores_safe, kits_me=kits_me)
        if not links:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(120, 115, 140)
            pdf.cell(page_w, 4.5, pdf_safe("  (sem links cadastrados)"), new_x="LMARGIN", new_y="NEXT")
        else:
            for label, url in links:
                if url:
                    _draw_link_line(pdf, label, url)
                else:
                    pdf.set_font("Helvetica", "I", 8)
                    pdf.set_text_color(100, 95, 120)
                    pdf.cell(page_w, 4.2, pdf_safe(f"  • {label}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    buf = BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def suggested_programa_links_filename(escala_row) -> str:
    row = escala_row if isinstance(escala_row, pd.Series) else pd.Series(escala_row)
    event = pdf_safe(str(row.get("event", "culto")), 24).replace(" ", "_")
    dt = pd.to_datetime(row.get("date"), errors="coerce")
    stamp = dt.strftime("%Y%m%d") if pd.notna(dt) else datetime.now().strftime("%Y%m%d")
    return f"programa_ibbj_{event}_{stamp}.pdf"
