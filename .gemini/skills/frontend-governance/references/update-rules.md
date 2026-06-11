# Regras de Atualização Documental

Determine se a mudança exige atualização de contexto seguindo estas regras:

### 1. Quando atualizar `docs/frontend/`?
- Quando um novo componente reutilizável é criado em `shared/`.
- Quando um padrão de interação é alterado (ex: como um modal fecha).
- Quando a estrutura de uma feature muda significativamente.

### 2. Quando criar uma ADR?
- Mudança de biblioteca principal (ex: trocar Lucide por outro).
- Mudança na estratégia de gerenciamento de estado.
- Decisões arquiteturais que afetem todo o frontend.

### 3. Quando registrar um Change Log?
- Mudanças visuais que alterem o "look and feel" de telas principais.
- Ajustes finos em Design Tokens globais.

### 4. Quando abrir Issue de Follow-up?
- Quando uma solução temporária ("hack") é necessária por limitação técnica.
- Quando uma refatoração maior é identificada mas está fora do escopo da task.
