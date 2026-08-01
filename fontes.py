from dataclasses import dataclass


@dataclass(frozen=True)
class Fonte:
    nome: str
    url: str
    dominio: str


FONTES = {
    "gremio": Fonte("Grêmio Oficial", "https://portal.gremio.net/noticias", "portal.gremio.net"),
    "gzh": Fonte("GZH", "https://gauchazh.clicrbs.com.br/esportes/gremio/ultimas-noticias/", "gauchazh.clicrbs.com.br"),
    "ge": Fonte("GE Grêmio", "https://ge.globo.com/rs/futebol/times/gremio/", "ge.globo.com"),
    "portaldogremista": Fonte("Portal do Gremista", "https://portaldogremista.com.br/categorias/noticias/", "portaldogremista.com.br"),
    "cbf": Fonte("CBF", "https://www.cbf.com.br/noticias", "cbf.com.br"),
    "conmebol": Fonte("CONMEBOL", "https://www.conmebol.com/ultimas-noticias/", "conmebol.com"),
    "ge_selecao": Fonte("GE Seleção", "https://ge.globo.com/futebol/selecao-brasileira/", "ge.globo.com"),
    "fgf": Fonte("FGF", "https://fgf.com.br/noticias/", "fgf.com.br"),
}

