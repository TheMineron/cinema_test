from datetime import timedelta

import pytest
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status


@pytest.mark.django_db
class TestIntegrationScenarios:

	@pytest.mark.integration
	def test_full_booking_flow(self, api_client, test_time):
		with freeze_time(test_time):
			film_data = {
				'title': 'Интеграционный фильм',
				'description': 'Описание',
				'duration_minutes': 120,
				'release_year': 2024,
				'genre': 'Драма'
			}
			film_response = api_client.post(reverse('film-list'), film_data, format='json')
			assert film_response.status_code == status.HTTP_201_CREATED
			film_id = film_response.data['id']

			hall_data = {
				'name': 'Интеграционный зал',
				'capacity': 50,
				'description': 'Описание'
			}
			hall_response = api_client.post(reverse('cinemahall-list'), hall_data, format='json')
			assert hall_response.status_code == status.HTTP_201_CREATED
			hall_id = hall_response.data['id']

			start_time = test_time + timedelta(days=2)
			end_time = start_time + timedelta(minutes=film_data['duration_minutes'] + 30)
			screening_data = {
				'film': film_id,
				'hall': hall_id,
				'start_time': start_time,
				'end_time': end_time,
				'price': 300.00,
				'available_seats': 50
			}
			screening_response = api_client.post(reverse('screening-list'), screening_data, format='json')
			assert screening_response.status_code == status.HTTP_201_CREATED
			screening_id = screening_response.data['id']

			booking_data = {
				'screening': screening_id,
				'customer_name': 'Интеграционный тест',
				'customer_email': 'test@example.com',
				'customer_phone': '+79160000000',
				'seats': 4
			}
			booking_response = api_client.post(reverse('booking-list'), booking_data, format='json')
			assert booking_response.status_code == status.HTTP_201_CREATED
			booking_id = booking_response.data['id']

			cancel_response = api_client.post(reverse('booking-cancel', args=[booking_id]))
			assert cancel_response.status_code == status.HTTP_200_OK

			screening_detail = api_client.get(reverse('screening-detail', args=[screening_id]))
			assert screening_detail.status_code == status.HTTP_200_OK
			assert screening_detail.data['available_seats'] == 50
