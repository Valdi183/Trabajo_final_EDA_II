# PROYECTO EDA_II (DICIEMBRE) FINAL: SIMULADOR BATALLAS POKEMON
Este repositorio contiene todos los archivos que hacen posible el simulador.

### Nota:
Para los datos de los pokemons que se utilizan para el combate, he utilizado una base de datos que contiene información sobre los pokemons (tipo, estadísticas...). Esta base de datos (pokemon.db),
Contiene una serie de tablas con toda la información, muchas de esas tablas son relacionales, ya que relaciona las características con los pokemons que las puedan tener, y son cruciales para una
optimización del juego. En caso de querer ver estas tablas, simplemente se tendrá que instalar la extensión _**SQLite Viewer**_ en VSCode. 

### [crear_pokemon.py](https://github.com/Valdi183/Trabajo_final_EDA_II/blob/main/crear_pokemon.py):
es el script con el que he creado la base de datos pokemon.db.

### [counter_equipo_random.py](https://github.com/Valdi183/Trabajo_final_EDA_II/blob/main/counter_equipo_random.py):
puedes ejecutar este script para ver como a un equipo random generado, se crea el equipo más fuerte contra el equipo generado.

###[grafo_pokemon_counter.py](https://github.com/Valdi183/Trabajo_final_EDA_II/blob/main/grafo_pokemon_counter.py):
puedes ejecutar este script, para ver cual es el pokemon más fuerte al pokemon que quieras introducir.