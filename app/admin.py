from django.contrib import admin
from .models import User, WatchList, Plotting

# Register your models here.
admin.site.register(User)
admin.site.register(Plotting)
admin.site.register(WatchList)
