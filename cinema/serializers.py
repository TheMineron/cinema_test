from rest_framework import serializers
from .models import Film, CinemaHall, Screening, Booking
from django.utils import timezone


class FilmSerializer(serializers.ModelSerializer):
	class Meta:
		model = Film
		fields = '__all__'


class CinemaHallSerializer(serializers.ModelSerializer):
	class Meta:
		model = CinemaHall
		fields = '__all__'


class ScreeningSerializer(serializers.ModelSerializer):
	film_title = serializers.CharField(source='film.title', read_only=True)
	hall_name = serializers.CharField(source='hall.name', read_only=True)
	is_available = serializers.SerializerMethodField()

	class Meta:
		model = Screening
		fields = '__all__'

	def get_is_available(self, obj):
		return obj.available_seats > 0 and obj.start_time > timezone.now()


class BookingSerializer(serializers.ModelSerializer):
	screening_info = serializers.CharField(source='screening.__str__', read_only=True)
	film_title = serializers.CharField(source='screening.film.title', read_only=True)

	class Meta:
		model = Booking
		fields = '__all__'
		read_only_fields = ('booking_reference', 'booking_date', 'total_price')

	def validate(self, data):
		screening = data.get('screening')
		seats = data.get('seats')

		if seats is not None and seats <= 0:
			raise serializers.ValidationError(
				{"seats": "Количество мест должно быть положительным числом"}
			)

		if screening and seats:
			if screening.start_time <= timezone.now():
				raise serializers.ValidationError("Нельзя забронировать билеты на прошедший сеанс")

			if seats > screening.available_seats:
				raise serializers.ValidationError(
					f"Недостаточно свободных мест. Доступно: {screening.available_seats}"
				)

		return data
