# Categorias de Drift Frontend

Definição dos tipos de divergência encontrados durante a auditoria.

### 1. Drift Visual
- Uso de cores fora da paleta semântica.
- Fontes ou tamanhos de texto inconsistentes.
- Espaçamentos (padding/margin) que não seguem a grade.

### 2. Drift Estrutural
- Componentes de feature importando outros componentes de feature (acoplamento).
- Lógica de domínio dentro da pasta `shared/ui`.
- Ausência de padrões Feature-Based.

### 3. Drift Funcional
- Componentes que não tratam estados de erro ou loading conforme especificado.
- Comportamentos de UI que divergem do walkthrough ou ADRs.

### 4. Drift de Governança
- Implementações sem documentação correspondente em `docs/frontend/`.
- Mudanças arquiteturais sem ADR.
- Decisões de design não registradas nos logs.
