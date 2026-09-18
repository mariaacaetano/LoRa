from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from monitoramento.models import Leitura, Sensor

class Command(BaseCommand):
    help = "Regenera o histórico de demonstração com variações suaves."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        Leitura.objects.all().delete()
        now = timezone.now().replace(second=0, microsecond=0)
        temperature_offsets = (0.0, 0.1, 0.2, 0.2, 0.1, 0.0)
        humidity_offsets = (0.0, 0.2, 0.4, 0.3, 0.2, 0.1)
        total = 0

        for sensor_index, sensor in enumerate(Sensor.objects.filter(ativo=True)):
            base_temperature = 23.6 + sensor_index * 0.15
            base_humidity = 64.5 + sensor_index * 0.25
            for point_index, (temperature_offset, humidity_offset) in enumerate(
                zip(temperature_offsets, humidity_offsets)
            ):
                reading = Leitura.objects.create(
                    sensor=sensor,
                    temperatura=round(base_temperature + temperature_offset, 1),
                    umidade=round(base_humidity + humidity_offset, 1),
                )
                timestamp = now - timedelta(minutes=(5 - point_index) * 10)
                Leitura.objects.filter(pk=reading.pk).update(timestamp=timestamp)
                total += 1

        self.stdout.write(self.style.SUCCESS(f"{total} leituras recentes e suaves criadas."))
