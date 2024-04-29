from django.db import models
from decimal import Decimal


class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    room = models.CharField(max_length=100)
    bsl = models.CharField(max_length=1, choices=[('1', 'BSL1'), ('2', 'BSL2'), ('3', 'BSL3'), ('4', 'BSL4')], null=True, blank=True)
    temperature = models.IntegerField(null=True, blank=True)
    humidity = models.IntegerField(null=True, blank=True)
    lights_on = models.TimeField(null=True, blank=True)
    lights_on_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return self.room


class Cage(models.Model):
    cage_id = models.AutoField(primary_key=True)
    cage = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    rack = models.CharField(max_length=100, null=True, blank=True)
    rack_position = models.CharField(max_length=100, null=True, blank=True)
    bedding = models.CharField(max_length=100, null=True, blank=True)
    water = models.CharField(max_length=100, null=True, blank=True)
    food = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.room}: {self.cage}"


class Experiment(models.Model):
    experiment_id = models.AutoField(primary_key=True)
    experiment = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.experiment


class ExperimentalGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    group = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.experiment}: {self.group}"


class Animal(models.Model):
    # Identification variables
    key = models.AutoField(primary_key=True)
    # Primary ID used to track all animals; must be unique
    animal_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    # Secondary ID that may be used for blinding or publication
    secondary_id = models.CharField(max_length=100, null=True, blank=True)
    # Method for visually marking the animal
    marking_method = models.CharField(max_length=1, choices=[('T', 'Tail Mark'), ('E', 'Ear Punch'), ('O', 'Other')], null=True, blank=True)
    marking = models.CharField(max_length=100, null=True, blank=True)

    # Biologic Variables
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')])
    species = models.CharField(max_length=100)
    strain = models.CharField(max_length=100)
    genotype = models.CharField(max_length=100, null=True, blank=True)
    female_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='offspring_of_female')
    male_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='offspring_of_male')
    wean_date = models.DateField(null=True, blank=True)
    euthanasia_datetime = models.DateTimeField(null=True, blank=True)

    # Administrative Variables
    protocol = models.CharField(max_length=100)
    use = models.CharField(max_length=1, choices=[('E', 'Experimental'), ('B', 'Breeder'), ('U', 'Undefined')])
    source = models.CharField(max_length=100, null=True, blank=True)
    room = models.ForeignKey(Room, editable=False, on_delete=models.SET_NULL, null=True, blank=True)
    cage = models.ForeignKey(Cage, on_delete=models.SET_NULL, null=True, blank=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    # Experimental Variables
    experiment = models.ForeignKey(Experiment, editable=False, on_delete=models.SET_NULL, null=True, blank=True)
    experimental_group = models.ForeignKey(ExperimentalGroup, on_delete=models.SET_NULL, null=True, blank=True)

    # Variables that can be calculated from existing data
    def age(self, date):
        return date - self.date_of_birth

    def weight(self, date):
        animal_weight = AnimalWeight.objects.filter(animal=self, date__lte=date).order_by('date').last()
        if animal_weight:
            return animal_weight.weight * Decimal(pow(10, animal_weight.weight_units))
        else:
            return None

    def save(self, *args, **kwargs):
        if self.cage:
            self.room = self.cage.room
        if self.experimental_group:
            self.experiment = self.experimental_group.experiment
        super().save(*args, **kwargs)

    def __str__(self):
        if self.animal_id:
            return self.animal_id
        else:
            return ''


class AnimalWeight(models.Model):
    animal_weight_id = models.AutoField(primary_key=True)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date = models.DateField()
    # Multiplies stored in the weight_units field normalize to g
    weight_units = models.IntegerField(choices=[(3, 'Kg'), (0, 'g'), (-3, 'mg')])
    weight = models.DecimalField(max_digits=7, decimal_places=3)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        rouded_weight = round(self.weight, 1)
        weight_units_display = dict(self._meta.get_field('weight_units').choices).get(self.weight_units)
        return f"{self.animal}: {rouded_weight} {weight_units_display}, ({self.date})"


class TreatmentPlan(models.Model):
    treatment_id = models.AutoField(primary_key=True)
    treatment = models.CharField(max_length=100)
    experimental_group = models.ForeignKey(ExperimentalGroup, on_delete=models.SET_NULL, null=True, blank=True)
    route = models.CharField(max_length=100)
    # Multiplies stored in the expected_animal_weight_units field normalize to Kg
    expected_animal_weight_units = models.IntegerField(choices=[(3, 'Kg'), (0, 'g'), (-3, 'mg')])
    expected_animal_weight = models.DecimalField(max_digits=7, decimal_places=3)
    # Multipliers stored in the volume_units field normalize to mL
    volume_units = models.IntegerField(choices=[(0, 'mL'), (-3, 'μL')])
    volume = models.DecimalField(max_digits=7, decimal_places=3)
    # Multipliers stored in the dose_units field normalize to mg
    dose_units = models.IntegerField(choices=[(0, 'mg'), (-3, 'μg'), (-6, 'ng'), (-9, 'pg')])
    dose = models.DecimalField(max_digits=7, decimal_places=3)

    # Variables that can be calculated from existing data
    @property
    def concentration(self):
        # Returns the treatment plan concentration in mg/mL
        return (Decimal(self.dose) * Decimal(pow(10, self.dose_units))) / (self.volume * Decimal(pow(10, self.volume_units)))

    @property
    def target_dose(self):
        # Returns the expected treatment plan dose in mg/Kg
        return round((Decimal(self.dose) * Decimal(pow(10, self.dose_units))) / (
                    self.expected_animal_weight * Decimal(pow(10, self.expected_animal_weight_units - 3))), 0)

    def __str__(self):
        return f"{self.treatment}: {self.target_dose} mg/Kg, {self.route}"


class TreatmentRecord(models.Model):
    treatment_record_id = models.AutoField(primary_key=True)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.SET_NULL, null=True, blank=True)
    datetime = models.DateTimeField()
    # Multipliers stored in the volume_units field normalize to mL
    volume_units = models.IntegerField(choices=[(0, 'mL'), (-3, 'μL')])
    volume = models.DecimalField(max_digits=7, decimal_places=3)
    notes = models.TextField(null=True, blank=True)

    # Variables that can be calculated based on existing data
    @property
    def actual_dose(self):
        # Returns the actual dose based on treatment plan concentration, actual volume, and last animal weight
        if self.animal.weight(self.datetime.date()):
            return Decimal(self.treatment_plan.concentration * self.volume * Decimal(pow(10, self.volume_units))) / (self.animal.weight(self.datetime.date()) / 1000)
        else:
            return 'n/a'

    def __str__(self):
        rounded_dose = round(self.actual_dose, 1)
        return f"{self.animal}: {self.treatment_plan.treatment}, {rounded_dose} mg/Kg, ({self.datetime.date()})"


