"""Menu guiado para escolher notícias e gerar posts no terminal do VS Code."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fontes import FONTES
from noticias import descobrir_noticias, extrair_materia, detectar_novidades
from historico import obter_gerenciador

# ReportLab não é mais necessário (email sem PDF)
REPORTLAB_AVAILABLE = False

RAIZ = Path(__file__).parent
selecionadas: list[tuple[str, str]] = []


def escolher_fontes() -> list[str]:
    itens = list(FONTES)
    print("\nFontes disponíveis:")
    for indice, chave in enumerate(itens, 1):
        print(f"  {indice}. {FONTES[chave].nome}")
    print("  9. Todas")
    escolha = input("Digite os números: ").strip().lower()
    if escolha == "9":
        return itens
    resultado = []
    for valor in escolha.split(","):
        valor = valor.strip()
        if "-" in valor:
            # Tratar intervalo (ex: 1-4)
            try:
                inicio, fim = valor.split("-")
                for i in range(int(inicio.strip()), int(fim.strip()) + 1):
                    if 1 <= i <= len(itens):
                        resultado.append(itens[i - 1])
            except (ValueError, IndexError):
                print(f"Intervalo inválido: {valor}")
        else:
            try:
                resultado.append(itens[int(valor) - 1])
            except (ValueError, IndexError):
                print(f"Opção ignorada: {valor}")
    return list(dict.fromkeys(resultado))


def adicionar_link(url: str, instrucao: str = "") -> None:
    url = url.strip()
    if not url.startswith(("https://", "http://")):
        print("Link inválido. Ele deve começar com https:// ou http://")
        return
    if any(item[0] == url for item in selecionadas):
        print("Esse link já está na sua seleção.")
        return
    selecionadas.append((url, instrucao.strip()))
    print("Link adicionado.")


def buscar_gremio_interativo() -> bool:
    """Função específica para busca Gremio Oficial com busca automática das 10 notícias mais recentes."""
    print("\nBuscando em Grêmio Oficial (10 notícias mais recentes)...")
    try:
        from noticias import descobrir_noticias_gremio, filtrar_noticias
        noticias = descobrir_noticias_gremio("recentes")
        noticias_filtradas = filtrar_noticias(noticias)
        noticias = noticias_filtradas[:5]
    except Exception as erro:
        print(f"  Não foi possível consultar: {erro}")
        return True
    
    if not noticias:
        print("Nenhuma notícia encontrada no Grêmio Oficial.")
        return True
    
    print("\nNotícias encontradas:")
    for indice, noticia in enumerate(noticias, 1):
        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
        print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
    
    escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
    
    # Se o usuário digitar '0', cancela a seleção
    if escolha == "0":
        print("Seleção cancelada.")
    else:
        # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
        if escolha.lower() in ["tudo", "todos", "all"]:
            indices = list(range(1, len(noticias) + 1))
        elif escolha:
            indices = []
            for valor in escolha.split(","):
                valor = valor.strip()
                if "-" in valor:
                    # Tratar intervalo (ex: 1-48)
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
                        if num > 0:  # Ignorar números negativos ou zero
                            indices.append(num)
                    except ValueError:
                        print(f"Opção ignorada: {valor}")
        else:
            indices = []
        
        # Remover duplicados e ordenar
        indices = sorted(set(indices))
        
        for indice in indices:
            try:
                noticia = noticias[indice - 1]
                adicionar_link(noticia.url, "")
            except (ValueError, IndexError):
                print(f"Opção ignorada: {indice}")
    
    # Voltar ao menu principal após a seleção
    return True


def buscar_ge_selecao_interativo() -> bool:
    """Função específica para busca GE Seleção com busca automática das 10 notícias mais recentes."""
    print("\nBuscando em GE Seleção (10 notícias mais recentes)...")
    try:
        from noticias import descobrir_noticias_ge_selecao, filtrar_noticias
        noticias = descobrir_noticias_ge_selecao("recentes")
        noticias_filtradas = filtrar_noticias(noticias)
        noticias = noticias_filtradas[:5]
    except Exception as erro:
        print(f"  Não foi possível consultar: {erro}")
        return True
    
    if not noticias:
        print("Nenhuma notícia encontrada no GE Seleção.")
        return True
    
    print("\nNotícias encontradas:")
    for indice, noticia in enumerate(noticias, 1):
        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
        print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
    
    escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
    
    # Se o usuário digitar '0', cancela a seleção
    if escolha == "0":
        print("Seleção cancelada.")
    else:
        # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
        if escolha.lower() in ["tudo", "todos", "all"]:
            indices = list(range(1, len(noticias) + 1))
        elif escolha:
            indices = []
            for valor in escolha.split(","):
                valor = valor.strip()
                if "-" in valor:
                    # Tratar intervalo (ex: 1-48)
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
                        if num > 0:  # Ignorar números negativos ou zero
                            indices.append(num)
                    except ValueError:
                        print(f"Opção ignorada: {valor}")
        else:
            indices = []
        
        # Remover duplicados e ordenar
        indices = sorted(set(indices))
        
        for indice in indices:
            try:
                noticia = noticias[indice - 1]
                adicionar_link(noticia.url, "")
            except (ValueError, IndexError):
                print(f"Opção ignorada: {indice}")
    
    # Voltar ao menu principal após a seleção
    return True


def buscar_fgf_interativo() -> bool:
    """Função específica para busca FGF com busca automática das 10 notícias mais recentes."""
    print("\nBuscando em FGF (10 notícias mais recentes)...")
    try:
        from noticias import descobrir_noticias_fgf, filtrar_noticias
        noticias = descobrir_noticias_fgf("recentes")
        noticias_filtradas = filtrar_noticias(noticias)
        noticias = noticias_filtradas[:3]
    except Exception as erro:
        print(f"  Não foi possível consultar: {erro}")
        return True
    
    if not noticias:
        print("Nenhuma notícia encontrada no FGF.")
        return True
    
    print("\nNotícias encontradas:")
    for indice, noticia in enumerate(noticias, 1):
        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
        print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
    
    escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
    
    # Se o usuário digitar '0', cancela a seleção
    if escolha == "0":
        print("Seleção cancelada.")
    else:
        # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
        if escolha.lower() in ["tudo", "todos", "all"]:
            indices = list(range(1, len(noticias) + 1))
        elif escolha:
            indices = []
            for valor in escolha.split(","):
                valor = valor.strip()
                if "-" in valor:
                    # Tratar intervalo (ex: 1-48)
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
                        if num > 0:  # Ignorar números negativos ou zero
                            indices.append(num)
                    except ValueError:
                        print(f"Opção ignorada: {valor}")
        else:
            indices = []
        
        # Remover duplicados e ordenar
        indices = sorted(set(indices))
        
        for indice in indices:
            try:
                noticia = noticias[indice - 1]
                adicionar_link(noticia.url, "")
            except (ValueError, IndexError):
                print(f"Opção ignorada: {indice}")
    
    # Voltar ao menu principal após a seleção
    return True


def buscar_portaldogremista_interativo() -> bool:
    """Função específica para busca Portal do Gremista com busca automática das 20 notícias mais recentes."""
    print("\nBuscando em Portal do Gremista (20 notícias mais recentes)...")
    try:
        from noticias import descobrir_noticias_portal_gremista, filtrar_noticias
        noticias = descobrir_noticias_portal_gremista("recentes")
        noticias_filtradas = filtrar_noticias(noticias)
        noticias = noticias_filtradas[:10]
    except Exception as erro:
        print(f"  Não foi possível consultar: {erro}")
        return True
    
    if not noticias:
        print("Nenhuma notícia encontrada no Portal do Gremista.")
        return True
    
    print("\nNotícias encontradas:")
    for indice, noticia in enumerate(noticias, 1):
        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
        print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
    
    escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
    
    # Se o usuário digitar '0', cancela a seleção
    if escolha == "0":
        print("Seleção cancelada.")
    else:
        # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
        if escolha.lower() in ["tudo", "todos", "all"]:
            indices = list(range(1, len(noticias) + 1))
        elif escolha:
            indices = []
            for valor in escolha.split(","):
                valor = valor.strip()
                if "-" in valor:
                    # Tratar intervalo (ex: 1-48)
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
                        if num > 0:  # Ignorar números negativos ou zero
                            indices.append(num)
                    except ValueError:
                        print(f"Opção ignorada: {valor}")
        else:
            indices = []
        
        # Remover duplicados e ordenar
        indices = sorted(set(indices))
        
        for indice in indices:
            try:
                noticia = noticias[indice - 1]
                adicionar_link(noticia.url, "")
            except (ValueError, IndexError):
                print(f"Opção ignorada: {indice}")
    
    # Voltar ao menu principal após a seleção
    return True


def buscar_conmebol_interativo() -> bool:
    """Função específica para busca CONMEBOL com busca automática das 5 notícias mais recentes."""
    print("\nBuscando em CONMEBOL (5 notícias mais recentes)...")
    try:
        from noticias import descobrir_noticias_conmebol, filtrar_noticias
        noticias = descobrir_noticias_conmebol("recentes")
        noticias_filtradas = filtrar_noticias(noticias)
        noticias = noticias_filtradas[:5]
    except Exception as erro:
        print(f"  Não foi possível consultar: {erro}")
        return True
    
    if not noticias:
        print("Nenhuma notícia encontrada na CONMEBOL.")
        return True
    
    print("\nNotícias encontradas:")
    for indice, noticia in enumerate(noticias, 1):
        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
        print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
    
    escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
    
    # Se o usuário digitar '0', cancela a seleção
    if escolha == "0":
        print("Seleção cancelada.")
    else:
        # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
        if escolha.lower() in ["tudo", "todos", "all"]:
            indices = list(range(1, len(noticias) + 1))
        elif escolha:
            indices = []
            for valor in escolha.split(","):
                valor = valor.strip()
                if "-" in valor:
                    # Tratar intervalo (ex: 1-48)
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
                        if num > 0:  # Ignorar números negativos ou zero
                            indices.append(num)
                    except ValueError:
                        print(f"Opção ignorada: {valor}")
        else:
            indices = []
        
        # Remover duplicados e ordenar
        indices = sorted(set(indices))
        
        for indice in indices:
            try:
                noticia = noticias[indice - 1]
                adicionar_link(noticia.url, "")
            except (ValueError, IndexError):
                print(f"Opção ignorada: {indice}")
    
    # Voltar ao menu principal após a seleção
    return True


def buscar_cbf_interativo() -> bool:
    """Função específica para busca CBF com busca automática das 15 notícias mais recentes."""
    print("\nBuscando em CBF (15 notícias mais recentes)...")
    try:
        from noticias import descobrir_noticias_cbf, filtrar_noticias
        noticias = descobrir_noticias_cbf("recentes")
        noticias_filtradas = filtrar_noticias(noticias)
        # Aplicar limite de 15 após o filtro
        noticias = noticias_filtradas[:7]
    except Exception as erro:
        print(f"  Não foi possível consultar: {erro}")
        return True
    
    if not noticias:
        print("Nenhuma notícia encontrada na CBF.")
        return True
    
    print("\nNotícias encontradas:")
    for indice, noticia in enumerate(noticias, 1):
        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
        print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
    
    escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
    
    # Se o usuário digitar '0', cancela a seleção
    if escolha == "0":
        print("Seleção cancelada.")
    else:
        # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
        if escolha.lower() in ["tudo", "todos", "all"]:
            indices = list(range(1, len(noticias) + 1))
        elif escolha:
            indices = []
            for valor in escolha.split(","):
                valor = valor.strip()
                if "-" in valor:
                    # Tratar intervalo (ex: 1-48)
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
                        if num > 0:  # Ignorar números negativos ou zero
                            indices.append(num)
                    except ValueError:
                        print(f"Opção ignorada: {valor}")
        else:
            indices = []
        
        # Remover duplicados e ordenar
        indices = sorted(set(indices))
        
        for indice in indices:
            try:
                noticia = noticias[indice - 1]
                adicionar_link(noticia.url, "")
            except (ValueError, IndexError):
                print(f"Opção ignorada: {indice}")
    
    # Voltar ao menu principal após a seleção
    return True


def buscar_ge_interativo() -> bool:
    """Função específica para busca GE Grêmio com busca automática das 10 notícias mais recentes."""
    print("\nBuscando em GE Grêmio (10 notícias mais recentes)...")
    try:
        from noticias import descobrir_noticias_ge_gremio, filtrar_noticias
        noticias = descobrir_noticias_ge_gremio("recentes")
        noticias_filtradas = filtrar_noticias(noticias)
        noticias = noticias_filtradas[:5]
    except Exception as erro:
        print(f"  Não foi possível consultar: {erro}")
        return True
    
    if not noticias:
        print("Nenhuma notícia encontrada no GE Grêmio.")
        return True
    
    print("\nNotícias encontradas:")
    for indice, noticia in enumerate(noticias, 1):
        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
        print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
    
    escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
    
    # Se o usuário digitar '0', cancela a seleção
    if escolha == "0":
        print("Seleção cancelada.")
    else:
        # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
        if escolha.lower() in ["tudo", "todos", "all"]:
            indices = list(range(1, len(noticias) + 1))
        elif escolha:
            indices = []
            for valor in escolha.split(","):
                valor = valor.strip()
                if "-" in valor:
                    # Tratar intervalo (ex: 1-48)
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
                        if num > 0:  # Ignorar números negativos ou zero
                            indices.append(num)
                    except ValueError:
                        print(f"Opção ignorada: {valor}")
        else:
            indices = []
        
        # Remover duplicados e ordenar
        indices = sorted(set(indices))
        
        for indice in indices:
            try:
                noticia = noticias[indice - 1]
                adicionar_link(noticia.url, "")
            except (ValueError, IndexError):
                print(f"Opção ignorada: {indice}")
    
    # Voltar ao menu principal após a seleção
    return True


def buscar_gzh_interativo(dia: str) -> bool:
    """Função específica para busca GZH com menu interativo para novas buscas."""
    driver_gzh = None
    
    try:
        while True:
            print(f"\nBuscando em GZH (período: {dia})...")
            try:
                noticias, driver_gzh = descobrir_noticias("https://gauchazh.clicrbs.com.br/esportes/gremio/ultimas-noticias/", "gauchazh.clicrbs.com.br", "GZH", dia, driver_gzh)
            except Exception as erro:
                print(f"  Não foi possível consultar: {erro}")
                if driver_gzh:
                    try:
                        driver_gzh.quit()
                    except:
                        pass
                return True
            
            if not noticias:
                print("Nenhuma notícia encontrada no GZH.")
                if driver_gzh:
                    try:
                        driver_gzh.quit()
                    except:
                        pass
                return True
            
            print("\nNotícias encontradas:")
            for indice, noticia in enumerate(noticias, 1):
                momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
                print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
            
            escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
            
            # Se o usuário digitar '0', cancela a seleção
            if escolha == "0":
                print("Seleção cancelada.")
            else:
                # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
                if escolha.lower() in ["tudo", "todos", "all"]:
                    indices = list(range(1, len(noticias) + 1))
                elif escolha:
                    indices = []
                    for valor in escolha.split(","):
                        valor = valor.strip()
                        if "-" in valor:
                            # Tratar intervalo (ex: 1-48)
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
                                if num > 0:  # Ignorar números negativos ou zero
                                    indices.append(num)
                            except ValueError:
                                print(f"Opção ignorada: {valor}")
                else:
                    indices = []
                
                # Remover duplicados e ordenar
                indices = sorted(set(indices))
                
                for indice in indices:
                    try:
                        noticia = noticias[indice - 1]
                        adicionar_link(noticia.url, "")
                    except (ValueError, IndexError):
                        print(f"Opção ignorada: {indice}")
            
            # Fechar o driver do Selenium após a busca
            if driver_gzh:
                try:
                    driver_gzh.quit()
                except:
                    pass
            
            # Voltar ao menu principal após a seleção
            return True
                
    finally:
        # Garantir que o driver seja fechado
        if driver_gzh:
            try:
                driver_gzh.quit()
            except:
                pass
    
    return True


def buscar_noticias() -> bool:
    fontes = escolher_fontes()
    if not fontes:
        print("Nenhuma fonte selecionada.")
        return True
    
    # Verificar se apenas GZH foi selecionado
    if len(fontes) == 1 and fontes[0] == "gzh":
        # Usar sempre "hoje" para GZH sem perguntar período
        dia = "hoje"
        print("Período: hoje")
        return buscar_gzh_interativo(dia)
    
    # Verificar se apenas Gremio Oficial foi selecionado
    if len(fontes) == 1 and fontes[0] == "gremio":
        # Usar busca automática das 10 notícias mais recentes
        return buscar_gremio_interativo()
    
    # Verificar se apenas GE Grêmio foi selecionado
    if len(fontes) == 1 and fontes[0] == "ge":
        # Usar busca automática das 10 notícias mais recentes
        return buscar_ge_interativo()
    
    # Verificar se apenas GE Seleção foi selecionado
    if len(fontes) == 1 and fontes[0] == "ge_selecao":
        # Usar busca automática das 10 notícias mais recentes
        return buscar_ge_selecao_interativo()
    
    # Verificar se apenas FGF foi selecionado
    if len(fontes) == 1 and fontes[0] == "fgf":
        # Usar busca automática das 10 notícias mais recentes
        return buscar_fgf_interativo()
    
    # Verificar se apenas CBF foi selecionado
    if len(fontes) == 1 and fontes[0] == "cbf":
        # Usar busca automática das 15 notícias mais recentes
        return buscar_cbf_interativo()
    
    # Verificar se apenas CONMEBOL foi selecionado
    if len(fontes) == 1 and fontes[0] == "conmebol":
        # Usar busca automática das 5 notícias mais recentes
        return buscar_conmebol_interativo()
    
    # Verificar se apenas Portal do Gremista foi selecionado
    if len(fontes) == 1 and fontes[0] == "portaldogremista":
        # Usar busca automática das 20 notícias mais recentes
        return buscar_portaldogremista_interativo()
    
    # Para múltiplas fontes, usar "recentes" para as que têm suporte, "ambos" para as demais
    print("Buscando notícias das fontes selecionadas...")
    encontradas = []
    driver_gzh = None  # Driver do Selenium para GZH
    
    for chave in fontes:
        fonte = FONTES[chave]
        print(f"\nBuscando em {fonte.nome}...")
        try:
            # Usar "recentes" para fontes que têm suporte
            if chave in ["gremio", "ge", "ge_selecao", "fgf", "cbf", "conmebol", "portaldogremista"]:
                noticias, driver = descobrir_noticias(fonte.url, fonte.dominio, fonte.nome, "recentes", driver_gzh)
            elif chave == "gzh":
                noticias, driver = descobrir_noticias(fonte.url, fonte.dominio, fonte.nome, "hoje", driver_gzh)
            else:
                noticias, driver = descobrir_noticias(fonte.url, fonte.dominio, fonte.nome, "ambos", driver_gzh)
            encontradas.extend(noticias)
            # Guardar o driver GZH para reutilização
            if driver and fonte.dominio == "gauchazh.clicrbs.com.br":
                driver_gzh = driver
        except Exception as erro:
            print(f"  Não foi possível consultar: {erro}")
    
    # Fechar o driver GZH se existir e não for mais necessário
    if driver_gzh:
        try:
            driver_gzh.quit()
        except:
            pass
    
    if not encontradas:
        print("Nenhuma notícia com data reconhecida. Você pode colar os links manualmente.")
        return True
    print("\nNotícias encontradas:")
    for indice, noticia in enumerate(encontradas, 1):
        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
        print(f"  {indice}. [{noticia.origem} — {momento}] {noticia.titulo}")
    escolha = input("Quais deseja adicionar? (0 para cancelar): ").strip()
    
    # Se o usuário digitar '0', cancela a seleção
    if escolha == "0":
        print("Seleção cancelada.")
        return True
    
    # Se o usuário digitar 'tudo', 'todos' ou 'all', seleciona todas
    if escolha.lower() in ["tudo", "todos", "all"]:
        indices = list(range(1, len(encontradas) + 1))
    elif escolha:
        indices = []
        for valor in escolha.split(","):
            valor = valor.strip()
            if "-" in valor:
                # Tratar intervalo (ex: 1-48)
                try:
                    inicio, fim = valor.split("-")
                    for i in range(int(inicio.strip()), int(fim.strip()) + 1):
                        if 1 <= i <= len(encontradas):
                            indices.append(i)
                except (ValueError, IndexError):
                    print(f"Intervalo inválido: {valor}")
            else:
                try:
                    num = int(valor)
                    if num > 0:  # Ignorar números negativos ou zero
                        indices.append(num)
                except ValueError:
                    print(f"Opção ignorada: {valor}")
    else:
        indices = []
    
    # Remover duplicados e ordenar
    indices = sorted(set(indices))
    
    for indice in indices:
        try:
            noticia = encontradas[indice - 1]
            adicionar_link(noticia.url, "")
        except (ValueError, IndexError):
            print(f"Opção ignorada: {indice}")
    
    # Se foram adicionadas notícias, oferecer opções de revisão e exportação
    if selecionadas:
        print(f"\n{len(selecionadas)} matéria(s) selecionada(s).")
        menu_pos_selecao()
    
    return True


def colar_links() -> None:
    print("\nCole um link por vez. Pressione Enter vazio para voltar ao menu.")
    while True:
        url = input("Link: ").strip()
        if not url:
            return
        instrucao = input("Instrução editorial opcional: ")
        adicionar_link(url, instrucao)


def revisar() -> None:
    if not selecionadas:
        print("\nSua seleção está vazia.")
        return False
    print("\nLinks selecionados:")
    for indice, (url, instrucao) in enumerate(selecionadas, 1):
        complemento = f" — {instrucao}" if instrucao else ""
        print(f"  {indice}. {url}{complemento}")
    remover = input("Digite um número para remover ou Enter para manter tudo: ").strip()
    if remover:
        try:
            removido = selecionadas.pop(int(remover) - 1)
            print(f"Removido: {removido[0]}")
            return True
        except (ValueError, IndexError):
            print("Número inválido.")
    return False


def gerar_pdf(data_coleta: str = "") -> None:
    """Gera PDF com as notícias selecionadas."""
    if not REPORTLAB_AVAILABLE:
        print("  reportlab não está instalado. Instale com: pip install reportlab")
        return
    
    if not selecionadas:
        print("  Nenhuma matéria selecionada para PDF.")
        return
    
    pasta = RAIZ / "saidas"
    pasta.mkdir(exist_ok=True)
    
    # Nome do arquivo PDF com data
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    destino_pdf = pasta / f"noticias_gremio_selecao_{timestamp}.pdf"
    
    # Criar documento PDF
    doc = SimpleDocTemplate(str(destino_pdf), pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#003366'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor('#003366'),
        spaceAfter=10,
        spaceBefore=20
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=14
    )
    info_style = ParagraphStyle(
        'CustomInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#666666'),
        spaceAfter=5
    )
    
    story = []
    
    # Título principal
    data_formatada = data_coleta if data_coleta else datetime.now().strftime("%d/%m/%Y")
    story.append(Paragraph("Notícias do Grêmio e Seleção", title_style))
    story.append(Paragraph(f"Data: {data_formatada}", subtitle_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Processar cada matéria
    for indice, (url, instrucao) in enumerate(selecionadas, 1):
        print(f"  Processando matéria {indice}/{len(selecionadas)} para PDF...")
        try:
            titulo, conteudo, data = extrair_materia(url)
            
            # Título da matéria
            story.append(Paragraph(f"Matéria {indice}", heading_style))
            story.append(Paragraph(titulo, heading_style))
            
            # Informações da matéria
            data_texto = data.strftime("%d/%m/%Y %H:%M") if data else "Data não identificada"
            story.append(Paragraph(f"<b>Data:</b> {data_texto}", info_style))
            story.append(Paragraph(f"<b>Link:</b> {url}", info_style))
            
            if instrucao:
                story.append(Paragraph(f"<b>Orientação:</b> {instrucao}", info_style))
            
            story.append(Spacer(1, 0.3*cm))
            
            # Conteúdo da matéria
            # Tratar quebras de linha e caracteres especiais
            conteudo_formatado = conteudo.replace('\n', '<br/>')
            story.append(Paragraph(conteudo_formatado, normal_style))
            
            # Separador entre matérias
            if indice < len(selecionadas):
                story.append(Spacer(1, 1*cm))
                story.append(Paragraph("=" * 80, info_style))
                story.append(Spacer(1, 1*cm))
                
        except Exception as erro:
            story.append(Paragraph(f"Matéria {indice}", heading_style))
            story.append(Paragraph(f"<b>Erro ao processar:</b> {erro}", info_style))
            story.append(Paragraph(f"<b>Link:</b> {url}", info_style))
            story.append(Spacer(1, 1*cm))
    
    # Construir PDF
    try:
        doc.build(story)
        print(f"  PDF criado: {destino_pdf}")
    except Exception as e:
        print(f"  Erro ao criar PDF: {e}")


def gerar() -> None:
    if not selecionadas:
        print("Adicione ao menos um link antes de exportar.")
        return
    
    # Usar data atual automaticamente
    data_coleta = ""
    
    blocos = [
        "INSTRUÇÃO SUGERIDA PARA O CHATGPT\n"
        "Com base nas matérias abaixo, crie posts para redes sociais."
        "Use apenas os fatos informados, linguagem envolvente e 2 a 5 emojis.\n"
    ]
    for indice, (url, instrucao) in enumerate(selecionadas, 1):
        print(f"Processando {indice}/{len(selecionadas)}...")
        try:
            titulo, conteudo, data = extrair_materia(url)
            if len(conteudo) < 200:
                raise ValueError("texto insuficiente extraído da matéria")
            data_texto = data.strftime("%d/%m/%Y %H:%M") if data else "não identificada"
            orientacao = f"\nORIENTAÇÃO: {instrucao}" if instrucao else ""
            blocos.append(
                f"MATÉRIA {indice}\n\nTÍTULO: {titulo}\nDATA: {data_texto}\nLINK: {url}"
                f"{orientacao}\n\nTEXTO COMPLETO:\n{conteudo}"
            )
        except Exception as erro:
            blocos.append(f"MATÉRIA {indice}\n\n[ERRO ao processar {url}: {erro}]")
    pasta = RAIZ / "saidas"
    pasta.mkdir(exist_ok=True)
    destino = pasta / f"materias_{datetime.now():%Y-%m-%d_%H%M}.txt"
    destino.write_text("\n\n".join(blocos) + "\n", encoding="utf-8")
    print(f"\nTXT criado: {destino}")
    
    # Gerar PDF
    print("Gerando PDF...")
    gerar_pdf(data_coleta)
    
    # Limpar seleção após exportação
    selecionadas.clear()
    print("Seleção limpa após exportação.")


def menu_pos_selecao() -> None:
    """Menu apresentado após adicionar links manualmente."""
    while True:
        print("\n" + "-" * 45)
        print(" OPÇÕES PARA SELEÇÃO ATUAL")
        print("-" * 45)
        print(f"Links selecionados: {len(selecionadas)}")
        print("1. Revisar ou remover links selecionados")
        print("2. Exportar textos completos em TXT")
        print("0. Voltar ao menu principal")
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            revisar()
        elif opcao == "2":
            gerar()
            if not selecionadas:
                return
        elif opcao == "0":
            return
        else:
            print("Opção inválida.")


def verificar_novidades() -> None:
    """Verifica novidades nos sites desde a última busca."""
    # Sites disponíveis para verificação (apenas sites, não redes sociais)
    sites_disponiveis = [
        ("gremio", "Grêmio Oficial"),
        ("gzh", "GZH"),
        ("ge", "GE Grêmio"),
        ("portaldogremista", "Portal do Gremista"),
        ("cbf", "CBF"),
        ("conmebol", "CONMEBOL"),
        ("ge_selecao", "GE Seleção"),
        ("fgf", "FGF"),
    ]
    
    print("\n" + "=" * 45)
    print(" VERIFICAR NOVIDADES")
    print("=" * 45)
    print("Sites disponíveis:")
    for indice, (chave, nome) in enumerate(sites_disponiveis, 1):
        print(f"  {indice}. {nome}")
    print("  9. Todos os sites")
    print("  0. Voltar")
    
    escolha = input("\nDigite os números: ").strip()
    
    if escolha == "0":
        return
    if escolha == "9":
        sites_escolhidos = [chave for chave, _ in sites_disponiveis]
    else:
        sites_escolhidos = []
        for valor in escolha.split(","):
            valor = valor.strip()
            if "-" in valor:
                try:
                    inicio, fim = valor.split("-")
                    for i in range(int(inicio.strip()), int(fim.strip()) + 1):
                        if 1 <= i <= len(sites_disponiveis):
                            sites_escolhidos.append(sites_disponiveis[i - 1][0])
                except (ValueError, IndexError):
                    print(f"Intervalo inválido: {valor}")
            else:
                try:
                    num = int(valor)
                    if 1 <= num <= len(sites_disponiveis):
                        sites_escolhidos.append(sites_disponiveis[num - 1][0])
                except ValueError:
                    print(f"Opção ignorada: {valor}")
    
    if not sites_escolhidos:
        print("Nenhum site selecionado.")
        return
    
    # Obter gerenciador de histórico
    gerenciador = obter_gerenciador()
    
    # Lista para armazenar todas as novidades encontradas
    todas_novidades = []
    
    for site in sites_escolhidos:
        print(f"\n--- Verificando {FONTES[site].nome} ---")
        
        # Obter URLs vistas anteriormente
        urls_anteriores = gerenciador.obter_urls_anteriores(site)
        ultima_busca = gerenciador.obter_ultima_busca(site)
        
        if ultima_busca:
            from datetime import datetime
            try:
                dt_ultima = datetime.fromisoformat(ultima_busca)
                print(f"Última busca: {dt_ultima.strftime('%d/%m/%Y %H:%M')}")
            except:
                print(f"Última busca: {ultima_busca}")
        else:
            print("Primeira busca - mostrando notícias atuais como novidades")
        
        # Buscar notícias atuais
        try:
            if site == "gremio":
                from noticias import descobrir_noticias_gremio, filtrar_noticias
                noticias_atuais = descobrir_noticias_gremio("recentes")
                noticias_atuais = filtrar_noticias(noticias_atuais)
            elif site == "ge_selecao":
                from noticias import descobrir_noticias_ge_selecao, filtrar_noticias
                noticias_atuais = descobrir_noticias_ge_selecao("recentes")
                noticias_atuais = filtrar_noticias(noticias_atuais)
            elif site == "fgf":
                from noticias import descobrir_noticias_fgf, filtrar_noticias
                noticias_atuais = descobrir_noticias_fgf("recentes")
                noticias_atuais = filtrar_noticias(noticias_atuais)
            else:
                fonte = FONTES[site]
                if site == "gzh":
                    from noticias import descobrir_noticias_gzh_simples
                    noticias_atuais = descobrir_noticias_gzh_simples()
                elif site == "ge":
                    from noticias import descobrir_noticias_ge_gremio, filtrar_noticias
                    noticias_atuais = descobrir_noticias_ge_gremio("recentes")
                    noticias_atuais = filtrar_noticias(noticias_atuais)
                elif site == "cbf":
                    from noticias import descobrir_noticias_cbf, filtrar_noticias
                    noticias_atuais = descobrir_noticias_cbf("recentes")
                    noticias_atuais = filtrar_noticias(noticias_atuais)
                elif site == "conmebol":
                    from noticias import descobrir_noticias_conmebol, filtrar_noticias
                    noticias_atuais = descobrir_noticias_conmebol("recentes")
                    noticias_atuais = filtrar_noticias(noticias_atuais)
                elif site == "portaldogremista":
                    from noticias import descobrir_noticias_portal_gremista, filtrar_noticias
                    noticias_atuais = descobrir_noticias_portal_gremista("recentes")
                    noticias_atuais = filtrar_noticias(noticias_atuais)
                else:
                    noticias_atuais = []
            
            # Detectar novidades
            novidades = detectar_novidades(noticias_atuais, urls_anteriores)
            
            if novidades:
                print(f"✓ {len(novidades)} novidade(s) encontrada(s)")
                todas_novidades.extend(novidades)
            else:
                if urls_anteriores:
                    print("Nenhuma novidade encontrada.")
                    # Mostrar as 3 notícias mais recentes como referência
                    if noticias_atuais:
                        print("  Últimas notícias conhecidas:")
                        for noticia in noticias_atuais[:3]:
                            momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
                            print(f"    - [{momento} - {noticia.origem}] {noticia.titulo}")
                else:
                    print("Nenhuma notícia encontrada no site.")
            
            # Atualizar histórico com as URLs atuais
            urls_atuais = {n.url for n in noticias_atuais}
            gerenciador.atualizar_historico(site, urls_atuais)
            
        except Exception as e:
            print(f"Erro ao verificar {FONTES[site].nome}: {e}")
    
    # Resumo final
    print("\n" + "=" * 45)
    print(" RESUMO DE NOVIDADES")
    print("=" * 45)
    if todas_novidades:
        print(f"Total de novidades: {len(todas_novidades)}")
        print("\nNovidades encontradas:")
        for noticia in todas_novidades:
            momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
            print(f"  - [{momento} - {noticia.origem}] {noticia.titulo}")
    else:
        print("Nenhuma novidade encontrada nos sites selecionados.")
        print("\nÚltimas notícias conhecidas por site:")
        
        # Mostrar as 3 últimas de cada site
        for site in sites_escolhidos:
            try:
                if site == "gremio":
                    from noticias import descobrir_noticias_gremio, filtrar_noticias
                    noticias_site = descobrir_noticias_gremio("recentes")
                    noticias_site = filtrar_noticias(noticias_site)
                elif site == "ge_selecao":
                    from noticias import descobrir_noticias_ge_selecao, filtrar_noticias
                    noticias_site = descobrir_noticias_ge_selecao("recentes")
                    noticias_site = filtrar_noticias(noticias_site)
                elif site == "fgf":
                    from noticias import descobrir_noticias_fgf, filtrar_noticias
                    noticias_site = descobrir_noticias_fgf("recentes")
                    noticias_site = filtrar_noticias(noticias_site)
                elif site == "gzh":
                    from noticias import descobrir_noticias_gzh_simples
                    noticias_site = descobrir_noticias_gzh_simples()
                elif site == "ge":
                    from noticias import descobrir_noticias_ge_gremio, filtrar_noticias
                    noticias_site = descobrir_noticias_ge_gremio("recentes")
                    noticias_site = filtrar_noticias(noticias_site)
                elif site == "cbf":
                    from noticias import descobrir_noticias_cbf, filtrar_noticias
                    noticias_site = descobrir_noticias_cbf("recentes")
                    noticias_site = filtrar_noticias(noticias_site)
                elif site == "conmebol":
                    from noticias import descobrir_noticias_conmebol, filtrar_noticias
                    noticias_site = descobrir_noticias_conmebol("recentes")
                    noticias_site = filtrar_noticias(noticias_site)
                elif site == "portaldogremista":
                    from noticias import descobrir_noticias_portal_gremista, filtrar_noticias
                    noticias_site = descobrir_noticias_portal_gremista("recentes")
                    noticias_site = filtrar_noticias(noticias_site)
                else:
                    noticias_site = []
                
                if noticias_site:
                    print(f"\n{FONTES[site].nome}:")
                    for noticia in noticias_site[:3]:
                        momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
                        print(f"  - [{momento} - {noticia.origem}] {noticia.titulo}")
            except Exception as e:
                print(f"\n{FONTES[site].nome}: Erro ao buscar notícias: {e}")
    
    # Perguntar se deseja gerar PDF
    if todas_novidades:
        # Relatório enviado automaticamente por email
        print("\nRelatório será enviado automaticamente por email (via automação GitHub Actions).")
    else:
        print("Nenhuma novidade encontrada nos sites selecionados.")


def gerar_pdf_novidades(noticias: list) -> str | None:
    """Gera PDF simplificado com título e link das novidades.
    Retorna o caminho do PDF gerado ou None em caso de erro.
    """
    if not REPORTLAB_AVAILABLE:
        print("ReportLab não está instalado. Não é possível gerar PDF.")
        return None
    
    pasta = RAIZ / "saidas"
    pasta.mkdir(exist_ok=True)
    destino_pdf = pasta / f"novidades_{datetime.now():%Y-%m-%d_%H%M}.pdf"
    
    try:
        doc = SimpleDocTemplate(
            str(destino_pdf),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Título principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#1a5490'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        story.append(Paragraph("NOVIDADES - FUTEBOL NOTÍCIAS", title_style))
        story.append(Paragraph(f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Listar novidades
        for indice, noticia in enumerate(noticias, 1):
            momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
            
            # Título da notícia com formato [DATA/HORA - ORIGEM]
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=HexColor('#1a5490'),
                spaceAfter=10
            )
            story.append(Paragraph(f"{indice}. [{momento} - {noticia.origem}] {noticia.titulo}", heading_style))
            
            # Data completa
            data_texto = noticia.data.strftime("%d/%m/%Y %H:%M") if noticia.data else "Data não identificada"
            info_style = ParagraphStyle(
                'CustomInfo',
                parent=styles['Normal'],
                fontSize=10,
                textColor=HexColor('#666666'),
                spaceAfter=5
            )
            story.append(Paragraph(f"Data: {data_texto}", info_style))
            
            # Link
            link_style = ParagraphStyle(
                'CustomLink',
                parent=styles['Normal'],
                fontSize=9,
                textColor=HexColor('#0066cc'),
                spaceAfter=20
            )
            story.append(Paragraph(f"Link: <a href='{noticia.url}'>{noticia.url}</a>", link_style))
            story.append(Spacer(1, 0.3*cm))
        
        # Construir PDF
        doc.build(story)
        print(f"PDF gerado: {destino_pdf}")
        return str(destino_pdf)
        
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return None


def main() -> None:
    while True:
        print("\n" + "=" * 45)
        print(" FUTEBOL NOTÍCIAS — MENU")
        print("=" * 45)
        print("1. Buscar notícias")
        print("2. Colar links")
        print("3. Novidades")
        print("0. Sair")
        opcao = input("\nEscolha uma opção: ").strip()
        if opcao == "1":
            if not buscar_noticias():
                return
        elif opcao == "2":
            colar_links()
            menu_pos_selecao()
        elif opcao == "3":
            verificar_novidades()
        elif opcao == "0":
            print("Até mais!")
            return
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
