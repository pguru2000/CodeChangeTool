# Generated by Django 2.2.7 on 2020-10-14 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managetemplate', '0007_permutationgeneral_permutationparagraphs_permutationprojects'),
    ]

    operations = [
        migrations.AddField(
            model_name='permutationparagraphs',
            name='content',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
