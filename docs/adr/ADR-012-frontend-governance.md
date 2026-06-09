# ADR-012: Governança do Frontend e Baseline Visual

**Data:** 2026-06-08  
**Status:** Aceita  
**Decisores:** Squad 13 / Arquiteto de Frontend  

---

## Contexto

À medida que o LexTrack evoluiu de um protótipo estático para uma aplicação dinâmica conectada a APIs reais do Congresso, a base de código do frontend acumulou algumas inconsistências técnicas e visuais:
* **Duplicidade de Componentes:** Presença de implementações redundantes com comportamentos distintos (ex: `<KPICard />` em `shared/components/` vs `<KpiCard />` em `shared/ui/`).
* **Conflitos de Estilização:** Alguns componentes de UI utilizam cores escuras fixas (`bg-ink-800`), enquanto o corpo estrutural do site depende de variáveis de tema (`bg-background`), gerando incompatibilidades visuais com o modo escuro (Dark Mode).
* **Páginas Inativas (Bypass):** Páginas físicas inteiras (como `relatorios-page.tsx` e `consulta-proposicoes-page.tsx`) e componentes associados estão fora do roteamento ativo (redirecionando para o `/dashboard`).

Para garantir que a interface evolua com alta qualidade técnica, consistência estética e sem acúmulo de código morto, torna-se necessário estabelecer uma política de governança do frontend e oficializar o baseline visual.

---

## Decisão

Adotamos as seguintes regras e diretrizes inegociáveis para o desenvolvimento e manutenção do frontend:

1. **Rigor de Documentação Técnica:** Toda a especificação do design system e padrões visuais residirá na pasta `./docs/frontend/` utilizando **links relativos** (`./` ou `../`) para garantir a portabilidade no GitHub e visualizadores locais.
2. **Padrão de Carregamento Assíncrono:** Todas as requisições paralelas e independentes de dados devem utilizar `Promise.allSettled` em vez de `Promise.all` ou chamadas sequenciais lineares, minimizando a latência e fornecendo resiliência contra falhas parciais de APIs do backend.
3. **Mapeamento de Estados Visuais:** Todos os novos componentes estruturais ou páginas dinâmicas devem obrigatoriamente prever e tratar os estados de **Carregamento** (Skeletons/Spinners), **Dados Ausentes** (`EmptyState`) e **Falhas de Conexão** (Error Fallbacks com injeção de dados de contingência).
4. **Higiene do Repositório (Exclusão de Código Legado):** É proibido reter arquivos órfãos ou rotas desabilitadas na branch de produção. Componentes e telas obsoletos devem ser deletados fisicamente do diretório após migração de suas dependências.
5. **Checklist de Aceite de UI:** Todo Pull Request contendo modificações visuais passará pela validação do checklist oficial de revisão de UI (`docs/frontend/07-governanca/checklist-review-ui.md`).

---

## Alternativas consideradas

| Opção | Prós | Contras |
| :--- | :--- | :--- |
| **Abordagem Ad-Hoc (Sem Governança)** | Velocidade imediata de codificação sem fricção documental. | Rápida fragmentação visual, duplicação massiva de código e quebras de layout sob novos temas. |
| **Isolar a Documentação em Pasta Separada de Frontend** | Mantém a pasta do frontend auto-contida. | Dificulta o acesso e a governança global do repositório, que já centraliza suas decisões em `./docs/`. |

---

## Consequências

**Positivas:**
* **Consistência Visual Estrita:** Unificação da experiência de uso do dashboard e telas de detalhe.
* **Resiliência da Aplicação:** O LexTrack permanece navegável e utilizável mesmo sob falhas críticas em endpoints específicos do backend.
* **Onboarding Simplificado:** Novos integrantes do Squad possuem um mapa factual claro de quais componentes usar, economizando tempo de análise.
* **Redução de Código Morto:** Bundle final compilado mais enxuto e livre de arquivos legados de protótipo.

**Negativas / trade-offs:**
* **Fricção Inicial em PRs:** Os desenvolvedores devem preencher o checklist de UI e validar conformidade de build/lint localmente antes de solicitar o merge.
* **Refatorações Futuras Requeridas:** Demanda tempo dedicado de engenharia nas próximas sprints para limpar as duplicidades e inconsistências apontadas pela auditoria.

**Riscos:**
* **Negligência do Checklist:** Risco de revisores aprovarem alterações de UI sem validar o checklist. 
* *Mitigação:* Configurar revisões obrigatórias de donos de código (Code Owners) para o subdiretório de frontend e rodar linters/testes automatizados na CI.
