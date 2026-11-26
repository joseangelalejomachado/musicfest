from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

# Create your models here.

class Artista(models.Model):
    nombre = models.CharField(max_length = 13, unique= True)
    pais = models.CharField(max_length=13)
    genero_musical = models.CharField(max_length=20)
    fecha_creacion = models.DateField()
    cache = models.DecimalField(max_digits=8, decimal_places=2)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre}"
    
class Escenario(models.Model):
    nombre = models.CharField(max_length=15, unique=True)
    ubicacion = models.CharField(max_length= 30)
    aforo = models.PositiveIntegerField("Aforo máximo")
    cubierto = models.BooleanField(default = False)
    
    def __str__(self):
        return f"{self.nombre} - {self.aforo}"

class Concierto (models.Model):
    nombre = models.CharField(max_length=15, unique=True)
    fecha_y_hora = models.DateTimeField()
    duracion = models.PositiveIntegerField("Duración en minutos del concierto")
    precio = models.PositiveIntegerField()
    escenario = models.ForeignKey(Escenario, on_delete=models.PROTECT, related_name='conciertos') 
    # No se deben borrar los conciertos si se borran los escenarios
    artistas = models.ManyToManyField(Artista, related_name='conciertos', blank=True) # Un conciertopuede tener varios artistas y un artista participa en diferentes conciertos
    entradas_disponibles = models.PositiveIntegerField("Cantidad de entradas disponibles")
    cancelado = models.BooleanField(default= False)
    descripcion = models.TextField(blank=True)
    
    # Las entradas no pueden superar el aforo máximo del escenario - Indicado por prof -> No se hace

    def __str__(self):
        return f"{self.nombre}"

class Perfil(models.Model):
    usuario = get_user_model()
    dni = models.CharField(max_length=9, unique=True)
    telefono = models.CharField(max_length=14) # 14 por si pone el prefijo
    fecha_nacimiento = models.DateField()
    localidad = models.CharField(max_length= 35)
    
    def __str__(self):
        return f"{self.dni} - {self.telefono}"
    
class Reserva(models.Model):
    class Estado(models.TextChoices):
        CONFIRMADA = "CON", "Confirmada"
        CANCELADA = "CAN", "Cancelada"
    localizador = models.CharField(max_length=10, unique=True)
    usuario = models.CharField(max_length=15, unique=False)
    concierto = models.ForeignKey(Concierto, on_delete=models.PROTECT, related_name='reservas')
    # No se puede eliminar conciertos con reservas asociadas
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    numero_entradas = models.PositiveIntegerField("Cantidad de entradas reservadas", default=1)
    estado = models.CharField(
        max_length=3, choices=Estado.choices, default=Estado.CONFIRMADA
    )
    
    def __str__(self) -> str:
        return f"{self.localizador} - {self.estado}"