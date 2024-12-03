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
