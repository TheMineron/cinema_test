from django.db import models
from django.core.exceptions import ValidationError


class Film(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	duration_minutes = models.PositiveIntegerField()
	release_year = models.PositiveIntegerField()
	genre = models.CharField(max_length=100)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['title']

	def __str__(self):
		return f"{self.title} ({self.release_year})"


class CinemaHall(models.Model):
	name = models.CharField(max_length=100)
	capacity = models.PositiveIntegerField()
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.name} (вместимость: {self.capacity})"


class Screening(models.Model):
	film = models.ForeignKey(Film, on_delete=models.CASCADE)
	hall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	price = models.DecimalField(max_digits=8, decimal_places=2)
	available_seats = models.PositiveIntegerField()

	class Meta:
		ordering = ['start_time']

	def clean(self):
		if self.start_time >= self.end_time:
			raise ValidationError("Время окончания должно быть после времени начала")

		conflicting_screenings = Screening.objects.filter(
			hall=self.hall,
			start_time__lt=self.end_time,
			end_time__gt=self.start_time
		).exclude(pk=self.pk)

		if conflicting_screenings.exists():
			raise ValidationError("В этом зале уже есть сеанс в указанное время")

	def save(self, *args, **kwargs):
		self.full_clean()
		if not self.available_seats:
			self.available_seats = self.hall.capacity
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.film.title} - {self.start_time.strftime('%d.%m.%Y %H:%M')}"


class Booking(models.Model):
	STATUS_CHOICES = [
		('confirmed', 'Подтверждено'),
		('cancelled', 'Отменено'),
		('pending', 'В ожидании'),
	]

	screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
	customer_name = models.CharField(max_length=100)
	customer_email = models.EmailField()
	customer_phone = models.CharField(max_length=20)
	seats = models.PositiveIntegerField()
	total_price = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	booking_date = models.DateTimeField(auto_now_add=True)
	booking_reference = models.CharField(max_length=10, unique=True)

	class Meta:
		ordering = ['-booking_date']

	def clean(self):
		if self.seats > self.screening.available_seats:
			raise ValidationError(f"Недостаточно свободных мест. Доступно: {self.screening.available_seats}")

	def save(self, *args, **kwargs):
		if not self.booking_reference:
			import random
			import string
			self.booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

		if not self.total_price:
			self.total_price = self.seats * self.screening.price

		self.full_clean()
		super().save(*args, **kwargs)

	def __str__(self):
		return f"Бронь #{self.booking_reference} - {self.customer_name}"
