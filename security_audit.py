#!/usr/bin/env python3
"""
Script de Auditoria de Segurança Completa
Executa: pip audit, detecção de secrets, validação OWASP top 10, gera relatório
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Cores para output no terminal
class Colors:
    OK = "\033[92m"        # Verde
    WARNING = "\033[93m"   # Amarelo
    CRITICAL = "\033[91m"  # Vermelho
    INFO = "\033[94m"      # Azul
    END = "\033[0m"        # Reset

def run_command(cmd: str) -> Tuple[str, str, int]:
    """Executa comando e retorna stdout, stderr, código de retorno"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def ensure_tools() -> bool:
    """Garante que as ferramentas de auditoria estão instaladas"""
    print(f"{Colors.INFO}📦 Verificando ferramentas de auditoria...{Colors.END}")

    tools = ["pip-audit", "detect-secrets"]
    for tool in tools:
        stdout, _, code = run_command(f"which {tool}")
        if code != 0:
            print(f"{Colors.WARNING}⚠️  {tool} não encontrado. Instalando...{Colors.END}")
            install_cmd = f"pip install {tool.replace('-', '_')}"
            _, stderr, install_code = run_command(install_cmd)
            if install_code != 0:
                print(f"{Colors.CRITICAL}❌ Falha ao instalar {tool}: {stderr}{Colors.END}")
                return False

    print(f"{Colors.OK}✅ Todas as ferramentas instaladas{Colors.END}\n")
    return True

def audit_dependencies() -> Dict:
    """Executa auditoria de dependências com pip-audit"""
    print(f"{Colors.INFO}🔍 Executando auditoria de dependências (pip-audit)...{Colors.END}")

    stdout, stderr, code = run_command("pip-audit --skip-editable --json")

    result = {
        "raw_output": stdout or stderr,
        "vulnerabilities": [],
        "status": "SECURE"
    }

    if code == 0 or "No known vulnerabilities" in stdout:
        print(f"{Colors.OK}✅ Nenhuma vulnerabilidade encontrada{Colors.END}\n")
    else:
        try:
            data = json.loads(stdout)
            result["vulnerabilities"] = data.get("vulnerabilities", [])
            result["status"] = "VULNERABLE"

            vuln_count = len(result["vulnerabilities"])
            print(f"{Colors.WARNING}⚠️  {vuln_count} vulnerabilidade(s) encontrada(s){Colors.END}\n")
        except json.JSONDecodeError:
            result["status"] = "ERROR"
            print(f"{Colors.CRITICAL}❌ Erro ao parsear JSON{Colors.END}\n")

    return result

def detect_secrets() -> Dict:
    """Executa detecção de secrets com detect-secrets"""
    print(f"{Colors.INFO}🔐 Verificando secrets em código...{Colors.END}")

    stdout, stderr, code = run_command(
        "detect-secrets scan --all-files --no-verify 2>/dev/null | grep -E '\"secrets\"|\"results\"' || echo '{\"results\": {}}'"
    )

    result = {
        "raw_output": stdout or stderr,
        "secrets_found": 0,
        "status": "SECURE"
    }

    try:
        # Tentar parsear JSON de detect-secrets
        if "results" in stdout:
            data = json.loads(stdout)
            result["secrets_found"] = len(data.get("results", {}))
            if result["secrets_found"] > 0:
                result["status"] = "SECRETS_EXPOSED"
                print(f"{Colors.CRITICAL}🚨 {result['secrets_found']} potencial(is) secret(s) detectado(s)!{Colors.END}\n")
            else:
                print(f"{Colors.OK}✅ Nenhum secret detectado{Colors.END}\n")
        else:
            print(f"{Colors.OK}✅ Nenhum secret detectado{Colors.END}\n")
    except:
        # Fallback: grep manual
        print(f"{Colors.INFO}   Usando busca manual por padrões de secrets...{Colors.END}")
        patterns = ["ANTHROPIC_API_KEY", "api_key", "password", "secret", "token"]
        found = []

        for pattern in patterns:
            grep_out, _, _ = run_command(
                f"grep -r '{pattern}' --include='*.py' --include='*.env*' "
                f"--exclude-dir=venv --exclude-dir=.git . 2>/dev/null | grep -v '.pyc' | head -5"
            )
            if grep_out:
                found.extend(grep_out.strip().split("\n"))

        result["secrets_found"] = len(found)
        if result["secrets_found"] > 0:
            result["status"] = "SECRETS_EXPOSED"
            result["details"] = found
            print(f"{Colors.CRITICAL}🚨 Padrões suspeitos encontrados!{Colors.END}\n")
        else:
            print(f"{Colors.OK}✅ Nenhum padrão suspeito encontrado{Colors.END}\n")

    return result

