# Generated by Django 2.2.4 on 2020-06-11 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managetemplate', '0004_auto_20200611_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='condition',
            name='project_name',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='conversionrule',
            name='project_name',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
    ]
