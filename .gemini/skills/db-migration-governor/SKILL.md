---
name: db-migration-governor
description: Use when database models (SQLModel) or seed data scripts are modified to verify DB schema initialization and prevent workspace synchronization issues.
---

# DB Migration Governor

Você é responsável por garantir que as modificações no banco de dados relacional e nos scripts de sementes (seeds) permaneçam consistentes, idempotentes e fáceis de sincronizar entre os desenvolvedores.

## Objetivo
Garantir que alterações nas entidades (`src/domain/entities/` ou `src/infrastructure/database/models/`) e nos scripts de dados sejam validadas e testadas localmente.

## Processo obrigatório

1. **Alteração em Entidades de Persistência**:
   - Sempre que alterar uma entidade SQLModel, verifique se campos novos obrigatórios possuem um valor `default` ou se aceitam `None` (nullable), para evitar quebras em registros existentes.
   - Se houver alterações estruturais incompatíveis no MVP, comunique a necessidade de reiniciar o banco de dados.

2. **Inicialização do Banco**:
   - Utilize o script `scripts/db/init.sh` para reconstruir o banco local de desenvolvimento e testar a aplicação de DDLs (Data Definition Language) do SQLModel.
   - Certifique-se de que a inicialização não dependa de conexões ativas com a internet (deve ser baseada em arquivos de seed locais).

3. **Validação do Seed de Produção/Demo**:
   - Toda alteração que adicione tabelas de apoio (como novos órgãos legislativos ou fases) deve ser refletida em `src/seed.py` ou `src/init_db.py`.
   - Utilize o script `scripts/dev/seed.sh` para certificar-se de que a injeção inicial de dados (seja estática ou conectando-se a dados mockados das APIs) ocorre sem erros.

4. **Idempotência**:
   - Os seeds de dados devem ser estritamente idempotentes. Rodar o seed duas vezes seguidas **nunca** deve duplicar registros no banco de dados.

## Scripts da Skill
- `scripts/db/init.sh`: Executa `init_db.py` para recriar as tabelas.
- `scripts/dev/seed.sh`: Executa `seed.py` para alimentar tabelas adicionais e validar consistência.
