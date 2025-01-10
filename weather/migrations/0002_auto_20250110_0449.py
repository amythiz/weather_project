# Generated by Django 3.2.16 on 2025-01-10 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weatherrequest',
            name='city',
        ),
        migrations.RemoveField(
            model_name='weatherinfo',
            name='city',
        ),
        migrations.AddField(
            model_name='weatherinfo',
            name='city_name',
            field=models.CharField(default='0', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='City',
        ),
        migrations.DeleteModel(
            name='WeatherRequest',
        ),
    ]