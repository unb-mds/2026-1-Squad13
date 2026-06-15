#!/usr/bin/env python3
import ast
import os
import sys


def check_file_imports(filepath):
    violations = []

    # Determina a camada do arquivo sendo analisado
    normalized_path = filepath.replace("\\", "/")

    # Só analisamos arquivos de código sob src/
    if "backend/src/" not in normalized_path or not normalized_path.endswith(".py"):
        return violations

    is_domain = "backend/src/domain/" in normalized_path
    is_application = "backend/src/application/" in normalized_path

    if not (is_domain or is_application):
        return violations

    try:
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
    except SyntaxError as e:
        print(f"⚠️ Erro de sintaxe ao parsear {filepath}: {e}", file=sys.stderr)
        return violations
    except Exception as e:
        print(f"⚠️ Erro ao ler arquivo {filepath}: {e}", file=sys.stderr)
        return violations

    for node in ast.walk(tree):
        # Verifica 'import module'
        if isinstance(node, ast.Import):
            for name in node.names:
                imported_module = name.name
                val = validate_import(
                    is_domain, is_application, imported_module, filepath, node.lineno
                )
                if val:
                    violations.append(val)
        # Verifica 'from module import name'
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_module = node.module
                val = validate_import(
                    is_domain, is_application, imported_module, filepath, node.lineno
                )
                if val:
                    violations.append(val)

    return violations


def validate_import(is_domain, is_application, module_name, filepath, lineno):
    parts = module_name.split(".")
    # Checa se o import se refere a pacotes internos
    internal_layers = {"infrastructure", "presentation", "application", "domain"}

    # Normaliza imports que começam com 'src.'
    if len(parts) > 1 and parts[0] == "src":
        referenced_layer = parts[1]
    else:
        referenced_layer = parts[0]

    if referenced_layer not in internal_layers:
        return None

    if is_domain:
        # Camada Domain não pode importar de infrastructure, presentation ou application
        forbidden = {"infrastructure", "presentation", "application"}
        if referenced_layer in forbidden:
            return {
                "file": filepath,
                "line": lineno,
                "module": module_name,
                "reason": f"Camada DOMAIN não pode importar da camada {referenced_layer.upper()} (acoplamento ilegal)",
            }

    if is_application:
        # Camada Application não pode importar de presentation
        if referenced_layer == "presentation":
            return {
                "file": filepath,
                "line": lineno,
                "module": module_name,
                "reason": "Camada APPLICATION não pode importar da camada PRESENTATION (fluxo de dependência reverso)",
            }

    return None


def main():
    if len(sys.argv) < 2:
        print("Uso: check-imports.py <arquivo1.py> [arquivo2.py ...]", file=sys.stderr)
        sys.exit(0)

    files_to_check = sys.argv[1:]
    all_violations = []

    for filepath in files_to_check:
        if os.path.exists(filepath):
            violations = check_file_imports(filepath)
            all_violations.extend(violations)

    if all_violations:
        print("\n❌ VIOLAÇÕES DE ARQUITETURA DETECTADAS:")
        print("----------------------------------------------------------------------")
        for v in all_violations:
            print(f"Arquivo: {v['file']}:{v['line']}")
            print(f"Importação ilegal: '{v['module']}'")
            print(f"Motivo: {v['reason']}")
            print(
                "----------------------------------------------------------------------"
            )
        sys.exit(1)

    print("✅ Todas as importações estão em conformidade com as camadas!")
    sys.exit(0)


if __name__ == "__main__":
    main()
