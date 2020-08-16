from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,  HttpResponseForbidden
from django.shortcuts import render, redirect
from collections import namedtuple
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from datetime import date
from .models import User, UsStates, UsCities, Trip, Message
import pytz

def namedtuplefetchall(cursor):
    "Function which returns all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def index(request):
    # Index page
    return render(request, "capstone/index.html")

def login_view(request):
    # Login page.
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
    # Logout user
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    # Register user
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
        return HttpResponseRedirect(reverse("user_extra_info"))
    else:
        return render(request, "capstone/register.html")


@login_required
def user_extra_info(request):
    # Second part of registration. This is optional information. 
    if request.method == 'POST':
        
        f_name = request.POST["first_name"]
        l_name = request.POST["last_name"]
        phone = request.POST["phone"]
        instagram = request.POST["instagram"]
        profession = request.POST["profession"]
        interests = request.POST["interests"]
        
        # Getting the user object.
        user = User.objects.get(username=request.user.username)
        
        # Checking if the input where empty and updating user infomration.
        if f_name is not None or f_name != '':
            user.first_name = f_name
        if l_name is not None or l_name != '':
            user.last_name = l_name
        if phone is not None or phone != '':
            user.phone = phone
        if instagram is not None or instagram != '':
            user.instagram = instagram   
        if profession is not None or profession != '':
            user.profession = profession    
        if interests is not None or interests != '':
            user.interests = interests
        user.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "capstone/user_extra_info.html")

    
@login_required
def set_timezone(request):
    # Sets timezone for synchronazing messages timestamp.
    if request.method == 'POST':
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/')
    else:
        return render(request, 'capstone/set_timezone.html', {'timezones': pytz.common_timezones})

@login_required
def profile(request, user_username):
    # Returns user information and displays its profile page.
    user = User.objects.get(username=user_username)
    if user is None:
        return render(request, "capstone/error.html", {
        "message": "That user doesn't not exist in the website. Maybe is your imagination."
    })
    return render(request, "capstone/profile.html", {
        "user": user
    })


@login_required
def messages(request):
    # Returns last 12 messages from the user from newer to older.
    return render(request, "capstone/messages.html", {
        "users": User.objects.all(),
        "received_messages": Message.objects.filter(receiver=request.user).order_by('-id')[:12],
        "sent_messages": Message.objects.filter(author=request.user).order_by('-id')[:12]
    })
    
@login_required
def send_message(request):
    # Creates a new message and returs messages page.
    if request.method == "POST":
        msg_content = request.POST['content']
        msg_receiver_id = request.POST.get('receiver')
        new_msg = Message.objects.create(author=request.user, content=msg_content, receiver=User.objects.get(id=msg_receiver_id))
        new_msg.save()
        return HttpResponseRedirect(reverse("messages"))
    else:
    # Just to make sure no one can send a message with a get request.
        return render(request, "capstone/error.html", {
            "message": "You cannot send messages with a get request"
        })
    
    
def trips(request):
    # Returns only future trips and orders them by date. 
    return render(request, "capstone/trips.html",{
        "states": UsStates.objects.all(),
        "trips": Trip.objects.filter(date__gte=date.today()).order_by('date')
    })
    
    
def user_trips(request):
    # Returns trips which the user either is a passenger or driver.
   user = request.user
   trips = Trip.objects.filter(date__gte=date.today()).order_by('date')
   return render(request,"capstone/user_trips.html", {
       "p_trips": trips.filter(passengers=user),
       "d_trips":  trips.filter(driver=user)
   })

    
def search_trip(request):
    # Handles search by checking which fields were used and adding a filter to main query.
    
    # Main query (Only future trips and ordered by date)
    qs = Trip.objects.filter(date__gte=date.today()).order_by('date')
    
    # Getting inputs 
    o_state = request.GET.get('o_state')
    o_city = request.GET.get('o_city')
    d_state = request.GET.get('d_state')
    d_city = request.GET.get('d_city')
    
    #Checking whether the input was filled. If so, it adds a filter to the main query depending on the input.
    if o_state != '' and o_state is not None:
        qs = qs.filter(origin__id_state__state_name__icontains=o_state)
    
    if o_city != '' and o_city is not None:
        qs = qs.filter(origin__city__icontains=o_city)
            
    if d_state != '' and d_state is not None:
        qs = qs.filter(destination__id_state__state_name__icontains=d_state)
        
    if d_city != '' and d_city is not None:
        qs = qs.filter(destination__city__icontains=d_city)
    
    return render(request, "capstone/trips.html", {
        "trips": qs
    })

