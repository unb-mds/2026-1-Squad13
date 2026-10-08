"""
Testes unitários para o módulo de ordenação customizado (EDA2) no LexTrack.
"""

import unittest
from domain.services.ordenacao.heap_sort import heap_sort
from domain.services.ordenacao.merge_sort import merge_sort
from domain.services.ordenacao.quick_sort import quick_sort
from domain.services.ordenacao.radix_sort import radix_sort


class TestOrdenacaoLexTrack(unittest.TestCase):

    def test_merge_sort_legislative_timeline(self):
        eventos = [
            {"dataEvento": "2026-05-12T14:30:00", "sequencia": 2},
            {"dataEvento": "2026-05-12T10:00:00", "sequencia": 1},
            {"dataEvento": "2026-05-12T10:00:00", "sequencia": 0},
        ]
        ordenados = merge_sort(eventos, key=lambda e: (e["dataEvento"], e["sequencia"]))
        self.assertEqual([e["sequencia"] for e in ordenados], [0, 1, 2])

    def test_radix_sort_gap_collection_years(self):
        gaps = [{"ano": 2024}, {"ano": 2026}, {"ano": 2020}, {"ano": 2025}]
        ordenados = radix_sort(gaps, key=lambda g: g["ano"], reverse=True)
        self.assertEqual([g["ano"] for g in ordenados], [2026, 2025, 2024, 2020])

    def test_heap_sort_gargalos_tiebreak(self):
        orgaos = [
            {"sigla": "CCJC", "taxa": 50},
            {"sigla": "PLEN", "taxa": 80},
            {"sigla": "CFT", "taxa": 50},
        ]
        ordenados = heap_sort(orgaos, key=lambda o: o["taxa"], reverse=True)
        self.assertEqual([o["sigla"] for o in ordenados], ["PLEN", "CCJC", "CFT"])

    def test_quick_sort_temas_dashboard(self):
        temas = [{"dias": 300}, {"dias": 100}, {"dias": 450}, {"dias": 200}]
        ordenados = quick_sort(temas, key=lambda t: t["dias"])
        self.assertEqual([t["dias"] for t in ordenados], [100, 200, 300, 450])


if __name__ == "__main__":
    unittest.main()
