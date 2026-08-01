# GUIA COMPLETO: Automação de Novidades via GitHub Actions

## 📋 Visão Geral
Este guia explica como configurar a automação para verificar novidades nos sites de futebol a cada 30 minutos e enviar o PDF por email automaticamente usando GitHub Actions.

---

## 🚀 PASSO A PASSO COMPLETO

### PASSO 1: Preparar o Repositório GitHub

1. **Criar um repositório no GitHub**
   - Acesse https://github.com e faça login
   - Clique no botão "+" no canto superior direito
   - Selecione "New repository"
   - Nome do repositório: `futebol-noticias-automacao` (ou outro nome de sua preferência)
   - Torne o repositório **Público** (GitHub Actions gratuitos funcionam melhor em repositórios públicos)
   - Clique em "Create repository"

2. **Fazer upload dos arquivos do projeto**
   - No seu computador, vá até a pasta `C:\Users\Win10\Desktop\app`
   - Arraste todos os arquivos para a página do GitHub ou use "uploading an existing file"
   - Certifique-se de incluir:
     - `automacao_novidades.py`
     - `menu.py`
     - `noticias.py`
     - `fontes.py`
     - `config.py`
     - `historico.py`
     - `.env.example`
     - Pasta `.github/workflows/` com o arquivo `novidades_automacao.yml`
     - Pasta `saidas/` (crie se não existir)

---

### PASSO 2: Configurar Credenciais de Email

#### Opção A: Gmail (Recomendada)

1. **Gerar Senha de App do Gmail**
   - Acesse sua conta Google em https://myaccount.google.com/
   - Vá em "Segurança"
   - Ative a "Verificação em duas etapas" (se ainda não tiver)
   - Em "Verificação em duas etapas", procure por "Senhas de app"
   - Clique em "+ Senhas de app"
   - Dê um nome: "Futebol Notícias Automacao"
   - Clique em "Gerar"
   - **Copie a senha gerada** (algo como `abcd efgh ijkl mnop`)
   - Esta senha será usada como `SMTP_PASSWORD`

2. **Configurar variáveis no GitHub**
   - No seu repositório GitHub, vá em "Settings"
   - No menu lateral, clique em "Secrets and variables" → "Actions"
   - Clique em "New repository secret"
   - Adicione os seguintes secrets:

   | Nome do Secret | Valor | Descrição |
   |----------------|-------|-----------|
   | `SMTP_SERVER` | `smtp.gmail.com` | Servidor SMTP do Gmail |
   | `SMTP_PORT` | `587` | Porta SMTP |
   | `SMTP_USER` | `seu_email@gmail.com` | Seu email Gmail |
   | `SMTP_PASSWORD` | `senha_gerada_app` | Senha de App gerada |
   | `EMAIL_FROM` | `seu_email@gmail.com` | Email remetente |
   | `EMAIL_DESTINATARIOS` | `email1@example.com,email2@example.com` | Emails que receberão as novidades (separados por vírgula) |

#### Configurar Múltiplos Destinatários

O sistema suporta múltiplos destinatários de email. Para configurar:

1. **No Secret `EMAIL_DESTINATARIOS`**, separe os emails por vírgula:
   ```
   email1@example.com,email2@example.com,email3@example.com
   ```

2. **Exemplos de configuração:**
   - Um único email: `joao@example.com`
   - Dois emails: `joao@example.com,maria@example.com`
   - Três emails: `joao@example.com,maria@example.com,jose@example.com`
   - Grupo de trabalho: `time1@empresa.com,time2@empresa.com,gerente@empresa.com`

3. **Todos os destinatários receberão:**
   - O mesmo email simultaneamente
   - O mesmo PDF anexado
   - As mesmas novidades

**Nota:** Não há limite técnico para o número de destinatários, mas verifique as políticas do seu provedor de email sobre envio em massa.

#### Opção B: Outlook/Hotmail

1. **Configurar variáveis no GitHub**
   - Mesmo processo acima, mas com estes valores:

   | Nome do Secret | Valor | Descrição |
   |----------------|-------|-----------|
   | `SMTP_SERVER` | `smtp.office365.com` | Servidor SMTP da Microsoft |
   | `SMTP_PORT` | `587` | Porta SMTP |
   | `SMTP_USER` | `seu_email@outlook.com` | Seu email Outlook |
   | `SMTP_PASSWORD` | `sua_senha_normal` | Sua senha normal |
   | `EMAIL_FROM` | `seu_email@outlook.com` | Email remetente |
   | `EMAIL_DESTINATARIOS` | `email1@example.com,email2@example.com` | Emails que receberão as novidades (separados por vírgula) |

---

### PASSO 3: Ativar GitHub Actions

1. **Habilitar Actions no repositório**
   - No seu repositório GitHub, vá em "Settings"
   - No menu lateral, clique em "Actions"
   - Clique em "General"
   - Em "Actions permissions", selecione:
     - "Allow all actions and reusable workflows"
   - Clique em "Save"