def trip(request, trip_id):
    # Displays trip details.
    trip_obj = Trip.objects.get(id=trip_id)
    trip_passengers = trip_obj.passengers.all()
    
    # Checking if the user is also the trip driver. Depending on this,
    # on one hand displays delete trip or the option to list or unlist
    # from the trip.
    if request.user == trip_obj.driver:
            return render(request, "capstone/trip.html", {
                "self": True,
                "trip": trip_obj,
                "passengers": trip_passengers,
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
            
@login_required
def create_trip(request):
    # Creates a new trip.

    # If the user submitted a form it tries to create a trip.
    if request.method == "POST":    # Reference: 'o' stands for 'origin' and 'd' for destination.
        # Selection part.
        o_state_id = request.POST["o_state"] # Getting the id of the state.
        o_city_name = request.POST.get("o_city") # Getting the name of the city.
        o_city_obj = UsCities.objects.filter(id_state=o_state_id, city=o_city_name).first()
        d_state_id = request.POST["d_state"] # Getting the id of the state.
        d_city_name = request.POST.get("d_city") # Getting the name of the city.
        d_city_obj = UsCities.objects.filter(id_state=d_state_id, city=d_city_name).first()
        
        date = request.POST["date_picker"]
        time = request.POST["time_picker"]
        est_time = request.POST["est_time"]
        car_size = request.POST["car_size"]
        avai_seats = request.POST["seats"]
        driver = request.user
        new_trip = Trip(driver=driver, origin=o_city_obj, destination=d_city_obj, date=date, time=time, est_time=est_time, car_size=car_size, avai_seats=avai_seats)
        new_trip.save()
        return redirect(reverse("trips"))
    else:
        return render(request, "capstone/create_trip.html", {
            "states": UsStates.objects.all()
        })
        
@login_required
def delete_trip(request, trip_id):
    # Deletes a trip.
    trip_obj = Trip.objects.get(id=trip_id)
    # Checking if the user is the driver of the trip since it should be the only one with the permission.
    if trip_obj.driver == request.user:
        trip_obj.delete()
        return render(request, "capstone/success.html", {
            "message": "You have succesfully deleted the trip."
        })
    # If not, displays an error.
    else:
        return render(request, "capstone/error.html", {
            "message": "You cannot delete a someone's else trip."
        })

@login_required
def add_passenger(request, trip_id):
    # Function that removes or add a passenger from/to certain trip.
    trip_obj = Trip.objects.get(id=trip_id)
    user = request.user
    # Checking if the user is already a passanger of such trip.
    if trip_obj.passengers.filter(id=user.id).exists():
        # If it is, removes the passenger from the trip.
        trip_obj.passengers.remove(user)
        trip_obj.avai_seats += 1
        trip_obj.save()
    # If it's not, it adds the passenger.
    else:
        if trip_obj.avai_seats > 0:
            trip_obj.passengers.add(user)
            trip_obj.avai_seats -= 1
            trip_obj.save()
         # If it doesn't have seats available, it displays message.
        else:
            return HttpResponseForbidden('This trip has no seats available.')

def full_trip(request):
    # Function that displays message.
    return render(request, "capstone/error.html", {
        "message": "This trips has no seats available"
    })
   
def get_cities(request,state_id):
    # Gets the cities from cetain state. (It is for create trip page selection input)
    cities = list(UsCities.objects.filter(id_state=state_id))
    return HttpResponse(cities)
    
def get_passengers(request, trip_id):
    # Function that gets passengers from certain trip. (It is for trip page)
    trip_obj = Trip.objects.filter(id=trip_id).first()
    return HttpResponse(trip_obj.passengers.count())

def get_seats(request, trip_id):
    # Function that gets seats from certain trip. (It is for trip page)
    trip_obj = Trip.objects.get(id=trip_id)
    return HttpResponse(trip_obj.avai_seats)

@login_required
def read_message(request, message_id):
    # Function that reads a message.
    message = Message.objects.get(id=message_id)
    # Checking if the user is the receiver of the trip. It should be the only one with the permission to do it.
    if request.user == message.receiver:
        message.read = True
        message.save()
        return HttpResponse(True)
    # If it's not, it displays an error.
    else:
        return render(request, "cpastone/error.html",{
            "message": "You cannot read someone's else message."
        })
    