## Descrição
Refatorar os controllers da camada de apresentação (ex: `proposicao_controller.py`, `auth_controller.py`) para utilizarem o sistema de Injeção de Dependência (`Depends`) do FastAPI. Atualmente, os controllers instanciam manualmente os repositórios, adaptadores e serviços de aplicação.

## Racional Técnico
A instanciação direta de componentes de infraestrutura nos controllers viola o princípio de responsabilidade única e dificulta testes de unidade puros na camada de apresentação. Ao utilizar o `Depends` do FastAPI, desacoplamos a lógica de roteamento da lógica de construção de objetos, permitindo que o framework gerencie o ciclo de vida das dependências e facilitando o uso de mocks em testes de integração de API.

## Critérios de Aceite
- [ ] Criação de fábricas ou provedores de dependência (ex: `get_proposicao_service`) no backend.
- [ ] Remoção de instanciações manuais (ex: `repo = SQLRepo(session)`) de dentro dos métodos de rota.
- [ ] Uso extensivo de `Depends` para injetar casos de uso e serviços nos controllers.
- [ ] Suíte de testes de integração (`test_proposicao_api.py`, etc.) atualizada para validar o novo fluxo de injeção.
