import random

# -----------------------------------------------------------------------------
# CLASE 1: EL MUNDO DE WUMPUS (EL SIMULADOR)
# - NO MODIFICAR ESTA CLASE -
# -----------------------------------------------------------------------------
class WumpusWorld:
    """
    Simula el entorno del Mundo de Wumpus.
    Maneja el tablero, la ubicación de los peligros y las percepciones.
    """
    def __init__(self, size=4):
        self.size = size
        self.agent_location = (1, 1)
        self.agent_has_gold = False
        self.agent_is_alive = True

        # Inicializa un tablero vacío
        # (W: Wumpus, P: Pozo, G: Oro, A: Agente)
        self.board = { (x,y): [] for x in range(1, size+1) for y in range(1, size+1) }

        # Colocar Oro
        self.gold_location = self._get_random_empty_cell()
        self.board[self.gold_location].append('G')

        # Colocar Wumpus
        self.wumpus_location = self._get_random_empty_cell()
        self.board[self.wumpus_location].append('W')

        # Colocar Pozos (Pits) - 20% de probabilidad por casilla
        for x in range(1, size + 1):
            for y in range(1, size + 1):
                if (x, y) != (1, 1) and (x, y) not in [self.gold_location, self.wumpus_location]:
                    if random.random() < 0.20:
                        self.board[(x, y)].append('P')

    def _get_random_empty_cell(self):
        """ Obtiene una celda aleatoria que no sea (1,1). """
        while True:
            x, y = random.randint(1, self.size), random.randint(1, self.size)
            if (x, y) != (1, 1) and not self.board[(x, y)]:
                return (x, y)

    def _is_valid_location(self, x, y):
        """ Comprueba si una coordenada está dentro del tablero. """
        return 1 <= x <= self.size and 1 <= y <= self.size

    def get_neighbors(self, x, y):
        """ Obtiene los vecinos válidos de una casilla. """
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self._is_valid_location(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def get_percepts_at(self, location):
        """ Devuelve lo que el agente percibe en una ubicación. """
        x, y = location
        percepts = {
            'stench': False, # Hedor (Wumpus)
            'breeze': False, # Brisa (Pozo)
            'glitter': False # Brillo (Oro)
        }

        # Comprobar si hay Oro
        if 'G' in self.board[location]:
            percepts['glitter'] = True

        # Comprobar si hay peligros adyacentes
        for nx, ny in self.get_neighbors(x, y):
            if 'W' in self.board[(nx, ny)]:
                percepts['stench'] = True
            if 'P' in self.board[(nx, ny)]:
                percepts['breeze'] = True

        return percepts

    def execute_action(self, action):
        """ Ejecuta la acción del agente y devuelve el estado. """
        if not self.agent_is_alive:
            return "El agente está muerto."

        x, y = self.agent_location

        if action == 'move_up':
            self.agent_location = (x, y + 1) if self._is_valid_location(x, y + 1) else (x, y)
        elif action == 'move_down':
            self.agent_location = (x, y - 1) if self._is_valid_location(x, y - 1) else (x, y)
        elif action == 'move_left':
            self.agent_location = (x - 1, y) if self._is_valid_location(x - 1, y) else (x, y)
        elif action == 'move_right':
            self.agent_location = (x + 1, y) if self._is_valid_location(x + 1, y) else (x, y)
        elif action == 'grab_gold':
            if 'G' in self.board[self.agent_location]:
                self.agent_has_gold = True
                self.board[self.agent_location].remove('G')
                return "¡El agente encontró el oro!"
            else:
                return "No hay oro aquí."
        elif action == 'climb_out':
            if self.agent_location == (1, 1):
                if self.agent_has_gold:
                    return "¡VICTORIA! El agente escapó con el oro."
                else:
                    return "El agente escapó sin el oro."
            else:
                return "Solo se puede salir desde (1, 1)."

        # Comprobar si el agente muere después de moverse
        if 'W' in self.board[self.agent_location] or 'P' in self.board[self.agent_location]:
            self.agent_is_alive = False
            return "¡MUERTE! El agente cayó en un pozo o fue comido por el Wumpus."

        return f"Agente se movió a {self.agent_location}"

# -----------------------------------------------------------------------------
# CLASE 2: LA BASE DE CONOCIMIENTO (KB)
# - NO MODIFICAR ESTA CLASE -
# -----------------------------------------------------------------------------
class KnowledgeBase:
    """
    Una Base de Conocimiento (KB) simple basada en hechos.
    Almacena 'hechos' (oraciones) como cadenas de texto.
    """
    def __init__(self):
        self.facts = set()

    def tell(self, fact):
        """ Añade un nuevo hecho a la KB. (Diapositiva 6: Representación) """
        self.facts.add(fact)

    def ask(self, fact):
        """ Comprueba si un hecho ya existe en la KB. (Diapositiva 6: Razonamiento) """
        return fact in self.facts

    def get_facts_starting_with(self, prefix):
        """ Devuelve una lista de hechos que comienzan con un prefijo. """
        return [f for f in self.facts if f.startswith(prefix)]

    def print_facts(self):
        """ Imprime todos los hechos conocidos. """
        print("--- Hechos Conocidos (KB) ---")
        for f in sorted(list(self.facts)):
            print(f)
        print("-------------------------------")

# -----------------------------------------------------------------------------
# CLASE 3: EL AGENTE LÓGICO
# - ¡AQUÍ TRABAJAS TÚ! -
# -----------------------------------------------------------------------------
class LogicalAgent:
    """
    El agente que razona sobre el Mundo de Wumpus.
    Debe completar los métodos marcados con 'TODO'.
    """
    def __init__(self, world, kb):
        self.world = world
        self.kb = kb
        self.location = (1, 1) # El agente siempre empieza en (1, 1)
        self.visited_squares = set() # Un conjunto de tuplas (x, y)

        # El agente sabe que la casilla (1, 1) es segura al empezar
        self.kb.tell("Safe at (1, 1)")
        self.visited_squares.add((1, 1))

    def procesar_perceptos(self, percepts):
        """
        Procesa los perceptos de la casilla actual y actualiza la KB.
        Este es el paso 'TELL'.
        """
        x, y = self.location

        ####################################################################
        # TODO 1: ACTUALIZAR LA KB CON LOS PERCEPTOS


        if percepts['breeze']:
            self.kb.tell(f"Breeze at ({x}, {y})")
        else:
            self.kb.tell(f"No Breeze at ({x}, {y})")

        if percepts['stench']:
            self.kb.tell(f"Stench at ({x}, {y})")
        else:
            self.kb.tell(f"No Stench at ({x}, {y})")
            
        if percepts['glitter']:
            self.kb.tell(f"Glitter at ({x}, {y})")
        else:
            self.kb.tell(f"No Glitter at ({x}, {y})")

    def inferir_seguridad(self):
        """
        Aplica reglas lógicas simples para deducir qué casillas son seguras.
        Este es el paso de 'INFERENCIA'.
        """

        # ####################################################################
        # TODO 2: INFERIR HECHOS NUEVOS


        # Regla 1: Inferir seguridad de pozos
        no_breeze_facts = self.kb.get_facts_starting_with("No Breeze at")
        for fact in no_breeze_facts:
            # Extraer coordenadas del hecho, ej. "No Breeze at (1, 1)"
            x, y = eval(fact.split(' at ')[1])

            for nx, ny in self.world.get_neighbors(x, y):
                # Si una casilla no tiene brisa, sus vecinas son seguras de pozos
                # (Simplificamos y decimos que son "Safe")
                self.kb.tell(f"Safe at ({nx}, {ny})")

        # Regla 2: Inferir seguridad del Wumpus
        no_stench_facts = self.kb.get_facts_starting_with("No Stench at")
        for fact in no_stench_facts:
            x, y = eval(fact.split(' at ')[1])

            for nx, ny in self.world.get_neighbors(x, y):
                # Si no hay hedor, sus vecinas son seguras del Wumpus
                self.kb.tell(f"Safe at ({nx}, {ny})")

        # Nota: Un agente más avanzado manejaría "Safe_Wumpus" y "Safe_Pit"
        # por separado y solo marcaría "Safe" si ambas son verdaderas.

    def elegir_accion(self):
        """
        Decide qué acción tomar basándose en la KB.
        Este es el paso 'ASK' y 'ACTÚA'.
        """

        # 1. Si hay "Brillo" (Glitter), toma el oro.
        if self.kb.ask(f"Glitter at {self.location}"):
            return 'grab_gold'

        # 2. Si tiene el oro y está en (1, 1), sal.
        if self.world.agent_has_gold and self.location == (1, 1):
            return 'climb_out'

        vecinos = self.world.get_neighbors(self.location[0], self.location[1])

        # ####################################################################
        # TODO 3: ELEGIR UN MOVIMIENTO SEGURO

        acciones_posibles = []
        if self._is_valid_and_get_action('up'): acciones_posibles.append('move_up')
        if self._is_valid_and_get_action('down'): acciones_posibles.append('move_down')
        if self._is_valid_and_get_action('left'): acciones_posibles.append('move_left')
        if self._is_valid_and_get_action('right'): acciones_posibles.append('move_right')

        random.shuffle(acciones_posibles) # Para evitar bucles entre dos casillas

        accion_segura_no_visitada = None
        accion_segura_visitada = None

        for action in acciones_posibles:
            vecino = self._get_target_location(action)

            # ASK a la KB
            if self.kb.ask(f"Safe at {vecino}"):
                if vecino not in self.visited_squares:
                    accion_segura_no_visitada = action
                    break # ¡Esta es la mejor opción!
                else:
                    accion_segura_visitada = action # Es una opción de retroceso

        # Decidir basado en la prioridad
        if accion_segura_no_visitada:
            return accion_segura_no_visitada
        elif accion_segura_visitada:
            return accion_segura_visitada
        else:
            # No hay ningún lugar seguro conocido a donde ir.
            # Un agente más inteligente podría tomar un riesgo
            # (ej. ir a una casilla 50% segura) o usar la flecha.
            # El nuestro se rinde.
            return 'climb_out'


    # --- Métodos Ayudantes (No modificar) ---

    def _is_valid_and_get_action(self, direction):
        x, y = self.location
        if direction == 'up': return self.world._is_valid_location(x, y + 1)
        if direction == 'down': return self.world._is_valid_location(x, y - 1)
        if direction == 'left': return self.world._is_valid_location(x - 1, y)
        if direction == 'right': return self.world._is_valid_location(x + 1, y)
        return False

    def _get_target_location(self, action):
        x, y = self.location
        if action == 'move_up': return (x, y + 1)
        if action == 'move_down': return (x, y - 1)
        if action == 'move_left': return (x - 1, y)
        if action == 'move_right': return (x + 1, y)
        return self.location

    def run_agent(self, max_steps=50):
        """ El ciclo principal del agente: PERCIBE -> PIENSA -> ACTÚA """
        print(f"Agente iniciando en {self.location}")

        for step in range(max_steps):
            if not self.world.agent_is_alive:
                print("El agente ha muerto. Fin de la simulación.")
                break

            print(f"\n--- Paso {step + 1} ---")

            # 1. PERCIBE
            self.location = self.world.agent_location
            self.visited_squares.add(self.location)
            percepts = self.world.get_percepts_at(self.location)
            print(f"Agente está en {self.location}")
            print(f"Agente percibe: {percepts}")

            # 2. PIENSA (TELL e INFERENCIA)
            # Primero, añade los perceptos actuales a la KB
            self.procesar_perceptos(percepts)

            # Si hay brillo, la KB se actualiza para la acción 'grab_gold'
            if percepts['glitter']:
                self.kb.tell(f"Glitter at {self.location}")

            # Segundo, deduce nuevos hechos (seguridad)
            self.inferir_seguridad()

            # (Opcional) Imprime la KB para depurar
            # self.kb.print_facts()

            # 3. DECIDE (ASK)
            action = self.elegir_accion()
            print(f"Agente decide: {action}")

            # 4. ACTÚA
            result = self.world.execute_action(action)
            print(f"Resultado: {result}")

            if "¡VICTORIA!" in result or "escapó" in result or "¡MUERTE!" in result:
                break
        else:
            print("Se alcanzó el límite de pasos.")

        print("\n--- Simulación Terminada ---")
        self.kb.print_facts()

# -----------------------------------------------------------------------------
# BLOQUE PRINCIPAL DE EJECUCIÓN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Crea el mundo
    world = WumpusWorld(size=4)

    # Crea la Base de Conocimiento
    kb = KnowledgeBase()

    # Crea el Agente
    agent = LogicalAgent(world, kb)

    # ¡Ejecuta el agente!
    agent.run_agent(max_steps=50)