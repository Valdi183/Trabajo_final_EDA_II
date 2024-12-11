"""
Este script, contiene las llamadas a la api para la creación de las tablas en la base de datos (pokemon.db) con los distintos datos de los pokemons.
Por un lado creo unas tablas simples que contienen los distintos pokemons, habilidades, movimientos, tipos y estadísticas, y su id asignado.
El resto de tablas relacionan a los pokemons con sus tipos, estadísticas, movimientos y habilidades, de esta forma puedo implementar un sistema
que sea capaz de encontar cual es el mejor counter contra un equipo random, generado con el script: counter_equipo_random.py
"""
import requests
import sqlite3

# Función para obtener todos los Pokémon desde la API
def obtener_pokemons():
    url = "https://pokeapi.co/api/v2/pokemon?limit=100&offset=0"
    pokemons = []
    while url:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            pokemons.extend(datos.get('results', []))  # Agrega los resultados a la lista
            url = datos.get('next')  # Obtiene la siguiente página, si existe
        else:
            print(f"Error al obtener datos: {respuesta.status_code}")
            break
    return pokemons

# Función para obtener los detalles de un Pokémon desde su URL
def obtener_detalles_pokemon(url):
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        print(f"Error al obtener detalles del Pokémon: {respuesta.status_code}")
        return None

# Conexión a la base de datos SQLite
conexion = sqlite3.connect("pokemon.db")
cursor = conexion.cursor()

# Creación de las distintas tablas para la base de datos tablas

# Tabla para los Pokémon (id, nombre y url)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        url TEXT NOT NULL
    )
''')

#Tabla para los tipos (id y nombre del tipo)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

# Tabla que relaciona pokemons con sus posibles movimientos (id pokemon e id tipo)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon_types (
        pokemon_id INTEGER,
        type_id INTEGER,
        PRIMARY KEY (pokemon_id, type_id),
        FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
        FOREIGN KEY (type_id) REFERENCES types (id)
    )
''')

# Tabla para las estadísticas (id y nombre de la estadística)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

# Tabla que relaciona pokemons con sus estadísticas (id pokemon e id estadística)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon_stats (
        pokemon_id INTEGER,
        stat_id INTEGER,
        value INTEGER NOT NULL,
        PRIMARY KEY (pokemon_id, stat_id),
        FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
        FOREIGN KEY (stat_id) REFERENCES stats (id)
    )
''')

# Tabla para las habilidades (id y nombre de la habilidad)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS abilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

# Tabla que relaciona pokemons con sus habilidades (id pokemon e id habilidad) y si es escondida (0 si no lo es (false), 1 si lo es (true))
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon_abilities (
        pokemon_id INTEGER,
        ability_id INTEGER,
        is_hidden BOOLEAN NOT NULL,
        PRIMARY KEY (pokemon_id, ability_id),
        FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
        FOREIGN KEY (ability_id) REFERENCES abilities (id)
    )

# Tabla para los movimientos (id y nombre del movimiento)
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')


# Tabla que relaciona pokemons con sus movimientos (id pokemon, id movimiento, método de aprendizaje, y nivel a partir del cual se puede aprender)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pokemon_moves (
        pokemon_id INTEGER,
        move_id INTEGER,
        method TEXT,
        level INTEGER,
        PRIMARY KEY (pokemon_id, move_id, method, level),
        FOREIGN KEY (pokemon_id) REFERENCES pokemon (id),
        FOREIGN KEY (move_id) REFERENCES moves (id)
    )
''')


# Obtener los datos de la API
pokemons = obtener_pokemons()

