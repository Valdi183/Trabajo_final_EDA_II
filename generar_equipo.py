import sqlite3
import random

# Conexión a la base de datos
conexion = sqlite3.connect("pokemon.db")
cursor = conexion.cursor()

# Función para obtener un Pokémon aleatorio con sus características
def generar_equipo_random():
    # Seleccionar 6 Pokémon aleatorios
    cursor.execute('SELECT id, name FROM pokemon ORDER BY RANDOM() LIMIT 6')
    equipo = cursor.fetchall()

    equipo_completo = []
    for pokemon_id, pokemon_name in equipo:
        # Obtener tipos
        cursor.execute('''
            SELECT t.name 
            FROM pokemon_types pt
            JOIN types t ON pt.type_id = t.id
            WHERE pt.pokemon_id = ?
        ''', (pokemon_id,))
        tipos = [tipo[0] for tipo in cursor.fetchall()]

        # Obtener habilidades y seleccionar una al azar
        cursor.execute('''
            SELECT a.name 
            FROM pokemon_abilities pa
            JOIN abilities a ON pa.ability_id = a.id
            WHERE pa.pokemon_id = ?
        ''', (pokemon_id,))
        habilidades = [habilidad[0] for habilidad in cursor.fetchall()]
        habilidad_random = random.choice(habilidades) if habilidades else None

        # Obtener movimientos y seleccionar 4 al azar
        cursor.execute('''
            SELECT m.name 
            FROM pokemon_moves pm
            JOIN moves m ON pm.move_id = m.id
            WHERE pm.pokemon_id = ?
        ''', (pokemon_id,))
        movimientos = [movimiento[0] for movimiento in cursor.fetchall()]
        movimientos_random = random.sample(movimientos, min(4, len(movimientos)))

        # Obtener estadísticas
        cursor.execute('''
            SELECT s.name, ps.value
            FROM pokemon_stats ps
            JOIN stats s ON ps.stat_id = s.id
            WHERE ps.pokemon_id = ?
        ''', (pokemon_id,))
        estadisticas = {stat_name: value for stat_name, value in cursor.fetchall()}

        # Agregar al equipo
        pokemon = {
            'id': pokemon_id,
            'name': pokemon_name,
            'types': tipos,
            'ability': habilidad_random,
            'moves': movimientos_random,
            'stats': estadisticas
        }
        equipo_completo.append(pokemon)

    return equipo_completo

# Generar un equipo aleatorio
equipo = generar_equipo_random()

# Mostrar el equipo generado
for pokemon in equipo:
    print(f"Pokémon: {pokemon['name']}")
    print(f"  Tipos: {', '.join(pokemon['types'])}")
    print(f"  Habilidad: {pokemon['ability']}")
    print(f"  Movimientos: {', '.join(pokemon['moves'])}")
    print("  Estadísticas:")
    for stat, value in pokemon['stats'].items():
        print(f"    {stat}: {value}")
    print()

# Cerrar la conexión
conexion.close()
