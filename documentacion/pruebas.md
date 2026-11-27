# Pruebas

Todas las salidas son de ejecuciones reales con Django 6.1.3, sobre SQLite y PostgreSQL 16. Los localizadores son aleatorios, así que cambian en cada ejecución.

## 1. Migraciones (apartado 6)

| Migración | Contenido |
|---|---|
| `0001_initial` | Modelos iniciales |
| `0002_concierto_descripcion_...` | Añade `Concierto.descripcion` y el valor por defecto de `numero_entradas` |
| `0003_modelo_completo` | Relaciones con el usuario, `importe_total`, ajuste de campos y restricciones |

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations festival
python manage.py sqlmigrate festival 0002
```

```text
festival
 [X] 0001_initial
 [X] 0002_concierto_descripcion_alter_reserva_numero_entradas
 [X] 0003_modelo_completo
```

### Comprobación de que no se pierden datos

Para reproducirlo, en una copia del proyecto con el modelo anterior (sin `descripcion`) se aplicó solo la `0001`, se insertaron un artista, un escenario y un concierto, y después se aplicaron la `0002` y la `0003`.

Concierto antes de añadir el campo:

```text
{'id': 1, 'nombre': 'Noche de Rock', 'fecha_y_hora': datetime.datetime(2027, 7, 10, 22, 0, tzinfo=datetime.timezone.utc), 'duracion': 120, 'precio': 45, 'escenario_id': 1, 'entradas_disponibles': 500, 'cancelado': False}
```

Después de la `0002` (se conserva y `descripcion` queda vacía), con sus artistas:

```text
[{'id': 1, 'nombre': 'Noche de Rock', 'descripcion': ''}]
[<Artista: Luna Roja>]
```

Después de la `0003` (nombre, precio, entradas disponibles y artistas):

```text
Noche de Rock 45.00 500 [<Artista: Luna Roja>]
```

> **Aviso:** la `0003` rellena `usuario` e `importe_total` en las filas antiguas con un valor puntual (`1` y `0`). Si una base de datos anterior tiene perfiles o reservas (con el usuario guardado como texto), la migración puede fallar. En ese caso, al ser datos de práctica, se parte de una base de datos nueva y se ejecuta la carga inicial.

## 2. Carga inicial (apartado 7)

```bash
python manage.py shell < cargar_datos.py
```

```text
Artistas: 8
Escenarios: 3
Conciertos: 6
Usuarios: 5
Perfiles: 5
Reservas: 10

Comprobación: disponibles = aforo - entradas confirmadas
Tarde Pop | aforo 100 | confirmadas 3 | disponibles 97 | OK
Noche de Rock | aforo 500 | confirmadas 7 | disponibles 493 | OK
Raíces | aforo 50 | confirmadas 6 | disponibles 44 | OK
Electro Fest | aforo 500 | confirmadas 6 | disponibles 494 | OK
Vermut en vivo | aforo 50 | confirmadas 0 | disponibles 50 | OK
Gran Clausura | aforo 500 | confirmadas 0 | disponibles 500 | OK
```

Incluye conciertos con varios artistas, artistas en varios conciertos (Luna Roja, Neon Wave y Los Faros), conciertos gratuitos y de pago, un concierto cancelado y 3 reservas canceladas. Los usuarios se crean sin contraseña y con datos ficticios.

## 3. Integridad (apartado 5)

```bash
python manage.py shell < pruebas_integridad.py
```

Se usa `update()` para comprobar que la regla la aplica la base de datos. Cada intento va en su propio `atomic()`, porque en PostgreSQL un error invalida la transacción en curso.

### SQLite

```text
Artista con nombre repetido -> RECHAZADO: UNIQUE constraint failed: festival_artista.nombre
Escenario con nombre repetido -> RECHAZADO: UNIQUE constraint failed: festival_escenario.nombre
Aforo 0 -> RECHAZADO: CHECK constraint failed: escenario_aforo_positivo
Duración 0 -> RECHAZADO: CHECK constraint failed: concierto_duracion_positiva
Caché negativo -> RECHAZADO: CHECK constraint failed: artista_cache_no_negativo
Precio negativo -> RECHAZADO: CHECK constraint failed: concierto_precio_no_negativo
Entradas disponibles negativas -> RECHAZADO: CHECK constraint failed: entradas_disponibles
DNI repetido -> RECHAZADO: UNIQUE constraint failed: festival_perfil.dni
Localizador repetido -> RECHAZADO: UNIQUE constraint failed: festival_reserva.localizador
Reserva con 0 entradas -> RECHAZADO: CHECK constraint failed: reserva_minimo_una_entrada
Segundo perfil para el mismo usuario -> RECHAZADO: UNIQUE constraint failed: festival_perfil.usuario_id
Borrar un concierto con reservas -> RECHAZADO: ProtectedError
```

### PostgreSQL

```text
Artista con nombre repetido -> RECHAZADO: duplicate key value violates unique constraint "festival_artista_nombre_key"
Escenario con nombre repetido -> RECHAZADO: duplicate key value violates unique constraint "festival_escenario_nombre_key"
Aforo 0 -> RECHAZADO: new row for relation "festival_escenario" violates check constraint "escenario_aforo_positivo"
Duración 0 -> RECHAZADO: new row for relation "festival_concierto" violates check constraint "concierto_duracion_positiva"
Caché negativo -> RECHAZADO: new row for relation "festival_artista" violates check constraint "artista_cache_no_negativo"
Precio negativo -> RECHAZADO: new row for relation "festival_concierto" violates check constraint "concierto_precio_no_negativo"
Entradas disponibles negativas -> RECHAZADO: new row for relation "festival_concierto" violates check constraint "festival_concierto_entradas_disponibles_check"
DNI repetido -> RECHAZADO: duplicate key value violates unique constraint "festival_perfil_dni_key"
Localizador repetido -> RECHAZADO: duplicate key value violates unique constraint "festival_reserva_localizador_key"
Reserva con 0 entradas -> RECHAZADO: new row for relation "festival_reserva" violates check constraint "reserva_minimo_una_entrada"
Segundo perfil para el mismo usuario -> RECHAZADO: duplicate key value violates unique constraint "festival_perfil_usuario_id_key"
Borrar un concierto con reservas -> RECHAZADO: ProtectedError
```

`ProtectedError` lo lanza el ORM de Django al aplicar `on_delete=models.PROTECT`.

**Límite:** la regla «las entradas disponibles no superan el aforo» **no** está en la base de datos. Un `CheckConstraint` solo puede usar columnas de su propia tabla y el aforo está en `Escenario`. Ver `modelo-datos.md`.

## 4. Transacciones (apartado 10.3, pruebas 1 a 7)

Sobre los datos recién cargados:

```bash
python manage.py shell < pruebas_transacciones.py
```

El resultado es el mismo en SQLite y en PostgreSQL:

```text
1. Reservar 2 entradas disponibles
Antes:   disponibles=97, reservas=10
Aceptada: Confirmada | importe 40.00
Después: disponibles=95, reservas=11

