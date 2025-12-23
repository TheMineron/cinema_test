import pytest

from django.urls import reverse
from rest_framework.test import APIClient
from freezegun import freeze_time
from datetime import datetime, timezone


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_time():
    test_time = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    with freeze_time(test_time):
        yield test_time

@pytest.fixture
def film_data():
    return {
        'title': 'Тестовый фильм',
        'description': 'Тестовое описание',
        'duration_minutes': 120,
        'release_year': 2023,
        'genre': 'Драма'
    }

@pytest.fixture
def hall_data():
    return {
        'name': 'VIP зал',
        'capacity': 100,
        'description': 'Премиальный зал с кожаными креслами'
    }

@pytest.fixture
def url_film_list():
    return reverse('film-list')

@pytest.fixture
def url_hall_list():
    return reverse('cinemahall-list')

@pytest.fixture
def url_screening_list():
    return reverse('screening-list')

@pytest.fixture
def url_booking_list():
    return reverse('booking-list')

@pytest.fixture
def url_screening_upcoming():
    return reverse('screening-upcoming')
