# Pruebas de integridad del apartado 5
# Ejecutar sobre los datos recién cargados:
#     python manage.py shell < pruebas_integridad.py
from datetime import date

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from festival.models import Artista, Concierto, Escenario, Perfil, Reserva

artista = Artista.objects.get(nombre="Luna Roja")
escenario = Escenario.objects.get(nombre="Carpa")
concierto = Concierto.objects.get(nombre="Noche de Rock")
perfil = Perfil.objects.get(dni="00000001A")
otro_perfil = Perfil.objects.get(dni="00000002B")
reserva = Reserva.objects.get(localizador="MF-0001")


def probar(descripcion, objeto, cambios):
    # Intenta un update() que la base de datos debe rechazar
    try:
        with transaction.atomic():
            type(objeto).objects.filter(pk=objeto.pk).update(**cambios)
        print(descripcion, "-> ACEPTADO (error)")
    except IntegrityError as error:
        print(descripcion, "-> RECHAZADO:", str(error).splitlines()[0])


try:
    with transaction.atomic():
        Artista.objects.create(
            nombre="Luna Roja", pais="España", genero_musical="Rock",
            fecha_creacion=date(2020, 1, 1), cache=1,
        )
except IntegrityError as error:
    print("Artista con nombre repetido -> RECHAZADO:", str(error).splitlines()[0])

try:
    with transaction.atomic():
        Escenario.objects.create(nombre="Carpa", ubicacion="Otra", aforo=10)
except IntegrityError as error:
    print("Escenario con nombre repetido -> RECHAZADO:", str(error).splitlines()[0])

probar("Aforo 0", escenario, {"aforo": 0})
probar("Duración 0", concierto, {"duracion": 0})
probar("Caché negativo", artista, {"cache": -1})
probar("Precio negativo", concierto, {"precio": -1})
probar("Entradas disponibles negativas", concierto, {"entradas_disponibles": -1})
probar("DNI repetido", otro_perfil, {"dni": perfil.dni})
probar("Localizador repetido", reserva, {"localizador": "MF-0002"})
probar("Reserva con 0 entradas", reserva, {"numero_entradas": 0})
probar("Segundo perfil para el mismo usuario", otro_perfil, {"usuario": perfil.usuario})

try:
    concierto.delete()
except ProtectedError:
    print("Borrar un concierto con reservas -> RECHAZADO: ProtectedError")