2. Reservar más entradas de las disponibles
Antes:   disponibles=95, reservas=11
Rechazada: No hay entradas suficientes
Después: disponibles=95, reservas=11

3. Reservar 0 entradas
Antes:   disponibles=95, reservas=11
Rechazada: La cantidad debe ser mayor que cero
Después: disponibles=95, reservas=11

4. Reservar para un concierto cancelado
Antes:   disponibles=500, reservas=11
Rechazada: El concierto está cancelado
Después: disponibles=500, reservas=11

5. Cancelar una reserva confirmada
Antes:   disponibles=95, reservas=11
Estado: Cancelada
Después: disponibles=97, reservas=11

6. Cancelar una reserva ya cancelada
Antes:   disponibles=97, reservas=11
Rechazada: La reserva ya está cancelada
Después: disponibles=97, reservas=11

7. Provocar un error durante una transacción
Antes:   disponibles=97, reservas=11
Dentro:  disponibles=94, reservas=12
Capturado fuera del atomic(): Error simulado
Después: disponibles=97, reservas=11
```

En la prueba 7, dentro del bloque ya se ve la reserva creada y las entradas descontadas. Como la excepción sale del `atomic()`, se deshacen los dos cambios, incluidos los de `realizar_reserva` (su `atomic()` queda anidado dentro del exterior).

## 5. Reservas simultáneas (prueba 8)

Sobre los datos recién cargados, en dos terminales; la segunda se lanza 2 o 3 segundos después de la primera:

```bash
python manage.py shell < prueba_concurrencia.py
```

Quedan 50 entradas y cada terminal pide 30. La primera mantiene la transacción abierta 8 segundos.

### PostgreSQL (3 de 3 ejecuciones con este resultado)

```text
[Terminal A]
Reserva hecha, se mantiene la transacción abierta 8 segundos...
ACEPTADA: B879236739
Aforo: 50 | confirmadas: 30 | disponibles: 20

[Terminal B]
RECHAZADA: ValueError - No hay entradas suficientes
Aforo: 50 | confirmadas: 30 | disponibles: 20
```

`select_for_update()` bloquea la fila del concierto. La terminal B espera a que A confirme, lee las 20 entradas que quedan y rechaza la reserva.

### SQLite (1 ejecución)

```text
[Terminal A]
Reserva hecha, se mantiene la transacción abierta 8 segundos...
ACEPTADA: 2BF4C1FF1D
Aforo: 50 | confirmadas: 30 | disponibles: 20

[Terminal B]
RECHAZADA: OperationalError - database is locked
Aforo: 50 | confirmadas: 0 | disponibles: 50
```

SQLite no bloquea filas: `select_for_update()` no tiene efecto. No hay sobreventa, pero B falla con un error de base de datos bloqueada, no con la comprobación de entradas. La terminal B muestra `confirmadas: 0` porque lee antes de que A confirme; el estado final es el que muestra A. Para ventas simultáneas se debe usar PostgreSQL.

## 6. Panel de administración (apartado 11)

Comprobado con el cliente de pruebas de Django sobre SQLite:

| Comprobación | Resultado |
|---|---|
| Listados y búsqueda de los 5 modelos | Cargan correctamente |
| Filtros de artistas, conciertos y reservas | Cargan correctamente |
| Crear un concierto con artistas | Se crea |
| Crear un concierto con precio -1 | No se crea |
| Editar un concierto | `entradas_disponibles` no es editable y se ven sus reservas en el inline |
| Añadir o borrar una reserva | Prohibido (403) |
| Borrar un concierto con reservas | El concierto no se elimina |
