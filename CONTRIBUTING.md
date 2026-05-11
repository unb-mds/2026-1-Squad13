# Guia de Contribuição

Referência rápida para contribuir com o projeto de forma consistente.

---

## Branches

Crie sempre uma branch a partir da `main` atualizada. Use o prefixo correspondente ao tipo de mudança:

| Prefixo | Quando usar |
|---------|-------------|
| `feat/` | nova funcionalidade |
| `fix/` | correção de bug |
| `chore/` | tarefas técnicas (config, deps, CI) |
| `docs/` | documentação |
| `refactor/` | refatoração sem mudança de comportamento |

```bash
git checkout main
git pull origin main
git checkout -b feat/nome-descritivo
```

---

## Commits

O projeto adota [Conventional Commits](https://www.conventionalcommits.org/).

```
<tipo>(escopo opcional): descrição curta no imperativo

feat(frontend): adiciona filtro por status de tramitação
fix(backend): corrige paginação na listagem de proposições
chore(frontend): atualiza dependências do ESLint
docs: atualiza guia de contribuição
```

Tipos aceitos: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`.

---

## Pull Requests

1. Abra o PR sempre para `main`.
2. Use um título no formato Conventional Commits.
3. Descreva o que mudou, por que mudou e o que o revisor deve verificar.
4. Não faça merge sem o CI passar.

O CI é disparado automaticamente ao abrir ou atualizar um PR.

---

## CI/CD — GitHub Actions

O repositório possui workflows separados por área, disparados apenas quando os arquivos relevantes mudam (path filter):

### Frontend (`frontend/**`)

Arquivo: `.github/workflows/frontend.yml`

- Roda em todo PR para `main` que altere `frontend/`
- Instala dependências: `npm ci`
- Verifica build: `npm run build`

### Backend (`backend/**`)

Arquivo: `.github/workflows/backend.yml`

- Roda em todo PR para `main` que altere `backend/`
- Instala dependências: `uv sync`
- Verifica sintaxe: `py_compile src/main.py`

### Squad Dashboard

Arquivos: `.github/workflows/deploy-squad-dashboard.yml` e `update-squad-dashboard-data.yml`

- Deploy automático para GitHub Pages a cada push para `main` em `squad-dashboard/`

---

## Qualidade de código — Frontend

O frontend usa [ESLint](https://eslint.org/) com flat config (`eslint.config.js`), configurado para React + TypeScript + Vite.

```bash
cd frontend
npm run lint          # reporta erros e avisos
npm run lint -- --fix # corrige automaticamente o que for possível
```

Execute o lint antes de abrir o PR. O CI ainda não inclui esse passo automaticamente — ele será adicionado em breve.

Regras ativas:

- Regras recomendadas de JavaScript (`@eslint/js`)
- Regras recomendadas de TypeScript (`typescript-eslint`)
- Rules of Hooks (`eslint-plugin-react-hooks`)
- Compatibilidade com HMR do Vite (`eslint-plugin-react-refresh`)

---

## Versionamento — o que não commitar

O arquivo `.gitignore` da raiz e o de `frontend/` já estão configurados corretamente. Nunca adicione ao Git:

- `node_modules/` — gerado pelo `npm install`, não deve ser versionado
- `dist/` e `build/` — artefatos de build
- `.env` — variáveis de ambiente locais (use `.env.example` como referência)
- `.venv/`, `__pycache__/` — ambiente Python local

---

## Links úteis

- [Arquitetura do sistema](./ARCHITECTURE.md)
- [ADRs](./docs/adr/)
- [Cheat sheet de comandos](./docs/cheat-sheet.md)
- [Tech stack](./docs/tech-stack.md)
