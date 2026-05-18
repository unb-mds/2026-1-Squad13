from application.ports.email_sender_provider import EmailSenderProvider


class DummyEmailSender(EmailSenderProvider):
    def enviar_email_recuperacao(self, email_destino: str, token: str) -> None:
        """
        Implementação dummy para desenvolvimento.
        Na prática, esta classe enviaria um e-mail de verdade (ex: usando SMTP, SendGrid, AWS SES).
        """
        link_recuperacao = f"http://localhost:5173/recuperar-senha?token={token}"
        print("\n[DUMMY E-MAIL SENDER]")
        print(f"Para: {email_destino}")
        print("Assunto: Recuperação de Senha")
        print(f"Link para criar nova senha: {link_recuperacao}\n")
