# MusicFest

Práctica integradora de la UT4 (Persistencia: bases de datos y ORM) de Desarrollo Web en Entorno Servidor, 2.º DAW.

## Objetivo

Desarrollar la capa de persistencia de un festival de música con el ORM de Django: artistas, escenarios, conciertos, perfiles de asistentes y reservas de entradas, garantizando la integridad de los datos y sin vender más entradas de las disponibles.

## Requisitos

- Python 3.12 o superior
- Las dependencias de `requirements.txt` (Django 6.1.3, `psycopg` y `python-decouple`)
- PostgreSQL, solo para usar ese gestor (probado con la versión 16)

## Instalación

```bash
git clone <url-del-repositorio>
cd musicfest
git switch examen-resuelto
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Configuración de la base de datos

`settings.py` lee la configuración con `config()` de `python-decouple`. Sin archivo `.env` se usa **SQLite** (`db.sqlite3`).

Para cambiarla, copia `.env.example` como `.env`. El archivo `.env` está en `.gitignore` y no se sube.

### SQLite

```dotenv
DB_ENGINE=sqlite
```

### PostgreSQL

Crea el usuario y la base de datos desde `psql` con un usuario administrador, usando tu propia contraseña:

```sql
CREATE USER musicfest_user WITH PASSWORD 'tu_clave_local';
CREATE DATABASE musicfest OWNER musicfest_user;
```

Y completa el `.env`:

```dotenv
DB_ENGINE=postgresql
DB_NAME=musicfest
DB_USER=musicfest_user
DB_PASSWORD=tu_clave_local
DB_HOST=localhost
DB_PORT=5432
```

Para comprobar el gestor activo, en `python manage.py shell`:

```python
from django.db import connection
print(connection.vendor)   # sqlite o postgresql
```

Cambiar de gestor no copia los datos: en la base de datos nueva hay que migrar y repetir la carga inicial.

## Ejecución

Sobre una base de datos **vacía**:

```bash
python manage.py check
python manage.py migrate
python manage.py showmigrations festival
python manage.py shell < cargar_datos.py
python manage.py createsuperuser
python manage.py runserver
```

El panel de administración está en <http://127.0.0.1:8000/admin/>.

> En Windows PowerShell no funciona `<`. Usa `Get-Content cargar_datos.py | python manage.py shell` o el símbolo del sistema (CMD).

Si ya tenías un `db.sqlite3` de una versión anterior del proyecto, borra solo ese archivo (se pierden sus datos) y vuelve a migrar. No borres las migraciones.

## Scripts

Cada uno parte de los datos recién cargados. Para repetirlos con SQLite, borra `db.sqlite3`, migra y vuelve a cargar. Con PostgreSQL, vacía los datos con `python manage.py flush` y vuelve a cargar.

| Comando | Contenido |
|---|---|
| `python manage.py shell < cargar_datos.py` | Carga inicial |
| `python manage.py shell < operaciones_crud.py` | Las 11 operaciones CRUD |
| `python manage.py shell < festival/consultas.py` | Las 24 consultas |
| `python manage.py shell < pruebas_integridad.py` | Restricciones de integridad |
| `python manage.py shell < pruebas_transacciones.py` | Pruebas 1 a 7 de transacciones |
| `python manage.py shell < prueba_concurrencia.py` | Prueba 8, en dos terminales a la vez |

Las funciones `realizar_reserva` y `cancelar_reserva` están en `festival/services.py`:

```python
from festival.services import cancelar_reserva, realizar_reserva

reserva = realizar_reserva(usuario_id, concierto_id, 2)
cancelar_reserva(reserva.pk)
```

Si la operación no es válida lanzan `ValueError`. Si no existe el usuario, el concierto o la reserva, lanzan `DoesNotExist`.

## Documentación

| Documento | Contenido |
|---|---|
| [Modelo de datos](documentacion/modelo-datos.md) | Modelos, relaciones, `on_delete`, `related_name` y restricciones |
| [Operaciones CRUD](documentacion/operaciones-crud.md) | Código y resultados |
| [Consultas ORM](documentacion/consultas-orm.md) | Las 24 consultas y sus resultados |
| [Pruebas](documentacion/pruebas.md) | Migraciones, carga, integridad, transacciones, concurrencia y admin |
