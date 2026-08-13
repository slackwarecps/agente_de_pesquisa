# Skill `/passa-skill-de-seguranca` — Guia de Implementação

## 📋 O que foi criado

Uma skill completa de auditoria de segurança a nível de projeto que:

✅ **Executa 4 etapas de auditoria:**
1. **pip audit** — Detecta vulnerabilidades em dependências Python
2. **detect-secrets** — Varre código para secrets/credenciais expostas
3. **OWASP Top 10** — Valida contra as 10 vulnerabilidades web mais críticas
4. **Relatório** — Gera `security_report.md` consolidado com todos os achados

---

## 📁 Arquivos Criados/Modificados

### ✨ Novos Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `.claude/agents/passa-skill-de-seguranca.md` | Definição da skill em Markdown |
| `.claude/agents/README.md` | Documentação das skills do projeto |
| `security_audit.py` | Script Python que orquestra toda a auditoria |

### 🔧 Modificados

| Arquivo | Alteração |
|---------|-----------|
| `.claude/settings.local.json` | Adicionadas permissões para `pip-audit`, `pip install`, `python3 security_audit.py` |
| `.gitignore` | Adicionado `security_report.md` à lista de exclusão |

---

## 🚀 Como Usar

### Opção 1: Invocar via Skill (Recomendado)

```bash
/passa-skill-de-seguranca
```

Isso acionará a skill conforme definido em `.claude/agents/passa-skill-de-seguranca.md`.

### Opção 2: Executar Script Diretamente

```bash
source venv/bin/activate
python3 security_audit.py
```

---

## 📊 Exemplo de Saída

```
============================================================
   AUDITORIA DE SEGURANÇA COMPLETA
============================================================

📦 Verificando ferramentas de auditoria...
✅ Todas as ferramentas instaladas

🔍 Executando auditoria de dependências (pip-audit)...
✅ Nenhuma vulnerabilidade encontrada

🔐 Verificando secrets em código...
✅ Nenhum secret detectado

⚠️  Analisando OWASP Top 10...
✅ Nenhuma vulnerabilidade óbvia OWASP detectada

📄 Gerando relatório consolidado...

============================================================
   ✅ AUDITORIA CONCLUÍDA
============================================================

📊 Resultados:
  • Vulnerabilidades de dependências: 0
  • Secrets expostos: 0
  • Achados OWASP: 0

📄 Relatório salvo em: security_report.md
```

---

## 📄 Relatório Gerado

O arquivo `security_report.md` contém:

```markdown
# Relatório de Segurança — [data]

## Resumo Executivo
- Status Geral
- Contagem de vulnerabilidades por tipo
- Conformidade OWASP

## 1. Auditoria de Dependências
- Listagem de vulnerabilidades
- Recomendações de upgrade

## 2. Detecção de Secrets
- Secrets encontrados
- Ações imediatas necessárias

## 3. Análise OWASP Top 10
- Categorias verificadas
- Problemas detectados
- Detalhes de vulnerabilidades

## 4. Recomendações Gerais
- Priorização de ações
- Próximos passos
```

---

## 🔐 Ferramentas Utilizadas

| Ferramenta | Instalação | Função |
|-----------|-----------|--------|
| `pip-audit` | `pip install pip-audit` | Auditoria de dependências Python |
| `detect-secrets` | `pip install detect-secrets` | Detecção de secrets em código |
| `grep` | Sistema | Busca de padrões OWASP |
| `python3` | Sistema | Orquestração via script |

**Nota:** Todas as ferramentas são instaladas automaticamente pelo script se não existirem.

---

## ⚙️ Configurações

### Permissões Adicionadas em `.claude/settings.local.json`

```json
"Bash(pip audit *)",
"Bash(pip install detect-secrets *)",
"Bash(detect-secrets *)",
"Bash(grep -r *)",
"Write(security_report.md)",
"Bash(python3 security_audit.py *)",
"Bash(pip-audit *)"
```

### Variáveis de Ambiente

Nenhuma variável especial necessária. O script usa:
- `ANTHROPIC_API_KEY` (se existir em `.env` — será detectado como potencial secret)

---

## 🎯 Casos de Uso

✅ **Use quando:**
- Antes de fazer release/deploy
- Após atualizar dependências
- Como parte de CI/CD automático
- Auditorias de segurança periódicas
- Onboarding de novos contribuidores

---

## 📝 Notas Importantes

1. **Falsos Positivos:** O `detect-secrets` pode detectar padrões em comentários, strings de exemplo, etc. Review manual é recomendado.

2. **Secrets Reais:** Se a ferramenta detectar secrets reais:
   - Rotacione imediatamente as credenciais
   - Remova do código
   - Migre para variáveis de ambiente

3. **Exclusões:** O script ignora:
   - Diretório `venv/`
   - Diretório `.git/`
   - Arquivos `.pyc` e `__pycache__/`

4. **Atualização Contínua:** Sempre mantenha `pip-audit` e `detect-secrets` atualizados:
   ```bash
   pip install --upgrade pip-audit detect-secrets
   ```

---

## ✅ Checklist de Implementação

- [x] Skill criada em `.claude/agents/passa-skill-de-seguranca.md`
- [x] Script Python `security_audit.py` implementado
- [x] Permissões configuradas em `.claude/settings.local.json`
- [x] Ferramentas (pip-audit, detect-secrets) instaláveis
- [x] Relatório gerado e salvo corretamente
- [x] `.gitignore` atualizado
- [x] Documentação completa

---

## 🚀 Próximos Passos Sugeridos

1. **CI/CD Integration:**
   ```yaml
   # .github/workflows/security-audit.yml
   - name: Security Audit
     run: python3 security_audit.py
   ```

2. **Pre-commit Hooks:**
   ```yaml
   # .pre-commit-config.yaml
   - repo: https://github.com/Yelp/detect-secrets
     rev: v1.5.0
     hooks:
       - id: detect-secrets
   ```

3. **Agendamento Periódico:**
   - Executar skill `/passa-skill-de-seguranca` mensalmente
   - Review automático de vulnerabilidades novas

---

**Data de Implementação:** 2026-08-13
**Responsável:** Claude Code
**Status:** ✅ Pronto para Uso
