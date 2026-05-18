from typing import Protocol


class EmailSenderProvider(Protocol):
    def enviar_email_recuperacao(self, email_destino: str, token: str) -> None:
        """Envia o link de recuperação de senha para o e-mail informado.
        Esta chamada na implementação concreta deve delegar para um background process ou ser não bloqueante.
        """
        ...
