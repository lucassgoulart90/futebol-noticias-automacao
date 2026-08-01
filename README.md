# Futebol Notícias → posts para redes sociais

Projeto Python para buscar notícias publicadas **hoje ou ontem** e exportar o texto completo de cada matéria em um TXT, pronto para ser usado manualmente no ChatGPT.

## Preparação no VS Code

No terminal integrado, abra esta pasta e execute:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Fluxo recomendado

### Opção mais simples: menu interativo

```powershell
python menu.py
```

No menu, aperte `1` para buscar notícias, `2` para colar links manualmente, `3` para revisar sua seleção e `4` para exportar um TXT. Nenhuma chave de API ou pagamento é necessário.

### Opção por comandos

1. Descubra os links de hoje e ontem em uma ou mais fontes:

```powershell
python main.py descobrir --fontes ge,gremio,portaldogremista --dia ambos
```

2. Copie os links que interessam para `links.txt`, um por linha. Opcionalmente, escreva uma instrução após ` | `:

```text
https://portal.gremio.net/noticias/exemplo | destaque a venda de ingressos
https://ge.globo.com/rs/futebol/times/gremio/noticia/exemplo.ghtml
```

3. Exporte o conteúdo completo das matérias:

```powershell
python main.py gerar --arquivo links.txt
```

O resultado será salvo em `saidas/materias_YYYY-MM-DD_HHMM.txt`, com título, data, link e texto completo de cada matéria. O início do arquivo já traz uma instrução sugerida para você colar no ChatGPT junto à matéria.

## Outras formas de uso

Gerar diretamente com URLs:

```powershell
python main.py gerar --urls "https://site.com/noticia-1" "https://site.com/noticia-2"
```

Descobrir apenas notícias de ontem em todas as fontes:

```powershell
python main.py descobrir --dia ontem
```

Fontes disponíveis: `gremio`, `ge`, `cbf`, `conmebol`, `fgf`, `portaldogremista`.

## Observações

- A busca trata textos como `há 11 horas`, `ontem`, `hoje` e datas explícitas no fuso de São Paulo.
- Os sites podem mudar o HTML ou limitar acessos automatizados. Quando isso ocorrer, use os links manualmente no `links.txt`: a extração individual continua sendo tentada.
- Confira a matéria e o texto gerado antes de publicar, principalmente informações de horário, escalação, resultado e valores.

## Personalização: Adicionar palavras-chave para filtro de notícias

O sistema possui um filtro automático que exclui notícias que contenham determinadas palavras no título. Para adicionar ou remover palavras do filtro:

### Como adicionar palavras ao filtro:

1. Abra o arquivo `config.py`
2. Encontre a lista `PALAVRAS_EXCLUIDAS`
3. Adicione novas palavras entre aspas, separadas por vírgula

### Exemplo:
```python
PALAVRAS_EXCLUIDAS = [
    "feminino",
    "feminina",
    "sub-20 feminino",
    "sub-17 feminino",
    "gurias",
    "guria",
    "nova_palavra_aqui",
    "outra_palavra",
]
```

### Observações:
- O filtro é case-insensitive (não diferencia maiúsculas de minúsculas)
- O filtro verifica se a palavra aparece em qualquer lugar do título (não apenas no início)
- O filtro é aplicado automaticamente em todas as fontes
- Notícias filtradas são mostradas no console com a mensagem "Notícia filtrada (contém palavra excluída)"

## Personalização: Alterar limite de notícias por fonte

Quando você seleciona uma fonte individualmente no menu interativo, o sistema busca automaticamente um número específico de notícias mais recentes. Para alterar esses limites:

### Fontes e seus limites atuais:
- **Grêmio Oficial**: 10 notícias mais recentes
- **GE Grêmio**: 10 notícias mais recentes
- **GE Seleção**: 10 notícias mais recentes  
- **FGF**: 10 notícias mais recentes
- **CBF**: 15 notícias mais recentes
- **CONMEBOL**: 5 notícias mais recentes
- **Portal do Gremista**: 20 notícias mais recentes
- **GZH**: Período "hoje" (mecânica de horário de postagem)

### Como alterar os limites:

1. **Para Grêmio Oficial (10 notícias)**:
   - Abra o arquivo `menu.py`
   - Encontre a função `buscar_gremio_interativo()`
   - Procure pela linha: `noticias = noticias[:10]`
   - Altere o número `10` para o limite desejado

2. **Para GE Grêmio, GE Seleção e FGF (10 notícias)**:
   - Abra o arquivo `menu.py`
   - Encontre as funções `buscar_ge_interativo()`, `buscar_ge_selecao_interativo()` e `buscar_fgf_interativo()`
   - Procure pela linha: `noticias = noticias[:10]`
   - Altere o número `10` para o limite desejado

2. **Para CBF (15 notícias)**:
   - Abra o arquivo `menu.py`
   - Encontre a função `buscar_cbf_interativo()`
   - Procure pela linha: `noticias = noticias[:15]`
   - Altere o número `15` para o limite desejado

3. **Para CONMEBOL (5 notícias)**:
   - Abra o arquivo `menu.py`
   - Encontre a função `buscar_conmebol_interativo()`
   - Procure pela linha: `noticias = noticias[:5]`
   - Altere o número `5` para o limite desejado

4. **Para Portal do Gremista (20 notícias)**:
   - Abra o arquivo `menu.py`
   - Encontre a função `buscar_portaldogremista_interativo()`
   - Procure pela linha: `noticias = noticias[:20]`
   - Altere o número `20` para o limite desejado

3. **Para os extratores (noticias.py)**:
   - Abra o arquivo `noticias.py`
   - Encontre as funções: `descobrir_noticias_gremio()`, `descobrir_noticias_ge_gremio()`, `descobrir_noticias_ge_selecao()`, `descobrir_noticias_fgf()`, `descobrir_noticias_cbf()`, `descobrir_noticias_conmebol()` e `descobrir_noticias_portal_gremista()`
   - Procure pelas linhas que retornam as notícias limitadas:
     - Para Grêmio Oficial: `return [noticia for noticia in noticias if noticia][:10]`
     - Para GE: `return noticias[:10]`
     - Para CBF: `return noticias[:15]`
     - Para CONMEBOL: `return noticias[:5]`
     - Para Portal do Gremista: `return noticias[:20]`
   - Altere os números conforme desejado

### Exemplo:
Para mudar GE Grêmio de 10 para 20 notícias:

1. Em `menu.py`, na função `buscar_ge_interativo()`:
   ```python
   noticias = noticias[:20]  # alterado de [:10] para [:20]
   ```

2. Em `noticias.py`, na função `descobrir_noticias_ge_gremio()`:
   ```python
   return noticias[:20]  # alterado de [:10] para [:20]
   ```

Repita o processo para cada fonte que desejar alterar.
