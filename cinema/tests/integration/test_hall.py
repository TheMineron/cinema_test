import pytest
from django.urls import reverse
from rest_framework import status

from cinema.tests.factories import CinemaHallFactory


@pytest.mark.django_db
class TestCinemaHallViewSet:

	@pytest.mark.integration
	def test_list_halls(self, api_client, url_hall_list):
		CinemaHallFactory.create_batch(3)

		response = api_client.get(url_hall_list)

		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 3

	@pytest.mark.integration
	def test_create_hall(self, api_client, url_hall_list, hall_data):
		response = api_client.post(url_hall_list, hall_data, format='json')

		assert response.status_code == status.HTTP_201_CREATED
		assert response.data['name'] == hall_data['name']
		assert response.data['capacity'] == hall_data['capacity']

	@pytest.mark.integration
	def test_retrieve_hall(self, api_client):
		hall = CinemaHallFactory()
		url = reverse('cinemahall-detail', args=[hall.pk])

		response = api_client.get(url)

		assert response.status_code == status.HTTP_200_OK
		assert response.data['id'] == hall.pk
		assert response.data['name'] == hall.name

	@pytest.mark.integration
	def test_update_hall(self, api_client):
		hall = CinemaHallFactory()
		url = reverse('cinemahall-detail', args=[hall.pk])

		update_data = {
			'name': 'Обновленный зал',
			'capacity': 150
		}
		response = api_client.patch(url, update_data, format='json')

		assert response.status_code == status.HTTP_200_OK
		assert response.data['name'] == 'Обновленный зал'
		assert response.data['capacity'] == 150

	@pytest.mark.integration
	def test_delete_hall(self, api_client):
		hall = CinemaHallFactory()
		url = reverse('cinemahall-detail', args=[hall.pk])

		response = api_client.delete(url)

		assert response.status_code == status.HTTP_204_NO_CONTENT
