from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"), path("logout/", views.sair, name="logout"), path("", views.dashboard, name="dashboard"), path("api/leituras/", views.leituras, name="leituras"), path("api/leituras/<str:setor>/", views.leituras, name="leituras_setor"), path("api/simular/", views.simular, name="simular"), path("api/alertas/", views.alertas, name="alertas")]
