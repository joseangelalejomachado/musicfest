# Operaciones CRUD

Todas usan el ORM, sin SQL directo. El código está en `operaciones_crud.py` y se ejecuta una vez sobre los datos recién cargados, porque modifica la base de datos:

```bash
python manage.py shell < operaciones_crud.py
```

Importaciones:

```python
from datetime import date, datetime
from decimal import Decimal

from django.db.models.deletion import ProtectedError
from django.utils import timezone

from festival.models import Artista, Concierto, Escenario, Reserva
```

### 1. Crear un artista

```python
nuevo_artista = Artista.objects.create(
    nombre="Brisa", pais="Portugal", genero_musical="Fado",
    fecha_creacion=date(2019, 3, 3), cache=Decimal("1800"),
)
print(nuevo_artista.pk, nuevo_artista)
```

Resultado:

```text
9 Brisa
```

### 2. Crear un escenario

```python
nuevo_escenario = Escenario.objects.create(
    nombre="Mirador", ubicacion="Zona este", aforo=80, cubierto=False
)
print(nuevo_escenario.pk, nuevo_escenario)
```

Resultado:

```text
4 Mirador - 80
```

### 3. Crear un concierto y asignarle varios artistas

```python
nuevo_concierto = Concierto.objects.create(
    nombre="Atardecer", fecha_y_hora=timezone.make_aware(datetime(2027, 7, 13, 19, 0)),
    duracion=60, precio=Decimal("15"), escenario=nuevo_escenario,
    entradas_disponibles=nuevo_escenario.aforo,
)
# El concierto debe estar guardado antes de usar la relación N:M
nuevo_concierto.artistas.add(nuevo_artista, Artista.objects.get(nombre="Los Faros"))
print(nuevo_concierto, list(nuevo_concierto.artistas.all()))
```

Resultado:

```text
Atardecer [<Artista: Brisa>, <Artista: Los Faros>]
```

### 4. Recuperar un artista por su identificador

```python
print(Artista.objects.get(pk=nuevo_artista.pk))
```

Resultado:

```text
Brisa
```

### 5. Recuperar una reserva por su localizador

```python
print(Reserva.objects.get(localizador="MF-0001"))
try:
    Reserva.objects.get(localizador="NOEXISTE")
except Reserva.DoesNotExist:
    print("No existe la reserva NOEXISTE")
```

Resultado:

```text
MF-0001 - Confirmada
No existe la reserva NOEXISTE
```

### 6. Modificar el precio de un concierto

```python
print("Antes:", nuevo_concierto.precio)
nuevo_concierto.precio = Decimal("18")
nuevo_concierto.save()
nuevo_concierto.refresh_from_db()
print("Después:", nuevo_concierto.precio)
```

Resultado:

```text
Antes: 15
Después: 18.00
```

### 7. Cambiar el escenario de un concierto sin reservas

```python
if nuevo_concierto.reservas.count() == 0:
    carpa = Escenario.objects.get(nombre="Carpa")
    nuevo_concierto.escenario = carpa
    nuevo_concierto.entradas_disponibles = carpa.aforo
    nuevo_concierto.save()
    print(nuevo_concierto.escenario, "| disponibles:", nuevo_concierto.entradas_disponibles)
else:
    print("Tiene reservas: no se cambia")
```

Resultado:

```text
Carpa - 100 | disponibles: 100
```

### 8. Añadir un artista a un concierto existente

```python
nuevo_concierto.artistas.add(Artista.objects.get(nombre="Sol Andino"))
print(list(nuevo_concierto.artistas.all()))
```

Resultado:

```text
[<Artista: Brisa>, <Artista: Los Faros>, <Artista: Sol Andino>]
```

### 9. Quitar la participación de un artista sin eliminarlo

```python
nuevo_concierto.artistas.remove(nuevo_artista)
print(list(nuevo_concierto.artistas.all()))
print("El artista sigue existiendo:", Artista.objects.get(pk=nuevo_artista.pk))
```

Resultado:

```text
[<Artista: Los Faros>, <Artista: Sol Andino>]
El artista sigue existiendo: Brisa
```

### 10. Eliminar un concierto sin reservas

```python
sin_reservas = Concierto.objects.get(nombre="Vermut en vivo")
print("Reservas:", sin_reservas.reservas.count())
print(sin_reservas.delete())
```

Resultado:

```text
Reservas: 0
(2, {'festival.Concierto_artistas': 1, 'festival.Concierto': 1})
```

### 11. Intentar eliminar un concierto con reservas

```python
con_reservas = Concierto.objects.get(nombre="Noche de Rock")
try:
    con_reservas.delete()
except ProtectedError:
    print("No se puede eliminar un concierto con reservas")
print(Concierto.objects.get(pk=con_reservas.pk), "| reservas:", con_reservas.reservas.count())
```

Resultado:

```text
No se puede eliminar un concierto con reservas
Noche de Rock | reservas: 4
```
