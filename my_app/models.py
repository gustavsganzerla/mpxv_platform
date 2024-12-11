from django.db import models

# Create your models here.
class Genome(models.Model):
    id = models.BigAutoField(primary_key=True)
    genome_id = models.CharField(max_length=50)
    clade = models.CharField(max_length=10)
    host = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    submission_date = models.DateField()
    length = models.IntegerField()
    sequence = models.TextField(max_length=500000)

    def __str__(self):
        return f"{self.genome_id}, {self.clade}, {self.host}, {self.country}, {self.region}, {self.submission_date}, {self.length}"
    
class Reference(models.Model):
    id = models.BigAutoField(primary_key=True)
    accession = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id}, {self.accession}"