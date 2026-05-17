import pytest
from pydantic import ValidationError
from presentation.controllers.proposicao_controller import EventoTramitacaoResponse


def test_evento_dto_campos_nulos_permitidos():
    # Testa os Optional (siglaOrgao, faseAnaliticaId, remessaOuRetorno)
    payload = {
        "proposicaoId": "123",
        "dataEvento": "2024-05-14T10:00:00Z",
        "sequencia": 1,
        "descricaoOriginal": "Texto",
        "tipoEvento": "NAO_CLASSIFICADO",
        "deliberativo": False,
        "mudouFase": False,
        "mudouOrgao": False,
    }
    # Como siglaOrgao, faseAnaliticaId e remessaOuRetorno não foram fornecidos, devem ser None
    obj = EventoTramitacaoResponse(**payload)
    assert obj.siglaOrgao is None
    assert obj.faseAnaliticaId is None
    assert obj.remessaOuRetorno is None
    assert obj.proposicaoId == "123"


def test_evento_dto_obrigatorios_falham_sem_valor():
    payload = {
        "proposicaoId": "123",
        "sequencia": 1,
        # Faltando dataEvento, descricaoOriginal, etc.
    }
    with pytest.raises(ValidationError):
        EventoTramitacaoResponse(**payload)


def test_evento_dto_aliases_camel_case():
    payload = {
        "proposicaoId": "123",
        "dataEvento": "2024-05-14T10:00:00Z",
        "sequencia": 1,
        "siglaOrgao": "CCJ",
        "descricaoOriginal": "Recebido na CCJ",
        "tipoEvento": "RECEBIMENTO_ORGAO",
        "faseAnaliticaId": 99,
        "deliberativo": False,
        "mudouFase": True,
        "mudouOrgao": True,
        "remessaOuRetorno": "REMESSA",
    }
    obj = EventoTramitacaoResponse(**payload)

    # Valida que as chaves mapeiam pros atributos Python
    assert obj.proposicaoId == "123"
    assert obj.dataEvento == "2024-05-14T10:00:00Z"
    assert obj.faseAnaliticaId == 99

    # Valida que a serialização pydantic usa as aliases corretamente
    dumped = obj.model_dump(by_alias=True)
    assert "dataEvento" in dumped
    assert "mudouFase" in dumped
    assert "mudouOrgao" in dumped
    assert dumped["faseAnaliticaId"] == 99

    # payload_bruto não pode existir no dump
    assert "payload_bruto" not in dumped
    assert "payloadBruto" not in dumped
