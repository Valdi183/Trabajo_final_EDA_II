"""
Este script, crea un equipo fuerte contra el equipo generado de manera aleatoria.
De esta forma, este script encuentra en función de los tipos, habilidades y estadísticas 
del equipo random, un equipo de pokemons con muy buenas fortalezas contra el equipo generado
"""
import sqlite3
import random

# Conexión a la base de datos
conexion = sqlite3.connect("pokemon.db")
cursor = conexion.cursor()

# Tabla de efectividades entre tipos
efec = {
    'normal': {'fuerte': [], 'debil': ['rock', 'steel'], 'inmune': ['ghost']},
    'fire': {'fuerte': ['grass', 'ice', 'bug', 'steel'], 'debil': ['fire', 'water', 'rock', 'dragon'], 'inmune': []},
    'water': {'fuerte': ['fire', 'ground', 'rock'], 'debil': ['water', 'grass', 'dragon'], 'inmune': []},
    'electric': {'fuerte': ['water', 'flying'], 'debil': ['electric', 'grass', 'dragon'], 'inmune': ['ground']},
    'grass': {'fuerte': ['water', 'ground', 'rock'], 'debil': ['fire', 'grass', 'poison', 'flying', 'bug', 'dragon', 'steel'], 'inmune': []},
    'ice': {'fuerte': ['grass', 'ground', 'flying', 'dragon'], 'debil': ['fire', 'water', 'ice', 'steel'], 'inmune': []},
    'fighting': {'fuerte': ['normal', 'ice', 'rock', 'dark', 'steel'], 'debil': ['poison', 'flying', 'psychic', 'bug', 'fairy'], 'inmune': ['ghost']},
    'poison': {'fuerte': ['grass', 'fairy'], 'debil': ['poison', 'ground', 'rock', 'ghost'], 'inmune': ['steel']},
    'ground': {'fuerte': ['fire', 'electric', 'poison', 'rock', 'steel'], 'debil': ['grass', 'bug'], 'inmune': ['flying']},
    'flying': {'fuerte': ['grass', 'fighting', 'bug'], 'debil': ['electric', 'rock', 'steel'], 'inmune': []},
    'psychic': {'fuerte': ['fighting', 'poison'], 'debil': ['psychic', 'steel'], 'inmune': ['dark']},
    'bug': {'fuerte': ['grass', 'psychic', 'dark'], 'debil': ['fire', 'fighting', 'poison', 'flying', 'ghost', 'steel', 'fairy'], 'inmune': []},
    'rock': {'fuerte': ['fire', 'ice', 'flying', 'bug'], 'debil': ['fighting', 'ground', 'steel'], 'inmune': []},
    'ghost': {'fuerte': ['ghost', 'psychic'], 'debil': ['dark'], 'inmune': ['normal']},
    'dragon': {'fuerte': ['dragon'], 'debil': ['steel'], 'inmune': ['fairy']},
    'dark': {'fuerte': ['psychic', 'ghost'], 'debil': ['fighting', 'dark', 'fairy'], 'inmune': []},
    'steel': {'fuerte': ['ice', 'rock', 'fairy'], 'debil': ['fire', 'water', 'electric', 'steel'], 'inmune': ['poison']},
    'fairy': {'fuerte': ['fighting', 'dragon', 'dark'], 'debil': ['fire', 'poison', 'steel'], 'inmune': ['dragon']}
}

# Función para obtener los tipos fuertes contra un conjunto de tipos
def obtener_tipos_fuertes(tipos_rivales):
    """
    Obtiene una lista de tipos que son fuertes contra los tipos del equipo rival.
    """
    tipos_favorables = set()
    for tipo_rival in tipos_rivales:
        if tipo_rival in efec:
            tipos_favorables.update(efec[tipo_rival]['fuerte'])

    # Filtrar los tipos que ya están representados en el equipo rival
    tipos_favorables.difference_update(tipos_rivales)
    
    return list(tipos_favorables)

