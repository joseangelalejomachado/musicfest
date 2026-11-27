# Consultas ORM del apartado 9
# Ejecutar sobre los datos recién cargados:
#     python manage.py shell < festival/consultas.py
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Min, Sum

from festival.models import Artista, Concierto, Escenario, Reserva

Usuario = get_user_model()
CONFIRMADA = Reserva.Estado.CONFIRMADA

print("\n# 9.1 Consultas básicas")

print("\n1. Artistas ordenados alfabéticamente")
print(list(Artista.objects.order_by("nombre")))

print("\n2. Artistas activos")
print(list(Artista.objects.filter(activo=True)))

print("\n3. Artistas de España")
print(list(Artista.objects.filter(pais="España")))

print("\n4. Artistas cuyo nombre contiene 'los'")
print(list(Artista.objects.filter(nombre__icontains="los")))

print("\n5. Conciertos entre 20 y 50 euros")
for c in Concierto.objects.filter(precio__gte=20, precio__lte=50).order_by("precio"):
    print(c.nombre, c.precio)

print("\n6. Conciertos gratuitos")
print(list(Concierto.objects.filter(precio=0).order_by("nombre")))

print("\n7. Conciertos con entradas disponibles y no cancelados")
for c in Concierto.objects.filter(entradas_disponibles__gt=0, cancelado=False).order_by("nombre"):
    print(c.nombre, c.entradas_disponibles)

print("\n8. Conciertos ordenados por fecha y hora")
for c in Concierto.objects.order_by("fecha_y_hora"):
    print(c.fecha_y_hora, c.nombre)

print("\n# 9.2 Consultas sobre modelos relacionados")

print("\n9. Conciertos del escenario Principal")
print(list(Concierto.objects.filter(escenario__nombre="Principal").order_by("fecha_y_hora")))

print("\n10. Artistas del concierto 'Noche de Rock'")
concierto = Concierto.objects.get(nombre="Noche de Rock")
print(list(concierto.artistas.all()))

print("\n11. Conciertos en los que participa 'Luna Roja'")
artista = Artista.objects.get(nombre="Luna Roja")
print(list(artista.conciertos.order_by("fecha_y_hora")))

print("\n12. Reservas del usuario 'ana'")
usuario = Usuario.objects.get(username="ana")
print(list(usuario.reservas.order_by("localizador")))

print("\n13. Usuarios con alguna reserva confirmada en 'Noche de Rock', sin duplicados")
# Las dos condiciones van en el mismo filter(): deben cumplirse en la misma reserva
usuarios = Usuario.objects.filter(
    reservas__concierto__nombre="Noche de Rock",
    reservas__estado=CONFIRMADA,
).distinct().order_by("username")
print(list(usuarios))

print("\n14. Conciertos con artistas de Reino Unido")
print(list(Concierto.objects.filter(artistas__pais="Reino Unido").distinct().order_by("nombre")))

print("\n15. Artistas que no participan en ningún concierto")
print(list(Artista.objects.filter(conciertos__isnull=True)))

print("\n# 9.3 Agregación y agrupación")

print("\n16. Precio medio de los conciertos")
print(Concierto.objects.aggregate(precio_medio=Avg("precio")))

print("\n17. Precio del concierto más caro y del más barato")
print(Concierto.objects.aggregate(maximo=Max("precio"), minimo=Min("precio")))

print("\n18. Aforo total de los escenarios")
print(Escenario.objects.aggregate(aforo_total=Sum("aforo")))

print("\n19. Número de conciertos de cada escenario")
for e in Escenario.objects.annotate(total=Count("conciertos")).order_by("nombre"):
    print(e.nombre, e.total)

print("\n20. Número de conciertos de cada artista")
for a in Artista.objects.annotate(total=Count("conciertos")).order_by("nombre"):
    print(a.nombre, a.total)

print("\n21. Entradas confirmadas por concierto")
consulta = (
    Reserva.objects.filter(estado=CONFIRMADA)
    .values("concierto__id", "concierto__nombre")
    .annotate(entradas=Sum("numero_entradas"))
    .order_by("concierto__nombre")
)
for fila in consulta:
    print(fila["concierto__nombre"], fila["entradas"])

print("\n22. Recaudación de cada concierto (sin reservas canceladas)")
consulta = (
    Reserva.objects.filter(estado=CONFIRMADA)
    .values("concierto__id", "concierto__nombre")
    .annotate(recaudacion=Sum("importe_total"))
    .order_by("concierto__nombre")
)
for fila in consulta:
    print(fila["concierto__nombre"], fila["recaudacion"])

print("\n23. Tres conciertos con más entradas confirmadas")
consulta = (
    Reserva.objects.filter(estado=CONFIRMADA)
    .values("concierto__id", "concierto__nombre")
    .annotate(entradas=Sum("numero_entradas"))
    .order_by("-entradas", "concierto__nombre")[:3]
)
for fila in consulta:
    print(fila["concierto__nombre"], fila["entradas"])

print("\n24. Usuarios con más de una reserva confirmada")
consulta = (
    Reserva.objects.filter(estado=CONFIRMADA)
    .values("usuario__id", "usuario__username")
    .annotate(total=Count("id"))
    .filter(total__gt=1)
    .order_by("usuario__username")
)
for fila in consulta:
    print(fila["usuario__username"], fila["total"])