# Insertar Pokémon en la base de datos
if pokemons:
    print(f"Se obtuvieron {len(pokemons)} Pokémon.")
    for pokemon in pokemons:
        try:
            # Extraer el ID y nombre del Pokémon
            pokemon_id = int(pokemon['url'].split('/')[-2])  # Extrae el número antes de la última '/'
            pokemon_name = pokemon['name']
            pokemon_url = pokemon['url']

            # Insertar en la tabla pokemon
            cursor.execute('''
                INSERT OR IGNORE INTO pokemon (id, name, url)
                VALUES (?, ?, ?)
            ''', (pokemon_id, pokemon_name, pokemon_url))

            # Obtener los detalles del Pokémon
            detalles = obtener_detalles_pokemon(pokemon_url)
            if detalles:
                # Obtener los tipos del Pokémon
                tipos = detalles.get('types', [])
                for tipo in tipos:
                    tipo_name = tipo['type']['name']
                    
                    # Insertar el tipo en la tabla types si no existe
                    cursor.execute('''
                        INSERT OR IGNORE INTO types (name)
                        VALUES (?)
                    ''', (tipo_name,))

                    # Obtener el ID del tipo
                    cursor.execute('''
                        SELECT id FROM types WHERE name = ?
                    ''', (tipo_name,))
                    tipo_id = cursor.fetchone()[0]

                    # Insertar la relación en pokemon_types
                    cursor.execute('''
                        INSERT OR IGNORE INTO pokemon_types (pokemon_id, type_id)
                        VALUES (?, ?)
                    ''', (pokemon_id, tipo_id))
                     # Obtener estadísticas del Pokémon
                estadisticas = detalles.get('stats', [])
                for estadistica in estadisticas:
                    stat_name = estadistica['stat']['name']
                    stat_value = estadistica['base_stat']

                    # Insertar la estadística en la tabla stats si no existe
                    cursor.execute('''
                        INSERT OR IGNORE INTO stats (name)
                        VALUES (?)
                    ''', (stat_name,))

                    # Obtener el ID de la estadística
                    cursor.execute('''
                        SELECT id FROM stats WHERE name = ?
                    ''', (stat_name,))
                    stat_id = cursor.fetchone()[0]

                    # Insertar la relación en pokemon_stats
                    cursor.execute('''
                        INSERT OR IGNORE INTO pokemon_stats (pokemon_id, stat_id, value)
                        VALUES (?, ?, ?)
                    ''', (pokemon_id, stat_id, stat_value))

                # Obtener habilidades del Pokémon
                habilidades = detalles.get('abilities', [])
                for habilidad in habilidades:
                    ability_name = habilidad['ability']['name']
                    is_hidden = habilidad['is_hidden']

                    # Insertar la habilidad en la tabla abilities si no existe
                    cursor.execute('''
                        INSERT OR IGNORE INTO abilities (name)
                        VALUES (?)
                    ''', (ability_name,))

                    # Obtener el ID de la habilidad
                    cursor.execute('''
                        SELECT id FROM abilities WHERE name = ?
                    ''', (ability_name,))
                    ability_id = cursor.fetchone()[0]

                    # Insertar la relación en pokemon_abilities
                    cursor.execute('''
                        INSERT OR IGNORE INTO pokemon_abilities (pokemon_id, ability_id, is_hidden)
                        VALUES (?, ?, ?)
                    ''', (pokemon_id, ability_id, is_hidden))
                     # Insertar movimientos del Pokémon
                movimientos = detalles.get('moves', [])
                for movimiento in movimientos:
                    move_name = movimiento['move']['name']
                    method = movimiento['version_group_details'][0]['move_learn_method']['name']
                    level = movimiento['version_group_details'][0].get('level_learned_at', None)
                    cursor.execute('INSERT OR IGNORE INTO moves (name) VALUES (?)', (move_name,))
                    cursor.execute('SELECT id FROM moves WHERE name = ?', (move_name,))
                    move_id = cursor.fetchone()[0]
                    cursor.execute(
                        '''INSERT OR IGNORE INTO pokemon_moves (pokemon_id, move_id, method, level) 
                        VALUES (?, ?, ?, ?)''' 
                        ,(pokemon_id, move_id, method, level))

        # Control de error
        except Exception as e:
            print(f"Error procesando Pokémon: {pokemon} - {e}")
    conexion.commit()
    print("Los datos se han insertado correctamente.")
else:
    print("No se obtuvieron datos de Pokémon.")

# Cerrar la conexión
conexion.close()
