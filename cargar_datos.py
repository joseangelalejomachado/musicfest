# Carga inicial de datos (sobre una base de datos vacía y migrada)
# Ejecutar:  python manage.py shell < cargar_datos.py
from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from festival.models import Artista, Concierto, Escenario, Perfil, Reserva

Usuario = get_user_model()

if Artista.objects.count() > 0:
    raise ValueError("La base de datos ya tiene datos: usa una vacía")

with transaction.atomic():
    # ---------- 8 artistas ----------
    datos_artistas = [
        # nombre, país, género, inicio de actividad, caché
        ("Luna Roja", "España", "Rock", date(2010, 3, 1), "5000"),
        ("Los Faros", "España", "Pop", date(2015, 6, 15), "3500"),
        ("Neon Wave", "Reino Unido", "Electrónica", date(2018, 1, 20), "7000"),
        ("Sol Andino", "Argentina", "Folk", date(2008, 9, 5), "2500"),
        ("Marea Negra", "España", "Rock", date(2012, 11, 11), "4000"),
        ("The Foxes", "Reino Unido", "Pop", date(2020, 2, 2), "3000"),
        ("Cumbia Club", "Argentina", "Cumbia", date(2016, 7, 7), "2000"),
        ("Silencio", "México", "Indie", date(2021, 5, 5), "1500"),  # sin conciertos
    ]
    artistas = {}
    for nombre, pais, genero, inicio, cache in datos_artistas:
        artistas[nombre] = Artista.objects.create(
            nombre=nombre, pais=pais, genero_musical=genero,
            fecha_creacion=inicio, cache=Decimal(cache),
        )
    Artista.objects.filter(nombre="Marea Negra").update(activo=False)

    # ---------- 3 escenarios ----------
    escenarios = {}
    for nombre, ubicacion, aforo, cubierto in [
        ("Principal", "Zona norte", 500, False),
        ("Carpa", "Zona sur", 100, True),
        ("Acústico", "Jardín", 50, False),
    ]:
        escenarios[nombre] = Escenario.objects.create(
            nombre=nombre, ubicacion=ubicacion, aforo=aforo, cubierto=cubierto
        )

    # ---------- 6 conciertos ----------
    datos_conciertos = [
        # nombre, día, hora, duración, precio, escenario, cancelado, artistas
        ("Noche de Rock", 10, 22, 120, "45", "Principal", False, ["Luna Roja", "Marea Negra"]),
        ("Tarde Pop", 10, 18, 90, "20", "Carpa", False, ["Los Faros", "The Foxes"]),
        ("Raíces", 11, 12, 75, "0", "Acústico", False, ["Sol Andino", "Cumbia Club"]),
        ("Electro Fest", 11, 23, 180, "50", "Principal", False, ["Neon Wave", "Los Faros"]),
        ("Vermut en vivo", 12, 13, 60, "0", "Acústico", False, ["Luna Roja"]),
        ("Gran Clausura", 12, 21, 150, "65", "Principal", True, ["Luna Roja", "Neon Wave"]),
    ]
    conciertos = {}
    for nombre, dia, hora, duracion, precio, escenario, cancelado, nombres in datos_conciertos:
        concierto = Concierto.objects.create(
            nombre=nombre,
            fecha_y_hora=timezone.make_aware(datetime(2027, 7, dia, hora, 0)),
            duracion=duracion,
            precio=Decimal(precio),
            escenario=escenarios[escenario],
            entradas_disponibles=escenarios[escenario].aforo,
            cancelado=cancelado,
        )
        for nombre_artista in nombres:
            concierto.artistas.add(artistas[nombre_artista])
        conciertos[nombre] = concierto

    # ---------- 5 usuarios y 5 perfiles (datos ficticios, sin contraseña) ----------
    usuarios = {}
    datos_usuarios = [
        ("ana", "00000001A", "600000001", date(2000, 1, 10), "Sevilla"),
        ("bruno", "00000002B", "600000002", date(1998, 4, 22), "Cádiz"),
        ("carla", "00000003C", "600000003", date(1995, 8, 3), "Huelva"),
        ("diego", "00000004D", "600000004", date(2002, 12, 1), "Córdoba"),
        ("elena", "00000005E", "600000005", date(1990, 6, 30), "Sevilla"),
    ]
    for username, dni, telefono, nacimiento, localidad in datos_usuarios:
        usuario = Usuario.objects.create(username=username)
        usuarios[username] = usuario
        Perfil.objects.create(
            usuario=usuario, dni=dni, telefono=telefono,
            fecha_nacimiento=nacimiento, localidad=localidad,
        )

    # ---------- 10 reservas ----------
    confirmada = Reserva.Estado.CONFIRMADA
    cancelada = Reserva.Estado.CANCELADA
    datos_reservas = [
        ("MF-0001", "ana", "Noche de Rock", 2, confirmada),
        ("MF-0002", "ana", "Noche de Rock", 1, confirmada),
        ("MF-0003", "bruno", "Noche de Rock", 4, confirmada),
        ("MF-0004", "carla", "Noche de Rock", 2, cancelada),
        ("MF-0005", "ana", "Tarde Pop", 3, confirmada),
        ("MF-0006", "bruno", "Tarde Pop", 2, cancelada),
        ("MF-0007", "carla", "Raíces", 5, confirmada),
        ("MF-0008", "diego", "Raíces", 1, confirmada),
        ("MF-0009", "elena", "Electro Fest", 6, confirmada),
        ("MF-0010", "diego", "Electro Fest", 2, cancelada),
    ]
    for localizador, username, nombre_concierto, cantidad, estado in datos_reservas:
        concierto = conciertos[nombre_concierto]
        concierto.refresh_from_db()
        Reserva.objects.create(
            localizador=localizador,
            usuario=usuarios[username],
            concierto=concierto,
            numero_entradas=cantidad,
            importe_total=concierto.precio * cantidad,
            estado=estado,
        )
        # Solo las reservas confirmadas ocupan entradas
        if estado == confirmada:
            concierto.entradas_disponibles = concierto.entradas_disponibles - cantidad
            concierto.save(update_fields=["entradas_disponibles"])

print("Artistas:", Artista.objects.count())
print("Escenarios:", Escenario.objects.count())
print("Conciertos:", Concierto.objects.count())
print("Usuarios:", Usuario.objects.count())
print("Perfiles:", Perfil.objects.count())
print("Reservas:", Reserva.objects.count())

print("\nComprobación: disponibles = aforo - entradas confirmadas")
for concierto in Concierto.objects.order_by("fecha_y_hora"):
    vendidas = 0
    for reserva in concierto.reservas.filter(estado=Reserva.Estado.CONFIRMADA):
        vendidas = vendidas + reserva.numero_entradas
    print(
        concierto.nombre, "| aforo", concierto.escenario.aforo,
        "| confirmadas", vendidas, "| disponibles", concierto.entradas_disponibles,
        "| OK" if concierto.escenario.aforo - vendidas == concierto.entradas_disponibles else "| ERROR",
    )
