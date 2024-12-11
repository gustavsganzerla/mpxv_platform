from django import forms


class GenomeQueryForm(forms.Form):
    clade = forms.ChoiceField(
            label='Clade',
            choices = [('Clade 1', 'Clade 1'), ('Clade 2', 'Clade 2')],
            widget = forms.RadioSelect, required = False)
    host = forms.CharField(max_length=50, required = False)
    country = forms.CharField(max_length=50, required = False)
    genome_id = forms.CharField(max_length=50, required = False)
    region = forms.CharField(max_length=50, required = False)

    start_date = forms.DateField(
            widget=forms.TextInput(attrs={'type':'date'}),
            label='Start Date',
            required=False)
    end_date = forms.DateField(
            widget=forms.TextInput(attrs={'type':'date'}),
            label='End Date',
            required=False)


class annotationForm(forms.Form):
    uploaded_file = forms.FileField(
        label = 'Upload the .FASTA file with your genome', required=True)

    ###.sbt file
    first_name = forms.CharField(required=True, max_length=100)
    last_name = forms.CharField(required=True, max_length=100)
    email = forms.EmailField(required=True, max_length=100)
    organization = forms.CharField(required=True, max_length=100)
    department = forms.CharField(required=True, max_length=100)
    street = forms.CharField(required=True, max_length=100)
    city = forms.CharField(required=True, max_length=100)
    state = forms.CharField(required=True, max_length=100)
    postal_code = forms.CharField(required=True, max_length=100)
    country = forms.CharField(required=True, max_length=100)
    author_first_name = forms.CharField(required=True, max_length=100)
    author_last_name = forms.CharField(required=True, max_length=100)
    reference_title = forms.CharField(required=True, max_length=100)

    ###.csv file with metadata
    strain = forms.CharField(required=True, max_length=50)
    collection_country = forms.CharField(required=True, max_length=100)
    collection_date = forms.CharField(required=True)
    coverage = forms.CharField(required=True, max_length=50)


    ###reference
    reference = forms.CharField(required=True, max_length=200)