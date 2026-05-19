## Descrição
Expandir o endpoint `/health` (ou criar um novo `/health/detailed`) para realizar verificações de integridade de todas as dependências críticas do sistema.

## Racional Técnico
Um healthcheck que apenas retorna 200 OK não é suficiente para sistemas distribuídos. É necessário garantir que o backend consegue se comunicar com o PostgreSQL, Redis e que possui conectividade básica com as APIs externas. Isso permite que orquestradores (como o Docker Compose no GCP ou Kubernetes futuramente) tomem decisões de reinicialização ou retirada de tráfego baseadas no estado real do sistema.

## Critérios de Aceite
- [ ] Verificação de conectividade com o Banco de Dados (PostgreSQL).
- [ ] Verificação de conectividade com o Cache (Redis).
- [ ] Verificação de conectividade (ping/head request) com APIs da Câmara e Senado.
- [ ] Retorno de status 503 Service Unavailable caso alguma dependência crítica falhe.
- [ ] Inclusão de metadados básicos (versão do sistema, uptime).
