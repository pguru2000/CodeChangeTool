from django.db import models

# Create your models here.
#from django.contrib.postgres.fields import jsonb, JSONField
from django.db import models

# Create your models here.

# For New Permutation
class NewPermutationProjects(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    name = models.CharField(max_length=100)

class NewPermutationGeneral(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    project_name = models.CharField(max_length=100)
    update_status = models.BooleanField()
    permute_sections = models.BooleanField()
    not_permute_conditional_sections = models.BooleanField()
    permutation_mode_section = models.CharField(max_length=100)
    sections_rand_from = models.IntegerField()
    sections_rand_to = models.IntegerField()
    min_words = models.IntegerField()
    max_words = models.IntegerField()
    normal_sections_txt = models.TextField()
    count_normalsections = models.IntegerField()

class NewPermutationParagraphs(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    project_name = models.CharField(max_length=100)
    section_name = models.CharField(max_length=100)
    section_visibility = models.BooleanField()
    type = models.CharField(max_length=100) #sectuib ir paragraph
    number_of_elements = models.IntegerField()
    permutation_mode = models.CharField(max_length=100)
    para_type = models.CharField(max_length=100)
    rand_from = models.IntegerField()
    rand_to = models.IntegerField()
    content = models.TextField()
    min_words = models.IntegerField()
    max_words = models.IntegerField()