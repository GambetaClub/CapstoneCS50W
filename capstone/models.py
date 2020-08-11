from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.timezone import activate
from django.conf import settings
activate(settings.TIME_ZONE)


class User(AbstractUser):
    pass

    def __str__(self):
        return f"{self.username}"


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField(max_length=230)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"<{self.timestamp}> {self.author}: {self.content}"

class UsCities(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    id_state = models.ForeignKey('UsStates', models.DO_NOTHING, db_column='ID_STATE')  # Field name made lowercase.
    city = models.CharField(db_column='CITY', max_length=50)  # Field name made lowercase.
    county = models.CharField(db_column='COUNTY', max_length=50)  # Field name made lowercase.
    latitude = models.TextField(db_column='LATITUDE')  # Field name made lowercase. This field type is a guess.
    longitude = models.TextField(db_column='LONGITUDE')  # Field name made lowercase. This field type is a guess.

    def __str__(self):
        return f"{self.city},"
    
    
    class Meta:
        managed = False
        db_table = 'US_CITIES'


class UsStates(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    state_code = models.CharField(db_column='STATE_CODE', max_length=2)  # Field name made lowercase.
    state_name = models.CharField(db_column='STATE_NAME', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'US_STATES'

        
class Trip(models.Model):
    driver = models.ForeignKey(User,on_delete=models.CASCADE, related_name="trips")
    passengers = models.ManyToManyField(User)
    origin = models.ForeignKey(UsCities, on_delete=models.CASCADE, related_name="departures")
    destination = models.ForeignKey(UsCities, on_delete=models.CASCADE, related_name="arrivals")
    date = models.DateField(verbose_name="departure day", null=False)
    time = models.TimeField(verbose_name="departure time", null=False)
    car_size = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(20)], default=2)
    avai_seats = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(19)], default=1)
    est_time = models.CharField(max_length=64)
    
    def __str__(self):
        return f"<Origin: {self.origin} {self.origin.id_state.state_name}>, <Destination: {self.destination} {self.destination.id_state.state_name}> <Date:{self.date}>, <Departure:{self.time}>"