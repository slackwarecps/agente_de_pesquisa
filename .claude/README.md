# Configuração Claude Code — `agente_de_pesquisa`

Este diretório contém as configurações do Claude Code para o projeto.

## 📋 Estrutura

```
.claude/
├── agents/                      # Skills (tarefas especializadas) do projeto
│   ├── passa-skill-de-seguranca.md
│   └── README.md
├── settings.json               # Configurações compartilhadas (se houver)
├── settings.local.json         # ⚠️ LOCAL - Não versionar
├── settings.local.json.example # Template para novos devs
├── SKILL_SETUP.md             # Documentação de skills
└── README.md                   # Este arquivo
```

## 🚀 Primeiros Passos para Novos Devs

### 1. Clonar o Repositório
```bash
git clone <repo-url>
cd agente_de_pesquisa
```

### 2. Configurar Claude Code Local
```bash
# Copiar template de configuração local
cp .claude/settings.local.json.example .claude/settings.local.json
```

### 3. (Opcional) Expandir Permissões
Se precisar de permissões adicionais, edite `.claude/settings.local.json` conforme necessário. O arquivo `.claude/settings.local.json.example` contém um bom ponto de partida.

### 4. Usar as Skills
```bash
# Listar skills disponíveis
/passa-skill-de-seguranca   # Auditoria de segurança completa
```

## 🔐 Permissões

### ✅ Configuradas no Projeto
As permissões essenciais já estão documentadas em `settings.local.json.example`. Incluem:

- Execução de Python e scripts
- Git operations (clone, push, pull, etc)
- GitHub CLI (gh)
- Ferramentas de segurança (pip-audit, detect-secrets)
- Geração de artefatos e relatórios

### ⚠️ Importante
**`settings.local.json` NÃO é versionado** porque pode conter:
- Permissões específicas do seu ambiente
- Tokens ou credenciais locais
- Configurações específicas da máquina

Use `settings.local.json.example` como referência.

## 📚 Skills Disponíveis

### `/passa-skill-de-seguranca`
Auditoria de segurança completa do projeto:
- ✅ pip audit (vulnerabilidades em dependências)
- 🔐 Detecção de secrets
- ⚠️ Validação OWASP Top 10
- 📄 Geração de relatório

**Usar:**
```bash
/passa-skill-de-seguranca
```

**Documentação:** Ver `agents/README.md` e `SKILL_SETUP.md`

## 🔧 Troubleshooting

### "Skill não encontrada"
Verifique se o arquivo `.claude/agents/passa-skill-de-seguranca.md` existe e está bem formatado.

### "Permissão negada"
Você pode precisar adicionar permissões ao `.claude/settings.local.json`. Use `settings.local.json.example` como referência.

### "Ferramentas não encontradas"
Execute uma vez a skill — ela instalará automaticamente as dependências necessárias (pip-audit, detect-secrets).

## 📖 Documentação Completa

- **`agents/README.md`** — Guia detalhado de skills
- **`SKILL_SETUP.md`** — Implementação e próximos passos
- **`agents/passa-skill-de-seguranca.md`** — Definição técnica da skill

## ✏️ Modificar ou Estender

Para criar novas skills ou modificar existentes:

1. Edite ou crie arquivo em `.claude/agents/` (Markdown com frontmatter)
2. Atualize `.claude/settings.local.json` se precisar de novas permissões
3. Documente em `agents/README.md`
4. Versione no git (`.claude/agents/` e documentação)

## 🤝 Contribuindo

Se criar novas skills:
1. Coloque em `.claude/agents/<nome-skill>.md`
2. Atualize `agents/README.md`
3. Considere adicionar ao `settings.local.json.example`
4. Faça commit e abra PR

---

**Última atualização:** 2026-08-13
**Versão Claude Code:** 1.0+
