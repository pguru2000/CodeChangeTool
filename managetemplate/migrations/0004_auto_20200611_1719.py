# Generated by Django 2.2.4 on 2020-06-11 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('managetemplate', '0003_auto_20200611_1715'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='condition',
            name='project_name',
        ),
        migrations.RemoveField(
            model_name='conversionrule',
            name='project_name',
        ),
    ]
