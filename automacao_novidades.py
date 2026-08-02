#!/usr/bin/env python3
"""
Script de automação para verificar novidades e enviar email.
Executa a verificação de novidades em todos os sites e envia PDF por email.
"""
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from historico import obter_gerenciador
from fontes import FONTES
from noticias import detectar_novidades


def verificar_todas_novidades():
    """Verifica novidades em todos os sites disponíveis e retorna as 3 últimas de cada."""
    sites_todos = ["gremio", "gzh", "ge", "portaldogremista", "cbf", "conmebol", "ge_selecao", "fgf"]
    
    gerenciador = obter_gerenciador()
    todas_novidades = []
    ultimas_por_site = {}  # Armazena as 3 últimas de cada site
    primeira_execucao = True  # Flag para controlar se é primeira execução
    
    print(f"=== VERIFICANDO NOVIDADES - {datetime.now():%d/%m/%Y %H:%M} ===")
    
    for site in sites_todos:
        print(f"\n--- Verificando {FONTES[site].nome} ---")
        
        # Obter URLs vistas anteriormente
        urls_anteriores = gerenciador.obter_urls_anteriores(site)
        ultima_busca = gerenciador.obter_ultima_busca(site)
        
        if ultima_busca:
            try:
                dt_ultima = datetime.fromisoformat(ultima_busca)
                print(f"Última busca: {dt_ultima.strftime('%d/%m/%Y %H:%M')}")
                primeira_execucao = False  # Se tem histórico, não é primeira execução
            except:
                print(f"Última busca: {ultima_busca}")
        else:
            print("Primeira busca neste site")
        
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
            elif site == "gzh":
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
            from noticias import detectar_novidades
            novidades = detectar_novidades(noticias_atuais, urls_anteriores)
            
            # Guardar as 3 últimas do site (seja novidade ou não)
            ultimas_por_site[site] = noticias_atuais[:3]
            
            if novidades:
                print(f"✓ {len(novidades)} novidade(s) encontrada(s)")
                todas_novidades.extend(novidades)
            else:
                if urls_anteriores:
                    print("Nenhuma novidade encontrada.")
                else:
                    print("Nenhuma notícia encontrada no site.")
            
            # Atualizar histórico com as URLs atuais
            urls_atuais = {n.url for n in noticias_atuais}
            gerenciador.atualizar_historico(site, urls_atuais)
            
        except Exception as e:
            print(f"Erro ao verificar {FONTES[site].nome}: {e}")
    
    print(f"\n=== RESUMO ===")
    if primeira_execucao:
        print("Primeira execução do sistema. Histórico criado.")
        print("Próxima execução mostrará apenas novidades reais.")
        todas_novidades = []  # Não mostrar novidades na primeira execução
    else:
        print(f"Total de novidades: {len(todas_novidades)}")
    
    return todas_novidades, ultimas_por_site, primeira_execucao


def enviar_email_relatorio(novidades, ultimas_por_site, destinatarios, primeira_execucao=False):
    """Envia email com relatório de novidades e últimas 3 de cada site no corpo do email."""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configurações do email (do arquivo .env)
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    email_from = os.getenv('EMAIL_FROM', smtp_user)
    
    if not smtp_user or not smtp_password:
        print("ERRO: SMTP_USER e SMTP_PASSWORD não configurados no arquivo .env")
        return False
    
    # Converter string de destinatários em lista
    if isinstance(destinatarios, str):
        destinatarios = [email.strip() for email in destinatarios.split(',')]
    
    print(f"Enviando email para {len(destinatarios)} destinatário(s): {', '.join(destinatarios)}")
    
    try:
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = ', '.join(destinatarios)
        
        # Usar fuso correto para o horário
        from zoneinfo import ZoneInfo
        fuso_sp = ZoneInfo("America/Sao_Paulo")
        agora_sp = datetime.now(fuso_sp)
        
        msg['Subject'] = f"⚽ Novidades Futebol - {agora_sp:%d/%m/%Y %H:%M}"
        
        # Construir corpo do email
        corpo = f"""
🏆 RELATÓRIO DE NOVIDADES - FUTEBOL
📅 Verificado em: {agora_sp:%d/%m/%Y às %H:%M} (Horário de São Paulo)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESUMO
"""
        
        if primeira_execucao:
            corpo += f"""
📭 Primeira execução do sistema
Histórico criado. Próxima execução mostrará apenas novidades reais.

"""
        else:
            corpo += f"""
{"✅" if novidades else "📭"} Novidades encontradas: {len(novidades)}

"""
        
        # Adicionar novidades se houver
        if novidades:
            corpo += f"""
🔔 NOVIDADES ENCONTRADAS:

"""
            for noticia in novidades:
                momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
                corpo += f"• [{momento} - {noticia.origem}] {noticia.titulo}\n"
                corpo += f"  Link: {noticia.url}\n\n"
        
        # Adicionar as 3 últimas de cada site
        corpo += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📰 ÚLTIMAS 3 NOTÍCIAS POR SITE:

"""
        for site, noticias in ultimas_por_site.items():
            corpo += f"\n📍 {FONTES[site].nome}:\n"
            for noticia in noticias:
                momento = noticia.data.strftime("%d/%m %H:%M") if noticia.data else "sem data"
                corpo += f"  • [{momento}] {noticia.titulo}\n"
                corpo += f"    {noticia.url}\n"
        
        corpo += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Próxima verificação: em 30 minutos
⏰ Horário de funcionamento: 7h30 às 23h30

---
Gerado automaticamente pelo sistema Futebol Notícias
"""
        
        msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
        
        # Enviar email para todos os destinatários
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"✓ Email enviado com sucesso para {len(destinatarios)} destinatário(s)")
        return True
        
    except Exception as e:
        print(f"✗ Erro ao enviar email: {e}")
        return False


def main():
    """Função principal da automação."""
    # Verificar horário permitido (7h30 às 23h30) - usando fuso de São Paulo
    from zoneinfo import ZoneInfo
    fuso_sp = ZoneInfo("America/Sao_Paulo")
    agora_sp = datetime.now(fuso_sp)
    
    hora_atual = agora_sp.hour
    minuto_atual = agora_sp.minute
    
    # Converter para minutos totais
    minutos_totais = hora_atual * 60 + minuto_atual
    inicio_permitido = 7 * 60 + 30  # 7h30 = 450 minutos
    fim_permitido = 23 * 60 + 30    # 23h30 = 1410 minutos
    
    if minutos_totais < inicio_permitido or minutos_totais > fim_permitido:
        print(f"Fora do horário permitido (7h30-23h30). Horário atual SP: {hora_atual:02d}:{minuto_atual:02d}")
        print("Automação não será executada.")
        return 0
    
    print(f"Horário permitido: {hora_atual:02d}:{minuto_atual:02d} (dentro do horário 7h30-23h30 SP)")
    
    # Configurações
    destinatarios_email = os.getenv('EMAIL_DESTINATARIOS', 'seu-email@example.com')
    
    # Verificar novidades
    novidades, ultimas_por_site, primeira_execucao = verificar_todas_novidades()
    
    # Enviar email sempre (com ou sem novidades)
    print("\nEnviando relatório por email...")
    sucesso = enviar_email_relatorio(novidades, ultimas_por_site, destinatarios_email, primeira_execucao)
    
    if sucesso:
        print("✓ Processo concluído com sucesso!")
        return 0
    else:
        print("✗ Erro ao enviar email")
        return 1


if __name__ == "__main__":
    sys.exit(main())
