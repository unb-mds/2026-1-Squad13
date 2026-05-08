# ADR-001: Layered Architecture como padrão arquitetural

**Data:** 2026-04-09  
**Status:** Aceita  
**Decisores:** Arquiteto, Dev, PO, Scrum Master  

---

## Contexto

O sistema de Monitoramento de Tempo de Tramitação de Proposições precisa de um padrão arquitetural que permita:

- Trabalho paralelo entre 6 pessoas com papéis distintos
- Isolamento das APIs externas da Câmara e do Senado, que não controlamos
- Testabilidade das regras de negócio sem depender de banco ou internet
- Curva de aprendizado compatível com um projeto acadêmico semestral

Precisamos de uma estrutura clara o suficiente para que qualquer membro do time saiba onde colocar o código que está escrevendo.

---

## Decisão

Vamos adotar **Layered Architecture** com 4 camadas: Apresentação, Aplicação, Domínio e Infraestrutura.

Regra principal: dependências sempre apontam para baixo. A camada de Domínio não importa nada das outras camadas.

```
Apresentação  →  Aplicação  →  Domínio  ←  Infraestrutura
```

---

## Alternativas consideradas

| Opção | Prós | Contras |
|-------|------|---------|
| MVC | Curva baixa, familiar | Fat Controller acumula responsabilidades; ruim para APIs externas |
| Layered Architecture | Equilíbrio entre clareza e testabilidade | Domínio ainda pode depender de interfaces de infra |
| Clean Architecture | Máximo isolamento, altamente testável | Overhead de abstrações (ports/adapters) atrasa entregas no prazo semestral |

---

## Consequências

**Positivas:**
- Qualquer membro do time sabe onde colocar o código que está escrevendo
- Regras de negócio (ex: `dias_parada()`) testáveis sem banco ou internet
- Mudança nas APIs externas afeta só a camada de Infraestrutura
- Estrutura preparada para migração futura para Clean Architecture

**Negativas / trade-offs:**
- Mais arquivos e pastas do que um MVC simples exigiria
- Time precisa respeitar as fronteiras entre camadas — requer disciplina

**Riscos:**
- Se o time não respeitar as fronteiras (ex: controller acessando banco diretamente), os benefícios desaparecem
- Mitigação: revisão de código nas PRs com checklist de camadas
