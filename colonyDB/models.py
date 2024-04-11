from django.db import models
from datetime import date
import json


class Experiment(models.Model):
    experiment_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()


class ExperimentalGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)
    description = models.TextField()


class Animal(models.Model):
    primary_key = models.AutoField(primary_key=True)

    # Biologic variables
    animal_id = models.IntegerField(unique=True)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')])
    species = models.CharField(max_length=100)
    strain = models.CharField(max_length=100)
    female_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='offspring_of_female')
    male_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='offspring_of_male')
    wean_date = models.DateField(null=True, blank=True)
    euthanasia_date = models.DateField(null=True, blank=True)

    # Administrative variables
    protocol = models.CharField(max_length=100)
    use = models.CharField(max_length=1, choices=[('E', 'Experimental'), ('B', 'Breeder'), ('U', 'Undefined')])
    room = models.CharField(max_length=100)
    cage = models.CharField(max_length=100)
    label = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField

    # Experimental Variables
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True, blank=True)
    experimental_group = models.ForeignKey(ExperimentalGroup, on_delete=models.SET_NULL, null=True, blank=True)

    # Variables that can be calculated from existing data
    @property
    def age(self):
        return date.today() - self.date_of_birth


class AnimalHistory(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    event_date = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=100)
    animal_snapshot = models.JSONField()

    @classmethod
    def create_from_Animal(cls, animal, event_type):
        animal_snapshot = {
            'animal_id': animal.animal_id,
            'date_of_birth': str(animal.date_of_birth),
            'sex': animal.sex,
            'species': animal.species,
            'strain': animal.strain,
            'female_parent_id': animal.female_parent.animal_id if animal.female_parent else None,
            'male_parent_id': animal.male_parent.animal_id if animal.male_parent else None,
            'wean_date': str(animal.wean_date),
            'euthanasia_date': str(animal.euthanasia_date),
            'protocol': animal.protocol,
            'use': animal.use,
            'room': animal.room,
            'cage': animal.cage,
            'label': animal.label,
            'notes': animal.notes,
            'experiment_id': animal.experiment.experiment_id if animal.experiment else None,
            'experimental_group_id': animal.experimental_group.group_id if animal.experimental_group else None,
        }
        return cls.objects.create(animal=animal, event_type=event_type, animal_snapshot=json.dumps(animal_snapshot))



