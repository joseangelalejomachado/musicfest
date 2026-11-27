# Consultas ORM

El código está en `festival/consultas.py`. Resultados obtenidos con SQLite sobre los datos recién cargados con `cargar_datos.py`:

```bash
python manage.py shell < festival/consultas.py
```

Importaciones y constantes comunes:

```python
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Min, Sum

from festival.models import Artista, Concierto, Escenario, Reserva

Usuario = get_user_model()
CONFIRMADA = Reserva.Estado.CONFIRMADA
```

## 9.1 Consultas básicas

### 1. Artistas ordenados alfabéticamente

```python
print(list(Artista.objects.order_by("nombre")))
```

Resultado:

```text
[<Artista: Cumbia Club>, <Artista: Los Faros>, <Artista: Luna Roja>, <Artista: Marea Negra>, <Artista: Neon Wave>, <Artista: Silencio>, <Artista: Sol Andino>, <Artista: The Foxes>]
```

### 2. Artistas activos

```python
print(list(Artista.objects.filter(activo=True)))
```

Resultado:

```text
[<Artista: Cumbia Club>, <Artista: Los Faros>, <Artista: Luna Roja>, <Artista: Neon Wave>, <Artista: Silencio>, <Artista: Sol Andino>, <Artista: The Foxes>]
```

### 3. Artistas de España

```python
print(list(Artista.objects.filter(pais="España")))
```

Resultado:

```text
[<Artista: Los Faros>, <Artista: Luna Roja>, <Artista: Marea Negra>]
```

### 4. Artistas cuyo nombre contiene 'los'

```python
print(list(Artista.objects.filter(nombre__icontains="los")))
```

Resultado:

```text
[<Artista: Los Faros>]
```

### 5. Conciertos entre 20 y 50 euros

```python
for c in Concierto.objects.filter(precio__gte=20, precio__lte=50).order_by("precio"):
    print(c.nombre, c.precio)
```

Resultado:

```text
Tarde Pop 20.00
Noche de Rock 45.00
Electro Fest 50.00
```

### 6. Conciertos gratuitos

```python
print(list(Concierto.objects.filter(precio=0).order_by("nombre")))
```

Resultado:

```text
[<Concierto: Raíces>, <Concierto: Vermut en vivo>]
```

### 7. Conciertos con entradas disponibles y no cancelados

```python
for c in Concierto.objects.filter(entradas_disponibles__gt=0, cancelado=False).order_by("nombre"):
    print(c.nombre, c.entradas_disponibles)
```

Resultado:

```text
Electro Fest 494
Noche de Rock 493
Raíces 44
Tarde Pop 97
Vermut en vivo 50
```

### 8. Conciertos ordenados por fecha y hora

```python
for c in Concierto.objects.order_by("fecha_y_hora"):
    print(c.fecha_y_hora, c.nombre)
```

Resultado:

```text
2027-07-10 16:00:00+00:00 Tarde Pop
2027-07-10 20:00:00+00:00 Noche de Rock
2027-07-11 10:00:00+00:00 Raíces
2027-07-11 21:00:00+00:00 Electro Fest
2027-07-12 11:00:00+00:00 Vermut en vivo
2027-07-12 19:00:00+00:00 Gran Clausura
```

## 9.2 Consultas sobre modelos relacionados

### 9. Conciertos del escenario Principal

```python
print(list(Concierto.objects.filter(escenario__nombre="Principal").order_by("fecha_y_hora")))
```

Resultado:

```text
[<Concierto: Noche de Rock>, <Concierto: Electro Fest>, <Concierto: Gran Clausura>]
```

### 10. Artistas del concierto 'Noche de Rock'

```python
concierto = Concierto.objects.get(nombre="Noche de Rock")
print(list(concierto.artistas.all()))
```

Resultado:

```text
[<Artista: Luna Roja>, <Artista: Marea Negra>]
```

### 11. Conciertos en los que participa 'Luna Roja'

```python
artista = Artista.objects.get(nombre="Luna Roja")
print(list(artista.conciertos.order_by("fecha_y_hora")))
```

Resultado:

```text
[<Concierto: Noche de Rock>, <Concierto: Vermut en vivo>, <Concierto: Gran Clausura>]
```

### 12. Reservas del usuario 'ana'

```python
usuario = Usuario.objects.get(username="ana")
print(list(usuario.reservas.order_by("localizador")))
```

Resultado:

```text
[<Reserva: MF-0001 - Confirmada>, <Reserva: MF-0002 - Confirmada>, <Reserva: MF-0005 - Confirmada>]
```

### 13. Usuarios con alguna reserva confirmada en 'Noche de Rock', sin duplicados

```python
# Las dos condiciones van en el mismo filter(): deben cumplirse en la misma reserva
usuarios = Usuario.objects.filter(
    reservas__concierto__nombre="Noche de Rock",
    reservas__estado=CONFIRMADA,
).distinct().order_by("username")
print(list(usuarios))
```