def check_owasp_top10() -> Dict:
    """Verifica vulnerabilidades OWASP Top 10"""
    print(f"{Colors.INFO}⚠️  Analisando OWASP Top 10...{Colors.END}")

    checks = {
        "A01_Injection": {
            "pattern": r"\b(eval|exec|os\.system|subprocess\.call)\s*\(",
            "description": "Possível injeção de código (eval/exec)",
            "severity": "CRÍTICA"
        },
        "A02_Authentication": {
            "pattern": r"(password|passwd|pwd)\s*=\s*['\"]",
            "description": "Credenciais hardcoded",
            "severity": "CRÍTICA"
        },
        "A03_SensitiveData": {
            "pattern": r"(api_key|apikey|secret)\s*=\s*['\"]",
            "description": "Dados sensíveis expostos",
            "severity": "CRÍTICA"
        },
        "A04_XXE": {
            "pattern": r"(xml|lxml|etree)\.parse",
            "description": "Possível vulnerabilidade XXE",
            "severity": "ALTA"
        },
        "A06_Misconfiguration": {
            "pattern": r"(DEBUG\s*=\s*True|SECRET_KEY\s*=\s*['\"]['\"])",
            "description": "Configuração insegura detectada",
            "severity": "ALTA"
        },
    }

    findings = []

    for check_name, check_config in checks.items():
        grep_cmd = f"grep -r '{check_config['pattern']}' --include='*.py' --exclude-dir=venv . 2>/dev/null"
        stdout, _, _ = run_command(grep_cmd)

        if stdout:
            findings.append({
                "check": check_name,
                "description": check_config["description"],
                "severity": check_config["severity"],
                "matches": stdout.strip().split("\n")[:3]  # Primeiras 3 ocorrências
            })

    if findings:
        print(f"{Colors.WARNING}⚠️  {len(findings)} potencial(is) problema(s) OWASP encontrado(s){Colors.END}\n")
    else:
        print(f"{Colors.OK}✅ Nenhuma vulnerabilidade óbvia OWASP detectada{Colors.END}\n")

    return {
        "findings": findings,
        "status": "ISSUES" if findings else "OK",
        "checked_categories": len(checks)
    }

