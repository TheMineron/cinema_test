import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
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
		film_id = self.request.query_params.get('film_id')
		date = self.request.query_params.get('date')

		if film_id:
			queryset = queryset.filter(film_id=film_id)
		if date:
			queryset = queryset.filter(start_time__date=date)

		return queryset.filter(start_time__gte=timezone.now())

	@action(detail=False, methods=['get'])
	def upcoming(self, request):
		screenings = self.get_queryset().filter(start_time__gte=timezone.now())[:10]
		serializer = self.get_serializer(screenings, many=True)
		return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
	queryset = Booking.objects.all()
	serializer_class = BookingSerializer

	def create(self, request, *args, **kwargs):
		try:
			serializer = self.get_serializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			screening = serializer.validated_data['screening']
			seats = serializer.validated_data['seats']

			if seats > screening.available_seats:
				return Response(
					{'error': f'Недостаточно мест. Доступно: {screening.available_seats}'},
					status=status.HTTP_400_BAD_REQUEST
				)

			booking = serializer.save()
			screening.available_seats -= seats
			screening.save()
			logger.info(f"Создана бронь #{booking.booking_reference} на {seats} мест")
			return Response(serializer.data, status=status.HTTP_201_CREATED)

		except Exception as e:
			logger.error(f"Ошибка при создании брони: {str(e)}")
			return Response(
				{'error': 'Ошибка при создании брони'},
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