Resultado:

```text
[<User: ana>, <User: bruno>]
```

### 14. Conciertos con artistas de Reino Unido

```python
print(list(Concierto.objects.filter(artistas__pais="Reino Unido").distinct().order_by("nombre")))
```

Resultado:

```text
[<Concierto: Electro Fest>, <Concierto: Gran Clausura>, <Concierto: Tarde Pop>]
```

### 15. Artistas que no participan en ningún concierto

```python
print(list(Artista.objects.filter(conciertos__isnull=True)))
```

Resultado:

```text
[<Artista: Silencio>]
```

## 9.3 Agregación y agrupación

### 16. Precio medio de los conciertos

```python
print(Concierto.objects.aggregate(precio_medio=Avg("precio")))
```

Resultado:

```text
{'precio_medio': Decimal('30')}
```

### 17. Precio del concierto más caro y del más barato

```python
print(Concierto.objects.aggregate(maximo=Max("precio"), minimo=Min("precio")))
```

Resultado:

```text
{'maximo': Decimal('65'), 'minimo': Decimal('0')}
```

### 18. Aforo total de los escenarios

```python
print(Escenario.objects.aggregate(aforo_total=Sum("aforo")))
```

Resultado:

```text
{'aforo_total': 650}
```

### 19. Número de conciertos de cada escenario

```python
for e in Escenario.objects.annotate(total=Count("conciertos")).order_by("nombre"):
    print(e.nombre, e.total)
```

Resultado:

```text
Acústico 2
Carpa 1
Principal 3
```

### 20. Número de conciertos de cada artista

```python
for a in Artista.objects.annotate(total=Count("conciertos")).order_by("nombre"):
    print(a.nombre, a.total)
```

Resultado:

```text
Cumbia Club 1
Los Faros 2
Luna Roja 3
Marea Negra 1
Neon Wave 2
Silencio 0
Sol Andino 1
The Foxes 1
```

### 21. Entradas confirmadas por concierto

```python
consulta = (
    Reserva.objects.filter(estado=CONFIRMADA)
    .values("concierto__id", "concierto__nombre")
    .annotate(entradas=Sum("numero_entradas"))
    .order_by("concierto__nombre")
)
for fila in consulta:
    print(fila["concierto__nombre"], fila["entradas"])
```

Resultado:

```text
Electro Fest 6
Noche de Rock 7
Raíces 6
Tarde Pop 3
```

### 22. Recaudación de cada concierto (sin reservas canceladas)

```python
consulta = (
    Reserva.objects.filter(estado=CONFIRMADA)
    .values("concierto__id", "concierto__nombre")
    .annotate(recaudacion=Sum("importe_total"))
    .order_by("concierto__nombre")
)
for fila in consulta:
    print(fila["concierto__nombre"], fila["recaudacion"])
```

Resultado:

```text
Electro Fest 300
Noche de Rock 315
Raíces 0
Tarde Pop 60
```

### 23. Tres conciertos con más entradas confirmadas

```python
consulta = (
    Reserva.objects.filter(estado=CONFIRMADA)
    .values("concierto__id", "concierto__nombre")
    .annotate(entradas=Sum("numero_entradas"))
    .order_by("-entradas", "concierto__nombre")[:3]
)
for fila in consulta:
    print(fila["concierto__nombre"], fila["entradas"])
```

Resultado:

```text
Noche de Rock 7
Electro Fest 6
Raíces 6
```

### 24. Usuarios con más de una reserva confirmada

```python
consulta = (
    Reserva.objects.filter(estado=CONFIRMADA)
    .values("usuario__id", "usuario__username")
    .annotate(total=Count("id"))
    .filter(total__gt=1)
    .order_by("usuario__username")
)
for fila in consulta:
    print(fila["usuario__username"], fila["total"])
```

Resultado:

```text
ana 3
```

## Notas

- `filter()` y `exclude()` devuelven un QuerySet; `get()` devuelve un único objeto y lanza `DoesNotExist` si no existe.
- `distinct()` evita filas repetidas al filtrar por relaciones con varios registros (consultas 13 y 14).
- `aggregate()` devuelve un diccionario con un resultado global (16 a 18). `annotate()` añade un valor a cada fila (19 a 24).
- En las consultas 21 a 24 se filtra antes de agrupar con `values().annotate()`, de modo que solo cuentan las reservas confirmadas. Los conciertos sin reservas confirmadas no aparecen.
- La recaudación se calcula con `importe_total`, que guarda lo que se pagó aunque después cambie el precio.
- Las fechas se muestran en UTC (`+00:00`), que es como las devuelve el ORM; en España en julio son dos horas más.
- Con PostgreSQL los resultados son los mismos. Solo cambia la representación de los decimales en las consultas 16, 17 y 22 (por ejemplo, `65.00` en lugar de `65`).
