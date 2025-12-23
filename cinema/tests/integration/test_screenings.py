from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from cinema.tests.factories import FilmFactory, CinemaHallFactory, ScreeningFactory


@pytest.mark.django_db
class TestScreeningViewSet:

	@pytest.mark.integration
	def test_create_screening(self, api_client, url_screening_list):
		film = FilmFactory()
		hall = CinemaHallFactory()

		start_time = timezone.now() + timedelta(days=1)
		end_time = start_time + timedelta(minutes=film.duration_minutes + 30)

		screening_data = {
			'film': film.pk,
			'hall': hall.pk,
			'start_time': start_time,
			'end_time': end_time,
			'price': 500.00,
			'available_seats': hall.capacity
		}

		response = api_client.post(url_screening_list, screening_data, format='json')

		assert response.status_code == status.HTTP_201_CREATED
		assert response.data['film'] == film.pk
		assert response.data['hall'] == hall.pk

	@pytest.mark.integration
	def test_create_screening_with_past_date(self, api_client, url_screening_list):
		film = FilmFactory()
		hall = CinemaHallFactory()

		screening_data = {
			'film': film.pk,
			'hall': hall.pk,
			'start_time': timezone.now() - timedelta(days=1),
			'price': 500.00,
			'available_seats': hall.capacity
		}

		response = api_client.post(url_screening_list, screening_data, format='json')

		assert response.status_code == status.HTTP_400_BAD_REQUEST

	@pytest.mark.integration
	def test_get_only_future_screenings(self, api_client, url_screening_list):
		ScreeningFactory(
			start_time=timezone.now() - timedelta(days=2),
			end_time=timezone.now() - timedelta(days=2) + timedelta(hours=2)
		)
		ScreeningFactory.create_batch(3)

		response = api_client.get(url_screening_list)

		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 3


	@pytest.mark.integration
	def test_booking_nonexistent_screening(self, api_client, url_booking_list):
		booking_data = {
			'screening': 99999,
			'customer_name': 'Иван Петров',
			'customer_email': 'ivan@example.com',
			'customer_phone': '+79161234567',
			'seats': 2
		}

		response = api_client.post(url_booking_list, booking_data, format='json')

		assert response.status_code == status.HTTP_400_BAD_REQUEST
