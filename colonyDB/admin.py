from django.contrib import admin

from .models import Animal, Experiment, ExperimentalGroup

admin.site.register(Animal)
admin.site.register(Experiment)
admin.site.register(ExperimentalGroup)
