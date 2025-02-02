# Generated by Django 2.2.7 on 2022-10-17 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variable_name', models.CharField(max_length=100)),
                ('condition_content', models.CharField(max_length=100)),
                ('text_for_fulfill', models.CharField(max_length=1000)),
                ('text_for_not_fulfill', models.CharField(max_length=1000)),
                ('project_name', models.CharField(max_length=100)),
            ],
        ),
    ]
