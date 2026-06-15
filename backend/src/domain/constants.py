"""
Constantes globais de Domínio do Projeto.
Centraliza regras de negócio quantitativas para evitar duplicação.
"""

# Regra de negócio: uma proposição é considerada em atraso crítico
# se estiver sem conclusão há mais de 180 dias.
LIMITE_DIAS_ATRASO = 180
