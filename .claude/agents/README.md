# Skills do Projeto

Neste diretório estão definidas as skills (tarefas especializadas) do projeto `agente_de_pesquisa`.

## Skills Disponíveis

### `/passa-skill-de-seguranca`

**Descrição:** Executa auditoria de segurança completa do projeto

**O que faz:**
1. ✅ **pip audit** — Detecta vulnerabilidades conhecidas em dependências Python
2. 🔐 **Detecção de Secrets** — Varre o código em busca de credenciais expostas (chaves API, tokens, senhas)
3. ⚠️ **Validação OWASP Top 10** — Inspeciona código quanto às 10 vulnerabilidades web mais críticas
4. 📄 **Geração de Relatório** — Cria `security_report.md` com todos os achados e recomendações

**Como usar:**

```bash
# No terminal ou prompt do Claude Code
/passa-skill-de-seguranca
```

**Saída esperada:**
- Relatório consolidado no console
- Arquivo `security_report.md` na raiz do projeto com análise detalhada

**Quando usar:**
- Antes de releases/deploys
- Após atualizar dependências
- Como parte de CI/CD
- Auditorias de segurança periódicas

**Exemplo de resultado:**
```
✅ AUDITORIA DE SEGURANÇA CONCLUÍDA

📊 Resultados:
  • Vulnerabilidades críticas: 0
  • Secrets expostos: Não
  • Conformidade OWASP: 10/10
  • Dependências auditadas: 15

📄 Relatório salvo em: security_report.md
```

---

## Estrutura de Skills

Cada skill é um arquivo Markdown (`.md`) com frontmatter YAML:

```yaml
---
name: nome-da-skill
description: Descrição breve
type: project  # ou global/org
---

# Conteúdo em Markdown com instruções
```

## Permissões Necessárias

As skills deste projeto têm permissões para executar:
- `pip audit` — auditoria de dependências
- `detect-secrets` — detecção de secrets
- `grep` — busca em arquivos
- `Write(security_report.md)` — escrita de relatórios

Todas as permissões estão configuradas em `.claude/settings.local.json`.
