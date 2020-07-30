from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from collections import namedtuple
import json
from django.core import serializers
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from flask import request

from .models import User, UsStates, UsCities, Trip

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def index(request):
    return render(request, "capstone/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "capstone/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "capstone/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "capstone/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "capstone/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "capstone/register.html")

def trips(request):
    return render(request, "capstone/trips.html",{
        "states": UsStates.objects.all(),
        "trips": Trip.objects.all().order_by('-id')
    })
    
def search_trip(request):
    if request.method == "POST":
        o_state_id = request.POST["o_state"] ##Getting the id of the state.
        o_city_name = request.POST.get("o_city") ##Getting the name of the city.
        o_city_obj = UsCities.objects.filter(id_state=o_state_id, city=o_city_name).first()
        d_state_id = request.POST["d_state"] ##Getting the id of the state.
        d_city_name = request.POST.get("d_city") ##Getting the name of the city.
        d_city_obj = UsCities.objects.filter(id_state=d_state_id, city=d_city_name).first()
        results = Trip.objects.filter(origin=o_city_obj, destination=d_city_obj).order_by('-id')
        if not results:
            return render(request, "capstone/trips.html", {
            "message": "No results",
            "states": UsStates.objects.all(),
            "trips": Trip.objects.all().order_by('-id')
        })
        else:
            return render(request, "capstone/trips.html", {
                "states": UsStates.objects.all(),
                "trips": results
            })
    else:
        return HttpResponseRedirect(reverse("trips"))
 
def trip(request, trip_id):
    trip_obj = Trip.objects.filter(id=trip_id).first()
    if request.user == trip_obj.driver:
            return render(request, "capstone/trip.html", {
                "self": True,
                "trip": trip_obj
            } )
    else:
        if trip_obj.passengers.filter(id=request.user.id).exists():
            return render(request, "capstone/trip.html", {
                "is_passenger": True,
                "trip": trip_obj
            })
        else:
            return render(request, "capstone/trip.html", {
                "trip": trip_obj
            })

def create_trip(request):
    if request.method == "POST":    ##Reference: 'o' stands for 'origin' and 'd' for destination.
        o_state_id = request.POST["o_state"] ##Getting the id of the state.
        o_city_name = request.POST.get("o_city") ##Getting the name of the city.
        o_city_obj = UsCities.objects.filter(id_state=o_state_id, city=o_city_name).first()
        d_state_id = request.POST["d_state"] ##Getting the id of the state.
        d_city_name = request.POST.get("d_city") ##Getting the name of the city.
        d_city_obj = UsCities.objects.filter(id_state=d_state_id, city=d_city_name).first()
        date = request.POST["date_picker"]
        time = request.POST["time_picker"]
        est_time = request.POST["est_time"]
        car_size = request.POST["car_size"]
        avai_seats = request.POST["seats"]
        driver = request.user
        new_trip = Trip(driver=driver, origin=o_city_obj, destination=d_city_obj, date=date, time=time, est_time=est_time, car_size=car_size, avai_seats=avai_seats)
        new_trip.save()
        return render(request, "capstone/success.html", {
            "message": new_trip
        })
    else:
        return render(request, "capstone/create_trip.html", {
            "states": UsStates.objects.all()
        })    
 
def delete_trip(request, trip_id):
    trip_obj = Trip.objects.get(id=trip_id)
    if trip_obj.driver == request.user:
        trip_obj.delete()
        return render(request, "capstone/success.html", {
            "message": "You have succesfully deleted the trip"
        })
    else:
        return render(request, "capstone/error.html", {
            "message": "You cannot delete a trip that is not yours"
        })
 
def get_cities(request,state_id):
    cities = list(UsCities.objects.filter(id_state=state_id))
    return HttpResponse(cities)

def add_passenger(request, trip_id):
    trip_obj = Trip.objects.filter(id=trip_id).first()
    user = request.user
    if trip_obj.passengers.filter(id=user.id).exists():
        trip_obj.passengers.remove(user)
        return HttpResponse('You have succesfully unlisted from the trip')
    else:
        trip_obj.passengers.add(user)
        return HttpResponse('You have succesfully registered for the trip.')
    
def get_passengers(request, trip_id):
    trip_obj = Trip.objects.filter(id=trip_id).first()
    return HttpResponse(trip_obj.passengers.count())


     