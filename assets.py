from state import state

def kinda_weather():
    image=""
    kind_of_weather=str(state.weathertoday['kind']) 
    if kind_of_weather == 'Clear':
        image="https://i.postimg.cc/J0xKJRwL/clear.png" 

    elif kind_of_weather == 'Sunny':
        image="https://i.postimg.cc/PfyMSfcG/sunny.png" 

    elif kind_of_weather == 'Partly Cloudy':
        image="https://i.postimg.cc/6qWfBF81/partly-cloudy.png" 

    elif kind_of_weather == 'Cloudy':
        image="https://i.postimg.cc/9FfYK55D/cloudy.png" 

    elif kind_of_weather == 'Very Cloudy':
        image="https://i.postimg.cc/qq1XqQnB/very-cloudy.png" 

    elif kind_of_weather == 'Fog':
        image="https://i.postimg.cc/63LhJBpv/fog.png" 

    elif kind_of_weather == 'Light Showers':
        image="https://i.postimg.cc/PJT2PPRy/light-showers.png" 

    elif kind_of_weather == 'Light Sleet Showers':
        image="https://i.postimg.cc/nhCTj80y/sleet-or-sleet-showers.png" 

    elif kind_of_weather == 'Light Sleet':
        image="https://i.postimg.cc/nhCTj80y/sleet-or-sleet-showers.png" 

    elif kind_of_weather == 'Thundery Showers':
        image="https://i.postimg.cc/pVJs3Jm6/thundery-showers.png" 

    elif kind_of_weather == 'Light Snow':
        image="https://i.postimg.cc/B6GCVj43/light-snow.png" 

    elif kind_of_weather == 'Heavy Snow':
        image="https://i.postimg.cc/TPb90V8Q/snow.png" 

    elif kind_of_weather == 'Light Rain':
        image="https://i.postimg.cc/bNYmPSbN/rain.png" 

    elif kind_of_weather == 'Heavy Showers':
        image="https://i.postimg.cc/fTHBRWj7/heavy-showers.png" 

    elif kind_of_weather == 'Heavy Rain':
        image="https://i.postimg.cc/YCZRQXPh/heavy-rain.png" 

    elif kind_of_weather == 'Light Snow Showers':
        image="https://i.postimg.cc/B6GCVj43/light-snow.png" 

    elif kind_of_weather == 'Heavy Snow Showers':
        image="https://i.postimg.cc/B6GCVj43/light-snow.png" 

    elif kind_of_weather == 'Thundery Heavy Rain':
        image="https://i.postimg.cc/pVJs3Jm6/thundery-showers.png" 

    elif kind_of_weather == 'Thundery Snow Showers':
        image="https://i.postimg.cc/ydFL1FvW/thundery-rain.png" 

    return image 
