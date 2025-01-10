import requests
import json
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CityForm
from .models import WeatherInfo
from django.conf import settings
from datetime import datetime
from django.http import JsonResponse


OPENWEATHER_API_KEY = '6cf024b69a9b8ce23ffeb16a72939a48'
ICON_URL = 'https://openweathermap.org/img/wn/' # <icon>@2x.png

def get_weather_data(city_name, units="metric"):
    """Функция для получения данных о погоде с OpenWeatherMap API."""
    api_key = OPENWEATHER_API_KEY
    base_url = "https://api.openweathermap.org/data/2.5/forecast" # forecast для получения прогноза на несколько дней
    url = f"{base_url}?q={city_name}&appid={api_key}&units={units}&lang=ru"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None

def parse_weather_data(data):
    """Извлечение нужных данных из ответа API."""
    if not data or data['cod'] != "200":
        return None

    city_name = data['city']['name']

    current_weather = data['list'][0]
    
    current_temp = current_weather['main']['temp']
    current_humidity = current_weather['main']['humidity']
    current_pressure = current_weather['main']['pressure']
    current_wind_speed = current_weather['wind']['speed']
    current_clouds = current_weather['clouds']['all']
    current_description = current_weather['weather'][0]['description'] # Дополнительное (подробное) описание погоды
    current_main = current_weather['weather'][0]['main'] # Основное описание погоды
    current_icon = current_weather['weather'][0]['icon'] # Иконка символа погоды
    current_weather_time = current_weather['dt_txt']
    forecast_list = data['list'] # список прогнозов на несколько дней
    
    return {
        'city_name': city_name,
        'current_temp': current_temp,
        'current_humidity': current_humidity,
        'current_pressure': current_pressure,
        'current_wind_speed': current_wind_speed,
        'current_clouds': current_clouds,
        'current_description': current_description,
        'current_main': current_main,
        'forecast_list': forecast_list,
        'current_icon': current_icon,
        'current_weather_time': current_weather_time,
    }

def weather_view(request):
    """
    View для отображения погоды и истории.
    Обрабатывает форму ввода города, делает запрос к API и отображает результаты.
    """
    history = WeatherInfo.objects.order_by('-timestamp')[:5]
    
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['city']
            if 'my_checkbox' in request.POST:
                  checkbox_checked = True
            else:
                 checkbox_checked = False
            
            if checkbox_checked:
                weather_data = get_weather_data(city_name, "imperial")
            else:
                weather_data = get_weather_data(city_name)
            
            parsed_data = parse_weather_data(weather_data)
            
            temps_list, days_list = get_forecast_chart_data(parsed_data['forecast_list'])

            if parsed_data:
               # Сохранение данных в БД
                weather_info = WeatherInfo.objects.create(
                    city_name = form.cleaned_data['city'],
                    temperature = parsed_data['current_temp'],
                    humidity = parsed_data['current_humidity'],
                    pressure = parsed_data['current_pressure'],
                    wind_speed = parsed_data['current_wind_speed'],
                    cloudiness = parsed_data['current_clouds'],
                    main = parsed_data['current_main'],
                    description = parsed_data['current_description'],
                    icon = parsed_data['current_icon'],
                    weather_time = parsed_data['current_weather_time'],
                    imperial = checkbox_checked, # Bool. Включает градусы F и мили/ч
                    timestamp = datetime.now(),
                )
                weather_info.save()
                
                context = {
                    'form': form,
                    'city': city_name,
                    'current_temp': parsed_data['current_temp'],
                    'current_humidity': parsed_data['current_humidity'],
                    'current_pressure': parsed_data['current_pressure'],
                    'current_wind_speed': parsed_data['current_wind_speed'],
                    'current_clouds': parsed_data['current_clouds'],
                    'current_icon': f'{ICON_URL}{parsed_data['current_icon']}@4x.png',
                    'current_description': parsed_data['current_description'],
                    'days_list_json': json.dumps(days_list),
                    'temps_list_json': json.dumps(temps_list),
                    'history': history,
                    'checkbox_checked': checkbox_checked,
                 }
                return render(request, 'weather/weather.html', context)
            else:
                 return render(request, 'weather/weather.html', {'form': form, 'error': 'Не удалось получить данные о погоде. Пожалуйста, проверьте название города и попробуйте еще раз.', 'history': history})

    else:
        form = CityForm()

    return render(request, 'weather/weather.html', {'form': form, 'history': history})


def get_forecast_chart_data(forecast_list):
    """Возвращает два списка  с температурами и датами из проргноза"""
    today = forecast_list[0]['dt_txt'][:10]
    temps = []
    days = []
    for weather in forecast_list:
        if weather['dt_txt'][:10] != today:
            if weather['dt_txt'][11:] == '09:00:00':
                temps.append(weather['main']['temp'])
                days.append(weather['dt_txt'][:10])
    return temps, days