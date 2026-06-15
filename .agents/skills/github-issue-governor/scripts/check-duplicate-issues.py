#!/usr/bin/env python3
import json
import re
import sys
from difflib import SequenceMatcher


def clean_title(title):
    # Converte para minúsculas e remove pontuação básica
    title = title.lower()
    title = re.sub(r"[^\w\s-]", "", title)
    return title.strip()


def get_similarity(t1, t2):
    # Medida 1: SequenceMatcher (similaridade de sequência e caracteres)
    seq_ratio = SequenceMatcher(None, t1, t2).ratio()

    # Medida 2: Intersecção de palavras (independente de ordem)
    words1 = set(t1.split())
    words2 = set(t2.split())

    if not words1 or not words2:
        word_ratio = 0
    else:
        word_ratio = len(words1.intersection(words2)) / max(len(words1), len(words2))

    # Retorna o maior score de similaridade
    return max(seq_ratio, word_ratio)


def main():
    if len(sys.argv) < 2:
        print("Erro: Título da nova issue não fornecido.", file=sys.stderr)
        print(
            'Uso: check-duplicate-issues.py "Novo Título" < open_issues.json',
            file=sys.stderr,
        )
        sys.exit(1)

    new_title = sys.argv[1]
    new_title_clean = clean_title(new_title)

    # Lê as issues via stdin
    try:
        issues_data = sys.stdin.read().strip()
        if not issues_data:
            # Entrada vazia, nenhuma issue para comparar
            sys.exit(0)
        open_issues = json.loads(issues_data)
    except Exception as e:
        print(f"Erro ao ler/parsear JSON de issues: {e}", file=sys.stderr)
        sys.exit(1)

    duplicates = []

    for issue in open_issues:
        existing_title = issue.get("title", "")
        existing_title_clean = clean_title(existing_title)

        score = get_similarity(new_title_clean, existing_title_clean)

        if score >= 0.60:
            duplicates.append(
                {
                    "number": issue.get("number"),
                    "title": existing_title,
                    "url": issue.get("url"),
                    "score": score,
                }
            )

    # Ordena duplicadas por maior similaridade
    duplicates.sort(key=lambda x: x["score"], reverse=True)

    if duplicates:
        print(
            "\n⚠️ AVISO: Foram encontradas issues existentes potencialmente duplicadas:"
        )
        print("----------------------------------------------------------------------")
        for dup in duplicates:
            percentage = int(dup["score"] * 100)
            print(f'- #{dup["number"]}: "{dup["title"]}"')
            print(f"  Similaridade estimada: {percentage}%")
            if dup["url"]:
                print(f"  Link: {dup['url']}")
            print(
                "----------------------------------------------------------------------"
            )
        sys.exit(2)  # Retorna exit code 2 se houver aviso de duplicado

    sys.exit(0)


if __name__ == "__main__":
    main()
