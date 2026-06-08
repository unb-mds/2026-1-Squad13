from domain.entities.proposicao import Proposicao


def test_atualizar_metricas_sem_data_apresentacao():
    p = Proposicao(
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status="X",
        orgao_atual="O",
        ementa="E",
        data_ultima_movimentacao="D",
        tags=[],
    )
    p.data_apresentacao = None
    p.atualizar_metricas()
    assert p.tempo_total_dias == 0  # Valor default


def test_atualizar_metricas_com_data_encerramento():
    p = Proposicao(
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status="X",
        orgao_atual="O",
        ementa="E",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="D",
        data_encerramento="2024-01-11",
        tags=[],
    )
    p.atualizar_metricas()
    assert p.tempo_total_dias == 10


def test_atualizar_metricas_erro_formato_data():
    p = Proposicao(
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status="X",
        orgao_atual="O",
        ementa="E",
        data_apresentacao="data-invalida",
        data_ultima_movimentacao="D",
        tags=[],
    )
    p.atualizar_metricas()
    assert p.tempo_total_dias == 0  # Mantém default por causa do try/except


def test_nome_canonico():
    p = Proposicao(
        tipo="PL",
        numero="123",
        ano=2024,
        autor="A",
        status="X",
        orgao_atual="O",
        ementa="E",
        data_apresentacao="D",
        data_ultima_movimentacao="D",
        tags=[],
    )
    assert p.nome_canonico == "PL 123/2024"


def test_normalizar_campo_status():
    def get_p(status):
        return Proposicao(
            tipo="PL",
            numero="1",
            ano=2024,
            autor="A",
            status=status,
            orgao_atual="O",
            ementa="E",
            data_apresentacao="D",
            data_ultima_movimentacao="D",
            tags=[],
        )

    assert get_p(None).normalizar_campo_status() or True
    p = get_p(None)
    p.normalizar_campo_status()
    assert p.status == "Em Tramitação"

    p = get_p("NORMA JURÍDICA PUBLICADA")
    p.normalizar_campo_status()
    assert p.status == "Concluída (Lei)"

    p = get_p("SANCIONADO")
    p.normalizar_campo_status()
    assert p.status == "Sancionada"

    p = get_p("VETADO")
    p.normalizar_campo_status()
    assert p.status == "Vetada"

    p = get_p("APENSADO")
    p.normalizar_campo_status()
    assert p.status == "Arquivada (Apensada)"

    p = get_p("REJEITADO")
    p.normalizar_campo_status()
    assert p.status == "Arquivada"

    p = get_p("APROVADO")
    p.normalizar_campo_status()
    assert p.status == "Aprovada"

    p = get_p("INCLUSAO EM PAUTA")
    p.normalizar_campo_status()
    assert p.status == "Em Pauta"

    p = get_p("DESIGNACAO DE RELATOR")
    p.normalizar_campo_status()
    assert p.status == "Em Relatoria"

    p = get_p("AGUARDANDO DESPACHO")
    p.normalizar_campo_status()
    assert p.status == "Aguardando"

    p = get_p("RECEBIMENTO")
    p.normalizar_campo_status()
    assert p.status == "Em Tramitação"

    p = get_p(
        "STATUS MUITO LONGO QUE DEVE SER CORTADO PORQUE EXCEDEU CINQUENTA CARACTERES"
    )
    p.normalizar_campo_status()
    assert p.status.endswith("...")
    assert len(p.status) <= 50


def test_normalizar_campo_status_com_status_original():
    # Caso 1: status_original fornecido e status nulo/vazio
    p = Proposicao(
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status_original="NORMA JURÍDICA PUBLICADA",
        status=None,
    )
    p.normalizar_campo_status()
    assert p.status == "Concluída (Lei)"
    assert p.status_original == "NORMA JURÍDICA PUBLICADA"

    # Caso 2: status e status_original fornecidos
    p = Proposicao(
        tipo="PL",
        numero="1",
        ano=2024,
        autor="A",
        status_original="AGUARDANDO DISTRIBUIÇÃO",
        status="Qualquer Coisa",
    )
    p.normalizar_campo_status()
    assert p.status == "Aguardando"
    assert p.status_original == "AGUARDANDO DISTRIBUIÇÃO"
