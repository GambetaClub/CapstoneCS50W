from django.contrib import admin

# Register your models here.

from .models import User, UsStates, UsCities, Trip

admin.site.register(User)
admin.site.register(UsStates)
admin.site.register(UsCities)
admin.site.register(Trip)