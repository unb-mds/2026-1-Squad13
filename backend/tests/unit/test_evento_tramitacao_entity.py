"""
Testes para EventoTramitacao — invariantes e properties.

Matriz:
  - Construção válida com todos os campos
  - Invariantes: tipo_evento inválido, remessa_ou_retorno inválido,
    sequencia < 1, data_evento formato inválido
  - Properties: eh_evento_terminal, eh_deliberativo, data_formatada

Nota: SQLModel table=True ignora model_validator. Os invariantes são
validados via __init__ e levantam ValueError (não ValidationError).
"""

import pytest

from domain.entities.evento_tramitacao import EventoTramitacao
from domain.entities.tipo_evento import TipoEvento


def _evento(**kwargs):
    """Factory com defaults válidos para reduzir boilerplate."""
    defaults = {
        "proposicao_id": "PL-123-2024",
        "data_evento": "2024-06-15",
        "sequencia": 1,
        "sigla_orgao": "CCJ",
        "descricao_original": "Despacho inicial",
        "tipo_evento": TipoEvento.DESPACHO.value,
    }
    defaults.update(kwargs)
    return EventoTramitacao(**defaults)


class TestConstrucaoValida:
    def test_campos_minimos(self):
        e = _evento()
        assert e.proposicao_id == "PL-123-2024"
        assert e.tipo_evento == "DESPACHO"
        assert e.deliberativo is False
        assert e.mudou_fase is False

    def test_com_todos_os_campos(self):
        e = _evento(
            fase_analitica_id=1,
            deliberativo=True,
            mudou_fase=True,
            mudou_orgao=True,
            remessa_ou_retorno="REMESSA",
            payload_bruto={"raw": "data"},
        )
        assert e.remessa_ou_retorno == "REMESSA"
        assert e.payload_bruto == {"raw": "data"}

    def test_data_com_hora(self):
        e = _evento(data_evento="2024-06-15T14:30")
        assert e.data_evento == "2024-06-15T14:30"

    def test_data_com_hora_e_segundos(self):
        e = _evento(data_evento="2024-06-15T14:30:45")
        assert e.data_evento == "2024-06-15T14:30:45"

    def test_remessa_retorno_none_valido(self):
        e = _evento(remessa_ou_retorno=None)
        assert e.remessa_ou_retorno is None

    def test_remessa_valido(self):
        e = _evento(remessa_ou_retorno="REMESSA")
        assert e.remessa_ou_retorno == "REMESSA"

    def test_retorno_valido(self):
        e = _evento(remessa_ou_retorno="RETORNO")
        assert e.remessa_ou_retorno == "RETORNO"


class TestInvarianteTipoEvento:
    def test_tipo_invalido_levanta_erro(self):
        with pytest.raises(ValueError, match="tipo_evento"):
            _evento(tipo_evento="TIPO_INEXISTENTE")

    def test_tipo_vazio_levanta_erro(self):
        with pytest.raises(ValueError, match="tipo_evento"):
            _evento(tipo_evento="")

    def test_todos_os_membros_validos(self):
        for membro in TipoEvento:
            e = _evento(tipo_evento=membro.value)
            assert e.tipo_evento == membro.value


class TestInvarianteRemessaOuRetorno:
    def test_valor_invalido_levanta_erro(self):
        with pytest.raises(ValueError, match="remessa_ou_retorno"):
            _evento(remessa_ou_retorno="IDA")

    def test_lowercase_invalido(self):
        with pytest.raises(ValueError, match="remessa_ou_retorno"):
            _evento(remessa_ou_retorno="remessa")


class TestInvarianteSequencia:
    def test_sequencia_zero_levanta_erro(self):
        with pytest.raises(ValueError, match="sequencia"):
            _evento(sequencia=0)

    def test_sequencia_negativa_levanta_erro(self):
        with pytest.raises(ValueError, match="sequencia"):
            _evento(sequencia=-1)

    def test_sequencia_um_valido(self):
        e = _evento(sequencia=1)
        assert e.sequencia == 1

    def test_sequencia_grande_valido(self):
        e = _evento(sequencia=9999)
        assert e.sequencia == 9999


class TestInvarianteDataEvento:
    def test_formato_invalido_levanta_erro(self):
        with pytest.raises(ValueError, match="data_evento"):
            _evento(data_evento="15/06/2024")

    def test_texto_livre_levanta_erro(self):
        with pytest.raises(ValueError, match="data_evento"):
            _evento(data_evento="ontem")

    def test_data_vazia_levanta_erro(self):
        with pytest.raises(ValueError, match="data_evento"):
            _evento(data_evento="")


class TestPropertyEhEventoTerminal:
    @pytest.mark.parametrize(
        "tipo",
        [
            TipoEvento.ARQUIVAMENTO,
            TipoEvento.PREJUDICIALIDADE,
            TipoEvento.SANCAO_OU_VETO,
            TipoEvento.PROMULGACAO,
            TipoEvento.REJEICAO,
        ],
        ids=lambda v: v.value,
    )
    def test_terminais(self, tipo):
        e = _evento(tipo_evento=tipo.value)
        assert e.eh_evento_terminal is True

    @pytest.mark.parametrize(
        "tipo",
        [
            TipoEvento.APRESENTACAO,
            TipoEvento.DESPACHO,
            TipoEvento.PARECER,
            TipoEvento.VOTACAO_PLENARIO,
            TipoEvento.APROVACAO,
            TipoEvento.NAO_CLASSIFICADO,
        ],
        ids=lambda v: v.value,
    )
    def test_nao_terminais(self, tipo):
        e = _evento(tipo_evento=tipo.value)
        assert e.eh_evento_terminal is False


class TestPropertyEhDeliberativo:
    @pytest.mark.parametrize(
        "tipo",
        [
            TipoEvento.VOTACAO_COMISSAO,
            TipoEvento.VOTACAO_PLENARIO,
            TipoEvento.APROVACAO,
            TipoEvento.REJEICAO,
        ],
        ids=lambda v: v.value,
    )
    def test_deliberativos(self, tipo):
        e = _evento(tipo_evento=tipo.value)
        assert e.eh_deliberativo is True

    @pytest.mark.parametrize(
        "tipo",
        [
            TipoEvento.APRESENTACAO,
            TipoEvento.DESPACHO,
            TipoEvento.PARECER,
            TipoEvento.ARQUIVAMENTO,
            TipoEvento.NAO_CLASSIFICADO,
        ],
        ids=lambda v: v.value,
    )
    def test_nao_deliberativos(self, tipo):
        e = _evento(tipo_evento=tipo.value)
        assert e.eh_deliberativo is False


class TestPropertyDataFormatada:
    def test_data_simples(self):
        e = _evento(data_evento="2024-06-15")
        assert e.data_formatada == "2024-06-15"

    def test_data_com_hora(self):
        e = _evento(data_evento="2024-06-15T14:30")
        assert e.data_formatada == "2024-06-15"

    def test_data_com_hora_e_segundos(self):
        e = _evento(data_evento="2024-06-15T14:30:45")
        assert e.data_formatada == "2024-06-15"
