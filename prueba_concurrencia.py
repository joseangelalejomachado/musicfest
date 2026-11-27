# Prueba 8 del apartado 10.3: dos reservas simultáneas
# Ejecutar sobre los datos recién cargados, en DOS terminales a la vez
# (lanzar la segunda 2 o 3 segundos después de la primera):
#     python manage.py shell < prueba_concurrencia.py
# Quedan 50 entradas en 'Vermut en vivo' y cada terminal pide 30.
import time

from django.contrib.auth import get_user_model
from django.db import transaction

from festival.models import Concierto
from festival.services import realizar_reserva

usuario = get_user_model().objects.get(username="elena")
concierto = Concierto.objects.get(nombre="Vermut en vivo")

try:
    with transaction.atomic():
        reserva = realizar_reserva(usuario.pk, concierto.pk, 30)
        print("Reserva hecha, se mantiene la transacción abierta 8 segundos...")
        time.sleep(8)
    print("ACEPTADA:", reserva.localizador)
except Exception as error:
    print("RECHAZADA:", type(error).__name__, "-", error)

concierto.refresh_from_db()
confirmadas = 0
for r in concierto.reservas.filter(estado="CON"):
    confirmadas = confirmadas + r.numero_entradas
print("Aforo:", concierto.escenario.aforo, "| confirmadas:", confirmadas,
      "| disponibles:", concierto.entradas_disponibles)
