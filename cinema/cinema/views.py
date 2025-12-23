import logging

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.utils import timezone
from .models import Film, CinemaHall, Screening, Booking
from .serializers import (
	FilmSerializer,
	CinemaHallSerializer,
	ScreeningSerializer,
	BookingSerializer
)

logger = logging.getLogger(__name__)


class FilmViewSet(viewsets.ModelViewSet):
	queryset = Film.objects.all()
	serializer_class = FilmSerializer

	def get_queryset(self):
		queryset = Film.objects.all()
		genre = self.request.query_params.get('genre')

		if genre:
			queryset = queryset.filter(genre__icontains=genre)

		return queryset

	def create(self, request, *args, **kwargs):
		try:
			logger.info(f"Создание фильма: {request.data.get('title')}")
			return super().create(request, *args, **kwargs)
		except Exception as e:
			logger.error(f"Ошибка при создании фильма: {str(e)}")
			return Response(
				{'error': 'Ошибка при создании фильма'},
				status=status.HTTP_400_BAD_REQUEST
			)


class CinemaHallViewSet(viewsets.ModelViewSet):
	queryset = CinemaHall.objects.all()
	serializer_class = CinemaHallSerializer


class ScreeningViewSet(viewsets.ModelViewSet):
	queryset = Screening.objects.all()
	serializer_class = ScreeningSerializer

	def get_queryset(self):
		queryset = Screening.objects.all()
		return queryset.filter(start_time__gte=timezone.now())

	@action(detail=False, methods=['get'])
	def upcoming(self, request):
		screenings = self.get_queryset().filter(start_time__gte=timezone.now())[:10]
		serializer = self.get_serializer(screenings, many=True)
		return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
	queryset = Booking.objects.all()
	serializer_class = BookingSerializer

	@transaction.atomic()
	def create(self, request, *args, **kwargs):
		try:
			serializer = self.get_serializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			screening = serializer.validated_data['screening']
			seats = serializer.validated_data['seats']

			booking = serializer.save()
			screening.available_seats -= seats
			screening.save()
			logger.info(f"Создана бронь #{booking.booking_reference} на {seats} мест")
			return Response(serializer.data, status=status.HTTP_201_CREATED)

		except ValidationError as e:
			logger.error(f"Ошибка валидации при создании брони: {e.detail}")
			return Response(
				{'error': e.detail},
				status=status.HTTP_400_BAD_REQUEST
			)

	@action(detail=True, methods=['post'])
	def cancel(self, request, pk=None):
		try:
			booking = self.get_object()

			if booking.status == 'cancelled':
				return Response(
					{'error': 'Бронь уже отменена'},
					status=status.HTTP_400_BAD_REQUEST
				)

			booking.screening.available_seats += booking.seats
			booking.screening.save()

			booking.status = 'cancelled'
			booking.save()

			logger.info(f"Бронь #{booking.booking_reference} отменена")

			return Response({'message': 'Бронь успешно отменена'})

		except Exception as e:
			logger.error(f"Ошибка при отмене брони: {str(e)}")
			return Response(
				{'error': 'Ошибка при отмене брони'},
				status=status.HTTP_400_BAD_REQUEST
			)
