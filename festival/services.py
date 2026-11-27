from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Concierto, Reserva


def realizar_reserva(usuario_id, concierto_id, cantidad):
    with transaction.atomic():
        # 1. Recuperar usuario y concierto (el concierto queda bloqueado)
        usuario = get_user_model().objects.get(pk=usuario_id)
        concierto = Concierto.objects.select_for_update().get(pk=concierto_id)

        # 2. Concierto no cancelado
        if concierto.cancelado:
            raise ValueError("El concierto está cancelado")

        # 3. Cantidad válida
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")

        # 4. Entradas suficientes
        if cantidad > concierto.entradas_disponibles:
            raise ValueError("No hay entradas suficientes")

        # 5. Importe total
        importe_total = concierto.precio * cantidad

        # 6. Localizador (unique=True impide guardar uno repetido)
        localizador = uuid4().hex[:10].upper()

        # 7. Crear la reserva confirmada
        reserva = Reserva.objects.create(
            localizador=localizador,
            usuario=usuario,
            concierto=concierto,
            numero_entradas=cantidad,
            importe_total=importe_total,
            estado=Reserva.Estado.CONFIRMADA,
        )

        # 8. Descontar las entradas
        concierto.entradas_disponibles = concierto.entradas_disponibles - cantidad
        concierto.save(update_fields=["entradas_disponibles"])

        return reserva


def cancelar_reserva(reserva_id):
    with transaction.atomic():
        reserva = Reserva.objects.select_for_update().get(pk=reserva_id)

        if reserva.estado != Reserva.Estado.CONFIRMADA:
            raise ValueError("La reserva ya está cancelada")

        concierto = Concierto.objects.select_for_update().get(pk=reserva.concierto.pk)

        reserva.estado = Reserva.Estado.CANCELADA
        reserva.save(update_fields=["estado"])

        concierto.entradas_disponibles = concierto.entradas_disponibles + reserva.numero_entradas
        concierto.save(update_fields=["entradas_disponibles"])

        return reserva