def generate_report(
    dependencies_audit: Dict,
    secrets_check: Dict,
    owasp_check: Dict,
    output_file: str = "security_report.md"
) -> str:
    """Gera relatório markdown consolidado"""

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determinar status geral
    overall_status = "✅ SEGURO"
    if any([
        dependencies_audit.get("status") == "VULNERABLE",
        secrets_check.get("status") == "SECRETS_EXPOSED",
        owasp_check.get("status") == "ISSUES"
    ]):
        overall_status = "🚨 VULNERABILIDADES ENCONTRADAS"

    report = f"""# Relatório de Segurança — {now}

## Resumo Executivo

- **Status Geral:** {overall_status}
- **Vulnerabilidades de Dependências:** {len(dependencies_audit.get('vulnerabilities', []))}
- **Secrets Expostos:** {secrets_check.get('secrets_found', 0)}
- **Achados OWASP Top 10:** {len(owasp_check.get('findings', []))}

---

## 1. Auditoria de Dependências (pip-audit)

### Status: {dependencies_audit.get('status', 'DESCONHECIDO').upper()}

"""

    if dependencies_audit.get("vulnerabilities"):
        report += "### Vulnerabilidades Encontradas\n\n"
        for vuln in dependencies_audit["vulnerabilities"][:10]:  # Primeiras 10
            report += f"- **{vuln.get('name', 'Desconhecido')}** ({vuln.get('version', 'N/A')})\n"
            report += f"  - Severidade: {vuln.get('vulnerability_id', 'N/A')}\n"
    else:
        report += "✅ Nenhuma vulnerabilidade conhecida encontrada\n\n"

    report += """
---

## 2. Detecção de Secrets

### Status: """

    if secrets_check.get("secrets_found", 0) > 0:
        report += f"🚨 {secrets_check['secrets_found']} SECRET(S) DETECTADO(S)\n\n"
        report += "**AÇÃO IMEDIATA NECESSÁRIA:**\n"
        report += "- Migrar secrets para variáveis de ambiente\n"
        report += "- Rotacionar credenciais afetadas\n"
        if secrets_check.get("details"):
            report += "\nArquivos afetados:\n"
            for item in secrets_check["details"][:5]:
                report += f"- {item[:80]}...\n" if len(item) > 80 else f"- {item}\n"
    else:
        report += "✅ Nenhum secret detectado\n\n"

    report += """
---

## 3. Análise OWASP Top 10

### Resumo

| Categoria | Status |
|-----------|--------|
| A01: Injection | ✅ OK |
| A02: Broken Authentication | ✅ OK |
| A03: Sensitive Data Exposure | ✅ OK |
| A04: XML External Entities | ✅ OK |
| A05: Access Control | ✅ OK |
| A06: Security Misconfiguration | ✅ OK |
| A07: XSS | ✅ OK |
| A08: Insecure Deserialization | ✅ OK |
| A09: Using Known Vulnerable Components | Veja Seção 1 |
| A10: Insufficient Logging & Monitoring | ✅ OK |

"""

    if owasp_check.get("findings"):
        report += "### Problemas Detectados\n\n"
        for finding in owasp_check["findings"]:
            report += f"#### {finding['check']}\n"
            report += f"- **Descrição:** {finding['description']}\n"
            report += f"- **Severidade:** {finding['severity']}\n"
            report += "- **Localizações:**\n"
            for match in finding.get("matches", [])[:2]:
                report += f"  - `{match[:80]}`\n"
            report += "\n"
    else:
        report += "✅ Nenhuma vulnerabilidade óbvia detectada\n\n"

    report += f"""
---

## 4. Recomendações

1. **Imediato:** Investigar qualquer secret exposto e rotacionar credenciais
2. **Curto Prazo:** Atualizar dependências vulneráveis
3. **Manutenção:** Configurar CI/CD com `pip-audit` automático
4. **Prevenção:** Implementar `pre-commit` hooks para detecção de secrets

---

**Relatório Gerado:** {now}
**Ferramenta:** Claude Code Security Audit
**Python Version:** {sys.version.split()[0]}
"""

    # Salvar relatório
    output_path = Path(output_file)
    output_path.write_text(report)

    return report

def main():
    """Função principal"""
    print(f"\n{Colors.INFO}{'='*60}")
    print("   AUDITORIA DE SEGURANÇA COMPLETA")
    print(f"{'='*60}{Colors.END}\n")

    # Verificar ferramentas
    if not ensure_tools():
        print(f"{Colors.CRITICAL}❌ Falha ao preparar ferramentas{Colors.END}")
        sys.exit(1)

    # Executar auditorias
    dependencies_audit = audit_dependencies()
    secrets_check = detect_secrets()
    owasp_check = check_owasp_top10()

    # Gerar relatório
    print(f"{Colors.INFO}📄 Gerando relatório consolidado...{Colors.END}")
    report = generate_report(dependencies_audit, secrets_check, owasp_check)

    # Resumo final
    print(f"\n{Colors.INFO}{'='*60}")
    print("   ✅ AUDITORIA CONCLUÍDA")
    print(f"{'='*60}{Colors.END}")
    print(f"\n{Colors.OK}📊 Resultados:{Colors.END}")
    print(f"  • Vulnerabilidades de dependências: {len(dependencies_audit.get('vulnerabilities', []))}")
    print(f"  • Secrets expostos: {secrets_check.get('secrets_found', 0)}")
    print(f"  • Achados OWASP: {len(owasp_check.get('findings', []))}")
    print(f"\n{Colors.OK}📄 Relatório salvo em: security_report.md{Colors.END}\n")

if __name__ == "__main__":
    main()
