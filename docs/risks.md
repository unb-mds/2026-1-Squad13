# Análise de Riscos

## Riscos de Gestão

### Escopo excessivamente amplo

**Impacto:** Alto  
**Mitigação:** Definir prioridades para o MVP e limitar funcionalidades secundárias. Story map separado por releases (R1/R2) com critérios claros de aceite.

---

### Falhas de comunicação entre integrantes

**Impacto:** Médio  
**Mitigação:** Manter alinhamentos frequentes, documentação atualizada e Squad Dashboard com métricas de contribuição individual.

---

### Mudanças frequentes nos requisitos

**Impacto:** Médio  
**Mitigação:** Utilizar versionamento da documentação, ADRs para decisões arquiteturais e rastreabilidade entre requisitos e issues.

---

## Riscos Técnicos

### APIs legislativas instáveis ou com formato variável

**Impacto:** Alto  
**Probabilidade:** Alta — já ocorreu com a API do Senado (campos ausentes, formato diferente do documentado).  
**Mitigação:** Padrão Adapter (ADR-005) isola cada fonte. Tratamento de dados incompletos com fallbacks (ex: `data_apresentacao` se `data_ultima_movimentacao` estiver vazia). Retry com backoff exponencial para erros 5xx.

---

### Taxa alta de eventos `NAO_CLASSIFICADO`

**Impacto:** Médio — compromete a precisão das métricas por fase.  
**Probabilidade:** Média — depende da qualidade das descrições vindas das APIs.  
**Mitigação:** O tipo `NAO_CLASSIFICADO` existe justamente para medir a taxa de cobertura do classificador. Patterns em `classificar_tipo_evento()` são iterativamente refinados. Eventos não classificados nunca alteram fase (regra de domínio).

---

### Migração de modelo de dados (já materializada)

**Impacto:** Alto — alteração estrutural do banco e de todos os serviços.  
**Probabilidade:** Ocorreu — migração de `Tramitacao` para `EventoTramitacao` concluída.  
**Mitigação:** Documentação prévia em `MIGRATION_SCOPE.md`, execução em 6 etapas incrementais, seed-only (sem dados reais de produção a perder).

---

### Dependência de Docker para desenvolvimento local

**Impacto:** Médio — onboarding mais lento para membros sem Docker instalado.  
**Probabilidade:** Baixa — a maioria dos membros já tem Docker configurado.  
**Mitigação:** Scripts de automação (`start_dev.sh`, `test_all.sh`) e documentação de setup manual no README.

---

## Riscos de Integração

### Problemas de integração frontend ↔ backend

**Impacto:** Médio  
**Mitigação:** Realizar integrações contínuas, CORS configurado, schemas Pydantic com conversão automática `snake_case` → `camelCase`.

---

### Curva de aprendizado de tecnologias

**Impacto:** Médio  
**Mitigação:** Separar tempo para estudo, material em `Estudos/`, provas de conceito e pair programming.