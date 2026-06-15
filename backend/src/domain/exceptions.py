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


class ApiException(Exception):
    """Exceção base para erros de integração com APIs externas."""

    pass


class ApiRateLimitError(ApiException):
    """Erro de Rate Limit (HTTP 429). Contém o tempo recomendado de retry-after."""

    def __init__(self, message: str, retry_after: str | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class ApiTimeoutError(ApiException):
    """Erro de Timeout na comunicação com o servidor externo."""

    pass


class ApiConnectionError(ApiException):
    """Erro de conexão física ou DNS com a API externa."""

    pass


class ApiServerError(ApiException):
    """Erro interno do servidor da API (HTTP 5xx)."""

    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code
