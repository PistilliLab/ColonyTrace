from decimal import Decimal
import datetime
from django.test import TestCase
from django.utils import timezone
from datetime import date
from .models import Animal, AnimalWeight, TreatmentRecord, TreatmentPlan


class TestAnimalAge(TestCase):
    def setUp(self):
        self.animal = Animal.objects.create(
            animal_id=1,
            date_of_birth=date(2022, 1, 1),
            sex='M',
            species='Mouse',
            strain='Balb/c'
        )

    def test_age_today(self):
        # Test age calculation when date of birth is same day
        expected_age = datetime.timedelta(days=0)
        self.assertEqual(self.animal.age(date(2022, 1, 1)), expected_age)

    def test_age_one_year_ago(self):
        # Test age calculation when date of birth is exactly 1 year prior
        expected_age = datetime.timedelta(days=365)
        self.assertEqual(self.animal.age(date(2023, 1, 1)), expected_age)

    def test_age_future_dob(self):
        # Test age calculation when date of birth is exactly 1 year in the future
        expected_age = datetime.timedelta(days=-365)
        self.assertEqual(self.animal.age(date(2021, 1, 1)), expected_age)


class TestAnimalWeight(TestCase):
    def setUp(self):
        # Create an animal
        self.animal = Animal.objects.create(
            animal_id=1,
            date_of_birth=date(2022, 1, 1),
            sex='M',
            species='Mouse',
            strain='Balb/c'
        )
        # Create animal weights
        AnimalWeight.objects.create(
            animal=self.animal,
            date=date(2022, 1, 1),
            weight_units=0,  # g
            weight=20.5
        )
        AnimalWeight.objects.create(
            animal=self.animal,
            date=date(2022, 1, 5),
            weight_units=3,  # g
            weight=22.1
        )

    def test_weight(self):
        # Test for weight on same date
        expected_weight = Decimal(20.5)
        weight_on_date = self.animal.weight(date=date(2022, 1, 1))
        self.assertTrue(abs(weight_on_date - expected_weight) < 0.0001) # The weight on 2022-01-01

        # Test for weight on a date after entry
        expected_weight = Decimal(22100)
        weight_on_date = self.animal.weight(date=date(2022, 1, 7))
        self.assertTrue(abs(weight_on_date - expected_weight) < 0.0001) # The weight on 2022-01-05

        # Test for weight on a date before any entry
        weight_on_date = self.animal.weight(date=date(2021, 1, 1))
        self.assertIsNone(weight_on_date)  # No weight on 2021-01-01


class TestTreatmentPlanProperties(TestCase):
    def setUp(self):
        # Create a TreatmentPlan object for testing
        self.treatment_plan = TreatmentPlan.objects.create(
            treatment='Test Treatment',
            expected_animal_weight_units=0,  # g
            expected_animal_weight=30,
            volume_units=-3,  # μL
            volume=150,
            dose_units=0,  # mg
            dose=0.9
        )

    def test_concentration(self):
        # Test the concentration property
        expected_concentration = 6
        calculated_concentration = self.treatment_plan.concentration
        self.assertTrue(abs(self.treatment_plan.concentration - expected_concentration) < 0.0001)

    def test_target_dose(self):
        # Test the target_dose property
        expected_target_dose = 30
        self.assertTrue(abs(self.treatment_plan.target_dose - expected_target_dose) < 0.0001)


class TestActualDose(TestCase):
    def setUp(self):
        # Create an animal
        self.animal = Animal.objects.create(
            animal_id=1,
            date_of_birth=date(2022, 1, 1),
            sex='M',
            species='Mouse',
            strain='Balb/c'
        )

        # Create animal weights
        AnimalWeight.objects.create(
            animal=self.animal,
            date=date(2022, 3, 15),
            weight_units=0,  # g
            weight=20.5
        )
        AnimalWeight.objects.create(
            animal=self.animal,
            date=date(2022, 3, 28),
            weight_units=0,  # g
            weight=21.5
        )

        # Create a treatment plan
        self.treatment_plan = TreatmentPlan.objects.create(
            treatment='Test Treatment',
            expected_animal_weight_units=0,  # g
            expected_animal_weight=30,
            volume_units=-3,  # μL
            volume=150,
            dose_units=0,  # mg
            dose=0.9
        )

        # Create a treatment record
        self.treatment_record = TreatmentRecord.objects.create(
            animal=self.animal,
            treatment_plan=self.treatment_plan,
            datetime = timezone.make_aware(datetime.datetime(2024, 3, 28, 8, 30, 0)),
            volume_units=-3,
            volume=150
        )

    def test_actual_dose(self):
        # Test the actual_dose property
        expected_dose = Decimal(41.86)
        print(f"\nActual Dose is: {self.treatment_record.actual_dose}")
        self.assertTrue(abs(self.treatment_record.actual_dose - expected_dose) < 0.001)