2. **Verificar o workflow**
   - No repositório, clique na aba "Actions"
   - Você deve ver o workflow "Verificar Novidades e Enviar Email"
   - Clique no workflow para ver os detalhes

---

### PASSO 4: Testar Manualmente

1. **Executar workflow manualmente**
   - Na aba "Actions", clique no workflow "Verificar Novidades e Enviar Email"
   - Clique no botão "Run workflow" → "Run workflow"
   - Aguarde a execução (pode levar 2-5 minutos)
   - Verifique se houve sucesso

2. **Verificar resultados**
   - Após a execução, você deve receber um email se houver novidades
   - Você também pode ver os logs clicando na execução do workflow

---

### PASSO 5: Ajustar Frequência (Opcional)

O workflow atual está configurado para rodar a cada 30 minutos:

```yaml
schedule:
  - cron: '*/30 * * * *'
```

**Para mudar a frequência, edite o arquivo `.github/workflows/novidades_automacao.yml`:**

| Frequência | Cron Expression |
|------------|-----------------|
| A cada 15 minutos | `*/15 * * * *` |
| A cada 30 minutos | `*/30 * * * *` |
| A cada 1 hora | `0 * * * *` |
| A cada 2 horas | `0 */2 * * *` |
| A cada 6 horas | `0 */6 * * *` |
| Uma vez por dia (às 9h) | `0 9 * * *` |
| Uma vez por dia (às 18h) | `0 18 * * *` |

---

### PASSO 6: Monitoramento e Solução de Problemas

#### Verificar Logs
1. Vá para a aba "Actions" no GitHub
2. Clique na execução mais recente
3. Clique no job "verificar-novidades"
4. Expanda os passos para ver os logs detalhados

#### Problemas Comuns

**Problema: "SMTP authentication failed"**
- Solução: Verifique se `SMTP_USER` e `SMTP_PASSWORD` estão corretos nos Secrets
- Para Gmail: Certifique-se de usar a Senha de App, não a senha normal

**Problema: "Chrome/Selenium error"**
- Solução: O workflow já instala Chrome automaticamente. Se der erro, pode ser temporário.

**Problema: "No email sent"**
- Solução: Verifique se há novidades. O sistema só envia email quando encontra novidades.

**Problema: "Workflow not running"**
- Solução: Verifique se GitHub Actions está habilitado em Settings → Actions

---

### PASSO 7: Personalizações Avançadas (Opcional)

#### Adicionar mais sites
Edite o arquivo `automacao_novidades.py` e adicione mais sites à lista `sites_todos`.

#### Mudar formato do email
Edite a função `enviar_email_com_pdf` no arquivo `automacao_novidades.py`.

#### Adicionar filtros específicos
Edite o arquivo `config.py` para adicionar mais palavras ao filtro `PALAVRAS_EXCLUIDAS`.

#### Configurar diferentes grupos de destinatários
Se você quiser diferentes grupos de destinatários para diferentes ocasiões:

1. Crie múltiplos workflows no GitHub Actions
2. Cada workflow pode ter um Secret diferente para `EMAIL_DESTINATARIOS`
3. Exemplo: `EMAIL_DESTINATARIOS_TRABALHO` e `EMAIL_DESTINATARIOS_PESSOAL`

#### Alterar formato do assunto do email
Edite a função `enviar_email_com_pdf` no arquivo `automacao_novidades.py`:
```python
msg['Subject'] = f"⚽ Novidades Futebol - {datetime.now():%d/%m/%Y %H:%M}"
```

---

## 📁 Estrutura Final do Repositório

```
futebol-noticias-automacao/
├── .github/
│   └── workflows/
│       └── novidades_automacao.yml
├── saidas/
│   └── (PDFs gerados ficam aqui)
├── automacao_novidades.py
├── menu.py
├── noticias.py
├── fontes.py
├── config.py
├── historico.py
├── .env.example
└── GUIA_AUTOMACAO_GITHUB.md
```

---

## 🔒 Segurança

- **Nunca** coloque senhas reais no código
- Sempre use GitHub Secrets para credenciais
- Para Gmail, use Senhas de App, não a senha principal
- Mantenha seu repositório privado se tiver informações sensíveis

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do GitHub Actions
2. Teste o script localmente: `python automacao_novidades.py`
3. Verifique se as credenciais de email estão corretas
4. Confirme que o workflow está habilitado

---

## ✅ Checklist Final

- [ ] Repositório criado no GitHub
- [ ] Arquivos do projeto uploaded
- [ ] GitHub Actions habilitado
- [ ] Secrets configurados (SMTP_USER, SMTP_PASSWORD, etc.)
- [ ] **EMAIL_DESTINATARIOS configurado com todos os emails necessários (separados por vírgula)**
- [ ] Workflow testado manualmente
- [ ] **Email recebido por todos os destinatários configurados**
- [ ] Frequência ajustada (se necessário)
- [ ] Monitoramento configurado

Parabéns! 🎉 Sua automação de novidades está configurada e funcionando!
