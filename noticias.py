import re
import unicodedata
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time
import os

import requests
import trafilatura
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

from config import PALAVRAS_EXCLUIDAS


def detectar_novidades(noticias_atuais: list[Noticia], urls_anteriores: set[str]) -> list[Noticia]:
    """Filtra notícias retornando apenas as novas (não vistas anteriormente)."""
    novas = []
    for noticia in noticias_atuais:
        if noticia.url not in urls_anteriores:
            novas.append(noticia)
    return novas


# Carregar variáveis de ambiente
load_dotenv()

# Ignorar warnings de timezone desconhecido do dateutil
warnings.filterwarnings("ignore", message=".*tzname.*identified but not understood.*")

FUSO = ZoneInfo("America/Sao_Paulo")
CABECALHOS = {"User-Agent": "Mozilla/5.0 (compatible; FutebolNoticias/1.0; +https://localhost)"}
GREMIO_FIREBASE_KEY = "AIzaSyAkH7Rmqp9vdek-HniQcxwDLAwPsJlpy70"
GREMIO_FIREBASE_URL = "https://firestore.googleapis.com/v1/projects/gremio-a1502/databases/(default)/documents"


@dataclass
class Noticia:
    titulo: str
    url: str
    data: datetime | None = None
    origem: str = ""


def agora() -> datetime:
    return datetime.now(FUSO)


