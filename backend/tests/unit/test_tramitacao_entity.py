from domain.entities.tramitacao import Tramitacao

def test_tramitacao_data_formatada():
    t = Tramitacao(
        proposicao_id="1", 
        data_hora="2024-05-14T10:00:00", 
        sequencia=1, 
        sigla_orgao="X", 
        descricao_tramitacao="Y"
    )
    assert t.data_formatada == "2024-05-14"
