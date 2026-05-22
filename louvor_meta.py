"""Temas bíblicos, referências, duração e validação de louvores."""

from __future__ import annotations

import re
import unicodedata

LOUVOR_THEMES = (
    "Ações de graça",
    "Adoração",
    "Alegria",
    "Amor e Misericórdia de Deus",
    "Arrependimento",
    "Atributos de Deus",
    "Bondade de Deus",
    "Ceia",
    "Compromisso",
    "Comunhão",
    "Confiança",
    "Credo",
    "Criação",
    "Criador",
    "Crucificação",
    "Dependência de Deus",
    "Deus",
    "Encarnação",
    "Entrega",
    "Esperança",
    "Espírito Santo",
    "Eternidade",
    "Eterno",
    "Evangelho",
    "Evangelismo e Missões",
    "Exaltação",
    "Expiação",
    "Fé",
    "Fidelidade",
    "Glória",
    "Gratidão",
    "Humildade",
    "Igreja",
    "Inimigo",
    "Jesus Cristo",
    "Justiça",
    "Justificação e Perdão",
    "Lei de Deus",
    "Majestade",
    "Onipresença",
    "Onipotência",
    "Natal",
    "Onisciência",
    "Oração",
    "Palavra de Deus",
    "Páscoa",
    "Pecado",
    "Perseverança",
    "Redenção",
    "Reforma",
    "Regeneração",
    "Reino",
    "Ressurreição",
    "Sabedoria",
    "Salmos",
    "Salvação",
    "Salvador",
    "Sangue de Cristo",
    "Santidade",
    "Santificação",
    "Segunda vinda",
    "Sofrimento",
    "Suficiência",
    "Transcendência",
    "Trindade",
    "União com Cristo",
    "Unidade",
    "Vida Cristã",
    "Vida eterna",
)

# Palavras-chave por tema (título + artista, sem acento)
_THEME_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Adoração": ("adora", "louvor", "adorar", "santo", "santidade", "gloria", "glória"),
    "Gratidão": ("graca", "graça", "agradec", "obrigado", "thank"),
    "Ações de graça": ("acao de gracas", "ações de graças", "gratidao", "gratidão"),
    "Alegria": ("alegr", "jubil", "festej", "gozo", "celebr"),
    "Amor e Misericórdia de Deus": ("amor", "misericord", "compassiv", "bondade"),
    "Arrependimento": ("arrepend", "perdao", "perdão", "confiss", "lamento"),
    "Cruzificação": ("cruz", "calvario", "calvário", "crucific", "paixao", "paixão"),
    "Ressurreição": ("ressurre", "ressuscit", "vive", "ressurgiu", "tumba"),
    "Páscoa": ("pascoa", "páscoa", "ressurre"),
    "Natal": ("natal", "noite feliz", "presepio", "presépio", "manjedour"),
    "Ceia": ("ceia", "santa ceia", "corpo", "sangue"),
    "Sangue de Cristo": ("sangue", "cordeiro"),
    "Espírito Santo": ("espirito", "espírito", "santo espirito", "consolador"),
    "Jesus Cristo": ("jesus", "cristo", "senhor", "messias", "emmanuel", "emanuel"),
    "Salvação": ("salv", "redim", "libert"),
    "Fé": ("fe ", " fé", "confio", "confian"),
    "Esperança": ("esperanc", "esperança"),
    "Evangelho": ("evangel", "bom nova"),
    "Evangelismo e Missões": ("missao", "missão", "mund", "nacao", "nação"),
    "Igreja": ("igreja", "corpo", "congreg"),
    "Comunhão": ("comunhao", "comunhão", "unidade"),
    "Oração": ("oracao", "oração", "orai", "clamo"),
    "Palavra de Deus": ("palavra", "biblia", "bíblia", "escritura"),
    "Salmos": ("salmo", "sl "),
    "Santidade": ("santo", "santidade", "pureza"),
    "Glória": ("gloria", "glória", "majestade"),
    "Majestade": ("majestade", "rei", "reino"),
    "Reino": ("reino", "reinar"),
    "Deus": ("deus", "jeova", "jeová", "yahweh", "pai"),
    "Criador": ("criador", "criou"),
    "Criação": ("criacao", "criação", "ceus", "céus"),
    "Trindade": ("trindade", "tres em um"),
    "Vida Cristã": ("caminh", "seguir", "discipul"),
    "Vida eterna": ("etern", "vida eterna"),
    "Humildade": ("humild", "servo", "servir"),
    "Sofrimento": ("sofr", "dor", "luto", "prant"),
    "Exaltação": ("exalt", "levant"),
    "Entrega": ("entreg", "rend", "renunci"),
    "Perseverança": ("persever", "firme", "constan"),
    "Expiação": ("expiac", "propiciac"),
    "Justificação e Perdão": ("justific", "perdao", "perdão"),
    "Dependência de Deus": ("depend", "preciso de ti", "sem ti"),
    "União com Cristo": ("uniao com", "união com", "em cristo"),
    "Fidelidade": ("fiel", "fidel"),
    "Confiança": ("confian", "confio"),
    "Atributos de Deus": ("onipot", "onisci", "onipres"),
    "Onipotência": ("onipot", "poderoso", "todo poder"),
    "Onisciência": ("onisci", "sabe tudo"),
    "Onipresença": ("onipres", "presente"),
    "Bondade de Deus": ("bondade", "bom ", "benigno"),
    "Pecado": ("pecado", "iniquid", "maldade"),
    "Inimigo": ("inimigo", "satan", "mal "),
    "Segunda vinda": ("volta", "vinda", "maranata"),
    "Transcendência": ("transcend", "infinit"),
    "Suficiência": ("sufici", "basta", "suprir"),
    "Compromisso": ("compromiss", "aliança", "alianca"),
    "Credo": ("credo", "creio", "confissao de fe"),
    "Encarnação": ("encarn", "verbo", "nascimento"),
    "Regeneração": ("regener", "novo nasc"),
    "Redenção": ("reden", "resgat"),
    "Reforma": ("reforma", "renov"),
    "Lei de Deus": ("lei ", "mandamento"),
    "Justiça": ("justic", "justiça"),
    "Eternidade": ("etern", "para sempre"),
    "Eterno": ("etern", "sempre"),
    "Salvador": ("salvador", "redentor"),
    "Santificação": ("santific", "santidade"),
}

