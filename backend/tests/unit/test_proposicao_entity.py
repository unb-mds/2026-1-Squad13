import pytest
from datetime import date
from domain.entities.proposicao import Proposicao

def test_atualizar_metricas_sem_data_apresentacao():
    p = Proposicao(tipo="PL", numero="1", ano=2024, autor="A", status="X", orgao_atual="O", ementa="E", 
                   data_ultima_movimentacao="D", tags=[])
    p.data_apresentacao = None
    p.atualizar_metricas()
    assert p.tempo_total_dias == 0 # Valor default

def test_atualizar_metricas_com_data_encerramento():
    p = Proposicao(tipo="PL", numero="1", ano=2024, autor="A", status="X", orgao_atual="O", ementa="E", 
                   data_apresentacao="2024-01-01", data_ultima_movimentacao="D", 
                   data_encerramento="2024-01-11", tags=[])
    p.atualizar_metricas()
    assert p.tempo_total_dias == 10

def test_atualizar_metricas_erro_formato_data():
    p = Proposicao(tipo="PL", numero="1", ano=2024, autor="A", status="X", orgao_atual="O", ementa="E", 
                   data_apresentacao="data-invalida", data_ultima_movimentacao="D", tags=[])
    p.atualizar_metricas()
    assert p.tempo_total_dias == 0 # Mantém default por causa do try/except

def test_nome_canonico():
    p = Proposicao(tipo="PL", numero="123", ano=2024, autor="A", status="X", orgao_atual="O", ementa="E", 
                   data_apresentacao="D", data_ultima_movimentacao="D", tags=[])
    assert p.nome_canonico == "PL 123/2024"
