from django.db import models

# Create your models here.
class WeatherInfo(models.Model):
    city_name = models.CharField(max_length=100)
    temperature = models.FloatField()
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    wind_speed = models.FloatField()
    cloudiness = models.IntegerField()
    main = models.CharField(max_length=100) # Основное описание погоды
    description = models.CharField(max_length=100) # Дополнительное (подробное) описание погоды
    icon = models.CharField(max_length=100) # Иконка символа погоды 
    weather_time = models.DateTimeField()
    imperial = models.BooleanField() # Bool. Включает градусы F и мили/ч
    timestamp = models.DateTimeField()