from django.contrib import admin

from .models import Experiment, ExperimentalGroup, Tumor, ImplantedTumor, Animal, AnimalWeight, TreatmentPlan, TreatmentRecord, TumorVolume

admin.site.register(Experiment)
admin.site.register(ExperimentalGroup)
admin.site.register(Tumor)
admin.site.register(ImplantedTumor)
admin.site.register(Animal)
admin.site.register(AnimalWeight)
admin.site.register(TreatmentPlan)
admin.site.register(TreatmentRecord)
admin.site.register(TumorVolume)
