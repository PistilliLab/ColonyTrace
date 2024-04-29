import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from colonyDB.models import Animal

class Command(BaseCommand):
    help = 'Import animals from a TSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the TSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        self.import_animals_from_tsv(file_path)

    def import_animals_from_tsv(self, file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            for row in reader:
                animal = Animal()
                animal.use = {'Experimental': 'E', 'Breeder': 'B', 'Undefined': 'U'}.get(row['Use'], 'U')
                animal.species = 'Mus Musculus'
                animal.strain = row['Strain']

                mouse_id = row['Mouse ID']
                if mouse_id:
                    existing_ids = Animal.objects.filter(animal_id=mouse_id).exists()
                    if existing_ids:
                        print(f"Skipping duplicate Mouse ID: {mouse_id}")
                        continue
                    animal.animal_id = mouse_id
                else:
                    # Generate a unique ID for empty mouse IDs
                    animal.animal_id = None

                animal.protocol = row['Protocol Number']
                animal.sex = {'Male': 'M', 'Female': 'F', 'Unknown': 'U'}.get(row['Sex'], 'U')
                animal.date_of_birth = datetime.strptime(row['DOB'], '%m/%d/%Y').date()
                animal.wean_date = datetime.strptime(row['Wean Date'], '%m/%d/%Y').date() if row['Wean Date'] else None
                animal.label = row['Labels']
                animal.notes = row['Notes']
                animal.save()