def interpretar_data(texto: str, referencia: datetime | None = None) -> datetime | None:
    """Interpreta datas absolutas e rótulos em português como 'há 11 horas'."""
    if not texto:
        return None
    referencia = referencia or agora()
    valor = " ".join(texto.lower().replace("às", " ").split())
    
    # Suporte para formatos relativos em português
    if "ontem" in valor:
        return referencia - timedelta(days=1)
    if "hoje" in valor:
        return referencia
    
    # Suporte para "há X tempo" e "now"
    padrao = re.search(r"h[áa]\s+(?:cerca\s+de\s+)?(\d+)\s*(minuto|minutos|hora|horas|dia|dias|semana|semanas|mês|meses|ano|anos)", valor)
    if padrao:
        quantidade, unidade = int(padrao.group(1)), padrao.group(2)
        if unidade.startswith("minuto"):
            return referencia - timedelta(minutes=quantidade)
        if unidade.startswith("hora"):
            return referencia - timedelta(hours=quantidade)
        if unidade.startswith("dia"):
            return referencia - timedelta(days=quantidade)
        if unidade.startswith("semana"):
            return referencia - timedelta(weeks=quantidade)
        if unidade.startswith("mês") or unidade.startswith("mes"):
            return referencia - timedelta(days=quantidade * 30)
        if unidade.startswith("ano"):
            return referencia - timedelta(days=quantidade * 365)
    
    # Suporte para formatos em inglês comuns em redes sociais
    padrao_ingles = re.search(r"(\d+)\s*(min|mins|minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)\s+ago", valor)
    if padrao_ingles:
        quantidade, unidade = int(padrao_ingles.group(1)), padrao_ingles.group(2)
        if unidade.startswith("min"):
            return referencia - timedelta(minutes=quantidade)
        if unidade.startswith("hour"):
            return referencia - timedelta(hours=quantidade)
        if unidade.startswith("day"):
            return referencia - timedelta(days=quantidade)
        if unidade.startswith("week"):
            return referencia - timedelta(weeks=quantidade)
        if unidade.startswith("month"):
            return referencia - timedelta(days=quantidade * 30)
        if unidade.startswith("year"):
            return referencia - timedelta(days=quantidade * 365)
    
    # Suporte para "now" ou "agora"
    if "now" in valor or "agora" in valor:
        return referencia
    
    # Adicionar suporte para formato "22 de julho de 2026"
    padrao_data_texto = re.search(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", valor)
    if padrao_data_texto:
        try:
            dia = int(padrao_data_texto.group(1))
            mes_texto = padrao_data_texto.group(2)
            ano = int(padrao_data_texto.group(3))
            meses = {
                "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6,
                "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
            }
            mes = meses.get(mes_texto)
            if mes:
                return datetime(ano, mes, dia, tzinfo=FUSO)
        except (ValueError, KeyError):
            pass
    
    # Tentar parsing com dateutil como fallback
    try:
        # Detectar formato ISO 8601 (ex: 2026-08-01T09:00:00.000Z)
        # Nesse caso, NÃO usar dayfirst=True para evitar confusão dia/mês
        is_iso_format = bool(re.match(r'\d{4}-\d{2}-\d{2}[T\s]', texto))
        
        resultado = date_parser.parse(
            texto, 
            dayfirst=not is_iso_format,  # dayfirst=False para formato ISO 8601
            fuzzy=True, 
            default=referencia.replace(hour=12, minute=0, second=0, microsecond=0)
        )
        # Se o resultado já tem timezone, converter para FUSO
        if resultado.tzinfo is not None:
            return resultado.astimezone(FUSO)
        # Se não tem timezone, verificar se o texto original indica UTC (com 'Z' ou '+00:00')
        if texto.endswith('Z') or '+00:00' in texto or 'UTC' in texto.upper():
            # Assumir UTC e converter para FUSO
            resultado = resultado.replace(tzinfo=ZoneInfo("UTC"))
            return resultado.astimezone(FUSO)
        # Caso contrário, assumir que já está no FUSO
        return resultado.replace(tzinfo=FUSO)
    except (ValueError, TypeError, OverflowError):
        return None


def eh_dia_alvo(data: datetime | None, dia: str, referencia: datetime | None = None) -> bool:
    if data is None:
        return False
    referencia = referencia or agora()
    hoje = referencia.date()
    ontem = (referencia - timedelta(days=1)).date()
    return data.date() == (hoje if dia == "hoje" else ontem) if dia != "ambos" else data.date() in {hoje, ontem}


def baixar(url: str) -> str:
    destino = urlparse(url)
    verificar_ssl = destino.netloc != "www.cbf.com.br"
    resposta = requests.get(url, headers=CABECALHOS, timeout=25, verify=verificar_ssl)
    resposta.raise_for_status()
    return resposta.text


def _valor_firestore(campo: dict | None):
    """Converte o formato de valores da API pública do Firestore."""
    if not campo:
        return None
    for chave, valor in campo.items():
        if chave.endswith("Value"):
            return valor
    return None


def _slug(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", normalizado.lower())).strip("-")


def _noticia_gremio(documento: dict) -> Noticia | None:
    campos = documento.get("fields", {})
    titulo = _valor_firestore(campos.get("Title__c")) or _valor_firestore(campos.get("Name"))
    data = interpretar_data(_valor_firestore(campos.get("PublishDateTimestamp")))
    identificador = documento.get("name", "").rsplit("/", 1)[-1]
    if not titulo or not identificador:
        return None
    url = f"https://portal.gremio.net/noticias/{identificador}/{_slug(titulo)}"
    return Noticia(titulo=titulo, url=url, data=data, origem="Grêmio")


def descobrir_noticias_gremio(dia: str) -> list[Noticia]:
    """Consulta a mesma base pública usada pela página de notícias do Grêmio.
    Quando dia == "recentes", busca as 10 notícias mais recentes sem filtro de data.
    """
    consulta = {
        "structuredQuery": {
            "from": [{"collectionId": "News"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "Active__c"},
                    "op": "EQUAL",
                    "value": {"booleanValue": True},
                }
            },
            "orderBy": [{"field": {"fieldPath": "PublishDateTimestamp"}, "direction": "DESCENDING"}],
            "limit": 100,  # Aumentar limite para garantir 10 após filtro
        }
    }
    resposta = requests.post(f"{GREMIO_FIREBASE_URL}:runQuery", params={"key": GREMIO_FIREBASE_KEY}, json=consulta, timeout=25)
    resposta.raise_for_status()
    noticias = [_noticia_gremio(item["document"]) for item in resposta.json() if item.get("document")]
    
    # Se for "recentes", não filtra por data e retorna todas para depois filtrar por palavras
    if dia == "recentes":
        return [noticia for noticia in noticias if noticia]
    
    return [noticia for noticia in noticias if noticia and eh_dia_alvo(noticia.data, dia)]


def descobrir_noticias_portal_gremista(dia: str) -> list[Noticia]:
    """Extrator específico para o Portal do Gremista com suporte a paginação.
    Quando dia == "recentes", busca as 10 notícias mais recentes sem filtro de data.
    """
    encontradas: dict[str, Noticia] = {}
    pagina_atual = 1
    max_paginas = 2  # Limitar a 2 páginas (hoje e ontem)
    
    # Se for "recentes", aumentar para 3 páginas para garantir 20 notícias
    if dia == "recentes":
        max_paginas = 3
    
    while pagina_atual <= max_paginas:
        url = f"https://portaldogremista.com.br/categorias/noticias/page/{pagina_atual}/" if pagina_atual > 1 else "https://portaldogremista.com.br/categorias/noticias/"
        
        try:
            sopa = BeautifulSoup(baixar(url), "html.parser")
            
            # Procurar por h2/h3 com links (estrutura do Portal do Gremista)
            for tag in ['h2', 'h3']:
                headers = sopa.find_all(tag)
                for h in headers:
                    link = h.find('a')
                    if not link:
                        continue
                    
                    href = link['href']
                    destino = urlparse(href)
                    
                    # Apenas links do próprio domínio
                    if not destino.netloc.endswith("portaldogremista.com.br"):
                        continue
                    
                    # Ignorar links de paginação
                    if "page/" in href:
                        continue
                    
                    titulo = link.get_text(" ", strip=True)
                    if len(titulo) < 20:
                        continue
                    
                    # Procurar data no elemento pai
                    cartao = h.find_parent(['div', 'article'])
                    contexto = cartao.get_text(" ", strip=True) if cartao else titulo
                    
                    elemento_tempo = (cartao.find("time") if cartao else None) or h.find_next("time")
                    texto_data = elemento_tempo.get("datetime") if elemento_tempo and elemento_tempo.get("datetime") else (elemento_tempo.get_text(" ", strip=True) if elemento_tempo else contexto)
                    
                    data = interpretar_data(texto_data)
                    
                    if eh_dia_alvo(data, dia):
                        encontradas[href] = Noticia(titulo=titulo, url=href, data=data, origem="Portal do Gremista")
        except Exception as e:
            print(f"  Erro ao carregar página {pagina_atual}: {e}")
        
        pagina_atual += 1
    
    noticias = sorted(encontradas.values(), key=lambda n: n.data or datetime.min.replace(tzinfo=FUSO), reverse=True)
    
    # Se for "recentes", retorna até 20 notícias mais recentes
    if dia == "recentes":
        return noticias[:20]
    
    return noticias


def descobrir_noticias_gzh_simples() -> list[Noticia]:
    """Extrator simplificado para GZH sem necessidade de login.
    Busca notícias apenas por título e link, sem conteúdo completo.
    Usa Selenium para renderizar JavaScript, mas sem exigir login.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium não está instalado. Instale com: pip install selenium")
        return []
    
    try:
        options = Options()
        options.add_argument('--headless')  # Modo silencioso
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.get('https://gauchazh.clicrbs.com.br/esportes/gremio/ultimas-noticias/')
        
        # Esperar JavaScript carregar
        time.sleep(5)
        
        html = driver.page_source
        driver.quit()
        
        sopa = BeautifulSoup(html, 'html.parser')
        encontradas: dict[str, Noticia] = {}
        
        # Procurar por links de notícias
        links = sopa.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            # Filtrar apenas links de notícias do GZH
            if '/esportes/gremio/' in href and not href.endswith('/esportes/gremio/'):
                # Construir URL completa se necessário
                if href.startswith('/'):
                    href = urljoin('https://gauchazh.clicrbs.com.br', href)
                
                # Evitar duplicatas
                if href in encontradas:
                    continue
                
                # Extrair título do link
                titulo = link.get_text(" ", strip=True)
                if len(titulo) < 5:
                    continue
                
                # Filtrar links que não parecem ser notícias
                palavras_ignorar = ['entrar', 'cadastre', 'assine', 'newsletter', 'rss', 'facebook', 'twitter', 'instagram']
                if any(palavra in titulo.lower() for palavra in palavras_ignorar):
                    continue
                
                # Tentar encontrar data
                data = None
                parent = link.find_parent(['div', 'article', 'li', 'section'])
                if parent:
                    time_elem = parent.find('time')
                    if time_elem:
                        data = interpretar_data(time_elem.get('datetime') or time_elem.get_text())
                
                encontradas[href] = Noticia(
                    titulo=titulo,
                    url=href,
                    data=data,
                    origem="GZH"
                )
        
        # Se não encontrou nada com o método acima, tentar abordagem mais agressiva
        if not encontradas:
            # Procurar por elementos article ou div com classes típicas de notícias
            artigos = sopa.find_all(['article', 'div'], class_=lambda x: x and any(term in str(x).lower() for term in ['noticia', 'news', 'post', 'conteudo']))
            for artigo in artigos:
                links_no_artigo = artigo.find_all('a', href=True)
                for link in links_no_artigo:
                    href = link.get('href', '')
                    if '/esportes/gremio/' in href and not href.endswith('/esportes/gremio/'):
                        if href.startswith('/'):
                            href = urljoin('https://gauchazh.clicrbs.com.br', href)
                        
                        if href in encontradas:
                            continue
                        
                        titulo = link.get_text(" ", strip=True)
                        if len(titulo) < 5:
                            continue
                        
                        encontradas[href] = Noticia(
                            titulo=titulo,
                            url=href,
                            data=None,
                            origem="GZH"
                        )
        
        return list(encontradas.values())
        
    except Exception as e:
        print(f"  Erro ao buscar GZH (modo simples): {e}")
        return []


def descobrir_noticias_gzh(dia: str, driver=None) -> tuple[list[Noticia], object]:
    """Extrator específico para GZH com login manual no navegador.
    Retorna tupla com (lista de notícias, driver do selenium).
    Se driver for fornecido, reutiliza a sessão existente.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium não está instalado. Instale com: pip install selenium")
        return [], None
    
    driver_fechado = False
    
    # Se não foi fornecido driver, criar nova instância
    if driver is None:
        # Sempre usar navegador visível para login manual
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')  # Suprimir logs do Chrome
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            driver = webdriver.Chrome(options=options)
            # Ir direto para a página de notícias do Grêmio
            driver.get('https://gauchazh.clicrbs.com.br/esportes/gremio/ultimas-noticias/')
            
            # Login manual
            print("\n  === LOGIN MANUAL GZH ===")
            print("  Por favor, faça o login manualmente no navegador aberto.")
            print("  1. Clique no botão ENTRAR no canto superior direito")
            print("  2. Preencha seu email e senha")
            print("  3. Após efetuar o login, volte aqui e pressione Enter")
            input("  Pressione Enter quando tiver feito o login...")
            
            # Esperar a página carregar após login e JavaScript renderizar
            time.sleep(5)
        except Exception as e:
            print(f"  Erro ao inicializar Selenium para GZH: {e}")
            return [], None
    else:
        # Driver fornecido, apenas navegar para a página
        try:
            driver.get('https://gauchazh.clicrbs.com.br/esportes/gremio/ultimas-noticias/')
            time.sleep(3)
        except Exception as e:
            print(f"  Erro ao navegar para página GZH: {e}")
            return [], driver
    
    try:
        while True:
            print(f"\nBuscando em GZH (período: {dia})...")
            try:
                noticias, driver_gzh = descobrir_noticias("https://gauchazh.clicrbs.com.br/esportes/gremio/ultimas-noticias/", "gauchazh.clicrbs.com.br", "GZH", dia, driver)
            except Exception as erro:
                print(f"  Não foi possível consultar: {erro}")
                if driver_gzh:
                    try:
                        driver_gzh.quit()
                    except:
                        pass
                return [], None
            
            if not noticias:
                print("  Nenhuma notícia encontrada.")
                pergunta = input("  Tentar novamente? (s/n): ").strip().lower()
                if pergunta != 's':
                    if driver_fechado:
                        driver.quit()
                    return [], driver
                continue
            
            print(f"\nNotícias encontradas: {len(noticias)}")
            for indice, noticia in enumerate(noticias, 1):
                momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
                print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
            
            pergunta = input("\nDeseja adicionar notícias à seleção? (s/n): ").strip().lower()
            if pergunta == 's':
                escolha = input("Quais deseja adicionar? (ex: 1,3,5 ou 1-5 ou 'todos'): ").strip()
                
                if escolha.lower() in ["tudo", "todos", "all"]:
                    indices = list(range(1, len(noticias) + 1))
                elif escolha:
                    indices = []
                    for valor in escolha.split(","):
                        valor = valor.strip()
                        if "-" in valor:
                            try:
                                inicio, fim = valor.split("-")
                                for i in range(int(inicio.strip()), int(fim.strip()) + 1):
                                    if 1 <= i <= len(noticias):
                                        indices.append(i)
                            except (ValueError, IndexError):
                                print(f"Intervalo inválido: {valor}")
                        else:
                            try:
                                num = int(valor)
                                if num > 0:
                                    indices.append(num)
                            except ValueError:
                                print(f"Opção ignorada: {valor}")
                else:
                    indices = []
                
                indices = sorted(set(indices))
                
                for indice in indices:
                    try:
                        noticia = noticias[indice - 1]
                        from menu import adicionar_link
                        adicionar_link(noticia.url, "")
                    except (ValueError, IndexError):
                        print(f"Opção ignorada: {indice}")
            
            pergunta = input("\nContinuar buscando no GZH? (s/n): ").strip().lower()
            if pergunta != 's':
                break
        
        return noticias, driver
    
    except Exception as e:
        print(f"  Erro ao processar GZH: {e}")
        if driver_fechado:
            try:
                driver.quit()
            except:
                pass
        return [], None


def descobrir_noticias_ge_gremio(dia: str) -> list[Noticia]:
    """Extrator específico para GE Grêmio usando Selenium para carregar mais notícias com scroll.
    Quando dia == "recentes", busca as 10 notícias mais recentes sem filtro de data.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium não está instalado. Instale com: pip install selenium")
        return []
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get('https://ge.globo.com/rs/futebol/times/gremio/')
        
        # Esperar o JavaScript carregar
        time.sleep(5)
        
        encontradas: dict[str, Noticia] = {}
        
        # Fazer scroll para carregar mais notícias
        for i in range(3):  # 3 rolagens para carregar mais conteúdo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        html = driver.page_source
        sopa = BeautifulSoup(html, 'html.parser')
        
        for link in sopa.select("a[href]"):
            href = link["href"]
            destino = urlparse(href)
            
            # Apenas links do GE
            if not destino.netloc.endswith("ge.globo.com"):
                continue
            
            # Ignorar links que não são de notícias
            if not href.endswith(".ghtml"):
                continue
            
            # Apenas notícias do Grêmio
            if "/rs/futebol/times/gremio/noticia/" not in href:
                continue
            
            titulo = link.get_text(" ", strip=True)
            if len(titulo) < 20:
                continue
            
            # Construir URL completa se necessário
            if href.startswith('/'):
                href = urljoin('https://ge.globo.com', href)
            
            # Procurar data
            data = None
            parent = link.find_parent(['div', 'article'])
            if parent:
                time_elem = parent.find('time')
                if time_elem:
                    data = interpretar_data(time_elem.get('datetime') or time_elem.get_text())
            
            encontradas[href] = Noticia(titulo=titulo, url=href, data=data, origem="GE Grêmio")
        
        driver.quit()
        
        noticias = sorted(encontradas.values(), key=lambda n: n.data or datetime.min.replace(tzinfo=FUSO), reverse=True)
        
        # Se for "recentes", retorna até 10 notícias mais recentes
        if dia == "recentes":
            return noticias[:10]
        
        return noticias
    
    except Exception as e:
        print(f"  Erro ao usar Selenium para GE Grêmio: {e}")
        return []


def descobrir_noticias_ge_selecao(dia: str) -> list[Noticia]:
    """Extrator específico para GE Seleção usando Selenium para carregar mais notícias com scroll.
    Quando dia == "recentes", busca as 10 notícias mais recentes sem filtro de data.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium não está instalado. Instale com: pip install selenium")
        return []
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get('https://ge.globo.com/futebol/selecao-brasileira/')
        
        # Esperar o JavaScript carregar
        time.sleep(5)
        
        encontradas: dict[str, Noticia] = {}
        
        # Fazer scroll para carregar mais notícias
        for i in range(10):  # 10 rolagens para carregar mais conteúdo
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Aumentar tempo de espera para 3 segundos
        
        html = driver.page_source
        sopa = BeautifulSoup(html, 'html.parser')
        
        for link in sopa.select("a[href]"):
            href = link["href"]
            destino = urlparse(href)
            
            # Apenas links do GE
            if not destino.netloc.endswith("ge.globo.com"):
                continue
            
            # Ignorar links que não são de notícias
            if not href.endswith(".ghtml"):
                continue
            
            # Apenas notícias da Seleção
            if "/futebol/selecao-brasileira/noticia/" not in href:
                continue
            
            titulo = link.get_text(" ", strip=True)
            if len(titulo) < 20:
                continue
            
            # Construir URL completa se necessário
            if href.startswith('/'):
                href = urljoin('https://ge.globo.com', href)
            
            # Procurar data
            data = None
            parent = link.find_parent(['div', 'article'])
            if parent:
                time_elem = parent.find('time')
                if time_elem:
                    data = interpretar_data(time_elem.get('datetime') or time_elem.get_text())
            
            encontradas[href] = Noticia(titulo=titulo, url=href, data=data, origem="GE Seleção")
        
        driver.quit()
        
        noticias = sorted(encontradas.values(), key=lambda n: n.data or datetime.min.replace(tzinfo=FUSO), reverse=True)
        
        # Se for "recentes", retorna até 10 notícias mais recentes (ou todas se tiver menos)
        if dia == "recentes":
            return noticias[:10]
        
        return noticias
    
    except Exception as e:
        print(f"  Erro ao usar Selenium para GE Seleção: {e}")
        return []


def descobrir_noticias_fgf(dia: str) -> list[Noticia]:
    """Extrator específico para o site da FGF usando Selenium para renderizar JavaScript.
    Quando dia == "recentes", busca as 10 notícias mais recentes sem filtro de data.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  Selenium não está instalado. Instale com: pip install selenium")
        return []
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get('https://fgf.com.br/noticias/')
        
        # Esperar o JavaScript carregar
        time.sleep(5)
        
        encontradas: dict[str, Noticia] = {}
        html = driver.page_source
        sopa = BeautifulSoup(html, 'html.parser')
        
        for link in sopa.select("a[href]"):
            href = link.get('href', '')
            if '/noticia/' not in href:
                continue
            
            url = urljoin('https://fgf.com.br', href)
            destino = urlparse(url)
            if destino.netloc != "fgf.com.br":
                continue
            
            titulo = link.get_text(" ", strip=True)
            if len(titulo) < 20:
                continue
            
            # Procurar data
            data = None
            parent = link.find_parent(['div', 'article'])
            if parent:
                time_elem = parent.find('time')
                if time_elem:
                    data = interpretar_data(time_elem.get('datetime') or time_elem.get_text())
            
            encontradas[url] = Noticia(titulo=titulo, url=url, data=data, origem="FGF")
        
        driver.quit()
        
        noticias = sorted(encontradas.values(), key=lambda n: n.data or datetime.min.replace(tzinfo=FUSO), reverse=True)
        
        # Se for "recentes", retorna até 10 notícias mais recentes
        if dia == "recentes":
            return noticias[:10]
        
        return noticias
    
    except Exception as e:
        print(f"  Erro ao usar Selenium para FGF: {e}")
        return []


def descobrir_noticias_conmebol(dia: str) -> list[Noticia]:
    """Extrator específico para o site da CONMEBOL usando Selenium para renderizar JavaScript.
    Quando dia == "recentes", busca as 5 notícias mais recentes sem filtro de data.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("  Selenium não está instalado. Instale com: pip install selenium")
        return []
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get('https://www.conmebol.com/ultimas-noticias/')
        
        # Esperar o JavaScript carregar
        time.sleep(5)
        
        encontradas: dict[str, Noticia] = {}
        html = driver.page_source
        sopa = BeautifulSoup(html, 'html.parser')
        
        for link in sopa.select("a[href]"):
            href = link.get('href', '')
            # Aceitar tanto /noticias/ quanto /news/ e dominios gol.conmebol.com e www.conmebol.com
            if '/noticias/' not in href and '/news/' not in href:
                continue
            
            # Adicionar domínio se necessário
            if href.startswith('/'):
                url = urljoin('https://www.conmebol.com', href)
            else:
                url = href
            
            destino = urlparse(url)
            # Aceitar ambos domínios da CONMEBOL
            if destino.netloc not in ["www.conmebol.com", "gol.conmebol.com"]:
                continue
            
            titulo = link.get_text(" ", strip=True)
            if len(titulo) < 20:
                continue
            
            cartao = link.find_parent(["article", "li", "div"])
            if cartao:
                contexto = cartao.get_text(" ", strip=True)
                elemento_tempo = cartao.find("time")
                texto_data = elemento_tempo.get("datetime") if elemento_tempo else contexto
                data = interpretar_data(texto_data)
            else:
                data = None
            
            if eh_dia_alvo(data, dia):
                encontradas[url] = Noticia(titulo=titulo, url=url, data=data, origem="CONMEBOL")
        
        driver.quit()
        
        noticias = sorted(encontradas.values(), key=lambda n: n.data or datetime.min.replace(tzinfo=FUSO), reverse=True)
        
        # Se for "recentes", retorna até 5 notícias mais recentes
        if dia == "recentes":
            return noticias[:5]
        
        return noticias
    
    except Exception as e:
        print(f"  Erro ao usar Selenium para CONMEBOL: {e}")
        return []


def descobrir_noticias_cbf(dia: str) -> list[Noticia]:
    """Extrator específico para o site da CBF usando Selenium para renderizar JavaScript.
    Quando dia == "recentes", busca as 15 notícias mais recentes sem filtro de data.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("  Selenium não está instalado. Instale com: pip install selenium")
        return []
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        driver = webdriver.Chrome(options=options)
        
        encontradas: dict[str, Noticia] = {}
        pagina_atual = 1
        max_paginas = 2  # Limitar a 2 páginas para "recentes", usar lógica normal para outros períodos
        
        # Se for "recentes", aumentar número de páginas para garantir 15 notícias após filtro
        if dia == "recentes":
            max_paginas = 5  # 5 páginas para garantir conteúdo suficiente após filtro
        
        while pagina_atual <= max_paginas:
            # Usar URL direta com parâmetro de página
            if pagina_atual == 1:
                url = 'https://www.cbf.com.br/noticias'
            else:
                url = f'https://www.cbf.com.br/noticias?pagina={pagina_atual}'
            
            driver.get(url)
            
            # Esperar o JavaScript carregar
            time.sleep(5)
            
            html = driver.page_source
            sopa = BeautifulSoup(html, 'html.parser')
            
            for link in sopa.select("a[href]"):
                href = link.get('href', '')
                if '/noticias/' not in href or href.endswith('/noticias/'):
                    continue
                
                # Construir URL completa se necessário
                if href.startswith('/'):
                    href = urljoin('https://www.cbf.com.br', href)
                
                destino = urlparse(href)
                if destino.netloc != "www.cbf.com.br":
                    continue
                
                titulo = link.get_text(" ", strip=True)
                if len(titulo) < 20:
                    continue
                
                # Procurar data
                data = None
                parent = link.find_parent(['div', 'article'])
                if parent:
                    time_elem = parent.find('time')
                    if time_elem:
                        data = interpretar_data(time_elem.get('datetime') or time_elem.get_text())
                
                encontradas[href] = Noticia(titulo=titulo, url=href, data=data, origem="CBF")
            
            pagina_atual += 1
        
        driver.quit()
        
        noticias = sorted(encontradas.values(), key=lambda n: n.data or datetime.min.replace(tzinfo=FUSO), reverse=True)
        
        # Se for "recentes", retorna até 15 notícias após aplicar limite
        if dia == "recentes":
            return noticias[:15]
        
        return noticias
    
    except Exception as e:
        print(f"  Erro ao usar Selenium para CBF: {e}")
        return []


def descobrir_noticias(url_fonte: str, dominio: str, origem: str, dia: str, driver=None) -> tuple[list[Noticia], object]:
    """Função genérica para descobrir notícias em sites de notícias."""
    try:
        sopa = BeautifulSoup(baixar(url_fonte), "html.parser")
        encontradas: dict[str, Noticia] = {}
        
        for link in sopa.select("a[href]"):
            href = link["href"]
            destino = urlparse(href)
            
            # Filtrar por domínio
            if not destino.netloc.endswith(dominio):
                continue
            
            # Ignorar links de paginação e navegação
            if any(termo in href for termo in ["page/", "pagina=", "categoria", "tag", "author"]):
                continue
            
            # Construir URL completa se necessário
            if href.startswith('/'):
                href = urljoin(url_fonte, href)
            
            # Evitar duplicatas
            if href in encontradas:
                continue
            
            titulo = link.get_text(" ", strip=True)
            if len(titulo) < 20:
                continue
            
            # Procurar data
            data = None
            parent = link.find_parent(['div', 'article', 'li'])
            if parent:
                time_elem = parent.find('time')
                if time_elem:
                    data = interpretar_data(time_elem.get('datetime') or time_elem.get_text())
            
            if eh_dia_alvo(data, dia):
                encontradas[href] = Noticia(titulo=titulo, url=href, data=data, origem=origem)
        
        return sorted(encontradas.values(), key=lambda n: n.data or datetime.min.replace(tzinfo=FUSO), reverse=True), None
    
    except Exception as e:
        print(f"  Erro ao buscar notícias: {e}")
        return [], None


def filtrar_noticias(noticias: list[Noticia]) -> list[Noticia]:
    """Filtra notícias removendo as que contêm palavras excluídas."""
    filtradas = []
    for noticia in noticias:
        if noticia.titulo:
            titulo_lower = noticia.titulo.lower()
            if not any(palavra.lower() in titulo_lower for palavra in PALAVRAS_EXCLUIDAS):
                filtradas.append(noticia)
    return filtradas


def extrair_materia(url: str) -> tuple[str, str, datetime | None]:
    destino = urlparse(url)
    partes = [parte for parte in destino.path.split("/") if parte]
    
    if destino.netloc == "portal.gremio.net" and len(partes) >= 2 and partes[0] == "noticias":
        identificador = partes[1]
        resposta = requests.get(f"{GREMIO_FIREBASE_URL}/News/{identificador}", params={"key": GREMIO_FIREBASE_KEY}, timeout=25)
        if resposta.ok:
            campos = resposta.json().get("fields", {})
            titulo = _valor_firestore(campos.get("Title__c")) or _valor_firestore(campos.get("Name")) or url
            conteudo_html = _valor_firestore(campos.get("Content__c")) or ""
            conteudo = BeautifulSoup(conteudo_html, "html.parser").get_text("\n", strip=True)
            data = interpretar_data(_valor_firestore(campos.get("PublishDateTimestamp")))
            if conteudo:
                return titulo, conteudo, data
    html = baixar(url)
    sopa = BeautifulSoup(html, "html.parser")
    titulo = (sopa.select_one("meta[property='og:title']") or sopa.select_one("h1"))
    titulo_texto = titulo.get("content", "") if titulo and titulo.name == "meta" else (titulo.get_text(" ", strip=True) if titulo else url)
    meta_data = sopa.select_one("meta[property='article:published_time'], meta[name='date'], time[datetime]")
    texto_data = meta_data.get("content") or meta_data.get("datetime") if meta_data else ""
    corpo = trafilatura.extract(html, include_comments=False, include_tables=False, favor_precision=True)
    if not corpo:
        artigo = sopa.select_one("article") or sopa.select_one("main") or sopa.body
        corpo = artigo.get_text("\n", strip=True) if artigo else ""
    return titulo_texto, corpo, interpretar_data(texto_data)
