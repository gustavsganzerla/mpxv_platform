from django.shortcuts import render
from django.http import HttpResponse
from . forms import GenomeQueryForm
from django.db.models import Q, Func
from . models import Genome
from datetime import datetime
import csv



#functions to treat data
class ConvertDate(Func):
    function = 'STR_TO_DATE'
    template = '%(function)s(%(expressions)s, %s)'

# Create your views here.

def home(request):
    return render(request, 'my_app/home.html')


def db_home(request):

    form = GenomeQueryForm()
    results = Genome.objects.all()

    if request.method == 'POST':
        form = GenomeQueryForm(request.POST)

        if form.is_valid():
            collected_data = form.cleaned_data
            
            q_objects = Q()

            #treat each of the model fields separately and keep appending to the Q object
            
            ###host
            if form.cleaned_data.get('host'):
                if collected_data['host'].lower == 'human':
                    collected_data['host'] = 'Homo sapiens'
                q_objects &= Q(host__icontains = collected_data['host'])

            ###country
            if form.cleaned_data.get('country'):
                q_objects &= Q(country__icontains = collected_data['country'])

            ###clade
            if form.cleaned_data.get('clade'):
                q_objects &= Q(clade__icontains = collected_data['clade'])                
            
            ###region
            if form.cleaned_data.get('region'):
                q_objects &= Q(region__icontains = collected_data['region'])


            ###genome id
            if form.cleaned_data.get('genome_id'):
                q_objects &= Q(genome_id__icontains = collected_data['genome_id'])

            if form.cleaned_data.get('start_date'):
                #the form is collecting in the YYYY-MM-DD format
                start_date = form.cleaned_data['start_date']
                # Ensure start_date is a string before converting
                if isinstance(start_date, str):
                    start_date_formatted = datetime.strptime(start_date, '%Y-%m-%d').date()
                else:
                    start_date_formatted = start_date  # It might already be a date object

                # i need to convert YYYY-MM-DD which is the DB format
                #now i can query in the db

                q_objects &= Q(submission_date__gte=start_date)


            if form.cleaned_data.get('end_date'):
                end_date = form.cleaned_data['end_date']
                if isinstance(end_date, str):
                    end_date_formatted = datetime.strptime(end_date, '%Y-%m-%d').date()
                else:
                    end_date_formatted = end_date

                q_objects &= Q(submission_date__lte=end_date)
                
            

            
            if q_objects:
                results = results.filter(q_objects)

                queryset_data = []
                queryset_data = list(results.values())
                
                context = []

                for item in queryset_data:
                    context.append({
                        'host':item['host'],
                        'country':item['country'],
                        'clade':item['clade'],
                        'region':item['region'],
                        'genome_id':item['genome_id'],
                        'submission_date':str(item['submission_date'])
                    })
                
                return render(request, 'my_app/view_db_query.html', {'context':context,
                                                                     'query_len':len(context)})
    
    else:
        form = GenomeQueryForm()

    return render(request, 'my_app/db_home.html', context = {'form': form})

def view_genome_db(request, genome_id):
    genome_queryset = Genome.objects.filter(genome_id__contains=genome_id)

    if genome_queryset is not None:
        queryset_data = list(genome_queryset.values())
        
        context = []
        for item in queryset_data:
            context.append({
                'genome_id': item['genome_id'],
                'host':item['host'],
                'country':item['country'],
                'region':item['region'],
                'clade':item['clade'],
                'sequence': item['sequence']})

            genome_len = len(item['sequence'])

            return render(request, 'my_app/view_genome_db.html', context = {'context':context,
                'genome_len':genome_len})
        
def download_query_csv(request):
    result_query= request.session.get('result_query', None)

    if result_query:
        csv_content = []
        csv_content.append(['Genome ID',
            'Host',
            'Country',
            'Region',
            'Clade'])

        for query in result_query:
            csv_content.append([
                query['genome_id'],
                query['host'],
                query['country'],
                query['region'],
                query['clade']
            ])

        if csv_content:
            response = HttpResponse(content_type = "text/csv")
            response['Content-Disposition'] = 'attachment; filename="query.csv"'
            
            csv_writer = csv.writer(response)

            for row in csv_content:
                csv_writer.writerow(row)
            return response
        
def download_genome(request, genome_id):
    genome_queryset = Genome.objects.filter(genome_id__contains=genome_id)

    if genome_queryset:

        response = HttpResponse(content_type = 'text/plain')
        response['Content-Disposition'] = 'attachment; filename = "genome.fasta"'
        queryset_data = list(genome_queryset.values())
        for item in queryset_data:
            response.write(f">{item['genome_id']}\n{item['sequence']}")
        return response