_BIBLICAL_REFS: dict[str, str] = {
    "Adoração": "João 4:23-24; Salmo 95:1-6",
    "Gratidão": "1 Tessalonicenses 5:18; Salmo 100:4",
    "Arrependimento": "Atos 3:19; 1 João 1:9",
    "Cruzificação": "1 Coríntios 15:3-4; Isaías 53:5",
    "Ressurreição": "1 Coríntios 15:20; Romanos 6:4",
    "Espírito Santo": "João 14:16-17; Atos 1:8",
    "Jesus Cristo": "João 14:6; Filipenses 2:9-11",
    "Salvação": "Efésios 2:8-9; Atos 4:12",
    "Fé": "Hebreus 11:6; Efésios 2:8",
    "Esperança": "Romanos 15:13; Jeremias 29:11",
    "Ceia": "1 Coríntios 11:23-26; Lucas 22:19",
    "Evangelho": "Romanos 1:16; Marcos 16:15",
    "Igreja": "Efésios 4:15-16; Atos 2:42",
    "Oração": "Filipenses 4:6-7; Mateus 6:9-13",
    "Palavra de Deus": "2 Timóteo 3:16-17; Salmo 119:105",
    "Santidade": "1 Pedro 1:15-16; Hebreus 12:14",
    "Amor e Misericórdia de Deus": "João 3:16; Salmo 103:8",
    "Vida Cristã": "Romanos 12:1-2; Colossenses 3:16",
    "Humildade": "Filipenses 2:3-5; Tiago 4:10",
    "Páscoa": "1 Coríntios 5:7; João 11:25",
    "Natal": "Lucas 2:10-11; Isaías 9:6",
}

_SENSITIVE_WARN = (
    "romantic", "romance", "namoro", "sexual", "sexy", "beer", "cerveja",
    "funk", "pagode", "profano", "palavrao",
)


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFKD", str(text or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def classify_themes(title: str, artist: str = "", extra: str = "") -> list[str]:
    """Até 5 temas sugeridos com base no título (heurística)."""
    blob = _norm(f"{title} {artist} {extra}")
    scores: list[tuple[int, str]] = []
    for theme, keys in _THEME_KEYWORDS.items():
        score = sum(1 for k in keys if k in blob)
        if score:
            scores.append((score, theme))
    scores.sort(key=lambda x: (-x[0], x[1]))
    out: list[str] = []
    for _, theme in scores:
        if theme not in out:
            out.append(theme)
        if len(out) >= 5:
            break
    if not out:
        if any(w in blob for w in ("louvor", "ador", "santo", "deus")):
            out = ["Adoração", "Exaltação"]
        else:
            out = ["Vida Cristã", "Adoração"]
    return out[:5]


def themes_to_csv(themes: list[str]) -> str:
    return "; ".join(t for t in themes if t)[:500]


def themes_from_csv(raw: str) -> list[str]:
    if not str(raw).strip():
        return []
    parts = [p.strip() for p in re.split(r"[;,|]", str(raw)) if p.strip()]
    valid = [p for p in parts if p in LOUVOR_THEMES]
    return valid[:5] if valid else parts[:5]