# Función para obtener la información completa de un Pokémon
def obtener_informacion_pokemon(pokemon_id):
    cursor.execute(''' 
        SELECT t.name
        FROM pokemon_types pt
        JOIN types t ON pt.type_id = t.id
        WHERE pt.pokemon_id = ?
    ''', (pokemon_id,))
    tipos = [tipo[0] for tipo in cursor.fetchall()]

    cursor.execute(''' 
        SELECT a.name
        FROM pokemon_abilities pa
        JOIN abilities a ON pa.ability_id = a.id
        WHERE pa.pokemon_id = ?
    ''', (pokemon_id,))
    habilidades = [habilidad[0] for habilidad in cursor.fetchall()]
    habilidad_random = random.choice(habilidades) if habilidades else None

    cursor.execute(''' 
        SELECT m.name
        FROM pokemon_moves pm
        JOIN moves m ON pm.move_id = m.id
        WHERE pm.pokemon_id = ?
    ''', (pokemon_id,))
    movimientos = [movimiento[0] for movimiento in cursor.fetchall()]
    movimientos_random = random.sample(movimientos, min(4, len(movimientos)))

    cursor.execute(''' 
        SELECT s.name, ps.value
        FROM pokemon_stats ps
        JOIN stats s ON ps.stat_id = s.id
        WHERE ps.pokemon_id = ?
    ''', (pokemon_id,))
    estadisticas = {stat_name: value for stat_name, value in cursor.fetchall()}

    return {
        'types': tipos,
        'ability': habilidad_random,
        'moves': movimientos_random,
        'stats': estadisticas
    }

# Función para obtener un equipo aleatorio
def generar_equipo_random():
    cursor.execute('''
        SELECT p.id, p.name
        FROM pokemon p
        ORDER BY RANDOM()
        LIMIT 6
    ''')
    pokemons_seleccionados = cursor.fetchall()

    equipo = []
    for pokemon_id, pokemon_name in pokemons_seleccionados:
        info_pokemon = obtener_informacion_pokemon(pokemon_id)
        pokemon = {
            'id': pokemon_id,
            'name': pokemon_name,
            'types': info_pokemon['types'],
            'ability': info_pokemon['ability'],
            'moves': info_pokemon['moves'],
            'stats': info_pokemon['stats']
        }
        equipo.append(pokemon)

    return equipo

# Función para encontrar un equipo fuerte
def encontrar_equipo_fuerte(equipo_rival):
    """
    Genera un equipo que contrarreste eficientemente los tipos del equipo rival.
    """
    tipos_rivales = []
    for pokemon in equipo_rival:
        tipos_rivales.extend(pokemon['types'])

    tipos_favorables = obtener_tipos_fuertes(tipos_rivales)

    equipo_fuerte = []
    
    cursor.execute('''
        SELECT p.id, p.name
        FROM pokemon p
        JOIN pokemon_types pt ON p.id = pt.pokemon_id
        JOIN types t ON pt.type_id = t.id
        WHERE t.name IN ({})
        GROUP BY p.id
        ORDER BY RANDOM()
        LIMIT 6
    '''.format(', '.join('?' for _ in tipos_favorables)), tipos_favorables)

    pokemons_seleccionados = cursor.fetchall()

    for pokemon_id, pokemon_name in pokemons_seleccionados:
        info_pokemon = obtener_informacion_pokemon(pokemon_id)
        pokemon = {
            'id': pokemon_id,
            'name': pokemon_name,
            'types': info_pokemon['types'],
            'ability': info_pokemon['ability'],
            'moves': info_pokemon['moves'],
            'stats': info_pokemon['stats']
        }
        equipo_fuerte.append(pokemon)

    return equipo_fuerte

# Generar equipo rival
print("Generando equipo rival...")
equipo_rival = generar_equipo_random()

# Encontrar el mejor equipo contra el rival
print("Buscando mejor equipo contra el rival...")
equipo_fuerte = encontrar_equipo_fuerte(equipo_rival)


print("\nEquipo Rival:")
for pokemon in equipo_rival:
    print(f"{pokemon['name']} - Tipos: {', '.join(pokemon['types'])}")

print("\nMejor Equipo:")
for pokemon in equipo_fuerte:
    print(f"{pokemon['name']} - Tipos: {', '.join(pokemon['types'])}")
    print(f"  Habilidad: {pokemon['ability']}")
    print(f"  Movimientos: {', '.join(pokemon['moves'])}")
    print("  Estadísticas:")
    for stat, value in pokemon['stats'].items():
        print(f"    {stat}: {value}")
    print()

# Cerrar la conexión
conexion.close()
