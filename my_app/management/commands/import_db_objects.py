import os
from my_app.models import Genome
from django.core.management.base import BaseCommand
from datetime import datetime

class Command(BaseCommand):
    help = "Import data"

    def add_arguments(self, parser):
        parser.add_argument('directory_path', type=str)

    def handle(self, *args, **options):
        directory_path = options['directory_path']

        for filename in os.listdir(directory_path):


                if 'database_file' in filename:
                    with open(os.path.join(directory_path, filename), 'r') as f:
                        vetor_dados= f.readlines() #jogar o arquivo de entrada para uma lista
                        vetor_dados = [line3.strip() for line3 in vetor_dados]#retira o \n da lista


                        for item in vetor_dados:
                            aux = item.split('\t')

                            Genome.objects.create(
                                        genome_id = aux[0],
                                        clade = 'Clade '+aux[1],
                                        submission_date = datetime.strptime(aux[2], '%d-%b-%Y').date(),
                                        country = aux[3],
                                        region = aux[4],
                                        host = aux[5],
                                        length = aux[6],
                                        sequence = aux[7]
                                    )