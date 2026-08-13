---
name: passa-skill-de-seguranca
description: Executa auditoria de segurança completa do projeto (pip audit, detecção de secrets, OWASP top 10, relatório)
type: skill
---

# Auditoria de Segurança Completa

## ⚡ Início Rápido

**Para executar a auditoria de segurança completa:**

```bash
python3 security_audit.py
```

Isso executará automaticamente todas as verificações e gerará `security_report.md` na raiz do projeto.

Você foi invocado para executar uma **auditoria de segurança abrangente** do projeto. Siga rigorosamente cada etapa e gere um relatório consolidado ao final.

## Etapas Obrigatórias

### 0. Pré-requisitos (Instalação de Ferramentas)

Instale as ferramentas de auditoria necessárias:

```bash
pip install pip-audit detect-secrets 2>/dev/null || true
```

### 1. Auditoria de Dependências (pip audit)

Primeiro, execute a auditoria de vulnerabilidades conhecidas nas dependências:

```bash
pip-audit --skip-editable
```

Se `pip-audit` não estiver disponível, tente:

```bash
pip audit
```

**Capte:**
- Todas as vulnerabilidades encontradas (ID, pacote, versão afetada, severidade)
- Recomendações de upgrade
- Contexto de cada vulnerabilidade

**Se houver vulnerabilidades críticas**, interrompa e solicite ao usuário se deseja prosseguir.

### 2. Detecção de Secrets em Código

Verifique se há secrets (chaves API, tokens, senhas) expostos no código-fonte:

```bash
pip install detect-secrets 2>/dev/null || true
detect-secrets scan --baseline .secrets.baseline --all-files --force-use-all-plugins
```

Se `detect-secrets` não estiver instalado, use `grep` para padrões comuns:

```bash
grep -r -E '(ANTHROPIC_API_KEY|api[_-]?key|password|secret|token)[\s]*[=:][\s]*["\']' \
  --include="*.py" --include="*.json" --include="*.env*" \
  --exclude-dir=venv --exclude-dir=.git --exclude-dir=node_modules \
  . 2>/dev/null | head -20
```

**Capte:**
- Padrões detectados
- Localizações exatas
- Severidade (crítica se em arquivo verificado no git)

### 3. Validação OWASP Top 10

Inspecione o código quanto às vulnerabilidades mais comuns (OWASP Top 10):

| Verificação | Comando/Análise |
|-------------|-----------------|
| **A01: Injection** | `grep -r "eval\|exec\|subprocess\|os.system" --include="*.py" .` (sem sanitização) |
| **A02: Broken Authentication** | Verificar uso de hardcoded credentials, falta de validação de token |
| **A03: Sensitive Data Exposure** | `grep -r "password\|secret" --include="*.py" .` + análise de criptografia |
| **A04: XML External Entities** | `grep -r "xml\|lxml\|etree" --include="*.py" .` (sem proteção XXE) |
| **A05: Access Control** | Verificar permissões de arquivo, controle de acesso inadequado |
| **A06: Security Misconfiguration** | Análise de env vars, configs padrão, logs expostos |
| **A07: XSS** | Verificar sanitização de entrada em templates/responses (se aplicável) |
| **A08: Insecure Deserialization** | `grep -r "pickle\|json.loads" --include="*.py" .` (sem validação) |
| **A09: Using Components with Known Vulnerabilities** | Resultado do pip audit (etapa 1) |
| **A10: Insufficient Logging & Monitoring** | Verificar presença de logging adequado |

**Para cada categoria identificada:**
- Descreva a vulnerabilidade específica
- Localize exatamente onde ocorre
- Proponha correção imediata

### 4. Geração do Relatório de Segurança

Crie um arquivo `security_report.md` no diretório raiz com a seguinte estrutura:

```markdown
# Relatório de Segurança — [DATA]

## Resumo Executivo

- **Status Geral:** [✅ SEGURO | ⚠️ VULNERABILIDADES BAIXAS | 🚨 VULNERABILIDADES CRÍTICAS]
- **Vulnerabilidades Críticas:** N
- **Vulnerabilidades Altas:** N
- **Vulnerabilidades Médias:** N
- **Secrets Expostos:** S/N
- **Conformidade OWASP:** X/10 categorias

---

## 1. Auditoria de Dependências (pip audit)

### Resultados
[Output do pip audit]

### Ações Recomendadas
- [Lista de pacotes a atualizar]
- [Priorização por severidade]

---

## 2. Detecção de Secrets

### Resultados
[Secrets encontrados ou "Nenhum secret detectado"]

### Arquivos Afetados
- [Se houver]

### Ações Imediatas
- [Se houver secrets: migrar para variáveis de ambiente]

---

## 3. Análise OWASP Top 10

### Vulnerabilidades Encontradas

#### [Categoria OWASP] — [Severidade]
- **Descrição:** ...
- **Localização:** [arquivo:linha]
- **Risco:** ...
- **Remediação:** ...

### Resumo por Categoria
| Categoria | Status |
|-----------|--------|
| A01: Injection | ✅ OK |
| A02: Broken Authentication | ✅ OK |
| ... | ... |

---

## 4. Recomendações Gerais

1. [Recomendação prioritária]
2. [Recomendação importante]
3. [Recomendação de manutenção]

---

## 5. Próximas Ações

- [ ] Resolver vulnerabilidades críticas
- [ ] Configurar CI/CD com `pip audit`
- [ ] Implementar `pre-commit` hooks para detecção de secrets
- [ ] Review mensal de segurança

---

**Relatório Gerado:** [DATA/HORA]
**Responsável:** Claude Code Security Review
```

Salve este arquivo com `Write` em `security_report.md` na raiz do projeto.

## Saída Final

Ao concluir todas as etapas, apresente um resumo:

```
✅ AUDITORIA DE SEGURANÇA CONCLUÍDA

📊 Resultados:
  • Vulnerabilidades críticas: [N]
  • Secrets expostos: [S/N]
  • Conformidade OWASP: [X/10]
  • Dependências auditadas: [N]

📄 Relatório salvo em: security_report.md

🔧 Próximas ações:
  1. [Ação prioritária]
  2. [Ação secundária]
```

## Notas Importantes

- **Objetivo:** Identificar e documentar riscos de segurança, não remediar automaticamente
- **Contexto:** Este é um projeto Python com dependências gerenciadas via `pip`
- **Permissões:** Você tem acesso de leitura ao projeto inteiro
- **Relatório:** Deve ser claro, acionável e salvo na raiz do projeto
