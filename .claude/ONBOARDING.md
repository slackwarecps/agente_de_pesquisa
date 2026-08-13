# 🚀 Onboarding — Usando Skills do Projeto

Bem-vindo ao `agente_de_pesquisa`! Este projeto tem skills especializadas que todo dev deve saber usar.

## ⚡ Quick Start (2 minutos)

### Passo 1: Configure Sua Máquina Local
```bash
# Clone o repo (já traz .claude/agents/ com skills)
git clone <url>
cd agente_de_pesquisa

# Copie o template de configurações locais
cp .claude/settings.local.json.example .claude/settings.local.json

# Pronto! 🎉
```

### Passo 2: Use as Skills

**Auditoria de Segurança:**
```bash
/passa-skill-de-seguranca
```

Isso vai:
- ✅ Executar `pip audit` (vulnerabilidades)
- 🔐 Detectar secrets/credenciais
- ⚠️ Validar OWASP Top 10
- 📄 Gerar `security_report.md`

### Passo 3: Review o Relatório
```bash
cat security_report.md
```

---

## 📚 Documentação Completa

| Arquivo | Para Quem | Conteúdo |
|---------|-----------|----------|
| **`.claude/README.md`** | Todos | Setup e estrutura |
| **`.claude/agents/README.md`** | Todos | Skills disponíveis |
| **`.claude/SKILL_SETUP.md`** | Devs | Implementação técnica |
| **`ONBOARDING.md`** | Novos | Este arquivo! |

---

## 🔍 Skills Disponíveis

### `/passa-skill-de-seguranca` 🔐

**O que faz:** Auditoria de segurança completa do projeto

**Quando usar:**
- ✅ Antes de fazer PR
- ✅ Antes de release/deploy
- ✅ Após atualizar dependências
- ✅ Rotina mensal de segurança

**Como usar:**
```bash
/passa-skill-de-seguranca
```

**Saída:**
```
✅ AUDITORIA CONCLUÍDA

📊 Resultados:
  • Vulnerabilidades de dependências: 0
  • Secrets expostos: 0
  • Achados OWASP: 0

📄 Relatório salvo em: security_report.md
```

**Se encontrar problemas:**
1. Revise o `security_report.md`
2. Cada achado tem "remediação" sugerida
3. Corrija no código
4. Rode novamente para validar

---

## 🎯 Workflow Recomendado

```
1. Clone/Pull
   $ git pull origin main

2. Trabalhe no seu código
   $ vim src/app.py

3. Antes de fazer commit:
   $ /passa-skill-de-seguranca
   $ pytest                  # (se tiver testes)

4. Se tudo OK, faça commit:
   $ git add .
   $ git commit -m "..."
   $ git push

5. Abra PR no GitHub
```

---

## ⚠️ Conceitos Importantes

### `.claude/settings.local.json` é LOCAL
```
❌ NÃO VERSIONE (git ignore)
✅ CRIE A PARTIR DO TEMPLATE: settings.local.json.example
```

**Por quê?** Cada dev pode ter diferentes permissões e configurações.

### Scripts vs Skills
```
Script Python (security_audit.py):
  $ python3 security_audit.py
  
Skill do Claude Code:
  $ /passa-skill-de-seguranca
  
↳ A skill é um wrapper que executa o script
```

### Relatórios são Temporários
```
security_report.md é GERADO a cada execução
↳ Não versione (já está no .gitignore)
↳ Review e delete depois de usar
```

---

## 🆘 Troubleshooting

### "Skill não encontrada"
```
❌ /passa-skill-de-seguranca: command not found

✅ Solução:
   1. Verifique se está no diretório correto
   2. Verifique .claude/agents/passa-skill-de-seguranca.md existe
   3. Reinicie o Claude Code
```

### "Permissão negada"
```
❌ Permission denied for Bash(python3 security_audit.py)

✅ Solução:
   1. Abra .claude/settings.local.json
   2. Adicione: "Bash(python3 security_audit.py *)"
   3. Salve e tente novamente
```

### "Ferramentas não instaladas"
```
❌ pip-audit: command not found

✅ Solução:
   1. O script instala automaticamente na primeira execução
   2. Ou instale manualmente:
      $ pip install pip-audit detect-secrets
```

---

## 💡 Boas Práticas

✅ **DO:**
- Use `/passa-skill-de-seguranca` antes de fazer PR
- Review o `security_report.md` com cuidado
- Corrija vulnerabilidades encontradas
- Atualize dependências quando alertado

❌ **DON'T:**
- Não versione `settings.local.json` (use o .example)
- Não ignore alertas de segurança
- Não versione `security_report.md` (é gerado)
- Não modifique skill sem consultar o time

---

## 🤝 Contribuindo Nova Skill

Se criar uma nova skill:

1. Crie em `.claude/agents/nova-skill.md`
2. Documente em `.claude/agents/README.md`
3. Atualize `.claude/settings.local.json.example` se precisar permissões
4. Abra PR com sua skill

---

## 📞 Perguntas?

- Veja `.claude/README.md` para estrutura
- Veja `.claude/agents/README.md` para skills
- Veja `.claude/SKILL_SETUP.md` para implementação

---

**Bem-vindo ao time! 🚀**

Qualquer dúvida, avise. Aproveite as skills! 🔐✨
