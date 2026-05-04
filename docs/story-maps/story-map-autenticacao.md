# Story Map — Autenticação de Usuário

## Épico

**Autenticação de Usuário** — cadastro, login, recuperação de senha e logout para acesso personalizado ao sistema de monitoramento legislativo.

---

## Cadastro

### Funcionalidade
Permitir que o usuário crie uma conta com e-mail e senha.

### História de Usuário
> Como usuário, quero criar uma conta com e-mail e senha para salvar minhas buscas e acompanhar proposições.

### Critérios de Aceitação
- Dado que o usuário preenche e-mail e senha válidos e confirma, a conta é criada e o usuário é redirecionado para a página inicial autenticado.
- E-mail deve ser único — sistema rejeita cadastro duplicado com mensagem clara.
- Senha deve ter no mínimo 8 caracteres. Sistema exibe força da senha em tempo real.
- Dado que o cadastro é concluído, o usuário recebe e-mail de confirmação.

---

## Login

### Funcionalidade
Permitir que o usuário acesse o sistema com suas credenciais.

### Histórias de Usuário
> Como usuário, quero entrar com meu e-mail e senha para acessar minhas preferências salvas.

> Como usuário, quero que minha sessão seja mantida para não precisar logar a cada visita.

### Critérios de Aceitação
- Dado que e-mail e senha estão corretos, o usuário é redirecionado para a página inicial autenticado.
- Credenciais incorretas exibem mensagem genérica sem revelar qual campo está errado.
- Após 5 tentativas falhas, conta é bloqueada por 15 minutos.
- Token de sessão expira em 7 dias. Usuário é redirecionado ao login ao expirar.

---

## Recuperação de Senha

### Funcionalidade
Permitir que o usuário redefina sua senha via e-mail.

### História de Usuário
> Como usuário, quero solicitar a redefinição de senha por e-mail caso esqueça minhas credenciais.

### Critérios de Aceitação
- Link de redefinição é enviado em até 2 minutos e expira em 1 hora.
- Link usado uma única vez — nova solicitação invalida o anterior.

---

## Logout

### Funcionalidade
Permitir que o usuário encerre sua sessão.

### História de Usuário
> Como usuário, quero encerrar minha sessão para proteger minha conta em dispositivos compartilhados.

### Critérios de Aceitação
- Logout invalida o token no servidor imediatamente.
- Após logout, botão voltar do navegador não restaura a sessão.
