#!/usr/bin/env python3
"""
Exemplo PROPOSITALMENTE RUIM para testar o Code Review.
Este arquivo contém vários anti-padrões e bugs para o Claude detectar.
"""

import os
import sqlite3
from pathlib import Path


# ❌ PROBLEMA 1: Hardcoded password (Risco de Segurança)
DATABASE_PASSWORD = "admin123"  # NUNCA faça isso!
API_KEY = "sk-abcd1234efgh5678"  # Credencial exposta!


def authenticate_user(username: str, password: str):
    """Autentica usuário contra banco de dados."""
    # ❌ PROBLEMA 2: SQL Injection (Risco de Segurança GRAVE)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    try:
        # ❌ PROBLEMA 3: Usando f-string com SQL sem prepared statements
        cursor.execute(query)
        result = cursor.fetchone()
        return result is not None
    except:
        # ❌ PROBLEMA 4: Exception handler genérico (bare except)
        print("Erro!")
        return False
    finally:
        conn.close()


def process_user_data(data: str):
    """Processa dados do usuário."""
    # ❌ PROBLEMA 5: Sem validação de entrada
    # Se data for None, vai quebrar silenciosamente
    lines = data.split("\n")

    # ❌ PROBLEMA 6: Variável nunca usada
    unused_variable = "isto não é usado"

    result = []
    for line in lines:
        # ❌ PROBLEMA 7: Possível IndexError
        parts = line.split(",")
        email = parts[3]  # E se houver menos de 4 partes?
        result.append(email)

    return result


def write_report(filename: str):
    """Escreve relatório em arquivo."""
    # ❌ PROBLEMA 8: Sem verificação se o diretório existe
    path = Path("/reports") / filename

    content = "Relatório\n" * 1000000  # ❌ PROBLEMA 9: Possível memory leak

    # ❌ PROBLEMA 10: Sem tratamento de erro de escrita
    with open(path, "w") as f:
        f.write(content)


def calculate_average(numbers):
    """Calcula média."""
    # ❌ PROBLEMA 11: Sem type hints
    # ❌ PROBLEMA 12: Sem validação de lista vazia
    return sum(numbers) / len(numbers)  # ZeroDivisionError se lista vazia!


# ❌ PROBLEMA 13: Função global que modifica estado
counter = 0

def increment_counter():
    """❌ Função com side effect global - difícil de testar."""
    global counter
    counter += 1
    return counter


# ❌ PROBLEMA 14: Classe sem __init__
class DataProcessor:
    def process(self):
        # ❌ PROBLEMA 15: Acessa atributos que não foram inicializados
        return self.data.upper()


# ❌ PROBLEMA 16: Função muito longa e complexa (deveria ser refatorada)
def complex_business_logic(a, b, c, d, e, f):
    """Função que faz muitas coisas."""
    if a > 0:
        if b < 100:
            if c == "test":
                if d != None:
                    if e:
                        if f:
                            return a + b
                            # ❌ Código aninhado demais (spaghetti code)
    return 0
