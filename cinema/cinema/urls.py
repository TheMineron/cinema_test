from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'films', views.FilmViewSet)
router.register(r'halls', views.CinemaHallViewSet)
router.register(r'screenings', views.ScreeningViewSet)
router.register(r'bookings', views.BookingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
