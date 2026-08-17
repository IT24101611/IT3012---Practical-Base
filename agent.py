from collections import deque
import heapq


class SearchAgent:
    """
    Search Agent implementing:
    - Breadth-First Search (BFS)
    - Depth-First Search (DFS)
    - Uniform-Cost Search (UCS)

    The agent creates an offline plan to reach food
    and then executes that plan one action at a time.
    """

    def __init__(self):
        # Available actions and their movement directions
        self.actions = {
            "Up": (0, 1),
            "Down": (0, -1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }

        # Step 1.3:
        # Store the planned sequence of actions
        self.plan = []

        # Select the search algorithm
        # Change this to "DFS" or "UCS" to compare algorithms
        self.active_algo = "BFS"

    # ---------------------------------------------------------
    # Get valid neighboring states
    # ---------------------------------------------------------

    def get_neighbors(self, state, grid_size, walls):

        x, y = state
        width, height = grid_size

        neighbors = []

        for action, (dx, dy) in self.actions.items():

            new_x = x + dx
            new_y = y + dy

            # Check grid boundaries
            if new_x < 0 or new_x >= width:
                continue

            if new_y < 0 or new_y >= height:
                continue

            new_state = (new_x, new_y)

            # Do not move through walls
            if new_state in walls:
                continue

            # Every action has cost 1
            neighbors.append(
                (new_state, action, 1)
            )

        return neighbors

    # ---------------------------------------------------------
    # BFS
    # ---------------------------------------------------------

    def bfs_search(self, start, goals, grid_size, walls):

        frontier = deque()

        # State + action path
        frontier.append(
            (start, [])
        )

        # Graph Search reached set
        reached = {start}

        while frontier:

            state, path = frontier.popleft()

            # Goal test
            if state in goals:
                return path

            for next_state, action, cost in self.get_neighbors(
                state,
                grid_size,
                walls
            ):

                if next_state not in reached:

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (next_state, new_path)
                    )

        return []

    # ---------------------------------------------------------
    # DFS
    # ---------------------------------------------------------

    def dfs_search(self, start, goals, grid_size, walls):

        frontier = []

        frontier.append(
            (start, [])
        )

        # Graph Search reached set
        reached = {start}

        while frontier:

            state, path = frontier.pop()

            # Goal test
            if state in goals:
                return path

            for next_state, action, cost in self.get_neighbors(
                state,
                grid_size,
                walls
            ):

                if next_state not in reached:

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (next_state, new_path)
                    )

        return []

    # ---------------------------------------------------------
    # UCS
    # ---------------------------------------------------------

    def ucs_search(self, start, goals, grid_size, walls):

        frontier = []

        # Priority Queue:
        # (path_cost, state, path)
        heapq.heappush(
            frontier,
            (0, start, [])
        )

        # Cheapest known cost for each state
        reached = {
            start: 0
        }

        while frontier:

            cost, state, path = heapq.heappop(frontier)

            # Goal test
            if state in goals:
                return path

            for next_state, action, step_cost in self.get_neighbors(
                state,
                grid_size,
                walls
            ):

                new_cost = cost + step_cost

                if (
                    next_state not in reached
                    or new_cost < reached[next_state]
                ):

                    reached[next_state] = new_cost

                    new_path = path + [action]

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            next_state,
                            new_path
                        )
                    )

        return []

    # ---------------------------------------------------------
    # Step 1.3 - Sense and Act
    # ---------------------------------------------------------

    def sense_and_act(self, percept):

        # If there is no current plan,
        # create a new plan.
        if not self.plan:

            # Current agent position
            start = tuple(percept["agent_pos"])

            # Get all available food
            all_food = [
                tuple(food)
                for food in percept["all_food"]
            ]

            # If there is no food left,
            # there is nothing to plan.
            if not all_food:
                return "Up"

            # Global environment information
            grid_size = percept["grid_size"]

            walls = {
                tuple(wall)
                for wall in percept["walls"]
            }

            # -------------------------------------------------
            # Find the closest food pellet
            # -------------------------------------------------

            closest_food = None
            shortest_distance = float("inf")

            for food in all_food:

                distance = abs(
                    start[0] - food[0]
                ) + abs(
                    start[1] - food[1]
                )

                if distance < shortest_distance:

                    shortest_distance = distance
                    closest_food = food

            # Search expects a set of goal states
            goals = {closest_food}

            # -------------------------------------------------
            # Select the active search algorithm
            # -------------------------------------------------

            if self.active_algo == "BFS":

                self.plan = self.bfs_search(
                    start,
                    goals,
                    grid_size,
                    walls
                )

            elif self.active_algo == "DFS":

                self.plan = self.dfs_search(
                    start,
                    goals,
                    grid_size,
                    walls
                )

            elif self.active_algo == "UCS":

                self.plan = self.ucs_search(
                    start,
                    goals,
                    grid_size,
                    walls
                )

            else:

                raise ValueError(
                    f"Unknown search algorithm: {self.active_algo}"
                )

            # Print the generated plan
            print(
                f"\nAlgorithm: {self.active_algo}"
            )

            print(
                f"Start: {start}"
            )

            print(
                f"Goal: {closest_food}"
            )

            print(
                f"Generated Plan: {self.plan}"
            )

            print(
                f"Plan Length: {len(self.plan)}"
            )

        # -----------------------------------------------------
        # Execute the plan one action at a time
        # -----------------------------------------------------

        if self.plan:

            return self.plan.pop(0)

        # No valid plan
        return "Up"