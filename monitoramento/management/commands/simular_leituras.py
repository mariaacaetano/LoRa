import random
from django.core.management.base import BaseCommand
from monitoramento.models import Leitura, Sensor

class Command(BaseCommand):
    help = "Gera leituras simuladas para os sensores cadastrados."
    def add_arguments(self, parser): parser.add_argument("--quantidade", type=int, default=30)
    def handle(self, *args, quantidade=30, **kwargs):
        sensors = list(Sensor.objects.filter(ativo=True))
        if not sensors: self.stderr.write("Cadastre sensores antes de simular."); return
        Leitura.objects.bulk_create([Leitura(sensor=random.choice(sensors), temperatura=round(random.gauss(24, 5), 1), umidade=round(random.uniform(40, 90), 1)) for _ in range(quantidade)])
        self.stdout.write(self.style.SUCCESS(f"{quantidade} leituras geradas."))

