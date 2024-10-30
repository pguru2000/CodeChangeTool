#from django.contrib.postgres.fields import jsonb, JSONField
from django.db import models

# Create your models here.

class ClusterCondition(models.Model):
    #no = models.IntegerField()

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    variable_name = models.CharField(max_length=100)
    condition_content = models.CharField(max_length=100)    
    text_for_fulfill = models.CharField(max_length=1000)    
    text_for_not_fulfill = models.CharField(max_length=1000)
    project_name = models.CharField(max_length=100)