def suggest_biblical_refs(themes: list[str], title: str = "") -> str:
    refs: list[str] = []
    for t in themes:
        r = _BIBLICAL_REFS.get(t)
        if r and r not in refs:
            refs.append(r)
    if not refs:
        refs.append("Salmo 150:1-6; Colossenses 3:16")
    return " | ".join(refs[:4])


def parse_duracao_min(value, default: float = 4.5) -> float:
    s = str(value or "").strip().replace(",", ".")
    if not s:
        return default
    try:
        v = float(s)
        return max(1.0, min(30.0, v))
    except ValueError:
        m = re.match(r"^(\d+):(\d+)$", s)
        if m:
            return max(1.0, int(m.group(1)) + int(m.group(2)) / 60.0)
    return default


def format_duracao_total(minutes: float) -> str:
    m = int(minutes)
    s = int(round((minutes - m) * 60))
    if s >= 60:
        m += 1
        s = 0
    return f"{m} min" + (f" {s:02d} s" if s else "")


def validate_louvor(
    title: str,
    artist: str = "",
    themes: list[str] | None = None,
    extra_notes: str = "",
) -> dict:
    """Validação honesta para líderes (temas + bom senso)."""
    title_n = _norm(title)
    themes = themes or classify_themes(title, artist)
    issues: list[str] = []
    positives: list[str] = []

    if len(title.strip()) < 2:
        issues.append("Título muito curto ou ausente.")
    if any(w in title_n for w in _SENSITIVE_WARN):
        issues.append(
            "O título sugere conteúdo possivelmente inadequado para o culto — revise letra e contexto."
        )

    if not themes:
        issues.append("Nenhum tema bíblico identificado; classifique manualmente.")
    else:
        positives.append(f"Temas: {', '.join(themes)}.")

    central = {"Adoração", "Jesus Cristo", "Salvação", "Fé", "Santidade", "Espírito Santo"}
    if themes and not central.intersection(set(themes)):
        issues.append(
            "Não há tema central claramente cristológico ou de adoração — confira se a letra edifica a igreja."
        )
    else:
        positives.append("Há foco cristológico ou de adoração nos temas.")

    guidance = (
        "Use a letra completa e o contexto do culto. Músicas devem glorificar a Deus, "
        "edificar a igreja e estar alinhadas à doutrina da comunidade. Em dúvida, "
        "consulte a liderança e a Palavra."
    )
    refs = suggest_biblical_refs(themes, title)
    ok = len(issues) == 0
    summary = "Aprovado para o repertório com ressalvas leves." if ok else "Requer revisão da liderança antes do culto."
    return {
        "ok": ok,
        "summary": summary,
        "issues": issues,
        "positives": positives,
        "themes": themes,
        "refs": refs,
        "guidance": guidance,
        "note": extra_notes.strip(),
    }


def guia_ministracao_text(
    *,
    evento: str,
    culto_date: str,
    louvores: list[str],
    themes_lines: list[str],
) -> str:
    """Texto simples para o ministrador falar com a igreja."""
    lista = "\n".join(f"- {l}" for l in louvores[:12]) or "- (programação em formação)"
    temas_txt = "\n".join(f"- {t}" for t in themes_lines[:8]) or "- Adoração e gratidão"
    return f"""## Guia de ministração — {evento} ({culto_date})

**Abertura (30–60 s)**  
Irmãos, o louvor não é espetáculo: é resposta de um povo que reconhece quem Deus é. Vamos cantar com entendimento e coração rendido.

**Antes do primeiro louvor**  
Conecte o tema do culto com a Palavra. Ex.: "Hoje cantamos sobre {themes_lines[0] if themes_lines else 'a fidelidade de Deus'}."

**Louvores deste culto**  
{lista}

**Temas do culto**  
{temas_txt}

**Referências para mencionar**  
- Salmo 150:1-6 — tudo que tem fôlego louve ao Senhor.  
- Colossenses 3:16 — a palavra de Cristo habite entre nós com louvor.  
- João 4:23-24 — adoradores em espírito e em verdade.

**Convite à igreja**  
Peça que cantem como quem ora, não apenas repete frases. Silêncio breve antes de um louvor mais íntimo pode ajudar.

**Encerramento**  
Agradeça a equipe (músicos e técnico de som). Ore brevemente entregando o culto ao Senhor.
"""


def ensure_louvor_row_metadata(title: str, artist: str, temas_csv: str, ref_csv: str, dur_csv: str) -> dict:
    themes = themes_from_csv(temas_csv)
    if not themes:
        themes = classify_themes(title, artist)
    refs = ref_csv.strip() or suggest_biblical_refs(themes, title)
    dur = parse_duracao_min(dur_csv)
    return {
        "temas": themes_to_csv(themes),
        "ref_biblica": refs,
        "duracao_min": f"{dur:.1f}",
    }
