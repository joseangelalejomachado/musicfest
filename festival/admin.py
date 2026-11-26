from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "pais", "genero_musical", "fecha_creacion", "cache", "activo")
    list_filter = ("pais", "genero_musical", "activo")
    search_fields = ("nombre",)


@admin.register(Escenario)
class EscenarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ubicacion", "aforo")

@admin.register(Concierto)
class ConciertoAdmin(admin.ModelAdmin):
    list_filter = ("fecha_y_hora", "escenario", "cancelado")

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    search_fields = ("usuario", "dni")

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    search_fields = ("localizador",)
    list_filder = ("concierto", "estado")