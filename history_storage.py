import json

history_list=[]

def save_history(data_set):
    data={
        "date":data_set[0],
        "time":data_set[1],
        "searched location":data_set[2],
        "fetched location":data_set[3],
        "temp in celsius":data_set[4],
        "temp in fahr":data_set[5],
        "weather description":data_set[6]
        }
    try:
        with open('weather_history.json', 'r') as file:
            history=json.load(file)
    except (FileNotFoundError,json.JSONDecodeError):
        history=[]

    history.append(data)
    with open('weather_history.json', 'w') as file:
        json.dump(history, file, indent=4)


def read_history(city_name):
    try:
        with open('weather_history.json', 'r') as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        message="Nothing in history."
        return message
    
    for data in history:
        if data["searched location"].lower() == city_name.lower():
            return data

    return None

def read_full_history():
    try:
        with open('weather_history.json', 'r+') as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        message="Nothing in history."
        return message

    return history


def delete_city_history(city_name):
    with open('weather_history.json', 'r') as file:
        history=json.load(file)
    new_data=[]
    for data in history:
        if data["searched location"].lower() != city_name.lower():
            new_data.append(data)
    
    with open('weather_history.json', 'w') as file:
        json.dump(new_data, file, indent=4)
    
def delete_all_history():
    with open('weather_history.json', 'w') as file:
        json.dump([], file)

