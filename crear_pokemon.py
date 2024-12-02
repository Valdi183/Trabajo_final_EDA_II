import requests

def obtener_pokemon(nombre):
    url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return datos
    else:
        return False

def obtener_pokemons():
    url = f"https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0"
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return datos
    else:
        return False
    
pokemons = obtener_pokemons()["results"]

for pokemon in pokemons:
    datos_pokemon = obtener_pokemon(pokemon["name"]) 
    print(datos_pokemon["abilities"])
    

