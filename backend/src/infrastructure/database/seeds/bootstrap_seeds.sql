-- Seed de Bootstrap para baseline_tramitacao
-- Definido conforme a especificação docs/especificacao_metricas_atraso.md

INSERT INTO baseline_tramitacao (escopo, tipo, regime_tramitacao, fase_codigo, mediana_dias, origem_dados)
VALUES
    -- Baselines de Escopo TOTAL (IAR)
    ('TOTAL', 'PL', 'ORDINARIO', NULL, 730, 'BOOTSTRAP_SEED'),
    ('TOTAL', 'PL', 'URGENCIA', NULL, 90, 'BOOTSTRAP_SEED'),
    ('TOTAL', 'PEC', 'ORDINARIO', NULL, 1095, 'BOOTSTRAP_SEED'),
    ('TOTAL', 'MPV', 'ORDINARIO', NULL, 60, 'BOOTSTRAP_SEED'),

    -- Baselines de Escopo FASE (IAF) - ANALISE_COMISSOES
    ('FASE', 'PL', 'ORDINARIO', 'ANALISE_COMISSOES', 180, 'BOOTSTRAP_SEED'),

    -- Baselines de Escopo FASE (IAF) - ETAPA_EXECUTIVO (Constitucional de sanção/veto)
    ('FASE', 'PL', 'ORDINARIO', 'ETAPA_EXECUTIVO', 15, 'BOOTSTRAP_SEED'),
    ('FASE', 'PL', 'URGENCIA', 'ETAPA_EXECUTIVO', 15, 'BOOTSTRAP_SEED'),
    ('FASE', 'PEC', 'ORDINARIO', 'ETAPA_EXECUTIVO', 15, 'BOOTSTRAP_SEED'),
    ('FASE', 'MPV', 'ORDINARIO', 'ETAPA_EXECUTIVO', 15, 'BOOTSTRAP_SEED'),
    ('FASE', NULL, NULL, 'ETAPA_EXECUTIVO', 15, 'BOOTSTRAP_SEED'), -- Fallback global

    -- Baselines de Escopo FASE (IAF) - PROTOCOLO_INICIAL
    ('FASE', 'PL', 'ORDINARIO', 'PROTOCOLO_INICIAL', 15, 'BOOTSTRAP_SEED'),
    ('FASE', 'PL', 'URGENCIA', 'PROTOCOLO_INICIAL', 15, 'BOOTSTRAP_SEED'),
    ('FASE', 'PEC', 'ORDINARIO', 'PROTOCOLO_INICIAL', 15, 'BOOTSTRAP_SEED'),
    ('FASE', 'MPV', 'ORDINARIO', 'PROTOCOLO_INICIAL', 15, 'BOOTSTRAP_SEED'),
    ('FASE', NULL, NULL, 'PROTOCOLO_INICIAL', 15, 'BOOTSTRAP_SEED') -- Fallback global
ON CONFLICT (escopo, tipo, regime_tramitacao, fase_codigo) DO NOTHING;
