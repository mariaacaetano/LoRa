import json
import random
import time
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseForbidden
from django.shortcuts import render
from .models import Leitura, Sensor

MIN_TEMPERATURE = 22.5
MAX_TEMPERATURE = 25.5
SIMULATION_CYCLE = 6

def role(user):
    return getattr(getattr(user, "perfil", None), "role", "pesquisador")

def sair(request):
    logout(request)
    from django.shortcuts import redirect
    return redirect("login")

@login_required
def dashboard(request):
    return render(request, "dashboard.html", {"role": role(request.user)})

@login_required
def leituras(request, setor=None):
    qs = Leitura.objects.select_related("sensor")
    if setor: qs = qs.filter(sensor__setor=setor)
    limite = max(2, min(int(request.GET.get("limite", 6)), 12))
    leituras_por_sensor = []
    sensor_ids = qs.order_by().values_list("sensor_id", flat=True).distinct()
    for sensor_id in sensor_ids:
        leituras_por_sensor.extend(qs.filter(sensor_id=sensor_id)[:limite])
    qs = sorted(leituras_por_sensor, key=lambda leitura: leitura.timestamp, reverse=True)
    data = [{"id": x.pk, "sensor": x.sensor.nome, "setor": x.sensor.setor, "temperatura": x.temperatura, "umidade": x.umidade, "timestamp": x.timestamp.isoformat()} for x in qs]
    return JsonResponse(data, safe=False)

@login_required
def simular(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Use POST para simular leituras."}, status=405)
    sensores = list(Sensor.objects.filter(ativo=True))
    iteration = request.session.get("simulation_iteration", 0) + 1
    event = request.session.get("simulation_event", {})
    recovering = request.session.get("simulation_recovering", {})

    if (iteration - 1) % SIMULATION_CYCLE == 0:
        recovering.update(event)
        available = [sensor for sensor in sensores if str(sensor.pk) not in recovering]
        if not available:
            available = sensores
            recovering = {}
        selected = random.sample(available, k=min(random.randint(1, 2), len(available)))
        event = {str(sensor.pk): random.choice((-1, 1)) for sensor in selected}

    leituras = []
    for sensor in sensores:
        anterior = Leitura.objects.filter(sensor=sensor).order_by("-timestamp").first()
        temperatura_anterior = anterior.temperatura if anterior else 24.0
        sensor_key = str(sensor.pk)

        if sensor_key in event:
            variacao = event[sensor_key] * random.uniform(0.32, 0.38)
        elif sensor_key in recovering:
            distancia = 24.0 - temperatura_anterior
            if abs(distancia) <= 0.4:
                recovering.pop(sensor_key)
                variacao = random.uniform(-0.1, 0.1)
            else:
                variacao = (1 if distancia > 0 else -1) * random.uniform(0.32, 0.4)
        else:
            # A inércia térmica mantém os ambientes estáveis fora dos ciclos de alerta.
            variacao = random.uniform(-0.1, 0.1)

        temperatura = round(max(15, min(34, temperatura_anterior + variacao)), 1)
        umidade_anterior = anterior.umidade if anterior else 65.0
        umidade = round(max(35, min(95, umidade_anterior + random.uniform(-0.6, 0.6))), 1)
        leituras.append(Leitura(sensor=sensor, temperatura=temperatura, umidade=umidade))
    Leitura.objects.bulk_create(leituras)

    for sensor in sensores:
        antigas = list(
            Leitura.objects.filter(sensor=sensor).values_list("pk", flat=True)[6:]
        )
        if antigas:
            Leitura.objects.filter(pk__in=antigas).delete()

    request.session["simulation_iteration"] = iteration
    request.session["simulation_event"] = event
    request.session["simulation_recovering"] = recovering

    return JsonResponse({
        "geradas": len(leituras),
        "iteracao": iteration,
        "ciclo": ((iteration - 1) % SIMULATION_CYCLE) + 1,
    })

@login_required
def alertas(request):
    if role(request.user) != "gestor": return HttpResponseForbidden("Apenas gestores recebem alertas.")
    def events():
        last = Leitura.objects.order_by("-pk").values_list("pk", flat=True).first() or 0
        while True:
            items = Leitura.objects.select_related("sensor").filter(
                Q(temperatura__lt=MIN_TEMPERATURE) | Q(temperatura__gt=MAX_TEMPERATURE),
                pk__gt=last,
            ).order_by("pk")
            for item in items:
                last = item.pk
                payload = {
                    "id": item.pk,
                    "sensor": item.sensor.nome,
                    "temperatura": item.temperatura,
                    "timestamp": item.timestamp.isoformat(),
                    "mensagem": f"{item.sensor.nome} ({item.sensor.setor}) registrou {item.temperatura:.1f}°C fora da faixa de 22,5°C a 25,5°C.",
                }
                yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(5)
    return StreamingHttpResponse(events(), content_type="text/event-stream")
