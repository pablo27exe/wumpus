import pygame
import sys
import random
from pygame.locals import *

# -----------------------------------------------------------------------------
# CLASE 1: EL MUNDO DE WUMPUS (EL SIMULADOR)
#MODIFICADA PARA INCLUIR FLECHAS -
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
        self.agent_has_arrow = True  # El agente comienza con una flecha
        self.wumpus_is_alive = True  # El Wumpus comienza vivo

        # Inicializa un tablero vacío
        self.board = { (x,y): [] for x in range(1, size+1) for y in range(1, size+1) }

        # Colocar Oro
        self.gold_location = self._get_random_empty_cell()
        self.board[self.gold_location].append('G')

        # Colocar Wumpus
        self.wumpus_location = self._get_random_empty_cell()
        self.board[self.wumpus_location].append('W')

        # Colocar Pozos 20% de probabilidad por casilla
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

        # Comprobar si hay peligros adyacentes (solo si el Wumpus está vivo)
        if self.wumpus_is_alive:
            for nx, ny in self.get_neighbors(x, y):
                if 'W' in self.board[(nx, ny)]:
                    percepts['stench'] = True
        for nx, ny in self.get_neighbors(x, y):
            if 'P' in self.board[(nx, ny)]:
                percepts['breeze'] = True

        return percepts

    def execute_action(self, action, direction=None):
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
        elif action == 'shoot_arrow':
            if not self.agent_has_arrow:
                return "No tienes flechas."
            
            self.agent_has_arrow = False
            # Determinar la dirección del disparo
            if direction == 'up':
                target_cells = [(x, y + i) for i in range(1, self.size + 1) if self._is_valid_location(x, y + i)]
            elif direction == 'down':
                target_cells = [(x, y - i) for i in range(1, self.size + 1) if self._is_valid_location(x, y - i)]
            elif direction == 'left':
                target_cells = [(x - i, y) for i in range(1, self.size + 1) if self._is_valid_location(x - i, y)]
            elif direction == 'right':
                target_cells = [(x + i, y) for i in range(1, self.size + 1) if self._is_valid_location(x + i, y)]
            else:
                return "Dirección de disparo no válida."
            
            # Verificar si el Wumpus está en alguna de las celdas objetivo
            for cell in target_cells:
                if cell == self.wumpus_location and self.wumpus_is_alive:
                    self.wumpus_is_alive = False
                    self.board[cell].remove('W')
                    return "¡Escuchas un grito! Has matado al Wumpus."
            
            return "La flecha no golpeó nada."

        # Comprobar si el agente muere después de moverse
        if 'W' in self.board[self.agent_location] and self.wumpus_is_alive:
            self.agent_is_alive = False
            return "¡MUERTE! El agente fue comido por el Wumpus."
        if 'P' in self.board[self.agent_location]:
            self.agent_is_alive = False
            return "¡MUERTE! El agente cayó en un pozo."

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
# - MODIFICADA PARA INCLUIR RETROCESO Y DISPARO MEJORADO -
# -----------------------------------------------------------------------------
class LogicalAgent:
    """
    El agente que razona sobre el Mundo de Wumpus.
    """
    def __init__(self, world, kb):
        self.world = world
        self.kb = kb
        self.location = (1, 1) # El agente siempre empieza en (1, 1)
        self.visited_squares = set() # Un conjunto de tuplas (x, y)
        self.path_stack = []  # Pila para realizar backtracking
        self.wumpus_killed = False  # Para saber si el Wumpus fue eliminado

        # El agente sabe que la casilla (1, 1) es segura al empezar
        self.kb.tell("Safe at (1, 1)")
        self.visited_squares.add((1, 1))
        self.path_stack.append((1, 1))  # Comienza en (1, 1)

    def procesar_perceptos(self, percepts):
        """
        Procesa los perceptos de la casilla actual y actualiza la KB.
        Este es el paso 'TELL'.
        """
        x, y = self.location

        # Solo registrar brisa/hedor si no los hemos registrado antes
        current_breeze = f"Breeze at ({x}, {y})"
        current_no_breeze = f"No Breeze at ({x}, {y})"
        current_stench = f"Stench at ({x}, {y})"
        current_no_stench = f"No Stench at ({x}, {y})"

        if percepts['breeze']:
            if not self.kb.ask(current_breeze):
                self.kb.tell(current_breeze)
                print(f"DEBUG: Registrada brisa en ({x}, {y})")
        else:
            if not self.kb.ask(current_no_breeze):
                self.kb.tell(current_no_breeze)
                print(f"DEBUG: Registrada NO brisa en ({x}, {y})")

        if percepts['stench']:
            if not self.kb.ask(current_stench):
                self.kb.tell(current_stench)
                print(f"DEBUG: Registrado hedor en ({x}, {y})")
        else:
            if not self.kb.ask(current_no_stench):
                self.kb.tell(current_no_stench)
                print(f"DEBUG: Registrado NO hedor en ({x}, {y})")

        # Siempre registrar brillo si está presente
        if percepts['glitter']:
            self.kb.tell(f"Glitter at ({x}, {y})")

    def inferir_seguridad(self):
        """
        Aplica reglas lógicas simples para deducir qué casillas son seguras.
        Este es el paso de 'INFERENCIA'.
        """

        # Regla 1: Las casillas visitadas son seguras 
        for location in self.visited_squares:
            if self.world.agent_is_alive:
                self.kb.tell(f"Safe at {location}")

        # Regla 2: Si no hay hedor, los vecinos son seguros del Wumpus
        no_stench_facts = self.kb.get_facts_starting_with("No Stench at")
        for fact in no_stench_facts:
            x, y = eval(fact.split(' at ')[1])
            for nx, ny in self.world.get_neighbors(x, y):
                if not self.kb.ask(f"Danger at ({nx}, {ny})"):
                    self.kb.tell(f"Safe at ({nx}, {ny})")
                    
        # -------------------------------------------------------------------------
        # REGLAS  PARA INFERIR PELIGRO
        # -------------------------------------------------------------------------
            
        # Regla 3: Si hay brisa, algun vecino tiene pozo
        breeze_facts = self.kb.get_facts_starting_with("Breeze at")
        
        # Primero, identificar todas las casillas con brisa
        breeze_locations = [eval(fact.split(' at ')[1]) for fact in breeze_facts]
        
        for breeze_loc in breeze_locations:
            x, y = breeze_loc
            neighbors = self.world.get_neighbors(x, y)
            
            # Filtrar vecinos que ya sabemos que son seguros
            unsafe_neighbors = [n for n in neighbors if not self.kb.ask(f"Safe at {n}")]
            
            # Si solo hay un vecino no seguro, debe ser un pozo
            if len(unsafe_neighbors) == 1:
                dangerous = unsafe_neighbors[0]
                self.kb.tell(f"Danger at {dangerous}")
                self.kb.tell(f"Pit at {dangerous}")
                print(f"DEBUG: Pozo inferido en {dangerous} por brisa en {breeze_loc}")

        # Regla 4: Inferencia mejorada para múltiples brisas
        if len(breeze_locations) >= 2:
            # Buscar intersecciones de vecinos entre casillas con brisa
            possible_pit_locations = set()
            
            for i, loc1 in enumerate(breeze_locations):
                neighbors1 = set(self.world.get_neighbors(loc1[0], loc1[1]))
                for j, loc2 in enumerate(breeze_locations):
                    if i != j:
                        neighbors2 = set(self.world.get_neighbors(loc2[0], loc2[1]))
                        intersection = neighbors1.intersection(neighbors2)
                        # Solo considerar intersecciones que no son seguras
                        intersection = [loc for loc in intersection if not self.kb.ask(f"Safe at {loc}")]
                        possible_pit_locations.update(intersection)
            
            # Si hay una única ubicación posible para el pozo, inferirla
            if len(possible_pit_locations) == 1:
                pit_loc = list(possible_pit_locations)[0]
                self.kb.tell(f"Danger at {pit_loc}")
                self.kb.tell(f"Pit at {pit_loc}")
                print(f"DEBUG: Pozo inferido en {pit_loc} por múltiples brisas")

        # Regla 5: Si hay hedor, algun vecino tiene Wumpus  
        stench_facts = self.kb.get_facts_starting_with("Stench at")
        for fact in stench_facts:
            x, y = eval(fact.split(' at ')[1])
            neighbors = self.world.get_neighbors(x, y)
                
            # Si todos los vecinos excepto uno son seguros, el restante tiene Wumpus
            safe_neighbors = [n for n in neighbors if self.kb.ask(f"Safe at {n}")]
            if len(safe_neighbors) == len(neighbors) - 1:
                wumpus_location = [n for n in neighbors if n not in safe_neighbors][0]
                self.kb.tell(f"Wumpus at {wumpus_location}")
                self.kb.tell(f"Danger at {wumpus_location}")
        
        # Regla 6: Inferencia mejorada para múltiples hedores
        if len(stench_facts) >= 2:
            stench_locations = [eval(fact.split(' at ')[1]) for fact in stench_facts]
            possible_wumpus_locations = set()
            
            # Encontrar intersección de vecinos de todas las casillas con hedor
            for i, loc1 in enumerate(stench_locations):
                neighbors1 = set(self.world.get_neighbors(loc1[0], loc1[1]))
                for j, loc2 in enumerate(stench_locations):
                    if i != j:
                        neighbors2 = set(self.world.get_neighbors(loc2[0], loc2[1]))
                        intersection = neighbors1.intersection(neighbors2)
                        possible_wumpus_locations.update(intersection)
            
            # Si solo hay una ubicación posible, es el Wumpus
            possible_wumpus_locations = [loc for loc in possible_wumpus_locations 
                                    if not self.kb.ask(f"Safe at {loc}")]
            
            if len(possible_wumpus_locations) == 1:
                wumpus_loc = possible_wumpus_locations[0]
                self.kb.tell(f"Wumpus at {wumpus_loc}")
                self.kb.tell(f"Danger at {wumpus_loc}")
                print(f"DEBUG: Wumpus inferido en {wumpus_loc} por múltiples hedores")

        # Regla 7: Si no hay brisa, todos los vecinos son seguros de pozos
        no_breeze_facts = self.kb.get_facts_starting_with("No Breeze at")
        for fact in no_breeze_facts:
            x, y = eval(fact.split(' at ')[1])
            for nx, ny in self.world.get_neighbors(x, y):
                if not self.kb.ask(f"Danger at ({nx}, {ny})"):
                    self.kb.tell(f"Safe at ({nx}, {ny})")
                        
        # Ver qué peligros se detectaron
        danger_facts = [f for f in self.kb.facts if 'Danger' in f]
        wumpus_facts = [f for f in self.kb.facts if 'Wumpus at' in f]
        pit_facts = [f for f in self.kb.facts if 'Pit at' in f]
        
        if danger_facts:
            print(f"DEBUG: Peligros inferidos: {danger_facts}")
        if wumpus_facts:
            print(f"DEBUG: Wumpus inferido en: {wumpus_facts}")
        if pit_facts:
            print(f"DEBUG: Pozos inferidos en: {pit_facts}")

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

        acciones_posibles = []
        if self._is_valid_and_get_action('up'): acciones_posibles.append('move_up')
        if self._is_valid_and_get_action('down'): acciones_posibles.append('move_down')
        if self._is_valid_and_get_action('left'): acciones_posibles.append('move_left')
        if self._is_valid_and_get_action('right'): acciones_posibles.append('move_right')
        
        # Lógica más para disparar flechas
        if self.world.agent_has_arrow:
            # Opción 1: Si se sabe exactamente dónde está el Wumpus, disparar
            wumpus_facts = self.kb.get_facts_starting_with("Wumpus at")
            if wumpus_facts:
                wumpus_location = eval(wumpus_facts[0].split(' at ')[1])
                # Determinar dirección para disparar
                if wumpus_location[0] == self.location[0]:  # Misma columna
                    if wumpus_location[1] > self.location[1]:
                        return ('shoot_arrow', 'up')
                    else:
                        return ('shoot_arrow', 'down')
                elif wumpus_location[1] == self.location[1]:  # Misma fila
                    if wumpus_location[0] > self.location[0]:
                        return ('shoot_arrow', 'right')
                    else:
                        return ('shoot_arrow', 'left')
            
            # Opción 2: Si el hedor persiste, considerar disparar
            stench_facts = self.kb.get_facts_starting_with("Stench at")
            if len(stench_facts) >= 2:  # Solo disparar si hay múltiples hedores
                print("DEBUG: Hedor persistente detectado, considerando disparar...")
                
                # Obtener vecinos no visitados y peligrosos
                vecinos_no_visitados = [v for v in vecinos if v not in self.visited_squares]
                vecinos_peligrosos = [v for v in vecinos_no_visitados if self.kb.ask(f"Danger at {v}")]
                
                if vecinos_peligrosos:
                    target = vecinos_peligrosos[0]
                    print(f"DEBUG: Disparando hacia vecino peligroso: {target}")
                    
                    # Determinar dirección del disparo
                    x, y = self.location
                    tx, ty = target
                    
                    if tx == x and ty == y + 1:
                        return ('shoot_arrow', 'up')
                    elif tx == x and ty == y - 1:
                        return ('shoot_arrow', 'down')
                    elif tx == x - 1 and ty == y:
                        return ('shoot_arrow', 'left')
                    elif tx == x + 1 and ty == y:
                        return ('shoot_arrow', 'right')

        random.shuffle(acciones_posibles) # Para evitar bucles entre dos casillas

        # Clasificar acciones por seguridad
        acciones_seguras_no_visitadas = []
        acciones_seguras_visitadas = []
        acciones_riesgosas = []

        for action in acciones_posibles:
            vecino = self._get_target_location(action)
            
            # EVITAR casillas peligrosas confirmadas
            if self.kb.ask(f"Danger at {vecino}"):
                continue

            # Clasificar por nivel de seguridad
            if self.kb.ask(f"Safe at {vecino}"):
                if vecino not in self.visited_squares:
                    acciones_seguras_no_visitadas.append(action)
                else:
                    acciones_seguras_visitadas.append(action)
            else:
                # NUEVO: Solo considerar riesgosas si no hay brisa actual
                percepts_actuales = self.world.get_percepts_at(self.location)
                if not percepts_actuales['breeze']:
                    acciones_riesgosas.append(action)

        # Decidir basado en la prioridad
        if acciones_seguras_no_visitadas:
            self.path_stack.append(self.location)
            return random.choice(acciones_seguras_no_visitadas)
        elif acciones_seguras_visitadas:
            self.path_stack.append(self.location)
            return random.choice(acciones_seguras_visitadas)
        elif acciones_riesgosas and len(self.visited_squares) > 3:
            # Solo considerar movimientos riesgosos si hemos explorado suficiente
            # y no hay brisa en la ubicación actual
            percepts_actuales = self.world.get_percepts_at(self.location)
            if not percepts_actuales['breeze']:
                print(f"DEBUG: Considerando movimiento riesgoso (sin brisa actual)")
                self.path_stack.append(self.location)
                return random.choice(acciones_riesgosas)
        else:
            # Realizar backtracking si no hay movimientos seguros
            if len(self.path_stack) > 1:
                previous_location = self.path_stack.pop()
                return self._get_backtrack_action(previous_location)
            else:
                # No hay ningún lugar seguro conocido a donde ir.
                return 'climb_out'

    def _get_backtrack_action(self, target_location):
        """Determina la acción para retroceder a una ubicación anterior"""
        x, y = self.location
        tx, ty = target_location
        
        if tx == x and ty == y + 1:
            return 'move_up'
        elif tx == x and ty == y - 1:
            return 'move_down'
        elif tx == x - 1 and ty == y:
            return 'move_left'
        elif tx == x + 1 and ty == y:
            return 'move_right'
        else:
            # Si no es un movimiento directo, elegir una dirección aleatoria
            acciones = []
            if self._is_valid_and_get_action('up'): acciones.append('move_up')
            if self._is_valid_and_get_action('down'): acciones.append('move_down')
            if self._is_valid_and_get_action('left'): acciones.append('move_left')
            if self._is_valid_and_get_action('right'): acciones.append('move_right')
            return random.choice(acciones) if acciones else 'climb_out'

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

            # 3. DECIDE (ASK)
            action_result = self.elegir_accion()
            if isinstance(action_result, tuple):
                action, direction = action_result
                print(f"Agente decide: {action} hacia {direction}")
            else:
                action = action_result
                print(f"Agente decide: {action}")

            # 4. ACTÚA
            if isinstance(action_result, tuple):
                result = self.world.execute_action(action, direction)
            else:
                result = self.world.execute_action(action)
            print(f"Resultado: {result}")

            # Actualizar estado si el Wumpus fue eliminado
            if "grito" in result.lower() or "matado" in result.lower():
                self.wumpus_killed = True
                # Limpiar hechos relacionados con el Wumpus
                wumpus_facts = self.kb.get_facts_starting_with("Wumpus at")
                for fact in wumpus_facts:
                    self.kb.facts.remove(fact)
                # Actualizar percepciones de hedor
                stench_facts = self.kb.get_facts_starting_with("Stench at")
                for fact in stench_facts:
                    self.kb.facts.remove(fact)
                    self.kb.tell(fact.replace("Stench", "No Stench"))

            if "¡VICTORIA!" in result or "escapó" in result or "¡MUERTE!" in result:
                break
        else:
            print("Se alcanzó el límite de pasos.")

        print("\n--- Simulación Terminada ---")
        self.kb.print_facts()

