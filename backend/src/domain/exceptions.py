class ProposicaoNaoEncontradaError(Exception):
    pass


class FiltroInvalidoError(Exception):
    pass


class TokenRevogadoError(Exception):
    """Lançada quando um token JWT já foi invalidado (logout)."""
    pass


class CredenciaisInvalidasError(Exception):
    """Lançada quando o e-mail ou senha estão incorretos no login."""
    pass


class UsuarioJaCadastradoError(Exception):
    """Lançada quando tenta registrar um e-mail já existente."""
    pass
