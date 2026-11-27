from django.contrib import admin

from .models import Artista, Concierto, Escenario, Perfil, Reserva


@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "pais", "genero_musical", "fecha_creacion", "cache", "activo")
    list_filter = ("pais", "genero_musical", "activo")
    search_fields = ("nombre",)
    ordering = ("nombre",)


@admin.register(Escenario)
class EscenarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ubicacion", "aforo")
    ordering = ("nombre",)


class ReservaInline(admin.TabularInline):
    # Permite consultar las reservas desde el concierto, sin modificarlas
    model = Reserva
    fields = ("localizador", "usuario", "numero_entradas", "importe_total", "estado")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Concierto)
class ConciertoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha_y_hora", "escenario", "precio", "entradas_disponibles", "cancelado")
    list_filter = ("fecha_y_hora", "escenario", "cancelado")
    search_fields = ("nombre",)
    ordering = ("fecha_y_hora",)
    filter_horizontal = ("artistas",)
    inlines = (ReservaInline,)

    def get_readonly_fields(self, request, obj=None):
        # Al crear (obj es None) hay que indicar escenario y entradas.
        # Al editar no se pueden tocar a mano.
        if obj:
            return ("escenario", "entradas_disponibles")
        return ()


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "dni", "telefono", "localidad")
    search_fields = ("dni", "usuario__username")
    ordering = ("dni",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("localizador", "usuario", "concierto", "numero_entradas", "importe_total", "estado")
    search_fields = ("localizador",)
    list_filter = ("estado", "concierto")
    ordering = ("localizador",)
    readonly_fields = (
        "localizador", "usuario", "concierto", "fecha_reserva",
        "numero_entradas", "importe_total", "estado",
    )

    # Las reservas solo se crean y cancelan con las funciones de services.py
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
