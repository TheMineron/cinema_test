import factory

from factory.django import DjangoModelFactory
from faker import Faker
from datetime import timedelta
from django.utils import timezone
from cinema.models import Film, CinemaHall, Screening, Booking

fake = Faker(['ru_RU'])


class FilmFactory(DjangoModelFactory):
	class Meta:
		model = Film

	title = factory.LazyFunction(lambda: f"Фильм {fake.word().capitalize()}")
	description = factory.Faker('paragraph', locale='ru_RU')
	duration_minutes = factory.Faker('random_int', min=60, max=180)
	release_year = factory.LazyFunction(lambda: int(fake.year()))
	genre = factory.Faker('random_element', elements=['Драма', 'Комедия', 'Боевик', 'Фантастика'])


class CinemaHallFactory(DjangoModelFactory):
	class Meta:
		model = CinemaHall

	name = factory.LazyFunction(lambda: f"Зал {fake.word().capitalize()}")
	capacity = factory.Faker('random_int', min=50, max=300)
	description = factory.Faker('sentence', locale='ru_RU')


class ScreeningFactory(DjangoModelFactory):
	class Meta:
		model = Screening

	film = factory.SubFactory(FilmFactory)
	hall = factory.SubFactory(CinemaHallFactory)
	start_time = factory.LazyFunction(
		lambda: timezone.now() + timedelta(days=fake.random_int(min=1, max=30))
	)
	end_time = factory.LazyAttribute(
		lambda o: o.start_time + timedelta(minutes=o.film.duration_minutes + 30)
	)
	price = factory.Faker('random_number', digits=3)
	available_seats = factory.LazyAttribute(lambda o: o.hall.capacity)


class BookingFactory(DjangoModelFactory):
	class Meta:
		model = Booking

	screening = factory.SubFactory(ScreeningFactory)
	customer_name = factory.Faker('name', locale='ru_RU')
	customer_email = factory.Faker('email')
	customer_phone = factory.Faker('phone_number', locale='ru_RU')
	seats = factory.Faker('random_int', min=1, max=5)
	status = 'confirmed'

	@factory.lazy_attribute
	def total_price(self):
		return self.seats * self.screening.price
