# Pruebas del apartado 10.3 (la de reservas simultáneas se hace aparte, ver pruebas.md)
# Ejecutar sobre los datos recién cargados:
#     python manage.py shell < pruebas_transacciones.py
from django.contrib.auth import get_user_model
from django.db import transaction

from festival.models import Concierto, Reserva
from festival.services import cancelar_reserva, realizar_reserva

usuario = get_user_model().objects.get(username="elena")
tarde = Concierto.objects.get(nombre="Tarde Pop")
cancelado = Concierto.objects.get(nombre="Gran Clausura")


def estado(concierto):
    concierto.refresh_from_db()
    return f"disponibles={concierto.entradas_disponibles}, reservas={Reserva.objects.count()}"


print("\n1. Reservar 2 entradas disponibles")
print("Antes:  ", estado(tarde))
reserva = realizar_reserva(usuario.pk, tarde.pk, 2)
print("Aceptada:", reserva.get_estado_display(), "| importe", reserva.importe_total)
print("Después:", estado(tarde))

print("\n2. Reservar más entradas de las disponibles")
print("Antes:  ", estado(tarde))
try:
    realizar_reserva(usuario.pk, tarde.pk, 1000)
except ValueError as error:
    print("Rechazada:", error)
print("Después:", estado(tarde))

print("\n3. Reservar 0 entradas")
print("Antes:  ", estado(tarde))
try:
    realizar_reserva(usuario.pk, tarde.pk, 0)
except ValueError as error:
    print("Rechazada:", error)
print("Después:", estado(tarde))

print("\n4. Reservar para un concierto cancelado")
print("Antes:  ", estado(cancelado))
try:
    realizar_reserva(usuario.pk, cancelado.pk, 1)
except ValueError as error:
    print("Rechazada:", error)
print("Después:", estado(cancelado))

print("\n5. Cancelar una reserva confirmada")
print("Antes:  ", estado(tarde))
cancelada = cancelar_reserva(reserva.pk)
print("Estado:", cancelada.get_estado_display())
print("Después:", estado(tarde))

print("\n6. Cancelar una reserva ya cancelada")
print("Antes:  ", estado(tarde))
try:
    cancelar_reserva(reserva.pk)
except ValueError as error:
    print("Rechazada:", error)
print("Después:", estado(tarde))

print("\n7. Provocar un error durante una transacción")
print("Antes:  ", estado(tarde))
try:
    with transaction.atomic():
        realizar_reserva(usuario.pk, tarde.pk, 3)
        print("Dentro: ", estado(tarde))
        raise RuntimeError("Error simulado")
except RuntimeError as error:
    print("Capturado fuera del atomic():", error)
print("Después:", estado(tarde))
