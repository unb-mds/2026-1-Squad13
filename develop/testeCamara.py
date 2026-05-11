from infrastructure.camaraAdapter import CamaraAdapter

adaptador = CamaraAdapter()

minhaLei = adaptador.buscarLeiPorID(2368289)

if minhaLei:
    print(minhaLei)
else:
    print("Erro ao biscar lei")