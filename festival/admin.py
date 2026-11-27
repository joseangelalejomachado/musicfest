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
    list_display = ("nombre", "ubicacion", "aforo", "cubierto")
    ordering = ("nombre",)


class ReservaInline(admin.TabularInline):
    """Reservas de un concierto, solo para consulta."""

    model = Reserva
    fields = ("localizador", "usuario", "numero_entradas", "importe_total", "estado", "fecha_reserva")
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
        # Al crear hay que indicar la disponibilidad; después no se toca a mano
        if obj:
            return ("entradas_disponibles",)
        return ()


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "dni", "telefono", "localidad")
    # En una relación se busca por un campo del modelo relacionado
    search_fields = ("dni", "usuario__username")
    ordering = ("usuario__username",)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("localizador", "usuario", "concierto", "numero_entradas", "importe_total", "estado")
    search_fields = ("localizador",)
    list_filter = ("estado", "concierto")
    ordering = ("-fecha_reserva",)

    # Pendiente: crear y cancelar reservas a través de services.py
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (
                "localizador", "usuario", "concierto", "numero_entradas",
                "importe_total", "estado", "fecha_reserva",
            )
        return ()
