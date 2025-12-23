import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError
from cinema.serializers import FilmSerializer, BookingSerializer
from cinema.tests.factories import ScreeningFactory, BookingFactory


@pytest.mark.django_db
class TestFilmSerializer:
	@pytest.mark.unit
	def test_film_serializer_valid(self, film_data):
		serializer = FilmSerializer(data=film_data)
		assert serializer.is_valid() is True
		assert serializer.validated_data['title'] == film_data['title']

	@pytest.mark.unit
	def test_film_serializer_invalid(self):
		invalid_data = {
			'title': '',
			'description': 'Тест',
			'duration_minutes': -10,
			'release_year': 1990,
			'genre': 'Драма'
		}
		serializer = FilmSerializer(data=invalid_data)
		assert serializer.is_valid() is False
		assert 'title' in serializer.errors
		assert 'duration_minutes' in serializer.errors


@pytest.mark.django_db
class TestBookingSerializer:
	@pytest.mark.unit
	def test_booking_serializer_valid(self):
		screening = ScreeningFactory(available_seats=10)
		booking_data = {
			'screening': screening.id,
			'customer_name': 'Тест Тестов',
			'customer_email': 'test@example.com',
			'customer_phone': '+79991234567',
			'seats': 2,
			'status': 'pending'
		}
		serializer = BookingSerializer(data=booking_data)
		assert serializer.is_valid() is True

	@pytest.mark.unit
	def test_booking_serializer_past_screening(self):
		screening = ScreeningFactory(
			start_time=timezone.now() - timedelta(days=1),
			end_time=timezone.now() - timedelta(days=1) + timedelta(hours=2)
		)

		booking_data = {
			'screening': screening.id,
			'customer_name': 'Тест Тестов',
			'customer_email': 'test@example.com',
			'customer_phone': '+79991234567',
			'seats': 2
		}

		serializer = BookingSerializer(data=booking_data)
		with pytest.raises(DRFValidationError) as exc:
			serializer.is_valid(raise_exception=True)

		assert "Нельзя забронировать билеты на прошедший сеанс" in str(exc.value)

	@pytest.mark.unit
	def test_booking_serializer_read_only_fields(self):
		booking = BookingFactory()
		serializer = BookingSerializer(booking)

		assert 'booking_reference' in serializer.data
		assert 'booking_date' in serializer.data
		assert 'total_price' in serializer.data
		assert 'screening_info' in serializer.data
		assert 'film_title' in serializer.data
