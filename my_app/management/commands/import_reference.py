from django.core.management.base import BaseCommand
from my_app.models import Reference
import os


class Command(BaseCommand):
    help = "Parse the file ids_mpox.txt to a sql model"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type = str)

    def handle(self, *args, **options):
        file_path = options['file_path']

        with open(file_path, 'r') as file:

             data_array = file.readlines()
             data_array = [line3.strip() for line3 in data_array]

             for item in data_array:

                 Reference.objects.create(
                     accession = item
                    
                    )