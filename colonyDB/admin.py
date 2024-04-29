from django.contrib import admin
from .models import Experiment, ExperimentalGroup, Tumor, ImplantedTumor, Animal, AnimalWeight, TreatmentPlan, TreatmentRecord, TumorVolume


class AnimalAdmin(admin.ModelAdmin):
    list_display = ('animal_id', 'strain', 'sex', 'date_of_birth', 'experimental_group')
    list_filter = ('species', 'strain', 'sex', 'use', 'experiment', 'experimental_group', 'euthanasia_datetime')
    search_fields = ('animal_id', 'experiment', 'experimental_group', 'euthanasia_datetime')

class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'description', 'start_date', 'end_date')
    list_filter = ('experiment', 'start_date', 'end_date')
    search_fields = ('experiment', 'start_date', 'end_date')

class AnimalWeightAdmin(admin.ModelAdmin):
    list_display = ('animal', 'weight', 'date')
    list_filter = ('animal', 'date')
    search_fields = ('animal', 'date')

class TreatmentRecordAdmin(admin.ModelAdmin):
    list_display = ('animal', 'treatment_plan', 'date')
    list_filter = ('animal', 'date')
    search_fields = ('animal', 'date')

admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(ExperimentalGroup)
admin.site.register(Tumor)
admin.site.register(ImplantedTumor)
admin.site.register(Animal, AnimalAdmin)
admin.site.register(AnimalWeight, AnimalWeightAdmin)
admin.site.register(TreatmentPlan)
admin.site.register(TreatmentRecord)
admin.site.register(TumorVolume)
