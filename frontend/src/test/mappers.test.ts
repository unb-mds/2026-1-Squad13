import { describe, it, expect, vi, beforeEach } from 'vitest';
import { formatarDataBr, identificarCasaDoEvento, mapMovimentacoesToTransitSteps } from '../shared/lib/mappers';

describe('mappers', () => {
  describe('formatarDataBr', () => {
    it('deve formatar data simples AAAA-MM-DD para DD/MM/AAAA', () => {
      expect(formatarDataBr('2011-05-16')).toBe('16/05/2011');
    });

    it('deve limpar o sufixo Z e formatar de forma idêntica à hora local', () => {
      // Evita o timezone-shift que diminuiria a data em 1 dia
      expect(formatarDataBr('2011-05-16Z')).toBe('16/05/2011');
    });

    it('deve formatar data ISO completa sem sofrer timezone shift', () => {
      expect(formatarDataBr('2014-08-08T13:17Z')).toBe('08/08/2014');
    });

    it('deve retornar string vazia para entrada indefinida', () => {
      expect(formatarDataBr(undefined)).toBe('');
      expect(formatarDataBr('')).toBe('');
    });
  });

  describe('identificarCasaDoEvento', () => {
    it('deve identificar pelo ID prefixado da proposição', () => {
      expect(identificarCasaDoEvento(undefined, undefined, 'senado:123')).toBe('Senado');
      expect(identificarCasaDoEvento(undefined, undefined, 'camara:456')).toBe('Câmara');
    });

    it('deve identificar pela heurística de siglas de órgãos do Senado', () => {
      expect(identificarCasaDoEvento('CCJ')).toBe('Senado');
      expect(identificarCasaDoEvento('SSCLSF')).toBe('Senado');
      expect(identificarCasaDoEvento(undefined, 'Senado Federal')).toBe('Senado');
    });

    it('deve identificar pela heurística de siglas de órgãos da Câmara', () => {
      expect(identificarCasaDoEvento('CCJC')).toBe('Câmara');
      expect(identificarCasaDoEvento('CFT')).toBe('Câmara');
      expect(identificarCasaDoEvento('MESA')).toBe('Câmara');
    });

    it('deve respeitar a flag REMESSA baseando-se na casa de origem', () => {
      expect(identificarCasaDoEvento(undefined, undefined, undefined, 'REMESSA', 'Câmara')).toBe('Senado');
      expect(identificarCasaDoEvento(undefined, undefined, undefined, 'REMESSA', 'Senado')).toBe('Câmara');
    });

    it('deve respeitar a flag RETORNO', () => {
      expect(identificarCasaDoEvento(undefined, undefined, undefined, 'RETORNO', 'Câmara')).toBe('Câmara');
      expect(identificarCasaDoEvento(undefined, undefined, undefined, 'RETORNO', 'Senado')).toBe('Senado');
    });
  });

  describe('mapMovimentacoesToTransitSteps', () => {
    beforeEach(() => {
      // Mock Date.now() para garantir consistência temporal nos testes
      vi.useFakeTimers();
      vi.setSystemTime(new Date('2026-06-25T18:00:00Z'));
    });

    it('deve retornar step de origem padrão para lista vazia', () => {
      const steps = mapMovimentacoesToTransitSteps([]);
      expect(steps).toHaveLength(1);
      expect(steps[0].casa).toBe('Câmara');
      expect(steps[0].tipo).toBe('origem');
    });

    it('deve mapear corretamente o trânsito da PEC 35/2011 (Senado para Câmara)', () => {
      const movs = [
        { proposicaoId: '100215', dataEvento: '2011-05-16Z', siglaOrgao: 'CCJ', descricao: 'Aguardando relator' },
        { proposicaoId: '100215', dataEvento: '2014-08-06Z', siglaOrgao: 'SEXPE', remessaOuRetorno: 'REMESSA', descricao: 'Remetida à Câmara' },
        { proposicaoId: '100215', dataEvento: '2014-08-08T13:17Z', siglaOrgao: 'MESA', descricao: 'Recebimento' },
        { proposicaoId: '100215', dataEvento: '2021-04-20Z', siglaOrgao: 'CCJC', descricao: 'Designação de relator' }
      ];

      const steps = mapMovimentacoesToTransitSteps(movs);

      // Deve detectar 2 steps (Senado como origem, Câmara como revisora)
      expect(steps).toHaveLength(2);

      // Step 1: Senado
      expect(steps[0].casa).toBe('Senado');
      expect(steps[0].tipo).toBe('origem');
      expect(steps[0].dataEntrada).toBe('16/05/2011');
      expect(steps[0].dataSaida).toBe('06/08/2014');
      expect(steps[0].duracaoDias).toBe(1178); // De 2011-05-16 a 2014-08-06

      // Step 2: Câmara
      expect(steps[1].casa).toBe('Câmara');
      expect(steps[1].tipo).toBe('revisora');
      expect(steps[1].dataEntrada).toBe('06/08/2014');
      expect(steps[1].duracaoDias).toBe(4341); // De 2014-08-06 a 2026-06-25 (Date.now() mockado)
    });
  });
});
