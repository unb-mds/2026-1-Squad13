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
    assert p.status == "Sancionada"

    p = get_p("SANCIONADO")
    p.normalizar_campo_status()
    assert p.status == "Sancionada"

    p = get_p("VETADO")
    p.normalizar_campo_status()
    assert p.status == "Vetada"

    p = get_p("APENSADO")
    p.normalizar_campo_status()
    assert p.status == "Arquivada"

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
    assert p.status == "Em Tramitação"

    p = get_p("AGUARDANDO DESPACHO")
    p.normalizar_campo_status()
    assert p.status == "Em Tramitação"

    p = get_p("RECEBIMENTO")
    p.normalizar_campo_status()
    assert p.status == "Em Tramitação"

    p = get_p(
        "STATUS MUITO LONGO QUE DEVE SER CORTADO PORQUE EXCEDEU CINQUENTA CARACTERES"
    )
    p.normalizar_campo_status()
    assert p.status == "Em Tramitação"


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
    assert p.status == "Sancionada"
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
    assert p.status == "Em Tramitação"
    assert p.status_original == "AGUARDANDO DISTRIBUIÇÃO"


def test_cobertura_dados_inclui_emendas():
    """Verifica se a falta do dado de emendas penaliza a cobertura."""
    p = Proposicao(
        tipo="PL",
        numero="123",
        ano=2024,
        ementa="Teste",
        autor="Autor",
        orgao_origem="Câmara",
        status="Em Tramitação",
        orgao_atual="CCJ",
        data_apresentacao="2024-01-01",
        data_ultima_movimentacao="2024-01-01",
        link_oficial="http://link",
        regime_tramitacao="ORDINARIO",
        numero_emendas=None,  # Faltando dado
    )

    cobertura_sem_dado = p.cobertura_dados

    p.numero_emendas = 10
    cobertura_com_dado = p.cobertura_dados

    assert cobertura_com_dado > cobertura_sem_dado


def test_numero_assinaturas_nao_pode_ser_negativo():
    """Valida que o número de assinaturas é >= 0."""
    p = Proposicao(tipo="PL", numero="1", ano=2024, numero_assinaturas=-5)
    assert p.numero_assinaturas == 0

    p.numero_assinaturas = -10
    assert p.numero_assinaturas == 0

    p.numero_assinaturas = 5
    assert p.numero_assinaturas == 5


def test_novos_campos_preditivos_presentes():
    """Valida que os campos bloco_legislativo e parecer_ccj_favoravel estão na entidade."""
    p = Proposicao(
        tipo="PL",
        numero="1",
        ano=2024,
        bloco_legislativo="Bloco X",
        parecer_ccj_favoravel=True,
    )
    assert p.bloco_legislativo == "Bloco X"
    assert p.parecer_ccj_favoravel is True
