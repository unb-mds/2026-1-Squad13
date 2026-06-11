class ProposicaoNaoEncontradaError(Exception):
    pass


class FiltroInvalidoError(Exception):
    pass


class TokenRevogadoError(Exception):
    """Lançada quando um token JWT já foi invalidado (logout)."""

    pass


class UsuarioNaoEncontradoError(Exception):
    pass


class TokenInvalidoError(Exception):
    pass


class ContaBloqueadaError(Exception):
    """Exceção lançada quando uma conta está temporariamente bloqueada por excesso de tentativas."""

    def __init__(self, email: str, segundos_restantes: int = 900):
        self.email = email
        self.segundos_restantes = segundos_restantes
        minutos = (segundos_restantes + 59) // 60  # Arredonda para cima
        self.message = f"A conta foi bloqueada por múltiplas tentativas falhas. Tente novamente em {minutos} minuto(s)."
        super().__init__(self.message)


class CredenciaisInvalidasError(Exception):
    """Exceção lançada quando as credenciais de login são inválidas."""

    def __init__(self, message="E-mail ou senha incorretos"):
        super().__init__(message)


class EmailJaCadastradoError(Exception):
    """Exceção lançada quando tenta-se registrar um e-mail já existente."""

    def __init__(self, message="E-mail já cadastrado"):
        super().__init__(message)
