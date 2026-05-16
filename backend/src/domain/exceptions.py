class ProposicaoNaoEncontradaError(Exception):
    pass


class FiltroInvalidoError(Exception):
    pass


class ContaBloqueadaError(Exception):
    """Exceção lançada quando uma conta está temporariamente bloqueada por excesso de tentativas."""
    def __init__(self, email: str, tempo_bloqueio_minutos: int = 15):
        self.email = email
        self.tempo_bloqueio_minutos = tempo_bloqueio_minutos
        self.message = f"Conta {email} bloqueada por {tempo_bloqueio_minutos} minutos devido a múltiplas tentativas falhas."
        super().__init__(self.message)
