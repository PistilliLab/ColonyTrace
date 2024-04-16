from django.db import models
from decimal import Decimal


class Experiment(models.Model):
    experiment_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class ExperimentalGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)
    description = models.TextField()


class Tumor(models.Model):
    tumor_id = models.AutoField(primary_key=True)
    source_species = models.CharField(max_length=100)
    source_sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')])
    source_age = models.IntegerField(null=True, blank=True)
    source_date = models.DateField(null=True, blank=True)
    tumor_type = models.CharField(max_length=200)
    tumor_subtype = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class ImplantedTumor(models.Model):
    implanted_tumor_id = models.AutoField(primary_key=True)
    tumor = models.ForeignKey(Tumor, on_delete=models.CASCADE)
    passage = models.IntegerField(null=True, blank=True)
    implant_date = models.DateField()
    implant_location = models.CharField(max_length=200)
    implantation_method = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)


class Animal(models.Model):
    primary_key = models.AutoField(primary_key=True)

    # Biologic Variables
    animal_id = models.IntegerField(unique=True)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')])
    species = models.CharField(max_length=100)
    strain = models.CharField(max_length=100)
    female_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='offspring_of_female')
    male_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='offspring_of_male')
    wean_date = models.DateField(null=True, blank=True)
    euthanasia_date = models.DateField(null=True, blank=True)

    # Administrative Variables
    protocol = models.CharField(max_length=100)
    use = models.CharField(max_length=1, choices=[('E', 'Experimental'), ('B', 'Breeder'), ('U', 'Undefined')])
    room = models.CharField(max_length=100, null=True, blank=True)
    cage = models.CharField(max_length=100, null=True, blank=True)
    label = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    # Experimental Variables
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True, blank=True)
    experimental_group = models.ForeignKey(ExperimentalGroup, on_delete=models.SET_NULL, null=True, blank=True)

    # Tumor Variables
    tumor = models.ForeignKey(Tumor, on_delete=models.SET_NULL, null=True, blank=True)
    implanted_tumor = models.ForeignKey(ImplantedTumor, on_delete=models.SET_NULL, null=True, blank=True)

    # Variables that can be calculated from existing data
    def age(self, date):
        return date - self.date_of_birth

    def weight(self, date):
        animal_weight = AnimalWeight.objects.filter(animal=self, date__lte=date).order_by('date').last()
        if animal_weight:
            return animal_weight.weight
        else:
            return None  # Or whatever default value you prefer if no weight is found


class AnimalWeight(models.Model):
    animal_weight_id = models.AutoField(primary_key=True)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date = models.DateField()
    # Multiplies stored in the weight_units field normalize to g
    weight_units = models.IntegerField(choices=[(3, 'Kg'), (0, 'g'), (-3, 'mg')])
    weight = models.DecimalField(max_digits=7, decimal_places=3)
    notes = models.TextField(null=True, blank=True)


class TreatmentPlan(models.Model):
    treatment_id = models.AutoField(primary_key=True)
    treatment = models.CharField(max_length=100)
    experiment = models.ForeignKey(Experiment, on_delete=models.SET_NULL, null=True, blank=True)
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
        return (self.dose * pow(10, self.dose_units)) / (self.volume * pow(10, self.volume_units))

    @property
    def target_dose(self):
        # Returns the expected treatment plan dose in mg/Kg
        return (self.dose * pow(10, self.dose_units)) / (
                    self.expected_animal_weight * pow(10, self.expected_animal_weight_units - 3))


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
        return Decimal(self.treatment_plan.concentration * self.volume * pow(10, self.volume_units)) / self.animal.weight(self.datetime.date())


class TumorVolume(models.Model):
    tumor_volume_id = models.AutoField(primary_key=True)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    implanted_tumor = models.ForeignKey(ImplantedTumor, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    method = models.CharField(max_length=100)
    # volumes should only be accepted in mm^3
    volume = models.DecimalField(max_digits=6, decimal_places=2)
    scan = models.FileField(null=True, blank=True)
