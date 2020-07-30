
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("trips", views.trips, name="trips"),
    path("create", views.create_trip, name="create_trip"),
    path("get_cities/<int:state_id>", views.get_cities, name="get_cities"),
    path("trip/<int:trip_id>", views.trip, name="trip"),
    path("add_passenger/<int:trip_id>", views.add_passenger, name="add_passenger"),
    path("passengers/<int:trip_id>", views.get_passengers, name="get_passengers"),
    path("delete_trip/<int:trip_id>", views.delete_trip, name="delete_trip"),
    path("search_trip", views.search_trip, name="search_trip")
]
