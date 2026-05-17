class ProposicaoNaoEncontradaError(Exception):
    pass


class FiltroInvalidoError(Exception):
    pass


class TokenRevogadoError(Exception):
    """Lançada quando um token JWT já foi invalidado (logout)."""
    pass
