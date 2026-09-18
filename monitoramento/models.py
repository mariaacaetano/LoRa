from django.conf import settings
from django.db import models

class Perfil(models.Model):
    ROLES = [("gestor", "Gestor"), ("professor", "Professor"), ("pesquisador", "Pesquisador")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    role = models.CharField(max_length=20, choices=ROLES, default="pesquisador")
    def __str__(self): return f"{self.user.username} ({self.role})"

class Sensor(models.Model):
    SETORES = [("bovinocultura", "Bovinocultura"), ("suinocultura", "Suinocultura"), ("avicultura", "Avicultura")]
    nome = models.CharField(max_length=80, unique=True)
    setor = models.CharField(max_length=30, choices=SETORES)
    ativo = models.BooleanField(default=True)
    def __str__(self): return self.nome

class Leitura(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name="leituras")
    temperatura = models.FloatField()
    umidade = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-timestamp"]

