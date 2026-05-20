"""Versículo bíblico do dia — mesmo texto para todos os usuários, muda a cada dia."""

from __future__ import annotations

import html
from datetime import date

import streamlit as st

from app_time import now_local

# Referência NVI / linguagem acessível para o ministério de louvor
VERSES_OF_DAY: tuple[dict[str, str], ...] = (
    {"ref": "Salmos 100:1", "text": "Cantem ao Senhor com alegria, todos os habitantes da terra!"},
    {"ref": "Salmos 150:6", "text": "Tudo o que tem fôlego, louve ao Senhor!"},
    {"ref": "Salmos 96:1", "text": "Cantem ao Senhor um novo cântico; cantem ao Senhor, todos os habitantes da terra!"},
    {"ref": "Colossenses 3:16", "text": "Habite ricamente em vocês a palavra de Cristo; ensinem e aconselhem-se uns aos outros com salmos, hinos e cânticos espirituais."},
    {"ref": "Efésios 5:19", "text": "Falem uns aos outros com salmos, hinos e cânticos espirituais. Cantem e louvem o Senhor com o coração."},
    {"ref": "Salmos 33:3", "text": "Cantem a ele uma nova canção; toquem com arte e com júbilo."},
    {"ref": "Salmos 47:6", "text": "Cantem louvores a Deus, cantem louvores; cantem louvores ao nosso Rei, cantem louvores."},
    {"ref": "Salmos 95:1", "text": "Venham, cantemos ao Senhor com alegria; celebremos a Rocha da nossa salvação."},
    {"ref": "Isaías 12:2", "text": "Deus é a minha salvação; terei confiança e não temerei. O Senhor é a minha força e o meu cântico."},
    {"ref": "Salmos 27:1", "text": "O Senhor é a minha luz e a minha salvação; de quem terei medo?"},
    {"ref": "Filipenses 4:13", "text": "Tudo posso naquele que me fortalece."},
    {"ref": "Jeremias 29:11", "text": "Eu é que sei os planos que tenho para vocês, planos de fazê-los prosperar e não de causar dano."},
    {"ref": "Romanos 8:28", "text": "Sabemos que Deus age em todas as coisas para o bem daqueles que o amam."},
    {"ref": "Provérbios 3:5-6", "text": "Confie no Senhor de todo o seu coração e não se apoie em seu próprio entendimento."},
    {"ref": "Josué 1:9", "text": "Seja forte e corajoso! Não se apavore nem desanime, pois o Senhor, o seu Deus, estará com você."},
    {"ref": "Salmos 23:1", "text": "O Senhor é o meu pastor; de nada terei falta."},
    {"ref": "Salmos 46:1", "text": "Deus é o nosso refúgio e fortaleza, socorro sempre presente na adversidade."},
    {"ref": "Mateus 11:28", "text": "Venham a mim, todos os que estão cansados e sobrecarregados, e eu lhes darei descanso."},
    {"ref": "João 3:16", "text": "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito."},
    {"ref": "João 14:6", "text": "Eu sou o caminho, a verdade e a vida. Ninguém vem ao Pai, a não ser por mim."},
    {"ref": "1 Coríntios 13:4", "text": "O amor é paciente, o amor é bondoso. Não inveja, não se vangloria, não se orgulha."},
    {"ref": "Gálatas 5:22", "text": "O fruto do Espírito é amor, alegria, paz, paciência, amabilidade, bondade, fidelidade."},
    {"ref": "Salmos 119:105", "text": "Lâmpada para os meus pés é a tua palavra e luz para o meu caminho."},
    {"ref": "Salmos 34:8", "text": "Provem e vejam que o Senhor é bom; como é feliz o homem que nele se refugia!"},
    {"ref": "Salmos 37:4", "text": "Deleite-se no Senhor, e ele atenderá aos desejos do seu coração."},
    {"ref": "Salmos 63:3", "text": "Porque o teu amor é melhor do que a vida, os meus lábios te louvarão."},
    {"ref": "Salmos 71:14", "text": "Mas eu sempre terei esperança e te louvarei cada vez mais."},
    {"ref": "Salmos 86:12", "text": "Com todo o meu coração te louvarei, Senhor, meu Deus; glorificarei o teu nome para sempre."},
    {"ref": "Salmos 92:1", "text": "Como é bom render graças ao Senhor e cantar louvores ao teu nome, ó Altíssimo!"},
    {"ref": "Salmos 98:4", "text": "Aclamem o Senhor todos os habitantes da terra! Quebrem em canções de alegria e o louvem!"},
    {"ref": "Salmos 103:1", "text": "Bendiga o Senhor a minha alma! Bendiga o Senhor, tudo o que há em mim, o seu santo nome."},
    {"ref": "Salmos 104:33", "text": "Cantarei ao Senhor enquanto eu viver; louvarei ao meu Deus enquanto existir."},
    {"ref": "Salmos 113:1", "text": "Aleluia! Louvem, servos do Senhor, louvem o nome do Senhor."},
    {"ref": "Salmos 115:1", "text": "Não a nós, Senhor, não a nós, mas ao teu nome dá a glória, por causa do teu amor e da tua fidelidade."},
    {"ref": "Salmos 118:24", "text": "Este é o dia que o Senhor fez; regozijemo-nos e alegremo-nos neste dia."},
    {"ref": "Salmos 121:1-2", "text": "Levanto os meus olhos para os montes e pergunto: De onde me vem o socorro? O meu socorro vem do Senhor."},
    {"ref": "Salmos 136:1", "text": "Dêem graças ao Senhor, porque ele é bom. O seu amor dura para sempre."},
    {"ref": "Salmos 139:14", "text": "Eu te louvo porque me formaste de modo especial e admirável. Tuas obras são maravilhosas."},
    {"ref": "Salmos 145:3", "text": "Grande é o Senhor e digno de todo louvor; a sua grandeza não se pode esgotar."},
    {"ref": "Salmos 147:1", "text": "Aleluia! Como é bom cantar louvores ao nosso Deus! Como é agradável e próprio louvá-lo!"},
    {"ref": "Salmos 149:1", "text": "Aleluia! Cantem ao Senhor um novo cântico; cantem-lhe o seu louvor na assembléia dos fiéis."},
    {"ref": "Isaías 40:31", "text": "Mas aqueles que esperam no Senhor renovam as suas forças; voam alto como águias."},
    {"ref": "Isaías 41:10", "text": "Não tema, pois estou com você; não fique assustado, pois sou o seu Deus."},
    {"ref": "Isaías 43:2", "text": "Quando você passar pelas águas, eu estarei com você; quando passar pelos rios, eles não o encobrirão."},
    {"ref": "Miqueias 6:8", "text": "Agir com justiça, amar a misericórdia e andar humildemente com o seu Deus."},
    {"ref": "Habacuque 3:19", "text": "O Senhor, o Soberano, é a minha força; ele faz os meus pés como os pés das corças."},
    {"ref": "Zacarias 4:6", "text": "Não por força nem por violência, mas pelo meu Espírito, diz o Senhor dos Exércitos."},
    {"ref": "Mateus 5:16", "text": "Assim brilhe a luz de vocês diante dos homens, para que vejam as suas boas obras e glorifiquem ao Pai."},
    {"ref": "Mateus 6:33", "text": "Busquem, pois, em primeiro lugar o Reino de Deus e a sua justiça, e todas essas coisas serão acrescentadas."},
    {"ref": "Mateus 22:37", "text": "Ame o Senhor, o seu Deus, de todo o seu coração, de toda a sua alma e de todo o seu entendimento."},
    {"ref": "Lucas 6:38", "text": "Dêem, e lhes será dado: uma boa medida, calcada, sacudida e transbordante."},
    {"ref": "João 15:5", "text": "Eu sou a videira; vocês são os ramos. Quem permanece em mim, e eu nele, esse dá muito fruto."},
    {"ref": "João 16:33", "text": "No mundo vocês terão aflições; contudo, tenham ânimo! Eu venci o mundo."},
    {"ref": "Atos 16:25", "text": "Por volta da meia-noite, Paulo e Silas estavam orando e cantando hinos a Deus."},
    {"ref": "Romanos 12:1", "text": "Rogo-lhes, irmãos, que se ofereçam em sacrifício vivo, santo e agradável a Deus."},
    {"ref": "Romanos 15:13", "text": "Que o Deus da esperança os encha de toda alegria e paz, na fé."},
    {"ref": "1 Coríntios 10:31", "text": "Portanto, quer comam, quer bebam, façam tudo para a glória de Deus."},
    {"ref": "2 Coríntios 5:7", "text": "Vivemos por fé, e não pelo que vemos."},
    {"ref": "2 Coríntios 12:9", "text": "A minha graça é suficiente para você, pois o meu poder se aperfeiçoa na fraqueza."},
    {"ref": "Gálatas 2:20", "text": "Já não sou eu quem vive, mas Cristo vive em mim."},
    {"ref": "Efésios 3:20", "text": "Àquele que é capaz de fazer infinitamente mais do que tudo o que pedimos ou pensamos."},
    {"ref": "Filipenses 4:6-7", "text": "Não andem ansiosos por coisa alguma, mas em tudo, pela oração, apresentem os seus pedidos a Deus."},
    {"ref": "Colossenses 3:23", "text": "Tudo o que fizerem, façam de todo o coração, como para o Senhor, e não para os homens."},
    {"ref": "1 Tessalonicenses 5:16-18", "text": "Alegrem-se sempre, orem continuamente, deem graças em todas as circunstâncias."},
    {"ref": "2 Timóteo 1:7", "text": "Porque Deus não nos deu espírito de covardia, mas de poder, de amor e de equilíbrio."},
    {"ref": "Hebreus 10:24", "text": "Preocupemo-nos uns com os outros, a fim de estimular o amor e as boas obras."},
    {"ref": "Hebreus 13:15", "text": "Por meio de Jesus, portanto, ofereçamos continuamente a Deus um sacrifício de louvor."},
    {"ref": "Tiago 1:5", "text": "Se algum de vocês tem falta de sabedoria, peça-a a Deus, que a todos dá livremente."},
    {"ref": "1 Pedro 5:7", "text": "Lancem sobre ele toda a sua ansiedade, porque ele tem cuidado de vocês."},
    {"ref": "1 João 4:19", "text": "Nós amamos porque ele nos amou primeiro."},
    {"ref": "Apocalipse 4:11", "text": "Digno és, Senhor e Deus nosso, de receber a glória, a honra e o poder."},
    {"ref": "Neemias 8:10", "text": "A alegria do Senhor é a vossa força."},
    {"ref": "2 Crônicas 20:21", "text": "Dêem graças ao Senhor, pois o seu amor dura para sempre."},
    {"ref": "Deuteronômio 31:6", "text": "Sejam fortes e corajosos. Não temam, pois o Senhor vai com vocês."},
    {"ref": "Êxodo 15:2", "text": "O Senhor é a minha força e o meu cântico; ele é a minha salvação."},
    {"ref": "1 Samuel 16:7", "text": "O Senhor não vê as coisas como o homem as vê; o homem vê a aparência exterior, mas o Senhor vê o coração."},
    {"ref": "Romanos 12:2", "text": "Transformem-se pela renovação da sua mente, para que sejam capazes de experimentar a boa vontade de Deus."},
    {"ref": "Salmos 16:11", "text": "Tu me farás conhecer a vereda da vida; na tua presença há plenitude de alegria."},
    {"ref": "Salmos 18:2", "text": "O Senhor é a minha rocha, a minha fortaleza e o meu libertador."},
    {"ref": "Salmos 30:11-12", "text": "Converteste o meu pranto em dança; tiraste o meu pano de saco e me cingiste de alegria."},
    {"ref": "Salmos 40:3", "text": "Pôs na minha boca um novo cântico, um hino de louvor ao nosso Deus."},
    {"ref": "Salmos 51:15", "text": "Abre os meus lábios, Senhor, e a minha boca cantará o teu louvor."},
    {"ref": "Salmos 66:1-2", "text": "Aclamem a Deus, todos os habitantes da terra! Cantem louvores ao seu nome glorioso."},
    {"ref": "Salmos 84:10", "text": "Um só dia nos teus átrios vale mais que mil noutro lugar."},
    {"ref": "Salmos 89:1", "text": "Cantarei para sempre o amor do Senhor; com a minha boca anunciarei a tua fidelidade."},
    {"ref": "Salmos 91:1", "text": "Aquele que habita no abrigo do Altíssimo e descansa à sombra do Todo-poderoso."},
    {"ref": "Salmos 103:2-3", "text": "Bendiga o Senhor a minha alma! Não esqueça nenhuma de suas bênçãos."},
    {"ref": "Salmos 126:3", "text": "Grandes coisas fez o Senhor por nós, e por isso estamos alegres."},
    {"ref": "Salmos 133:1", "text": "Como é bom e agradável quando os irmãos convivem em união!"},
    {"ref": "Salmos 138:1-2", "text": "Eu te louvarei, Senhor, de todo o coração; diante dos deuses te cantarei louvores."},
    {"ref": "Salmos 141:2", "text": "Suba a minha oração como incenso diante de ti; o levantar das minhas mãos, como oferta da tarde."},
    {"ref": "Salmos 144:9", "text": "A ti, ó Deus, cantarei um novo cântico; no saltério de dez cordas te louvarei."},
    {"ref": "Salmos 148:1-2", "text": "Aleluia! Louvem o Senhor desde os céus, louvem-no nas alturas!"},
)


def verse_for_date(when: date | None = None) -> dict[str, str]:
    """Mesmo versículo para todos no mesmo dia (fuso de Brasília)."""
    when = when or now_local().date()
    idx = when.toordinal() % len(VERSES_OF_DAY)
    return VERSES_OF_DAY[idx]


def render_verse_of_day() -> None:
    v = verse_for_date()
    text = html.escape(v["text"])
    ref = html.escape(v["ref"])
    st.markdown(
        f"""
        <div class="verse-of-day">
            <p class="verse-label">📖 Versículo do dia</p>
            <p class="verse-text">"{text}"</p>
            <p class="verse-ref">{ref}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