class Tumor(models.Model):
    tumor_id = models.AutoField(primary_key=True)
    tumor = models.CharField(max_length=100, null=True, blank=True)
    source_species = models.CharField(max_length=100)
    source_sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')])
    source_age = models.IntegerField(null=True, blank=True)
    source_date = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=200)
    subtype = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.tumor


class ImplantedTumor(models.Model):
    implanted_tumor_id = models.AutoField(primary_key=True)
    tumor = models.ForeignKey(Tumor, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    passage = models.IntegerField(null=True, blank=True)
    implant_datetime = models.DateTimeField()
    implant_location = models.CharField(max_length=200)
    implant_method = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.animal}: {self.tumor}p{self.passage}, {self.implant_location}"


class TumorVolume(models.Model):
    tumor_volume_id = models.AutoField(primary_key=True)
    animal = models.ForeignKey(Animal, editable=False, on_delete=models.CASCADE)
    implanted_tumor = models.ForeignKey(ImplantedTumor, on_delete=models.CASCADE)
    date = models.DateField()
    method = models.CharField(max_length=100)
    # volumes should only be accepted in mm^3
    volume = models.DecimalField(max_digits=6, decimal_places=2)
    scan = models.FileField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.implanted_tumor:
            self.animal = self.implanted_tumor.animal
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.animal}: {self.implanted_tumor}, {self.volume} mm^3 ({self.date})"