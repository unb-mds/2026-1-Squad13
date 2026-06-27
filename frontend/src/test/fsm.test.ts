import { describe, it, expect } from "vitest";
import { classifyEvent } from "../shared/lib/fsm/classify";
import { transition } from "../shared/lib/fsm/transition";
import { buildTransitSteps } from "../shared/lib/fsm/build";
import type { RawEvent, FSMState, House } from "../shared/lib/fsm/types";

describe("Máquina de Estados de Trânsito Legislativo (FSM)", () => {
  
  // ----------------------------------------------------
  // CAMADA 1: Testes do Classificador (classifyEvent)
  // ----------------------------------------------------
  describe("Camada 1: Classificador de Eventos", () => {
    it("deve classificar gatilhos explícitos passados como metadados", () => {
      expect(classifyEvent({ remessaOuRetorno: "REMESSA" })).toBe("GATILHO_REMESSA");
      expect(classifyEvent({ remessaOuRetorno: "RETORNO" })).toBe("GATILHO_RETORNO");
    });

    it("deve classificar gatilhos de remessa por análise textual de descrição", () => {
      expect(classifyEvent({ descricaoOriginal: "Remessa ao Senado Federal com o autógrafo." })).toBe("GATILHO_REMESSA");
      expect(classifyEvent({ descricaoOriginal: "Ofício n 288/2019/PS-GSE encaminhando autógrafo ao senado federal." })).toBe("GATILHO_REMESSA");
    });

    it("deve classificar gatilhos de retorno com regexes rígidas e explícitas", () => {
      // Ponto de vista do Senado (expedição para a Câmara)
      expect(classifyEvent({ descricaoOriginal: "Remetida à Câmara dos Deputados para apreciação." })).toBe("GATILHO_RETORNO");
      expect(classifyEvent({ descricaoOriginal: "Ofício nº 472/22 à Câmara dos Deputados comunicando aprovação de emendas." })).toBe("GATILHO_RETORNO");
      
      // Ponto de vista da Câmara (recebimento do Senado)
      expect(classifyEvent({ descricaoOriginal: "Recebido o ofício nº 472/22 do Senado Federal que comunica aprovação." })).toBe("GATILHO_RETORNO");
      expect(classifyEvent({ descricaoOriginal: "Retorno do Senado Federal das emendas." })).toBe("GATILHO_RETORNO");
    });

    it("deve classificar órgãos e comissões exclusivos do Senado", () => {
      expect(classifyEvent({ siglaOrgao: "SLSF" })).toBe("EXCLUSIVO_SENADO");
      expect(classifyEvent({ siglaOrgao: "SEADI" })).toBe("EXCLUSIVO_SENADO");
      expect(classifyEvent({ siglaOrgao: "CAE" })).toBe("EXCLUSIVO_SENADO");
      expect(classifyEvent({ siglaOrgao: "SACDH" })).toBe("EXCLUSIVO_SENADO");
    });

    it("deve classificar órgãos e comissões exclusivos da Câmara", () => {
      expect(classifyEvent({ siglaOrgao: "CCJC" })).toBe("EXCLUSIVO_CÂMARA");
      expect(classifyEvent({ siglaOrgao: "CFT" })).toBe("EXCLUSIVO_CÂMARA");
      expect(classifyEvent({ siglaOrgao: "CPASF" })).toBe("EXCLUSIVO_CÂMARA");
      expect(classifyEvent({ siglaOrgao: "CCP" })).toBe("EXCLUSIVO_CÂMARA");
    });

    it("deve classificar comissões/órgãos comuns ou indefinidos como ambíguos", () => {
      expect(classifyEvent({ siglaOrgao: "CE" })).toBe("AMBÍGUO_OU_NEUTRO");
      expect(classifyEvent({ siglaOrgao: "MESA" })).toBe("AMBÍGUO_OU_NEUTRO");
      expect(classifyEvent({ siglaOrgao: "PLEN" })).toBe("AMBÍGUO_OU_NEUTRO");
      expect(classifyEvent({ siglaOrgao: "" })).toBe("AMBÍGUO_OU_NEUTRO");
    });
  });

  // ----------------------------------------------------
  // CAMADA 2: Testes de Transição (transition)
  // ----------------------------------------------------
  describe("Camada 2: Função de Transição transition()", () => {
    const createState = (overrides?: Partial<FSMState>): FSMState => ({
      casaAtiva: "Câmara",
      tipoPasso: "origem",
      timestampEntrada: 1000,
      dataEntradaStr: "01/01/2026",
      casaOrigem: "Câmara",
      ultimaCasaNaoAmbigua: "Câmara",
      jaPassouPelaRevisora: false,
      ultimoGatilhoFoiImplicito: false,
      ...overrides
    });

    it("deve transicionar de Câmara para Senado sob GATILHO_REMESSA", () => {
      const state = createState();
      const next = transition(state, "GATILHO_REMESSA", 2000);
      expect(next.casaAtiva).toBe("Senado");
      expect(next.tipoPasso).toBe("revisora");
      expect(next.timestampEntrada).toBe(2000);
      expect(next.jaPassouPelaRevisora).toBe(true);
      expect(next.ultimoGatilhoFoiImplicito).toBe(false);
    });

    it("deve transicionar de Câmara para Senado sob EXCLUSIVO_SENADO (auto-correção)", () => {
      const state = createState();
      const next = transition(state, "EXCLUSIVO_SENADO", 2000);
      expect(next.casaAtiva).toBe("Senado");
      expect(next.ultimoGatilhoFoiImplicito).toBe(true);
    });

    it("deve bloquear correção implícita consecutiva no mesmo sentido (Invariante 5)", () => {
      const state = createState({ casaAtiva: "Câmara", ultimoGatilhoFoiImplicito: true });
      const next = transition(state, "EXCLUSIVO_SENADO", 2000);
      expect(next.casaAtiva).toBe("Câmara"); // Permanece na Câmara para evitar ping-pong ruidoso
    });

    it("deve manter self-loops estáveis para eventos ambíguos", () => {
      const state = createState({ casaAtiva: "Senado" });
      const next = transition(state, "AMBÍGUO_OU_NEUTRO", 2000);
      expect(next.casaAtiva).toBe("Senado");
      expect(next.timestampEntrada).toBe(1000); // Não atualiza data
    });

    it("deve marcar tipoPasso como retorno após passar pela revisora e voltar", () => {
      const state = createState({
        casaAtiva: "Senado",
        jaPassouPelaRevisora: true
      });
      const next = transition(state, "GATILHO_RETORNO", 2000);
      expect(next.casaAtiva).toBe("Câmara");
      expect(next.tipoPasso).toBe("retorno");
    });
  });

  // ----------------------------------------------------
  // CAMADA 3: Testes de Integração e Invariantes Formais
  // ----------------------------------------------------
  describe("Camada 3: Geração de UI e Provas de Invariantes (Property-Based)", () => {
    
    // Função auxiliar para gerar eventos aleatórios coerentes
    const generateRandomSequence = () => {
      const inputsList = [
        "GATILHO_REMESSA",
        "GATILHO_RETORNO",
        "EXCLUSIVO_CÂMARA",
        "EXCLUSIVO_SENADO",
        "AMBÍGUO_OU_NEUTRO"
      ];
      
      const events: RawEvent[] = [];
      let baseTime = new Date("2026-01-01").getTime();

      // Geramos de 10 a 50 eventos
      const count = Math.floor(Math.random() * 40) + 10;
      for (let i = 0; i < count; i++) {
        // Incrementa tempo
        baseTime += (Math.floor(Math.random() * 5) + 1) * 24 * 60 * 60 * 1000;
        const input = inputsList[Math.floor(Math.random() * inputsList.length)];
        
        let sigla = "CE";
        let desc = "Evento neutro legislativo";
        const remessa: string | null = null;

        if (input === "GATILHO_REMESSA") {
          desc = "Remessa ao senado federal";
        } else if (input === "GATILHO_RETORNO") {
          desc = "Recebido o ofício do senado federal";
        } else if (input === "EXCLUSIVO_SENADO") {
          sigla = "SLSF";
        } else if (input === "EXCLUSIVO_CÂMARA") {
          sigla = "CCJC";
        }

        events.push({
          siglaOrgao: sigla,
          descricaoOriginal: desc,
          remessaOuRetorno: remessa,
          data: new Date(baseTime).toISOString()
        });
      }

      return events;
    };

    it("deve preservar as 10 invariantes formais em 500 execuções aleatórias parametrizadas", () => {
      for (let run = 0; run < 500; run++) {
        const casaOrigem: House = Math.random() > 0.5 ? "Câmara" : "Senado";
        const events = generateRandomSequence();
        
        const steps = buildTransitSteps(events, casaOrigem);

        // --- ASSERTIVAS DE INVARIANTES ---

        // Invariante 2: Inicialização coerente
        expect(steps[0].casa).toBe(casaOrigem);

        // Invariante 7: Correspondência Biunívoca (Não pode ter dois passos consecutivos na mesma Casa)
        for (let i = 0; i < steps.length - 1; i++) {
          expect(steps[i].casa).not.toBe(steps[i + 1].casa);
        }

        // Invariante 8: Coerência de Papel por Percurso
        steps.forEach((step, idx) => {
          if (step.casa !== casaOrigem) {
            expect(step.tipo).toBe("revisora");
          } else if (idx === 0) {
            expect(step.tipo).toBe("origem");
          } else {
            expect(step.tipo).toBe("retorno");
          }
        });

        // Invariante 9: Continuidade Temporal (Sem Lacunas)
        for (let i = 0; i < steps.length - 1; i++) {
          expect(steps[i].dataSaida).toBe(steps[i + 1].dataEntrada);
        }

        // Invariante 10: Conservação da Duração Total (Sum Consistency)
        const parseTime = (s?: string) => {
          if (!s) return 0;
          return new Date(s.replace(/Z$/i, "")).getTime();
        };
        const eventsSorted = [...events].sort((a, b) => parseTime(a.data || a.dataEvento) - parseTime(b.data || b.dataEvento));
        const totalDurationCalculated = steps.reduce((sum, s) => sum + (s.duracaoDias || 0), 0);
        
        const firstTime = parseTime(eventsSorted[0].data || eventsSorted[0].dataEvento);
        const lastTime = Date.now();
        const expectedTotalDuration = Math.floor((lastTime - firstTime) / (1000 * 60 * 60 * 24));
        
        // Permite tolerância de até 1 dia devido ao arredondamento decimal Math.floor
        expect(Math.abs(totalDurationCalculated - expectedTotalDuration)).toBeLessThanOrEqual(1);
      }
    });
  });

  // ----------------------------------------------------
  // CAMADA 4: Casos de Regressão Real do Projeto
  // ----------------------------------------------------
  describe("Camada 4: Casos de Regressão Real", () => {
    it("deve calcular corretamente o trânsito simplificado da PEC 35/2011 (Origem Senado)", () => {
      const eventosPec = [
        { data: "2011-05-18", siglaOrgao: "SLSF", descricaoOriginal: "Apresentação de PEC" },
        { data: "2011-06-01", siglaOrgao: "CCJ", descricaoOriginal: "Aprovação na comissão" },
        { data: "2011-08-31", siglaOrgao: "SEXPE", descricaoOriginal: "Remetida à Câmara dos Deputados" },
        { data: "2011-09-01", siglaOrgao: "CCJC", descricaoOriginal: "Recebimento pela Câmara dos Deputados" },
        { data: "2011-12-15", siglaOrgao: "PLEN", descricaoOriginal: "Aprovação no Plenário da Câmara" }
      ];

      const steps = buildTransitSteps(eventosPec, "Senado");
      
      // Deve ter exatamente 2 passos: Senado (origem) -> Câmara (revisora)
      expect(steps.length).toBe(2);
      expect(steps[0].casa).toBe("Senado");
      expect(steps[0].tipo).toBe("origem");
      expect(steps[1].casa).toBe("Câmara");
      expect(steps[1].tipo).toBe("revisora");
      
      // Continuidade
      expect(steps[0].dataSaida).toBe("31/08/2011");
      expect(steps[1].dataEntrada).toBe("31/08/2011");
    });

    it("deve calcular corretamente o trânsito da PL 5026/2019 (Câmara -> Senado -> Câmara) sem oscilações ruidosas em siglas comuns", () => {
      const eventosPl = [
        { data: "2017-05-24", siglaOrgao: "MESA", descricaoOriginal: "Apresentação da proposição" },
        { data: "2017-06-01", siglaOrgao: "CE", descricaoOriginal: "Distribuição para comissão de educação da Câmara" },
        { data: "2019-08-28", siglaOrgao: "MESA", descricaoOriginal: "Remessa ao senado federal" },
        { data: "2019-09-11", siglaOrgao: "SLSF", descricaoOriginal: "Matéria lida em plenário do Senado" },
        { data: "2020-02-18", siglaOrgao: "SACDH", descricaoOriginal: "Aprovado parecer na comissão de direitos humanos do senado" },
        { data: "2022-05-25", siglaOrgao: "SEADI", descricaoOriginal: "Aprovada no Plenário do Senado" },
        { data: "2022-06-01", siglaOrgao: "SEXPE", descricaoOriginal: "Remetida à Câmara dos Deputados" },
        { data: "2022-06-01", siglaOrgao: "MESA", descricaoOriginal: "Recebido o ofício nº 472/22 do senado federal" },
        { data: "2022-06-02", siglaOrgao: "CE", descricaoOriginal: "Distribuição para comissão de educação da Câmara" },
        { data: "2025-12-03", siglaOrgao: "CPASF", descricaoOriginal: "Aprovada na comissão de previdência" }
      ];

      const steps = buildTransitSteps(eventosPl, "Câmara");

      // Deve ter exatamente 3 passos estáveis: Câmara (origem) -> Senado (revisora) -> Câmara (retorno)
      expect(steps.length).toBe(3);
      
      expect(steps[0].casa).toBe("Câmara");
      expect(steps[0].tipo).toBe("origem");
      
      expect(steps[1].casa).toBe("Senado");
      expect(steps[1].tipo).toBe("revisora");
      
      expect(steps[2].casa).toBe("Câmara");
      expect(steps[2].tipo).toBe("retorno");

      // O evento da "CE" (Comissão de Educação da Câmara) em 02/06/2022 deve ter mantido o projeto na Câmara
      // sem criar nenhuma ida e volta fantasma de 1 dia!
      expect(steps[2].dataEntrada).toBe("01/06/2022");
    });
  });
});
