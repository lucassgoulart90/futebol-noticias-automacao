"""Sistema de persistência para histórico de buscas de notícias."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict

from fontes import FONTES

RAIZ = Path(__file__).parent
ARQUIVO_HISTORICO = RAIZ / ".historico_buscas.json"


@dataclass
class HistoricoFonte:
    """Representa o histórico de notícias de uma fonte."""
    ultima_busca: str  # ISO format datetime
    urls_vistas: Set[str]


class GerenciadorHistorico:
    """Gerencia o histórico de buscas para detecção de novidades."""
    
    def __init__(self):
        self.historico: Dict[str, HistoricoFonte] = {}
        self._carregar_historico()
    
    def _carregar_historico(self):
        """Carrega o histórico do arquivo JSON."""
        if ARQUIVO_HISTORICO.exists():
            try:
                with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    for chave, valor in dados.items():
                        self.historico[chave] = HistoricoFonte(
                            ultima_busca=valor['ultima_busca'],
                            urls_vistas=set(valor['urls_vistas'])
                        )
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"  Aviso: Erro ao carregar histórico: {e}")
                self.historico = {}
    
    def _salvar_historico(self):
        """Salva o histórico no arquivo JSON."""
        dados = {}
        for chave, valor in self.historico.items():
            dados[chave] = {
                'ultima_busca': valor.ultima_busca,
                'urls_vistas': list(valor.urls_vistas)
            }
        
        try:
            with open(ARQUIVO_HISTORICO, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  Erro ao salvar histórico: {e}")
    
    def obter_urls_anteriores(self, fonte: str) -> Set[str]:
        """Retorna as URLs vistas anteriormente para uma fonte."""
        if fonte in self.historico:
            return self.historico[fonte].urls_vistas
        return set()
    
    def atualizar_historico(self, fonte: str, urls_atuais: Set[str]):
        """Atualiza o histórico com as URLs atuais."""
        agora = datetime.now().isoformat()
        self.historico[fonte] = HistoricoFonte(
            ultima_busca=agora,
            urls_vistas=urls_atuais
        )
        self._salvar_historico()
    
    def obter_ultima_busca(self, fonte: str) -> str | None:
        """Retorna a data/hora da última busca para uma fonte."""
        if fonte in self.historico:
            return self.historico[fonte].ultima_busca
        return None
    
    def limpar_historico(self, fonte: str | None = None):
        """Limpa o histórico de uma fonte específica ou de todas."""
        if fonte:
            if fonte in self.historico:
                del self.historico[fonte]
        else:
            self.historico.clear()
        self._salvar_historico()


# Instância global do gerenciador
_gerenciador_historico = None

def obter_gerenciador() -> GerenciadorHistorico:
    """Retorna a instância singleton do gerenciador de histórico."""
    global _gerenciador_historico
    if _gerenciador_historico is None:
        _gerenciador_historico = GerenciadorHistorico()
    return _gerenciador_historico
