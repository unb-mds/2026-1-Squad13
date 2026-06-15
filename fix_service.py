import re

with open("backend/src/application/services/listar_movimentacoes_service.py", "r") as f:
    content = f.read()

conflict_pattern = re.compile(r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> origin/revert-152-feat/129-campo-relevante-evento-tramitacao\n", re.DOTALL)

def replacer(match):
    head = match.group(1)
    remote = match.group(2)
    # The remote has the async awaits. 
    # We want the logic from HEAD, but with await added to the adapter calls.
    resolved = head.replace(
        "self.camara_adapter.buscar_tramitacoes_brutas",
        "await self.camara_adapter.buscar_tramitacoes_brutas"
    ).replace(
        "self.senado_adapter.buscar_tramitacoes_brutas",
        "await self.senado_adapter.buscar_tramitacoes_brutas"
    )
    return resolved

new_content = conflict_pattern.sub(replacer, content)

with open("backend/src/application/services/listar_movimentacoes_service.py", "w") as f:
    f.write(new_content)
