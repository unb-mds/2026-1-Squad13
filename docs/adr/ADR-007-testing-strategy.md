# ADR-007: Estratégia de Testes

**Data:** 2026-05-06  
**Status:** Aceita  
**Decisores:** Time de Desenvolvimento  

---

## Contexto

Para garantir a qualidade e a manutenção do sistema a longo prazo, especialmente em um ambiente acadêmico com múltiplos colaboradores, é necessário estabelecer uma estratégia clara de testes. Sem testes, o risco de regressões ao refatorar ou adicionar novas funcionalidades é alto.

---

## Decisão

Adotaremos o framework **pytest** para automatizar os testes do backend. A estrutura de testes será dividida em:

1.  **Testes de Unidade:** Focados em validar o comportamento de entidades de domínio e serviços de aplicação, garantindo que as regras de negócio (ex: filtros obrigatórios) funcionem corretamente.
2.  **Testes de Integração:** Focados em validar a integração entre as camadas do sistema e a exposição correta dos endpoints via FastAPI.

Utilizaremos o `TestClient` do FastAPI para simular requisições HTTP e validar as respostas da API sem a necessidade de subir o servidor completo.

A configuração será gerenciada por um arquivo `pytest.ini` e as fixtures serão organizadas de forma hierárquica usando múltiplos arquivos `conftest.py`:
- Fixtures globais na raiz de `tests/`.
- Fixtures específicas para unidade e integração em suas respectivas subpastas.

Testes que realizam chamadas a APIs externas reais serão marcados com `@pytest.mark.integration`.

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| pytest (escolhida) | Flexível, extensível, amplamente usado no ecossistema Python | N/A |
| unittest (built-in) | Sem dependências extras | Sintaxe mais verbosa, menos recursos modernos |

---

## Consequências

**Positivas:**
- Aumento da confiança na entrega de novas funcionalidades.
- Documentação viva do comportamento esperado do sistema.
- Facilitação de refatorações futuras.

**Negativas / trade-offs:**
- Requer tempo adicional de desenvolvimento para escrita e manutenção dos testes.

**Riscos:**
- Testes de integração excessivamente complexos podem se tornar lentos ou frágeis se dependerem de estados de banco de dados voláteis.
- Mitigação: Uso de fixtures e mocks controlados.
