import pytest

from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from cinema.models import Film, Screening
from cinema.tests.factories import (
	FilmFactory,
	CinemaHallFactory,
	ScreeningFactory,
	BookingFactory
)


@pytest.mark.django_db
class TestFilmModel:
	@pytest.mark.unit
	def test_create_film(self):
		film = FilmFactory()
		assert film.pk is not None
		assert isinstance(film.title, str)
		assert film.duration_minutes > 0
		assert 1900 <= film.release_year <= datetime.now().year

	@pytest.mark.unit
	def test_film_string_representation(self):
		film = FilmFactory(title="Матрица", release_year=1999)
		assert str(film) == "Матрица (1999)"

	@pytest.mark.unit
	def test_film_ordering(self):
		film1 = FilmFactory(title="Бэтмен")
		film2 = FilmFactory(title="Аватар")

		films = Film.objects.all()
		assert films[0].title == "Аватар"
		assert films[1].title == "Бэтмен"


@pytest.mark.django_db
class TestCinemaHallModel:
	@pytest.mark.unit
	def test_create_hall(self):
		hall = CinemaHallFactory()
		assert hall.pk is not None
		assert hall.capacity > 0

	@pytest.mark.unit
	def test_hall_string_representation(self):
		hall = CinemaHallFactory(name="Goodwen", capacity=250)
		assert str(hall) == "Goodwen (вместимость: 250)"


@pytest.mark.django_db
class TestScreeningModel:
	@pytest.mark.unit
	def test_create_screening(self):
		screening = ScreeningFactory()
		assert screening.pk is not None
		assert screening.start_time < screening.end_time
		assert screening.price > 0

	@pytest.mark.unit
	def test_screening_available_seats_default(self):
		hall = CinemaHallFactory(capacity=150)
		screening = ScreeningFactory(hall=hall)
		assert screening.available_seats == 150

	@pytest.mark.unit
	def test_screening_validation_start_after_end(self):
		with pytest.raises(ValidationError) as exc:
			screening = ScreeningFactory(
				start_time=timezone.now() + timedelta(hours=2),
				end_time=timezone.now() + timedelta(hours=1)
			)
			screening.full_clean()
		assert "Время окончания должно быть после времени начала" in str(exc.value)

	@pytest.mark.unit
	def test_screening_validation_time_conflict(self):
		hall = CinemaHallFactory()
		existing_screening = ScreeningFactory(
			hall=hall,
			start_time=timezone.now() + timedelta(days=1, hours=14),
			end_time=timezone.now() + timedelta(days=1, hours=16)
		)

		with pytest.raises(ValidationError) as exc:
			conflicting_screening = Screening(
				film=FilmFactory(),
				hall=hall,
				start_time=timezone.now() + timedelta(days=1, hours=15),
				end_time=timezone.now() + timedelta(days=1, hours=17),
				price=500,
				available_seats=100
			)
			conflicting_screening.full_clean()

		assert "уже есть сеанс в указанное время" in str(exc.value)

	@pytest.mark.unit
	def test_screening_string_representation(self, test_time):
		film = FilmFactory(title="Интерстеллар")
		screening = ScreeningFactory(
			film=film,
			start_time=test_time + timedelta(days=1)
		)

		expected_date = expected_date = test_time + timedelta(days=1)
		expected_str = f"Интерстеллар - {expected_date.strftime('%d.%m.%Y %H:%M')}"
		assert str(screening) == expected_str


@pytest.mark.django_db
class TestBookingModel:
	@pytest.mark.unit
	def test_create_booking(self):
		booking = BookingFactory()
		assert booking.pk is not None
		assert booking.booking_reference is not None
		assert len(booking.booking_reference) == 8
		assert booking.total_price == booking.seats * booking.screening.price

	@pytest.mark.unit
	def test_booking_validation_insufficient_seats(self):
		screening = ScreeningFactory(available_seats=5)

		with pytest.raises(ValidationError) as exc:
			booking = BookingFactory(
				screening=screening,
				seats=10
			)
			booking.full_clean()

		assert "Недостаточно свободных мест" in str(exc.value)

	@pytest.mark.unit
	def test_booking_string_representation(self):
		booking = BookingFactory(customer_name="Иван Иванов")
		assert str(booking).startswith("Бронь #")
		assert "Иван Иванов" in str(booking)

	@pytest.mark.unit
	def test_booking_total_price_calculation(self):
		screening = ScreeningFactory(price=300)
		booking = BookingFactory(screening=screening, seats=3)
		assert booking.total_price == 900
