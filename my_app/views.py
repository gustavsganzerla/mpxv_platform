from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from . forms import GenomeQueryForm, annotationForm
from django.db.models import Q, Func
from . models import Genome, Reference
from datetime import datetime
import csv
import tempfile
from Bio import SeqIO
import os
import subprocess
from io import StringIO



#functions to treat data
class ConvertDate(Func):
    function = 'STR_TO_DATE'
    template = '%(function)s(%(expressions)s, %s)'

# Create your views here.

def home(request):
    return render(request, 'my_app/home.html')

###database views
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
                
                request.session['result_query'] = context
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
    
###annotation views
def annotation(request):
    form = annotationForm()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'term' in request.GET:
        term = request.GET.get('term')

        qs = Reference.objects.filter(accession__contains=term)
        names = list(qs.values_list('accession', flat=True))
        return JsonResponse(names, safe=False)
    
    if request.method=='POST':
        form = annotationForm(request.POST, request.FILES)
        if form.is_valid():
            collected_data = form.cleaned_data
            uploaded_file = collected_data.get('uploaded_file')

            ###in the annotation pipeline, i will need 3 files, all from user input
            if uploaded_file:
                uploaded_file_data = uploaded_file.read().decode('utf-8')
                uploaded_file_io = StringIO(uploaded_file_data)

                ###file 1: user fasta sequence
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_seq_file:
                    temp_seq_file_path = temp_seq_file.name

                    for record in SeqIO.parse(uploaded_file_io, 'fasta'):
                        temp_seq_file.write(f">{record.id}\n{record.seq}\n")
                        temp_strain = record.id

                ###file 2: the .sbt file with submission details.
                first_name = collected_data.get('first_name')
                last_name = collected_data.get('last_name')
                email = collected_data.get('email')
                organization = collected_data.get('organization')
                department = collected_data.get('department')
                street = collected_data.get('street')
                city = collected_data.get('city')
                state = collected_data.get('state')
                postal_code = collected_data.get('postal_code')
                country = collected_data.get('country')
                author_first_name = collected_data.get('author_first_name')
                author_last_name = collected_data.get('author_last_name')
                reference_title = collected_data.get('reference_title')

                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_sbt_file:
                    temp_sbt_file_path = temp_sbt_file.name

                    temp_sbt_file.write(f'Submit-block ::= {{\n  contact {{\n    contact {{\n      name name {{\n')
                    temp_sbt_file.write(f'        last "{last_name}",\n        first "{first_name}",\n')
                    temp_sbt_file.write(f'        middle "",\n        initials "",\n        suffix "",\n        title ""\n      }},\n')
                    temp_sbt_file.write(f'      affil std{{\n')
                    temp_sbt_file.write(f'        affil "{organization}",\n        div "{department}",\n        city "{city}",\n        sub"{state}",\n')
                    temp_sbt_file.write(f'        country "{country}",\n        email "{email}",\n        postal-code"{postal_code}"\n')
                    temp_sbt_file.write(f'      }}\n    }}\n  }},\n')
                    temp_sbt_file.write(f'  cit {{\n')
                    temp_sbt_file.write(f'    authors {{\n')
                    temp_sbt_file.write(f'      names std {{\n')
                    temp_sbt_file.write(f'        {{\n')
                    temp_sbt_file.write(f'          name name {{\n')
                    temp_sbt_file.write(f'            last "{author_last_name}",\n')
                    temp_sbt_file.write(f'            first "{author_first_name}",\n')
                    temp_sbt_file.write(f'            middle "",\n            initials "",\n            suffix "",\n            title ""\n')
                    temp_sbt_file.write(f'          }}\n        }}\n      }},\n')
                    temp_sbt_file.write(f'      affil std {{\n')
                    temp_sbt_file.write(f'        affil "{organization}",\n        div "{department}",\n        city "{city}",\n        sub"{state}",\n')
                    temp_sbt_file.write(f'        country "{country}",\n        email "{email}",\n        postal-code"{postal_code}"\n')
                    temp_sbt_file.write(f'      }}\n    }}\n  }},\n')
                    temp_sbt_file.write(f'  subtype new\n}}\n')
                    temp_sbt_file.write(f'Seqdesc ::= pub {{\n  pub {{\n    gen {{\n      cit "{reference_title}",\n')
                    temp_sbt_file.write(f'      authors {{\n        names std {{\n          {{\n            name name {{\n')
                    temp_sbt_file.write(f'              last "{author_last_name}",\n')
                    temp_sbt_file.write(f'              first "{author_first_name}",\n')
                    temp_sbt_file.write(f'              middle "",\n              initials "",\n              suffix "",\n              title ""\n            }}\n')
                    temp_sbt_file.write(f'          }}\n        }}\n      }},\n')
                    temp_sbt_file.write(f'      title "{reference_title}"\n    }}\n  }}\n}}\n')
                    temp_sbt_file.write(f'Seqdesc ::= user {{\n  type str "Submission",\n  data {{\n    {{\n')
                    temp_sbt_file.write(f'      label str "AdditionalComment",\n      data str "ALT EMAIL:{email}"\n    }}\n  }}\n}}\n')
                    temp_sbt_file.write(f'Seqdesc ::= user {{\n  type str "Submission",\n  data {{\n    {{\n')
                    temp_sbt_file.write(f'      label str "AdditionalComment",\n      data str "Submission Title:{reference_title}"\n    }}\n  }}\n}}\n')
                    
               ###file 3: the csv file containing the metadata
                strain = temp_strain
                collection_country = collected_data.get('collection_country')
                collection_date = collected_data.get('collection_date')
                coverage = collected_data.get('coverage')

                with tempfile.NamedTemporaryFile(mode = 'w', delete=False) as temp_csv_file:
                    temp_csv_file_path = temp_csv_file.name
                    temp_csv_file.write(f'strain,collection-date,country,coverage\n')
                    temp_csv_file.write(f'{strain},{collection_date},{collection_country},{coverage}')


                ###now i should have the three files
                ref = 'NC003310.1'

                if os.path.exists(temp_csv_file_path) and os.path.exists(temp_sbt_file_path):
                    script_dir = '/var/www/django_app/external_software/vapid/VAPiD-master/'
                    script_path = os.path.join(script_dir, 'vapid3.py')

                    try:
                        #start the process
                        process = subprocess.Popen(
                            [
                                'python3',
                                script_path,
                                temp_seq_file_path,
                                temp_sbt_file_path,
                                '--metadata_loc', temp_csv_file_path,
                                '--r', ref
                            ],
                            cwd=script_dir, 
                            stdin=subprocess.PIPE, 
                            stdout=subprocess.PIPE,  
                            stderr=subprocess.PIPE, 
                            text=True 
                        )

                        # Define the input that the script is expecting
                        script_input = "input1\ninput2\n"

                        # Send input to the script and read the output
                        stdout, stderr = process.communicate(input=script_input)

                        ###script output file
                        request.session['stdout'] = stdout

                        ###script error file
                        request.session['stderr'] = stderr


                        # Check if the process was successful
                        if process.returncode == 0:
                            created_dir = os.path.join(script_dir, strain)

                            if os.path.exists(created_dir):
                                ###remove temp files
                                os.remove(temp_csv_file_path)
                                os.remove(temp_seq_file_path)
                                os.remove(temp_sbt_file_path)

                                ###save the generated files
                                ###tbl
                                output_tbl = []
                                with open(created_dir+'/'+strain+'.tbl', 'r') as f:
                                    for line in f:
                                        output_tbl.append(line)
                                    request.session['output_tbl'] = output_tbl
                                
                                output_gbf = []
                                with open(created_dir+'/'+strain+'.gbf', 'r') as f:
                                    for line in f:
                                        output_gbf.append(line)
                                    request.session['output_gbf'] = output_gbf

                                output_ali = []
                                with open(created_dir+'/'+strain+'.ali', 'r') as f:
                                    for line in f:
                                        output_ali.append(line)
                                    request.session['output_ali'] = output_ali


                                return render(request, 'my_app/annotation_results.html', 
                                        context={'strain':strain,'ref':ref})



                    except subprocess.CalledProcessError as e:
                        # Print error details
                        print(f"An error has occurred: {e}")
                        print("Script output:\n", e.stdout)
                        print("Script errors:\n", e.stderr)

                    



    
    return render(request, 'my_app/annotation.html', context = {'form':form})