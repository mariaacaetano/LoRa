import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from monitoramento.models import Leitura, Perfil, Sensor

class Command(BaseCommand):
    help = "Cria usuários e sensores para demonstração."
    def handle(self, *args, **kwargs):
        User = get_user_model()
        for username, role in [("gestor", "gestor"), ("professor", "professor"), ("pesquisador", "pesquisador")]:
            user, created = User.objects.get_or_create(username=username, defaults={"is_staff": role == "gestor"})
            if created: user.set_password("123"); user.save()
            Perfil.objects.update_or_create(user=user, defaults={"role": role})
        nomes_antigos = {"sensor-bov-01": "Comedouro", "sensor-bov-02": "Ordenha", "sensor-bov-03": "Bezerrário", "sensor-sui-01": "Maternidade", "sensor-sui-02": "Área Comum", "sensor-avi-01": "Avicultura"}
        for antigo, novo in nomes_antigos.items():
            sensor = Sensor.objects.filter(nome=antigo).first()
            if sensor and not Sensor.objects.filter(nome=novo).exists():
                sensor.nome = novo
                sensor.save(update_fields=["nome"])
        sensores = [("Comedouro", "bovinocultura"), ("Ordenha", "bovinocultura"), ("Bezerrário", "bovinocultura"), ("Maternidade", "suinocultura"), ("Área Comum", "suinocultura"), ("Avicultura", "avicultura")]
        for nome, setor in sensores:
            Sensor.objects.update_or_create(nome=nome, defaults={"setor": setor, "ativo": True})
        sensores_ativos = list(Sensor.objects.filter(ativo=True))
        if not Leitura.objects.exists():
            historico = []
            for sensor in sensores_ativos:
                for _ in range(10):
                    historico.append(Leitura(sensor=sensor, temperatura=round(random.uniform(20, 28), 1), umidade=round(random.uniform(50, 80), 1)))
            Leitura.objects.bulk_create(historico)
        self.stdout.write(self.style.SUCCESS("Dados de demonstração criados."))
