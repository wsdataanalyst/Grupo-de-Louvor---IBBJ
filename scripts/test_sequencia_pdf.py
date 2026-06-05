import traceback

import pandas as pd

from sequencia_pdf import build_sequencia_culto_pdf

escala = pd.DataFrame(
    [
        {
            "id": "e1",
            "event": "Santa Ceia",
            "date": "2026-06-07",
            "notes": "Tema teste",
            "member_name": "Will",
            "member_email": "a@b.com",
            "rehearsal_date": "2026-06-04",
        }
    ]
)
programa = pd.DataFrame(
    [
        {
            "id": "p1",
            "escala_id": "e1",
            "ordem": 1,
            "parte": "Abertura",
            "louvor_title": "Grande e Forte",
            "artist": "Ana Nobrega",
            "key": "G",
            "leader_name": "",
            "youtube_url": "",
            "cifra_url": "",
        },
    ]
)
equipe = pd.DataFrame(
    [
        {
            "id": "q1",
            "escala_id": "e1",
            "member_name": "Camila",
            "member_email": "c@d.com",
            "funcao": "Banda",
        }
    ]
)
members = pd.DataFrame(
    [
        {
            "email": "a@b.com",
            "first_name": "Will",
            "last_name": "S",
            "roles": "Ministrador",
            "bio": "",
        }
    ]
)
louvores = pd.read_csv("data/louvores.csv")
seq = pd.DataFrame(
    [
        {
            "programa_id": "p1",
            "lyrics_text": "Deus e grande\n\nEle e forte",
            "lyrics_markup": '{"trechos":[{"paragrafo":0,"tipo":"Solo","integrantes":["Maria"],"nota":""}]}',
            "cifra_text": "",
            "tom_programa": "G",
            "capo": 0,
            "cifra_markup": "",
            "updated_at": "",
        },
    ]
)

import app

orig = app.load_programa_sequencia_df
app.load_programa_sequencia_df = lambda: seq
app.hydrate_escala_sequencia_content = lambda *a, **k: (0, 0)
try:
    b = build_sequencia_culto_pdf(
        escala.iloc[0], programa, equipe, members, louvores
    )
    print("ok", len(b))
except Exception:
    traceback.print_exc()
finally:
    app.load_programa_sequencia_df = orig
