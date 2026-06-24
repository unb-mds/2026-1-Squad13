import { describe, it, expect } from 'vitest';
import {
  formatarDataBr,
  normalizarStatus,
  mapProposicaoToProposition,
  mapPeriodoFaseToPhaseEntry,
  mapEventoTramitacaoToTimelineEvent,
  mapMovimentacoesToTransitSteps,
} from '../shared/lib/mappers';
import type { Proposicao, StatusProposicao } from '../shared/types';

describe('formatarDataBr', () => {
  it('retorna data no formato pt-BR quando string ISO valida', () => {
    expect(formatarDataBr('2024-02-28T10:00:00Z')).toBe('28/02/2024');
  });

  it('tenta fazer split simples se for formato yyyy-mm-dd', () => {
    expect(formatarDataBr('2024-02-28')).toBe('28/02/2024');
  });

  it('usa split simples quando ano-mes-dia sao invalidos no construtor de Date', () => {
    expect(formatarDataBr('2024-13-45')).toBe('45/13/2024');
  });

  it('retorna a propria string se for formato invalido', () => {
    expect(formatarDataBr('data-invalida')).toBe('data-invalida');
  });

  it('retorna string vazia quando data nao e fornecida', () => {
    expect(formatarDataBr(undefined)).toBe('');
  });

  it('cai no catch e retorna a propria string se toLocaleDateString lancar erro', () => {
    const originalLocaleString = Date.prototype.toLocaleDateString;
    Date.prototype.toLocaleDateString = () => {
      throw new Error('Erro forçado');
    };
    try {
      expect(formatarDataBr('2024-02-28T10:00:00Z')).toBe('2024-02-28T10:00:00Z');
    } finally {
      Date.prototype.toLocaleDateString = originalLocaleString;
    }
  });

});

describe('normalizarStatus', () => {
  it('preserva status canonicos conhecidos', () => {
    expect(normalizarStatus('Aprovada')).toBe('Aprovada');
    expect(normalizarStatus('Vetada')).toBe('Vetada');
    expect(normalizarStatus('Em Tramitação')).toBe('Em Tramitação');
  });

  it('mapeia termos especiais para status correspondentes', () => {
    expect(normalizarStatus('Norma Jurídica Publicada')).toBe('Sancionada');
    expect(normalizarStatus('Sancionad')).toBe('Sancionada');
    expect(normalizarStatus('VETADO')).toBe('Vetada');
    expect(normalizarStatus('Arquivado definitivamente')).toBe('Arquivada');
    expect(normalizarStatus('Aprovada no Plenario')).toBe('Aprovada');
    expect(normalizarStatus('AGUARDANDO DISTRIBUIÇÃO')).toBe('Em Pauta');
  });

  it('retorna Em Tramitação como fallback', () => {
    expect(normalizarStatus('STATUS_DESCONHECIDO')).toBe('Em Tramitação');
    expect(normalizarStatus(undefined)).toBe('Em Tramitação');
  });
});

describe('mapProposicaoToProposition', () => {
  const baseProp: Proposicao = {
    id: 'camara:123',
    tipo: 'PL',
    numero: '123',
    ano: 2024,
    ementa: 'Ementa de teste',
    ementaResumida: 'Ementa de teste',
    autor: 'Autor Ficticio',
    status: 'Em Tramitação',
    orgaoAtual: 'CCJC',
    dataApresentacao: '2024-01-01',
    dataUltimaMovimentacao: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 dias atras
    orgaoOrigem: 'Câmara dos Deputados',
    temAtraso: false,
    atrasoCritico: false,
    temPrevisaoIA: false,
    tempoTotalDias: 30,
    coberturaDados: 90,
    confiabilidade: 'alta',
    tags: []
  };

  it('mapeia propriedades basicas corretamente', () => {
    const result = mapProposicaoToProposition(baseProp);
    expect(result.id).toBe('camara:123');
    expect(result.numero).toBe('123/2024');
    expect(result.casaAtual).toBe('Câmara');
    expect(result.diasNaEtapa).toBe(5);
    expect(result.statusTramitacao).toBe('em-tramitacao');
    expect(result.status).toBe('Em Tramitação');
  });

  it('identifica casaAtual como Senado quando orgaoOrigem ou orgaoAtual e do Senado', () => {
    const senadoProp = { ...baseProp, orgaoOrigem: 'Senado Federal' };
    expect(mapProposicaoToProposition(senadoProp).casaAtual).toBe('Senado');
  });

  it('identifica casaAtual como Sanção quando status e Sancionada ou Vetada', () => {
    const sancionadaProp = { ...baseProp, status: 'Sancionada' as StatusProposicao };
    expect(mapProposicaoToProposition(sancionadaProp).casaAtual).toBe('Sanção');
  });

  it('identifica statusTramitacao como em-atraso se temAtraso e true', () => {
    const atrasoProp = { ...baseProp, temAtraso: true, tempoTotalDias: 200 };
    const result = mapProposicaoToProposition(atrasoProp);
    expect(result.statusTramitacao).toBe('em-atraso');
    expect(result.atraso).toBe(20); // 200 - 180 = 20
    expect(result.statusLabel).toBe('Em atraso');
  });

  it('identifica statusTramitacao como aprovada/arquivada/aguardando baseado em palavras-chave', () => {
    expect(mapProposicaoToProposition({ ...baseProp, status: 'Rejeitada' as unknown as StatusProposicao }).statusTramitacao).toBe('arquivada');
    expect(mapProposicaoToProposition({ ...baseProp, status: 'Aprovada' as StatusProposicao }).statusTramitacao).toBe('aprovada');
    expect(mapProposicaoToProposition({ ...baseProp, status: 'Aguardando' as unknown as StatusProposicao }).statusTramitacao).toBe('aguardando');
  });
});

