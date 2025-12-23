import pytest
from django.urls import reverse
from rest_framework import status

from cinema.tests.factories import FilmFactory


@pytest.mark.django_db
class TestFilmViewSet:

	@pytest.mark.integration
	def test_delete_film(self, api_client):
		film = FilmFactory()
		url = reverse('film-detail', args=[film.pk])

		response = api_client.delete(url)

		assert response.status_code == status.HTTP_204_NO_CONTENT

	@pytest.mark.integration
	def test_create_film_invalid_data(self, api_client, url_film_list):
		invalid_data = {
			'title': '',
			'description': 'Тестовое описание',
			'duration_minutes': -10,
			'release_year': 3000,
			'genre': 'Драма'
		}

		response = api_client.post(url_film_list, invalid_data, format='json')

		assert response.status_code == status.HTTP_400_BAD_REQUEST

	@pytest.mark.integration
	def test_filter_films_by_genre(self, api_client, url_film_list):
		FilmFactory.create_batch(3, genre='Драма')
		FilmFactory.create_batch(2, genre='Комедия')

		response = api_client.get(url_film_list)
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 5

		response = api_client.get(f"{url_film_list}?genre=Драма")
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 3
		assert all(film['genre'] == 'Драма' for film in response.data)

		response = api_client.get(f"{url_film_list}?genre=Комедия")
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 2
		assert all(film['genre'] == 'Комедия' for film in response.data)

		response = api_client.get(f"{url_film_list}?genre=дра")  # 'дра' в 'Драма'
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 3
		assert all('Драма' in film['genre'] for film in response.data)

	@pytest.mark.integration
	def test_filter_films_by_genre_case_insensitive(self, api_client, url_film_list):
		FilmFactory.create_batch(2, genre='ДРАМА')
		FilmFactory.create_batch(1, genre='драма')
		FilmFactory.create_batch(2, genre='Комедия')

		response = api_client.get(f"{url_film_list}?genre=драма")
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 3

		response = api_client.get(f"{url_film_list}?genre=ДРАМА")
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 3

	@pytest.mark.integration
	def test_filter_films_by_nonexistent_genre(self, api_client, url_film_list):
		FilmFactory.create_batch(3, genre='Драма')

		response = api_client.get(f"{url_film_list}?genre=Фантастика")
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 0

	@pytest.mark.integration
	def test_filter_films_empty_genre_param(self, api_client, url_film_list):
		FilmFactory.create_batch(3, genre='Драма')

		response = api_client.get(f"{url_film_list}?genre=")
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 3


	@pytest.mark.integration
	def test_get_nonexistent_film(self, api_client):
		url = reverse('film-detail', args=[99999])
		response = api_client.get(url)

		assert response.status_code == status.HTTP_404_NOT_FOUND
