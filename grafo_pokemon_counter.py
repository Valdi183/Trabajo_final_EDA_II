"""
Este script pregunte al usuario por un pokemon, y devuelve que pokemon sería el más fuerte contra el pokemon pedido por el usuario.
Para hacer esto, creo un grafo ponderado que conecta a todos los pokemons entre ellos. La ponderación de cada arista, va a depender 
de lo fuerte que es un pokemon (nodo) contra el pokemon (nodo) al que se dirije. Para decidir esta fuerza, va a ir en función de los tipos. 
Poniendo un ejemplo que involucre a solo dos pokemons: el grafo serán dos nodos (cada nodo es un pokemon) y tendrá dos aristas, una del nodo 1 al nodo 2,
y la otra del nodo 2 al nodo 1. la ponderación del nodo 1 al nodo 2, dependerá de lo fuerte que es el pokemon del nodo 1 contra el del nodo 2, y viceversa. 
Las posibles ponderaciones son las siguientes: 4 (el pokemon tiene un tipo fuerte contra los dos tipos del pokemon al que se dirije), 
2 (el pokemon tiene un tipo fuerte  contra uno de los tipos del pokemon al que se dirije), 1 (el pokemon no tiene ningún tipo fuerte contra el pokemon 
al que se dirije o tiene un tipo fuerte y un tipo débil (2 * 1/2), 1/2 (el pokemon tiene un tipo debil  y ningún tipo fuerte contra el pokemon al que se dirije), 
1/4 (el pokemon tiene dos tipos debiles contra el pokemon al que se dirije) y 0 (el pokemon tiene a menos un tipo "sin efecto" contra el pokemon al que se dirije).
"""
import sqlite3
import networkx as nx

# Conexión a la base de datos
conexion = sqlite3.connect("pokemon.db")
cursor = conexion.cursor()

# Efectividades entre tipos
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

# Función para calcular la efectividad contra tipos
def calcular_ponderacion(tipos_atacante, tipos_defensor):
    ponderacion = 1.0
    for tipo_atacante in tipos_atacante:
        for tipo_defensor in tipos_defensor:
            if tipo_defensor in efec[tipo_atacante]['fuerte']:
                ponderacion *= 2
            elif tipo_defensor in efec[tipo_atacante]['debil']:
                ponderacion *= 0.5
            elif tipo_defensor in efec[tipo_atacante]['inmune']:
                return 0
    return ponderacion

# Cargo datos en memoria para optimizar el tiempo a la hora de construir el grafo
def construir_grafo():
    G = nx.DiGraph()

    # Obtener Pokémon y sus tipos de una vez
    cursor.execute("""
        SELECT p.id, p.name, t.name
        FROM pokemon p
        JOIN pokemon_types pt ON p.id = pt.pokemon_id
        JOIN types t ON pt.type_id = t.id
    """)
    datos = cursor.fetchall()

    # Cachear tipos por Pokémon
    tipos_por_pokemon = {}
    for id_pokemon, nombre, tipo in datos:
        if nombre not in tipos_por_pokemon:
            tipos_por_pokemon[nombre] = []
        tipos_por_pokemon[nombre].append(tipo)

    # Construir el grafo
    nombres = list(tipos_por_pokemon.keys())
    for i, nombre1 in enumerate(nombres):
        tipos1 = tipos_por_pokemon[nombre1]
        for j, nombre2 in enumerate(nombres):
            if i != j:  # Evitar lazos
                tipos2 = tipos_por_pokemon[nombre2]
                ponderacion = calcular_ponderacion(tipos1, tipos2)
                if ponderacion > 0:  # Solo agrega conexiones relevantes
                    G.add_edge(nombre1, nombre2, weight=ponderacion)

    return G

# Función para buscar el pokémon más fuerte
def encontrar_fuerte_contra(pokemon, grafo):
    if pokemon not in grafo:
        return f"El Pokémon '{pokemon}' no está en la base de datos."
    
    # Evalua los nodos que atacan al Pokémon dado
    fortaleza = {
        atacante: grafo[atacante][pokemon]['weight']
        for atacante in grafo.predecessors(pokemon)
    }
    
    if not fortaleza:
        return "No se encontraron atacantes efectivos."
    
    mejor_pokemon = max(fortaleza, key=fortaleza.get)
    return mejor_pokemon, fortaleza[mejor_pokemon]

# Construcción del grafo
print("Construyendo el grafo...")
grafo_pokemon = construir_grafo()
print("Grafo construido")

# Pregunta al usuario por un pokemon, si el usuario introduce "0", para
while True:
    pokemon_usuario = input("Ingresa el nombre de un Pokémon (o '0' para salir): ").strip().lower()
    if pokemon_usuario == '0':
        print("si quiere saber más pokemons counters, vuelva a ejecutar el código")
        break
    
    resultado = encontrar_fuerte_contra(pokemon_usuario, grafo_pokemon)
    if isinstance(resultado, tuple):
        print(f"El Pokémon más fuerte contra '{pokemon_usuario}' es '{resultado[0]}' con efectividad de {resultado[1]:.2f}.")
    else:
        print(resultado)

conexion.close()