#from django.contrib.postgres.fields import jsonb, JSONField
from django.db import models

# Create your models here.

#class casetemplate(models.Model):
#    name = models.CharField(max_length=200)
#    path = models.CharField(max_length=200)
    #data = JSONField()

#    def __str__(self):
#        return self.name

class ConversionRule(models.Model):
    #no = models.IntegerField()

    no = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    srcpattern = models.CharField(max_length=100)
    destpattern = models.CharField(max_length=100)
    enabled = models.BooleanField()
    case_sensitive = models.BooleanField()
    exceptions = models.CharField(max_length=100)
    priority = models.IntegerField()
    project_name = models.CharField(max_length=100)


class Condition(models.Model):
    #no = models.IntegerField()

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    condition_id = models.CharField(max_length=100)
    condition_content = models.CharField(max_length=100)
    project_name = models.CharField(max_length=100)


class VariableFields(models.Model):
    name = models.CharField(max_length=100)


class Projects(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    name = models.CharField(max_length=100)

class VariableCondition(models.Model):
    #no = models.IntegerField()

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    variable_name = models.CharField(max_length=100)
    condition_content = models.CharField(max_length=100)
    use_excel_for_fulfill = models.BooleanField()
    text_for_fulfill = models.CharField(max_length=1000)
    use_excel_for_not_fulfill = models.BooleanField()
    text_for_not_fulfill = models.CharField(max_length=1000)
    project_name = models.CharField(max_length=100)


# For Permutation
class PermutationProjects(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    name = models.CharField(max_length=100)

class PermutationGeneral(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    project_name = models.CharField(max_length=100)
    update_status = models.BooleanField()
    apply_to_all_para = models.BooleanField()
    permutation_mode = models.CharField(max_length=100)
    rand_from = models.IntegerField()
    rand_to = models.IntegerField()
    min_words = models.IntegerField()
    max_words = models.IntegerField()

class PermutationParagraphs(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    project_name = models.CharField(max_length=100)
    section_name = models.CharField(max_length=100)
    section_visibility = models.BooleanField()
    type = models.CharField(max_length=100)
    number_of_elements = models.IntegerField()
    permutation_mode = models.CharField(max_length=100)
    rand_from = models.IntegerField()
    rand_to = models.IntegerField()
    content = models.TextField()
    min_words = models.IntegerField()
    max_words = models.IntegerField()