describe('mapPeriodoFaseToPhaseEntry', () => {
  const basePeriod = {
    faseNome: 'CCJC',
    ocorrencia: 1,
    dataEntrada: '2024-01-01',
    dataSaida: '2024-01-10',
    diasCorridos: 10,
    motivoTravamento: null,
    numeroTurno: null,
    subtipoFase: null,
  };

  it('converte PeriodoFaseResponse do backend para PhaseEntry do frontend', () => {
    const result = mapPeriodoFaseToPhaseEntry(basePeriod, 0, true);
    expect(result.id).toBe('1');
    expect(result.fase).toBe('CCJC');
    expect(result.duracaoDias).toBe(10);
    expect(result.isCurrent).toBe(true);
    expect(result.atrasoDias).toBe(0);
  });

  it('calcula atrasoDias se diasCorridos > 45', () => {
    const slowPeriod = { ...basePeriod, diasCorridos: 50 };
    expect(mapPeriodoFaseToPhaseEntry(slowPeriod, 0, false).atrasoDias).toBe(5);
  });
});

describe('mapEventoTramitacaoToTimelineEvent', () => {
  const baseEvent = {
    sequencia: 1,
    dataEvento: '2024-01-01T14:00:00',
    siglaOrgao: 'CCJC',
    tipoEvento: 'Apresentacao de Proposicao',
    descricaoOriginal: 'Apresentação da proposição PL 123/2024',
    relevante: true,
  };

  it('converte evento do backend para TimelineEvent', () => {
    const result = mapEventoTramitacaoToTimelineEvent(baseEvent);
    expect(result.id).toBe('1');
    expect(result.orgao).toBe('CCJC');
    expect(result.tipoEvento).toBe('mudanca-fase');
    expect(result.hora).toBe('14:00');
    expect(result.isRelevante).toBe(true);
  });

  it('identifica tipos de eventos baseados em palavras-chave', () => {
    expect(mapEventoTramitacaoToTimelineEvent({ ...baseEvent, tipoEvento: 'Votacao' }).tipoEvento).toBe('deliberacao');
    expect(mapEventoTramitacaoToTimelineEvent({ ...baseEvent, tipoEvento: 'Apensamento' }).tipoEvento).toBe('apensamento');
    expect(mapEventoTramitacaoToTimelineEvent({ ...baseEvent, tipoEvento: 'Remessa' }).tipoEvento).toBe('transicao-casa');
    expect(mapEventoTramitacaoToTimelineEvent({ ...baseEvent, tipoEvento: 'Despacho' }).tipoEvento).toBe('despacho');
    expect(mapEventoTramitacaoToTimelineEvent({ ...baseEvent, tipoEvento: 'Parecer' }).tipoEvento).toBe('parecer');
    expect(mapEventoTramitacaoToTimelineEvent({ ...baseEvent, tipoEvento: 'Emenda' }).tipoEvento).toBe('emenda');
  });
});

describe('mapMovimentacoesToTransitSteps', () => {
  it('retorna origem padrao quando movimentacoes vazias', () => {
    const result = mapMovimentacoesToTransitSteps([]);
    expect(result.length).toBe(1);
    expect(result[0].casa).toBe('Câmara');
    expect(result[0].tipo).toBe('origem');
  });

  it('calcula etapas de transicao de casa corretamente', () => {
    const movs = [
      { siglaOrgao: 'CCJC', dataEvento: '2024-01-01' },
      { siglaOrgao: 'SF', dataEvento: '2024-01-10' }
    ];
    const result = mapMovimentacoesToTransitSteps(movs);
    expect(result.length).toBe(2);
    expect(result[0].casa).toBe('Câmara');
    expect(result[0].duracaoDias).toBe(9);
    expect(result[0].dataSaida).toBe('10/01/2024');
    expect(result[1].casa).toBe('Senado');
  });
});
