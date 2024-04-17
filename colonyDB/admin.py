from django.contrib import admin
from .models import Experiment, ExperimentalGroup, Tumor, ImplantedTumor, Animal, AnimalWeight, TreatmentPlan, TreatmentRecord, TumorVolume


class AnimalAdmin(admin.ModelAdmin):
    list_display = ('animal_id', 'strain', 'sex', 'date_of_birth', 'experiment', 'label')
    list_filter = ('species', 'strain', 'sex', 'use', 'experiment')
    search_fields = ('animal_id', 'experiment')

class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'start_date', 'end_date')
    list_filter = ('title', 'start_date', 'end_date')
    search_fields = ('title', 'start_date', 'end_date')

admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(ExperimentalGroup)
admin.site.register(Tumor)
admin.site.register(ImplantedTumor)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(AnimalWeight)
admin.site.register(TreatmentPlan)
admin.site.register(TreatmentRecord)
admin.site.register(TumorVolume)
