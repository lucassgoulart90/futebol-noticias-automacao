#!/usr/bin/env python3
"""
Script de automação para verificar novidades e enviar email.
Executa a verificação de novidades em todos os sites e envia PDF por email.
"""
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from fontes import FONTES


def verificar_todas_novidades():
    """Verifica novidades em todos os sites disponíveis e retorna as 3 últimas de cada.
    Mostra notícias das últimas 24 horas como novidades.
    """
    from zoneinfo import ZoneInfo
    fuso_sp = ZoneInfo("America/Sao_Paulo")
    agora_sp = datetime.now(fuso_sp)
    limite_24h = agora_sp - timedelta(hours=24)
    
    sites_todos = ["gremio", "gzh", "ge", "portaldogremista", "cbf", "conmebol", "ge_selecao", "fgf"]
    
    todas_novidades = []
    ultimas_por_site = {}  # Armazena as 3 últimas de cada site
    
    print(f"=== VERIFICANDO NOVIDADES - {agora_sp:%d/%m/%Y %H:%M} ===")
    print(f"Buscando notícias das últimas 24 horas (desde {limite_24h:%d/%m/%Y %H:%M})")
    
    for site in sites_todos:
        print(f"\n--- Verificando {FONTES[site].nome} ---")
        
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
            
            # Filtrar apenas notícias das últimas 24 horas
            novidades_24h = []
            for noticia in noticias_atuais:
                if noticia.data and noticia.data >= limite_24h:
                    novidades_24h.append(noticia)
            
            # Guardar as 3 últimas do site (seja novidade ou não)
            ultimas_por_site[site] = noticias_atuais[:3]
            
            if novidades_24h:
                print(f"✓ {len(novidades_24h)} notícia(s) nas últimas 24h")
                todas_novidades.extend(novidades_24h)
            else:
                print("Nenhuma notícia nas últimas 24h.")
            
        except Exception as e:
            print(f"Erro ao verificar {FONTES[site].nome}: {e}")
    
    print(f"\n=== RESUMO ===")
    print(f"Total de notícias nas últimas 24h: {len(todas_novidades)}")
    
    return todas_novidades, ultimas_por_site


def enviar_email_relatorio(novidades, ultimas_por_site, destinatarios):
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
{"✅" if novidades else "📭"} Notícias nas últimas 24h: {len(novidades)}

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

🔄 Próxima verificação: em 1 hora
⏰ Horário de funcionamento: 8h00 às 23h00 (verifica notícias do período 23h01-7h59)

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
    # Verificar horário permitido (8h00 às 23h00) - usando fuso de São Paulo
    from zoneinfo import ZoneInfo
    fuso_sp = ZoneInfo("America/Sao_Paulo")
    agora_sp = datetime.now(fuso_sp)
    
    hora_atual = agora_sp.hour
    minuto_atual = agora_sp.minute
    
    # Converter para minutos totais
    minutos_totais = hora_atual * 60 + minuto_atual
    inicio_permitido = 8 * 60 + 0  # 8h00 = 480 minutos
    fim_permitido = 23 * 60 + 0    # 23h00 = 1380 minutos
    
    if minutos_totais < inicio_permitido or minutos_totais > fim_permitido:
        print(f"Fora do horário permitido (8h00-23h00). Horário atual SP: {hora_atual:02d}:{minuto_atual:02d}")
        print("Automação não será executada.")
        return 0
    
    print(f"Horário permitido: {hora_atual:02d}:{minuto_atual:02d} (dentro do horário 8h00-23h00 SP)")
    
    # Configurações
    destinatarios_email = os.getenv('EMAIL_DESTINATARIOS', 'seu-email@example.com')
    
    # Verificar novidades
    novidades, ultimas_por_site = verificar_todas_novidades()
    
    # Enviar email sempre (com ou sem novidades)
    print("\nEnviando relatório por email...")
    sucesso = enviar_email_relatorio(novidades, ultimas_por_site, destinatarios_email)
    
    if sucesso:
        print("✓ Processo concluído com sucesso!")
        return 0
    else:
        print("✗ Erro ao enviar email")
        return 1


if __name__ == "__main__":
    sys.exit(main())
