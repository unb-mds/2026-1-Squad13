## Descrição
Implementar testes de contrato para as APIs externas (Câmara e Senado) utilizando ferramentas de gravação de requisições como `VCR.py` ou `pytest-recording`.

## Racional Técnico
Mocks manuais podem ficar defasados em relação às APIs reais sem que a suíte de testes detecte. O uso de "cassetes" (gravações de requisições reais) garante que o sistema está sendo testado contra payloads autênticos, mantendo a velocidade de execução (sem chamadas de rede reais no CI) e permitindo a detecção de mudanças de contrato quando as gravações forem atualizadas periodicamente.

## Critérios de Aceite
- [ ] Configuração de `VCR.py` ou `pytest-recording` no backend.
- [ ] Gravação de cassetes para os principais fluxos de integração (busca de proposição, detalhamento, movimentações).
- [ ] Documentação de como atualizar os cassetes.
- [ ] CI configurado para rodar apenas com cassetes existentes (fail if missing).
