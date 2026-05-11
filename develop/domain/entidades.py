from datetime import datetime
from zoneinfo import ZoneInfo

class LeiNormalizada:
    def __init__(self, idOrigem, titulo, autores, status, casaOrigem, ementa, dataApresentacao):
        self.idOrigem = idOrigem
        self.titulo = titulo
        self.autores = autores
        self.status = status
        self.casaOrigem = casaOrigem
        self.ementa = ementa
        self.dataApresentacao = dataApresentacao
    
    @property
    def tempo_tramitacao(self):
        if not self.dataApresentacao:
            return "Data de apresentação desconhecida"  
        try:
            tz = ZoneInfo("America/Sao_Paulo")
            agora = datetime.now(tz)
            dataIso = datetime.fromisoformat(self.dataApresentacao).replace(tzinfo=tz)
            delta = agora - dataIso
            
            dias = delta.days
            horas = delta.seconds // 3600
            
            return f"{dias} dias e {horas} horas"
        except Exception:
            return "Erro ao calcular tempo"

    def __str__(self):
        return f"[{self.casaOrigem}]\n- {self.titulo}\n- Status: {self.status}\n- Autores: {self.autores}\n- Ementa: {self.ementa}\n- Tramitando à: {self.tempo_tramitacao}"