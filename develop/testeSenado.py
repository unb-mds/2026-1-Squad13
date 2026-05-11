from infrastructure.senadoAdapter import SenadoAdapter

adaptador = SenadoAdapter()

minha_lei = adaptador.buscarLeiPorID(8147067)
if minha_lei:
    print("Sucesso ao buscar lei do Senado:")
    print(minha_lei)
else:
    print("Falha ao buscar lei do Senado ou ID inválido.")
