# Generated by Django 2.2.4 on 2020-11-02 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewPermutationGeneral',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100)),
                ('update_status', models.BooleanField()),
                ('apply_to_all_para', models.BooleanField()),
                ('permutation_mode', models.CharField(max_length=100)),
                ('rand_from', models.IntegerField()),
                ('rand_to', models.IntegerField()),
                ('min_words', models.IntegerField()),
                ('max_words', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='NewPermutationParagraphs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100)),
                ('section_name', models.CharField(max_length=100)),
                ('section_visibility', models.BooleanField()),
                ('type', models.CharField(max_length=100)),
                ('number_of_elements', models.IntegerField()),
                ('permutation_mode', models.CharField(max_length=100)),
                ('para_type', models.CharField(max_length=100)),
                ('rand_from', models.IntegerField()),
                ('rand_to', models.IntegerField()),
                ('content', models.TextField()),
                ('min_words', models.IntegerField()),
                ('max_words', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='NewPermutationProjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
