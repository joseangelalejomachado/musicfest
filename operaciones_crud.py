# Operaciones CRUD del apartado 8 (solo ORM)
# Ejecutar UNA vez sobre los datos recién cargados:
#     python manage.py shell < operaciones_crud.py
from datetime import date, datetime
from decimal import Decimal

from django.db.models.deletion import ProtectedError
from django.utils import timezone

from festival.models import Artista, Concierto, Escenario, Reserva

print("\n1. Crear un artista")
nuevo_artista = Artista.objects.create(
    nombre="Brisa", pais="Portugal", genero_musical="Fado",
    fecha_creacion=date(2019, 3, 3), cache=Decimal("1800"),
)
print(nuevo_artista.pk, nuevo_artista)

print("\n2. Crear un escenario")
nuevo_escenario = Escenario.objects.create(
    nombre="Mirador", ubicacion="Zona este", aforo=80, cubierto=False
)
print(nuevo_escenario.pk, nuevo_escenario)

print("\n3. Crear un concierto y asignarle varios artistas")
nuevo_concierto = Concierto.objects.create(
    nombre="Atardecer", fecha_y_hora=timezone.make_aware(datetime(2027, 7, 13, 19, 0)),
    duracion=60, precio=Decimal("15"), escenario=nuevo_escenario,
    entradas_disponibles=nuevo_escenario.aforo,
)
# El concierto debe estar guardado antes de usar la relación N:M
nuevo_concierto.artistas.add(nuevo_artista, Artista.objects.get(nombre="Los Faros"))
print(nuevo_concierto, list(nuevo_concierto.artistas.all()))

print("\n4. Recuperar un artista por su identificador")
print(Artista.objects.get(pk=nuevo_artista.pk))

print("\n5. Recuperar una reserva por su localizador")
print(Reserva.objects.get(localizador="MF-0001"))
try:
    Reserva.objects.get(localizador="NOEXISTE")
except Reserva.DoesNotExist:
    print("No existe la reserva NOEXISTE")

print("\n6. Modificar el precio de un concierto")
print("Antes:", nuevo_concierto.precio)
nuevo_concierto.precio = Decimal("18")
nuevo_concierto.save()
nuevo_concierto.refresh_from_db()
print("Después:", nuevo_concierto.precio)

print("\n7. Cambiar el escenario de un concierto sin reservas")
if nuevo_concierto.reservas.count() == 0:
    carpa = Escenario.objects.get(nombre="Carpa")
    nuevo_concierto.escenario = carpa
    nuevo_concierto.entradas_disponibles = carpa.aforo
    nuevo_concierto.save()
    print(nuevo_concierto.escenario, "| disponibles:", nuevo_concierto.entradas_disponibles)
else:
    print("Tiene reservas: no se cambia")

print("\n8. Añadir un artista a un concierto existente")
nuevo_concierto.artistas.add(Artista.objects.get(nombre="Sol Andino"))
print(list(nuevo_concierto.artistas.all()))

print("\n9. Quitar la participación de un artista sin eliminarlo")
nuevo_concierto.artistas.remove(nuevo_artista)
print(list(nuevo_concierto.artistas.all()))
print("El artista sigue existiendo:", Artista.objects.get(pk=nuevo_artista.pk))

print("\n10. Eliminar un concierto sin reservas")
sin_reservas = Concierto.objects.get(nombre="Vermut en vivo")
print("Reservas:", sin_reservas.reservas.count())
print(sin_reservas.delete())

print("\n11. Intentar eliminar un concierto con reservas")
con_reservas = Concierto.objects.get(nombre="Noche de Rock")
try:
    con_reservas.delete()
except ProtectedError:
    print("No se puede eliminar un concierto con reservas")
print(Concierto.objects.get(pk=con_reservas.pk), "| reservas:", con_reservas.reservas.count())
