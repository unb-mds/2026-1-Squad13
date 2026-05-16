class ProposicaoNaoEncontradaError(Exception):
    pass


class FiltroInvalidoError(Exception):
    pass


class ContaBloqueadaError(Exception):
    """Exceção lançada quando uma conta está temporariamente bloqueada por excesso de tentativas."""

    def __init__(self, email: str):
        self.email = email
        self.message = "A conta foi bloqueada por múltiplas tentativas falhas. Tente novamente mais tarde."
        super().__init__(self.message)


class CredenciaisInvalidasError(Exception):
    """Exceção lançada quando as credenciais de login são inválidas."""

    def __init__(self):
        super().__init__("E-mail ou senha incorretos")


class EmailJaCadastradoError(Exception):
    """Exceção lançada quando tenta-se registrar um e-mail já existente."""

    def __init__(self):
        super().__init__("E-mail já cadastrado")
