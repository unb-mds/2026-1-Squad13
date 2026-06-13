# Checklist de Revisão de UI/Frontend

Sempre valide estes pontos após qualquer mudança:

- [ ] **Tokens:** Foram usados tokens de cores/espaçamento do Tailwind? (Zero hardcoded values).
- [ ] **Responsividade:** O layout se mantém íntegro em diferentes tamanhos de tela?
- [ ] **Acessibilidade:** Contrastes mínimos respeitados? Tags semânticas usadas?
- [ ] **Estados:** Foram tratados os estados de Loading, Empty e Error?
- [ ] **Arquitetura:** O componente está na pasta correta (`features` vs `shared`)?
- [ ] **Documentação:** A mudança exige atualização em `docs/frontend/`?
- [ ] **Dark Mode:** A mudança funciona corretamente no tema escuro?
- [ ] **Performance:** Há renders desnecessários ou chamadas de API duplicadas?
