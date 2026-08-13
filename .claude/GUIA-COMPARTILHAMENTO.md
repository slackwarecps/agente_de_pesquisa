# 📦 Guia de Compartilhamento de Skills

## ❓ Pergunta: "Preciso versionar a pasta `.claude`?"

### ✅ Resposta Curta
**SIM, mas parcialmente.** Versione a pasta `.claude/` EXCETO o arquivo `settings.local.json`.

---

## 📋 O que Versionar ✅

```bash
git add .claude/agents/
git add .claude/README.md
git add .claude/SKILL_SETUP.md
git add .claude/ONBOARDING.md
git add .claude/settings.local.json.example
```

**Esses arquivos compartilham as skills com todo o time.**

---

## 🔒 O que NÃO Versionar ❌

```bash
# NÃO FAZER:
# git add .claude/settings.local.json

# Adicionar ao .gitignore:
echo ".claude/settings.local.json" >> .gitignore
```

**Esse arquivo é LOCAL de cada desenvolvedor.**

---

## 🎯 Workflow Completo

### Para o Criador (Você)

```bash
# 1. Criar a skill
mkdir -p .claude/agents
echo "..." > .claude/agents/minha-skill.md

# 2. Versionar (sem o .local.json!)
git add .claude/agents/
git add .claude/README.md
git add .claude/settings.local.json.example  # Template, não o real!
git commit -m "feat: adiciona skill X"
git push

# 3. Pronto! 🚀
```

### Para Novos Devs

```bash
# 1. Clonar (já traz .claude/agents/ automaticamente)
git clone <url>
cd agente_de_pesquisa

# 2. Setup local (criar arquivo pessoal)
cp .claude/settings.local.json.example .claude/settings.local.json

# 3. Usar skills!
/passa-skill-de-seguranca
```

---

## 📊 Estrutura Final no Repositório

```
.claude/
├── agents/                              ✅ VERSIONADO
│   ├── passa-skill-de-seguranca.md     ✅ Compartilhado
│   └── README.md                        ✅ Compartilhado
├── README.md                            ✅ Compartilhado
├── SKILL_SETUP.md                       ✅ Compartilhado
├── ONBOARDING.md                        ✅ Compartilhado
├── GUIA-COMPARTILHAMENTO.md            ✅ Compartilhado (este!)
├── settings.local.json.example          ✅ Compartilhado (template)
└── settings.local.json                  ❌ LOCAL (cada dev cria)
```

---

## 💡 Por que Dividir Assim?

### `settings.local.json` é LOCAL porque:
- Contém permissões específicas de cada desenvolvedor
- Pode conter tokens pessoais
- Varia entre máquinas (Windows/Mac/Linux)
- Mudanças locais não devem afetar o time

### `settings.local.json.example` é COMPARTILHADO porque:
- É um template com permissões base recomendadas
- Facilita onboarding (copia e pronto)
- Documenta quais permissões a skill precisa

---

## 🚀 Git Commands Rápidos

### Setup de Versionamento (uma vez)

```bash
# Atualizar .gitignore para excluir arquivo local
echo ".claude/settings.local.json" >> .gitignore
git add .gitignore
git commit -m "chore: exclui settings.local.json de versionamento"
```

### Adicionar Skills ao Repositório

```bash
# Criar skill
vim .claude/agents/minha-skill.md

# Versionar
git add .claude/agents/minha-skill.md
git add .claude/README.md  # Atualizar referências
git commit -m "feat: adiciona skill minha-skill"
git push
```

---

## ✅ Checklist para Compartilhar Skills

- [ ] Skill criada em `.claude/agents/nome.md`
- [ ] Documentação atualizada em `.claude/agents/README.md`
- [ ] Template de permissões em `.claude/settings.local.json.example`
- [ ] `.gitignore` tem entrada `.claude/settings.local.json`
- [ ] Commit feito e pushed
- [ ] Novos devs podem clonar e usar em 2 minutos

---

## 📚 Referências Rápidas

| Arquivo | Propósito | Ação |
|---------|-----------|------|
| `.claude/agents/` | Skills do projeto | ✅ Versionar |
| `.claude/README.md` | Setup do projeto | ✅ Versionar |
| `.claude/ONBOARDING.md` | Guia para novos | ✅ Versionar |
| `settings.local.json.example` | Template | ✅ Versionar |
| `settings.local.json` | Configuração pessoal | ❌ Ignorar |

---

## 🎉 Resultado Final

Quando alguém clona seu repo:

```bash
$ git clone <url>
$ cd agente_de_pesquisa
$ cp .claude/settings.local.json.example .claude/settings.local.json
$ /passa-skill-de-seguranca  # ✅ Funciona!
```

**Simples, seguro e compartilhável!** 🚀

---

## ❓ Dúvidas Comuns

**P: E se alguém fizer commit do `settings.local.json` por engano?**
```bash
# Remover do histórico:
git rm --cached .claude/settings.local.json
git commit -m "chore: remove settings.local.json"
git push
```

**P: Posso ter múltiplas skills?**
Sim! Basta adicionar mais arquivos em `.claude/agents/`
```bash
.claude/agents/
├── passa-skill-de-seguranca.md
├── sua-nova-skill.md          ← Adicionar aqui
└── README.md                   ← Documentar aqui
```

**P: Preciso versionar a pasta vazia?**
Não. Git só rastreia arquivos. Quando há arquivos em `.claude/agents/`, a pasta é criada automaticamente.

---

**Última atualização:** 2026-08-13
**Status:** ✅ Pronto para Compartilhamento
