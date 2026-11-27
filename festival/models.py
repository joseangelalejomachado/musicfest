from django.conf import settings
from django.db import models
from django.db.models import Q


class Artista(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    pais = models.CharField(max_length=60)
    genero_musical = models.CharField(max_length=50)
    # Inicio de actividad del artista (la introduce el usuario)
    fecha_creacion = models.DateField()
    cache = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(condition=Q(cache__gte=0), name="artista_cache_no_negativo"),
        ]

    def __str__(self):
        return self.nombre


class Escenario(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=100)
    aforo = models.PositiveIntegerField("Aforo máximo")
    cubierto = models.BooleanField(default=False)

    class Meta:
        constraints = [
            # PositiveIntegerField admite el 0, por eso hace falta la restricción
            models.CheckConstraint(condition=Q(aforo__gt=0), name="escenario_aforo_positivo"),
        ]

    def __str__(self):
        return f"{self.nombre} - {self.aforo}"


class Concierto(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_y_hora = models.DateTimeField()
    duracion = models.PositiveIntegerField("Duración en minutos del concierto")
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    # PROTECT: no se puede borrar un escenario que tenga conciertos
    escenario = models.ForeignKey(Escenario, on_delete=models.PROTECT, related_name="conciertos")
    # Un concierto tiene varios artistas y un artista participa en varios conciertos
    artistas = models.ManyToManyField(Artista, related_name="conciertos", blank=True)
    entradas_disponibles = models.PositiveIntegerField("Cantidad de entradas disponibles")
    cancelado = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True)

    # Las entradas no pueden superar el aforo máximo del escenario - Indicado por prof -> No se hace

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(duracion__gt=0), name="concierto_duracion_positiva"),
            models.CheckConstraint(condition=Q(precio__gte=0), name="concierto_precio_no_negativo"),
        ]

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    # 1:1. CASCADE: el perfil no tiene sentido sin su usuario
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil"
    )
    dni = models.CharField(max_length=9, unique=True)
    telefono = models.CharField(max_length=14)  # 14 por si pone el prefijo
    fecha_nacimiento = models.DateField()
    localidad = models.CharField(max_length=35)

    class Meta:
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"{self.usuario} - {self.dni}"


class Reserva(models.Model):
    class Estado(models.TextChoices):
        CONFIRMADA = "CON", "Confirmada"
        CANCELADA = "CAN", "Cancelada"

    localizador = models.CharField(max_length=10, unique=True)
    # PROTECT: se conserva el historial de reservas
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reservas"
    )
    # PROTECT: no se puede eliminar un concierto con reservas asociadas
    concierto = models.ForeignKey(Concierto, on_delete=models.PROTECT, related_name="reservas")
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    numero_entradas = models.PositiveIntegerField("Cantidad de entradas reservadas", default=1)
    # Se guarda lo que se pagó, aunque después cambie el precio del concierto
    importe_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=3, choices=Estado.choices, default=Estado.CONFIRMADA)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(numero_entradas__gt=0), name="reserva_minimo_una_entrada"
            ),
            models.CheckConstraint(
                condition=Q(importe_total__gte=0), name="reserva_importe_no_negativo"
            ),
        ]

    def __str__(self):
        return f"{self.localizador} - {self.get_estado_display()}"
