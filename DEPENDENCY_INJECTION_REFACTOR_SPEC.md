# Especificação: Refatoração de Injeção de Dependência (Issue #132)

## 1. Motivação e Objetivos

O projeto segue uma arquitetura em camadas (Layered Architecture) conforme definido na `ARCHITECTURE.md` e `ADR-001`. No entanto, existe um acoplamento direto de serviços da camada de `application` com classes concretas de `infrastructure` (repositórios baseados em SQLModel e Adapters de APIs externas).

Esta especificação define o plano para implementar o padrão **Ports and Adapters (Hexagonal Architecture)** completo, utilizando `typing.Protocol` para definir interfaces (Ports) que a camada de Aplicação deve consumir, desacoplando-a totalmente dos detalhes de implementação do banco de dados e APIs de terceiros.

**Principais Metas:**
- Remover dependência de `Session` (SQLAlchemy/SQLModel) de dentro dos Application Services.
- Garantir que `application/services/` não importe nada de `infrastructure/`.
- Facilitar a criação de Mocks e Stubs para testes unitários.
- Padronizar a injeção via construtor (`__init__`) em todos os serviços.

## 2. Estrutura de Ports (Interfaces)

Serão criadas as seguintes interfaces em `backend/src/application/ports/`:

| Nome da Interface | Arquivo | Principais Métodos |
| :--- | :--- | :--- |
| `ProposicaoRepositoryPort` | `proposicao_repository.py` | `filtrar`, `contar`, `buscar_por_id`, `salvar`, `upsert_em_lote` |
| `EventoTramitacaoRepositoryPort` | `evento_tramitacao_repository.py` | `buscar_por_proposicao`, `salvar_lote`, `existe_algum_evento` |
| `FaseAnaliticaRepositoryPort` | `fase_analitica_repository.py` | `buscar_todas`, `buscar_por_id` |
| `OrgaoLegislativoRepositoryPort` | `orgao_legislativo_repository.py` | `buscar_ou_criar`, `listar_todos` |
| `ApensamentoRepositoryPort` | `apensamento_repository.py` | `salvar`, `buscar_por_materia` |
| `DashboardRepositoryPort` | `dashboard_repository.py` | `obter_metricas_gerais`, `obter_gargalos`, `obter_dados_status` |
| `CamaraAdapterPort` | `camara_adapter.py` | `obter_proposicao_detalhada`, `listar_tramitacoes` |
| `SenadoAdapterPort` | `senado_adapter.py` | `obter_materia_detalhada`, `listar_tramitacoes` |

*Nota: O `BaselineTramitacaoRepositoryPort` já existe e servirá de base.*

## 3. Plano de Implementação

### Fase 1: Criação dos Arquivos de Port
Definir os `Protocols` com os exatos nomes de métodos e assinaturas de tipos já utilizados pelos repositórios concretos.

### Fase 2: Refatoração dos Serviços (Application)
1. **Remoção de Imports:** Todos os arquivos em `src/application/services/*.py` devem ser alterados para importar os Ports em vez de classes SQL.
2. **Injeção no `ColetarEmLoteService`:** 
   - Atual: `__init__(self, session: Session, ...)`
   - Novo: `__init__(self, repository: ProposicaoRepositoryPort, evento_repo: EventoTramitacaoRepositoryPort, ...)`
3. **Normalização de Nomes:** Garantir que o nome das variáveis internas (`self.repository`, `self.fase_repo`) seja consistente em todos os serviços.

### Fase 3: Composition Root (Ponto de Entrada)
A instanciação das classes concretas (Infrastructure) e sua injeção nos serviços (Application) será centralizada na camada de **Presentation** e nos **Workers/Scripts**:
- **Presentation:** `backend/src/presentation/*_dependencies.py` utilizarão FastAPI `Depends` para injetar as instâncias de SQLModel nos serviços.
- **Workers:** `backend/src/infrastructure/workers/coleta_worker.py` criará as instâncias dos repositórios passando a `Session` e entregará os objetos prontos para o `ColetarEmLoteService`.
- **Scripts:** `backend/src/seed.py` e comandos CLI seguirão o mesmo padrão.

## 4. Critérios de Aceite e Validação

- [ ] Nenhum arquivo em `src/application/services/` importa nada de `src/infrastructure/`.
- [ ] O comando `ruff check .` não retorna erros de importação ou tipos.
- [ ] A suíte de testes `./scripts/ci/test.sh` passa integralmente (validando que os mappers e fluxos de dados continuam corretos).
- [ ] O worker de coleta (`task_coletar_proposicoes_diario`) executa com sucesso em ambiente Docker.

---
*Este documento serve como guia técnico para a execução da Issue #132.*
