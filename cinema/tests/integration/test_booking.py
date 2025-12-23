import pytest
from django.urls import reverse
from rest_framework import status

from cinema.tests.factories import ScreeningFactory, BookingFactory


@pytest.mark.django_db
class TestBookingViewSet:

	@pytest.mark.integration
	def test_list_bookings(self, api_client, url_booking_list):
		BookingFactory.create_batch(5)

		response = api_client.get(url_booking_list)

		assert response.status_code == status.HTTP_200_OK
		assert len(response.data) == 5

	@pytest.mark.integration
	def test_retrieve_booking(self, api_client):
		booking = BookingFactory()
		url = reverse('booking-detail', args=[booking.pk])

		response = api_client.get(url)

		assert response.status_code == status.HTTP_200_OK
		assert response.data['booking_reference'] == booking.booking_reference
		assert response.data['customer_name'] == booking.customer_name

	@pytest.mark.integration
	def test_update_booking_status(self, api_client):
		booking = BookingFactory(status='pending')
		url = reverse('booking-detail', args=[booking.pk])

		update_data = {'status': 'confirmed'}
		response = api_client.patch(url, update_data, format='json')

		assert response.status_code == status.HTTP_200_OK
		assert response.data['status'] == 'confirmed'

	@pytest.mark.integration
	def test_create_booking_with_zero_seats(self, api_client, url_booking_list):
		screening = ScreeningFactory(available_seats=10)

		booking_data = {
			'screening': screening.pk,
			'customer_name': 'Иван Петров',
			'customer_email': 'ivan@example.com',
			'customer_phone': '+79161234567',
			'seats': 0,
			'status': 'pending'
		}

		response = api_client.post(url_booking_list, booking_data, format='json')

		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert 'Количество мест должно быть положительным числом' in str(response.data['error'])

	@pytest.mark.integration
	def test_create_booking_with_invalid_email(self, api_client, url_booking_list):
		screening = ScreeningFactory(available_seats=10)

		booking_data = {
			'screening': screening.pk,
			'customer_name': 'Иван Петров',
			'customer_email': 'invalid-email',
			'customer_phone': '+79161234567',
			'seats': 2
		}

		response = api_client.post(url_booking_list, booking_data, format='json')

		assert response.status_code == status.HTTP_400_BAD_REQUEST


	@pytest.mark.integration
	def test_cancel_nonexistent_booking(self, api_client):
		url = reverse('booking-cancel', args=[99999])
		response = api_client.post(url)

		assert response.status_code == status.HTTP_400_BAD_REQUEST