# -----------------------------------------------------------------------------
# INTERFAZ GRÁFICA CON PYGAME
# -----------------------------------------------------------------------------
class WumpusGUI:
    def __init__(self, world, agent):
        self.world = world
        self.agent = agent
        self.cell_size = 80
        self.margin = 5
        self.width = world.size * (self.cell_size + self.margin) + self.margin + 300
        self.height = world.size * (self.cell_size + self.margin) + self.margin
        
        # Colores
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.BROWN = (165, 42, 42)
        self.PURPLE = (128, 0, 128)
        self.ORANGE = (255, 165, 0)
        
        # Inicializar Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mundo de Wumpus - Agente Lógico")
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        self.step_delay = 1000  # Milisegundos entre pasos
        self.last_step_time = 0
        self.running = True
        self.auto_mode = False
        self.current_step = 0
        self.game_state = "Ejecutando"
        self.message = "Presiona ESPACIO para avanzar o A para modo automático"

    def draw_board(self):
        """Dibuja el tablero del Mundo de Wumpus"""
        # Fondo
        self.screen.fill(self.BLACK)
        
        # Dibujar tablero
        for x in range(1, self.world.size + 1):
            for y in range(1, self.world.size + 1):
                rect_x = self.margin + (x - 1) * (self.cell_size + self.margin)
                rect_y = self.height - self.margin - y * (self.cell_size + self.margin)
                
                # Color de la celda
                color = self.WHITE
                if (x, y) in self.agent.visited_squares:
                    color = self.GRAY
                if (x, y) == self.world.agent_location:
                    color = self.BLUE
                
                pygame.draw.rect(self.screen, color, 
                               (rect_x, rect_y, self.cell_size, self.cell_size))
                
                # Dibujar elementos
                cell_content = self.world.board[(x, y)]
                
                # Wumpus (rojo) - solo si está vivo
                if 'W' in cell_content and self.world.wumpus_is_alive and (not self.world.agent_is_alive or self.game_state != "Ejecutando"):
                    pygame.draw.circle(self.screen, self.RED, 
                                     (rect_x + self.cell_size // 2, rect_y + self.cell_size // 2), 
                                     self.cell_size // 3)
                    w_text = self.font.render("W", True, self.WHITE)
                    self.screen.blit(w_text, (rect_x + self.cell_size // 2 - 5, rect_y + self.cell_size // 2 - 8))
                
                # Pozo (marrón)
                if 'P' in cell_content and (not self.world.agent_is_alive or self.game_state != "Ejecutando"):
                    pygame.draw.circle(self.screen, self.BROWN, 
                                     (rect_x + self.cell_size // 2, rect_y + self.cell_size // 2), 
                                     self.cell_size // 4)
                
                # Oro (amarillo)
                if 'G' in cell_content and not self.world.agent_has_gold:
                    pygame.draw.circle(self.screen, self.YELLOW, 
                                     (rect_x + self.cell_size // 2, rect_y + self.cell_size // 2), 
                                     self.cell_size // 5)
                
                # Agente (verde si vivo, rojo si muerto)
                if (x, y) == self.world.agent_location:
                    agent_color = self.GREEN if self.world.agent_is_alive else self.RED
                    pygame.draw.circle(self.screen, agent_color, 
                                     (rect_x + self.cell_size // 2, rect_y + self.cell_size // 2), 
                                     self.cell_size // 6)
                    
                    # Dibujar flecha si el agente la tiene
                    if self.world.agent_has_arrow:
                        arrow_color = self.ORANGE
                        pygame.draw.polygon(self.screen, arrow_color, [
                            (rect_x + self.cell_size - 10, rect_y + 10),
                            (rect_x + self.cell_size - 20, rect_y + 5),
                            (rect_x + self.cell_size - 20, rect_y + 15)
                        ])
                
                # Coordenadas
                coord_text = self.font.render(f"({x},{y})", True, self.BLACK)
                self.screen.blit(coord_text, (rect_x + 5, rect_y + 5))

    def draw_info_panel(self):
        """Dibuja el panel de información lateral"""
        panel_x = self.world.size * (self.cell_size + self.margin) + self.margin + 20
        panel_y = 20
        
        # Título
        title = self.title_font.render("MUNDO DE WUMPUS", True, self.WHITE)
        self.screen.blit(title, (panel_x, panel_y))
        
        # Estado del juego
        state_y = panel_y + 40
        state_text = self.font.render(f"Estado: {self.game_state}", True, self.WHITE)
        self.screen.blit(state_text, (panel_x, state_y))
        
        # Paso actual
        step_text = self.font.render(f"Paso: {self.current_step}", True, self.WHITE)
        self.screen.blit(step_text, (panel_x, state_y + 30))
        
        # Ubicación del agente
        loc_text = self.font.render(f"Posición: {self.world.agent_location}", True, self.WHITE)
        self.screen.blit(loc_text, (panel_x, state_y + 60))
        
        # Perceptos actuales
        percepts = self.world.get_percepts_at(self.world.agent_location)
        percepts_y = state_y + 90
        percepts_title = self.font.render("Perceptos:", True, self.WHITE)
        self.screen.blit(percepts_title, (panel_x, percepts_y))
        
        percept_items = [
            f"Hedor: {'SÍ' if percepts['stench'] else 'NO'}",
            f"Brisa: {'SÍ' if percepts['breeze'] else 'NO'}",
            f"Brillo: {'SÍ' if percepts['glitter'] else 'NO'}"
        ]
        
        for i, item in enumerate(percept_items):
            color = self.YELLOW if "SÍ" in item else self.WHITE
            text = self.font.render(item, True, color)
            self.screen.blit(text, (panel_x + 10, percepts_y + 30 + i * 25))
        
        # Estado del agente
        agent_y = percepts_y + 120
        agent_title = self.font.render("Estado Agente:", True, self.WHITE)
        self.screen.blit(agent_title, (panel_x, agent_y))
        
        agent_items = [
            f"Vivo: {'SÍ' if self.world.agent_is_alive else 'NO'}",
            f"Tiene oro: {'SÍ' if self.world.agent_has_gold else 'NO'}",
            f"Tiene flecha: {'SÍ' if self.world.agent_has_arrow else 'NO'}",
            f"Wumpus vivo: {'SÍ' if self.world.wumpus_is_alive else 'NO'}",
            f"Casillas visitadas: {len(self.agent.visited_squares)}"
        ]
        
        for i, item in enumerate(agent_items):
            color = self.GREEN if "SÍ" in item and "Vivo" in item else self.WHITE
            color = self.YELLOW if "SÍ" in item and "oro" in item else color
            color = self.RED if "SÍ" in item and "Wumpus vivo" in item else color
            text = self.font.render(item, True, color)
            self.screen.blit(text, (panel_x + 10, agent_y + 30 + i * 25))
        
        # Base de conocimiento (algunos hechos)
        kb_y = agent_y + 150
        kb_title = self.font.render("Base de Conocimiento:", True, self.WHITE)
        self.screen.blit(kb_title, (panel_x, kb_y))
        
        safe_cells = [f for f in self.agent.kb.facts if f.startswith("Safe at")]
        danger_cells = [f for f in self.agent.kb.facts if f.startswith("Danger at")]
        kb_items = [
            f"Hechos seguros: {len(safe_cells)}",
            f"Hechos peligrosos: {len(danger_cells)}"
        ]
        
        for i, item in enumerate(kb_items):
            text = self.font.render(item, True, self.WHITE)
            self.screen.blit(text, (panel_x + 10, kb_y + 30 + i * 20))
        
        # Mostrar algunos hechos de seguridad y peligro
        fact_y = kb_y + 80
        for i, fact in enumerate(list(safe_cells)[:3]):
            text = self.font.render(fact, True, self.GREEN)
            self.screen.blit(text, (panel_x + 10, fact_y + i * 20))
        
        for i, fact in enumerate(list(danger_cells)[:3]):
            text = self.font.render(fact, True, self.RED)
            self.screen.blit(text, (panel_x + 150, fact_y + i * 20))
        
        # Controles
        controls_y = fact_y + 80
        controls_title = self.font.render("Controles:", True, self.WHITE)
        self.screen.blit(controls_title, (panel_x, controls_y))
        
        controls = [
            "ESPACIO: Siguiente paso",
            "A: Modo automático",
            "R: Reiniciar",
            "Q: Salir"
        ]
        
        for i, control in enumerate(controls):
            text = self.font.render(control, True, self.WHITE)
            self.screen.blit(text, (panel_x + 10, controls_y + 30 + i * 25))
        
        # Mensaje
        msg_y = controls_y + 150
        msg_text = self.font.render(self.message, True, self.YELLOW)
        self.screen.blit(msg_text, (panel_x, msg_y))

    def run_step(self):
        """Ejecuta un paso del agente"""
        if not self.world.agent_is_alive or (self.world.agent_has_gold and self.world.agent_location == (1, 1)):
            self.game_state = "Terminado"
            if not self.world.agent_is_alive:
                self.message = "¡EL AGENTE MURIÓ! Presiona R para reiniciar"
            else:
                self.message = "¡VICTORIA! El agente escapó con el oro. Presiona R para reiniciar"
            return
        
        self.current_step += 1
        
        # Ejecutar un paso del agente
        self.agent.location = self.world.agent_location
        self.agent.visited_squares.add(self.agent.location)
        percepts = self.world.get_percepts_at(self.agent.location)
        
        # Procesar perceptos y razonar
        self.agent.procesar_perceptos(percepts)
        if percepts['glitter']:
            self.agent.kb.tell(f"Glitter at {self.agent.location}")
        self.agent.inferir_seguridad()
        
        # Elegir y ejecutar acción
        action_result = self.agent.elegir_accion()
        if isinstance(action_result, tuple):
            action, direction = action_result
            result = self.world.execute_action(action, direction)
            self.message = f"Paso {self.current_step}: {action} {direction} -> {result}"
        else:
            action = action_result
            result = self.world.execute_action(action)
            self.message = f"Paso {self.current_step}: {action} -> {result}"
        
        # Actualizar si el Wumpus fue eliminado
        if "grito" in result.lower() or "matado" in result.lower():
            self.agent.wumpus_killed = True
            # Limpiar hechos relacionados con el Wumpus
            wumpus_facts = self.agent.kb.get_facts_starting_with("Wumpus at")
            for fact in wumpus_facts:
                self.agent.kb.facts.remove(fact)
            # Actualizar percepciones de hedor
            stench_facts = self.agent.kb.get_facts_starting_with("Stench at")
            for fact in stench_facts:
                self.agent.kb.facts.remove(fact)
                self.agent.kb.tell(fact.replace("Stench", "No Stench"))

    def reset_game(self):
        """Reinicia el juego"""
        self.world = WumpusWorld(size=4)
        kb = KnowledgeBase()
        self.agent = LogicalAgent(self.world, kb)
        self.current_step = 0
        self.game_state = "Ejecutando"
        self.message = "Juego reiniciado. Presiona ESPACIO para avanzar o A para modo automático"

    def run(self):
        """Bucle principal de la interfaz gráfica"""
        clock = pygame.time.Clock()
        
        while self.running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_q:
                        self.running = False
                    elif event.key == K_SPACE:
                        self.run_step()
                    elif event.key == K_a:
                        self.auto_mode = not self.auto_mode
                        self.message = f"Modo automático: {'ACTIVADO' if self.auto_mode else 'DESACTIVADO'}"
                    elif event.key == K_r:
                        self.reset_game()
            
            # Ejecutar paso automáticamente si está en modo automático
            if self.auto_mode and current_time - self.last_step_time > self.step_delay:
                if self.game_state == "Ejecutando":
                    self.run_step()
                self.last_step_time = current_time
            
            # Dibujar interfaz
            self.draw_board()
            self.draw_info_panel()
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

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

    # Ejecutar en modo gráfico o consola
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        # Modo consola
        agent.run_agent(max_steps=50)
    else:
        # Modo gráfico
        gui = WumpusGUI(world, agent)
        gui.run()