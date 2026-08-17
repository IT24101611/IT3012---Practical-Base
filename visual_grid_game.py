# visual_grid_game.py

import random
import tkinter as tk


class VisualGridHuntGame:
    """
    A flexible Pacman-style grid environment with:
    - Food
    - Walls
    - Optional opponents
    - Toxic traps
    - Global state percepts for search agents
    """

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None
    ):
        self.width = width
        self.height = height

        # Starting position of the agent
        self.agent_pos = [0, 0]

        # ---------------------------------------------------------
        # Walls
        # ---------------------------------------------------------

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # ---------------------------------------------------------
        # Food
        # ---------------------------------------------------------

        self.food_positions = set()

        while len(self.food_positions) < num_food:

            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)

            pos_tuple = (fx, fy)

            if (
                pos_tuple != (0, 0)
                and pos_tuple not in self.walls
            ):
                self.food_positions.add(pos_tuple)

        # ---------------------------------------------------------
        # Opponents
        # ---------------------------------------------------------

        self.opponents = []

        while len(self.opponents) < num_opponents:

            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)

            op_pos = [ox, oy]
            op_tuple = tuple(op_pos)

            if (
                op_tuple != (0, 0)
                and op_tuple not in self.walls
                and op_tuple not in self.food_positions
            ):
                self.opponents.append(op_pos)

        # ---------------------------------------------------------
        # Toxic Traps
        # ---------------------------------------------------------

        self.toxic_traps = set()

        num_traps = 2

        while len(self.toxic_traps) < num_traps:

            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            pos_tuple = (tx, ty)

            opponent_positions = {
                tuple(op)
                for op in self.opponents
            }

            if (
                pos_tuple != (0, 0)
                and pos_tuple not in self.walls
                and pos_tuple not in self.food_positions
                and pos_tuple not in opponent_positions
            ):
                self.toxic_traps.add(pos_tuple)

        # ---------------------------------------------------------
        # Game State
        # ---------------------------------------------------------

        self.score = 0
        self.steps = 0
        self.collision = False

        # Agent starts facing Up
        self.facing = "Up"

    # =============================================================
    # PERCEPTION
    # =============================================================

    def get_percept(self) -> dict:
        """
        Return the environment percept.

        This includes the global state required by the
        BFS, DFS and UCS SearchAgent.
        """

        return {
            # Current agent position
            "agent_pos": list(self.agent_pos),

            # Opponent positions
            "opponent_positions": [
                list(op)
                for op in self.opponents
            ],

            # Local food sensor
            "smells_food": (
                tuple(self.agent_pos)
                in self.food_positions
            ),

            # Whether current position is a wall
            "hit_wall": (
                tuple(self.agent_pos)
                in self.walls
            ),

            # Collision state
            "collision": self.collision,

            # Current score
            "score": self.score,

            # Number of food pellets remaining
            "remaining_food": len(
                self.food_positions
            ),

            # -----------------------------------------------------
            # GLOBAL STATE
            # Required for SearchAgent
            # -----------------------------------------------------

            # Grid dimensions
            "grid_size": (
                self.width,
                self.height
            ),

            # All wall coordinates
            "walls": list(
                self.walls
            ),

            # All remaining food coordinates
            "all_food": list(
                self.food_positions
            ),

            # Toxic trap information
            "smells_toxin": (
                tuple(self.agent_pos)
                in self.toxic_traps
            )
        }

    # =============================================================
    # ACTION EXECUTION
    # =============================================================

    def execute_action(self, action: str):

        self.steps += 1

        directions = [
            "Up",
            "Right",
            "Down",
            "Left"
        ]

        # ---------------------------------------------------------
        # Turn Left
        # ---------------------------------------------------------

        if action in ["turn_left", "Turn_Left"]:

            current_index = directions.index(
                self.facing
            )

            self.facing = directions[
                (current_index - 1) % 4
            ]

        # ---------------------------------------------------------
        # Turn Right
        # ---------------------------------------------------------

        elif action in ["turn_right", "Turn_Right"]:

            current_index = directions.index(
                self.facing
            )

            self.facing = directions[
                (current_index + 1) % 4
            ]

        # ---------------------------------------------------------
        # Suck / Collect Food
        # ---------------------------------------------------------

        elif action in ["suck", "Collect"]:

            current_position = tuple(
                self.agent_pos
            )

            if current_position in self.food_positions:

                self.food_positions.remove(
                    current_position
                )

                self.score += 20

        # ---------------------------------------------------------
        # Movement
        # ---------------------------------------------------------

        elif (
            action == "move_forward"
            or action == "Move_Forward"
            or action in [
                "Up",
                "Down",
                "Left",
                "Right"
            ]
        ):

            new_pos = list(
                self.agent_pos
            )

            # Determine movement direction
            if action in [
                "move_forward",
                "Move_Forward"
            ]:
                move_direction = self.facing
            else:
                move_direction = action

            # Move Up
            if move_direction == "Up":

                new_pos[1] = min(
                    self.height - 1,
                    new_pos[1] + 1
                )

            # Move Down
            elif move_direction == "Down":

                new_pos[1] = max(
                    0,
                    new_pos[1] - 1
                )

            # Move Left
            elif move_direction == "Left":

                new_pos[0] = max(
                    0,
                    new_pos[0] - 1
                )

            # Move Right
            elif move_direction == "Right":

                new_pos[0] = min(
                    self.width - 1,
                    new_pos[0] + 1
                )

            # -----------------------------------------------------
            # Wall Collision
            # -----------------------------------------------------

            if tuple(new_pos) in self.walls:

                self.score -= 5

            else:

                self.agent_pos = new_pos

        # ---------------------------------------------------------
        # Food Collection
        # ---------------------------------------------------------

        current_position = tuple(
            self.agent_pos
        )

        if current_position in self.food_positions:

            self.food_positions.remove(
                current_position
            )

            self.score += 20

        # ---------------------------------------------------------
        # Toxic Trap
        # ---------------------------------------------------------

        if current_position in self.toxic_traps:

            self.score -= 15

            # Remove the trap after it is triggered
            self.toxic_traps.remove(
                current_position
            )

        # ---------------------------------------------------------
        # Opponent Movement
        # ---------------------------------------------------------

        for opponent in self.opponents:

            move = random.choice([
                "Up",
                "Down",
                "Left",
                "Right",
                "Stay"
            ])

            # Opponent moves Up
            if (
                move == "Up"
                and opponent[1] < self.height - 1
            ):
                opponent[1] += 1

            # Opponent moves Down
            elif (
                move == "Down"
                and opponent[1] > 0
            ):
                opponent[1] -= 1

            # Opponent moves Left
            elif (
                move == "Left"
                and opponent[0] > 0
            ):
                opponent[0] -= 1

            # Opponent moves Right
            elif (
                move == "Right"
                and opponent[0] < self.width - 1
            ):
                opponent[0] += 1

            # -----------------------------------------------------
            # Agent / Opponent Collision
            # -----------------------------------------------------

            if opponent == self.agent_pos:

                self.score -= 50

                self.collision = True

    # =============================================================
    # END CONDITION
    # =============================================================

    def is_done(self) -> bool:

        return (
            len(self.food_positions) == 0
            or self.steps >= 1000
            or self.collision
        )


# =================================================================
# GUI
# =================================================================

class GridGameGUI:
    """
    Tkinter GUI for the Visual Grid Hunt Game.
    """

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        walls=None
    ):

        self.root = root

        self.root.title(
            "IT3012 - Search-Based Grid Hunt"
        )

        # Create environment
        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # ---------------------------------------------------------
        # Canvas Size
        # ---------------------------------------------------------

        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )

        canvas_width = (
            self.env.width
            * self.cell_size
        )

        canvas_height = (
            self.env.height
            * self.cell_size
        )

        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg="white"
        )

        self.canvas.pack()

        # ---------------------------------------------------------
        # Status Label
        # ---------------------------------------------------------

        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )

        self.label.pack(
            pady=10
        )

        # ---------------------------------------------------------
        # Algorithm Selection
        # ---------------------------------------------------------

        self.algorithm_label = tk.Label(
            root,
            text="Search Algorithm: BFS",
            font=("Arial", 12)
        )

        self.algorithm_label.pack(
            pady=2
        )

        # ---------------------------------------------------------
        # Start Button
        # ---------------------------------------------------------

        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )

        self.btn.pack(
            pady=5
        )

        # Draw initial environment
        self.draw_grid()

    # =============================================================
    # DRAW GRID
    # =============================================================

    def draw_grid(self):

        self.canvas.delete(
            "all"
        )

        # ---------------------------------------------------------
        # Draw Grid Cells and Walls
        # ---------------------------------------------------------

        for x in range(
            self.env.width
        ):

            for y in range(
                self.env.height
            ):

                x1 = (
                    x
                    * self.cell_size
                )

                y1 = (
                    self.env.height
                    - 1
                    - y
                ) * self.cell_size

                x2 = (
                    x1
                    + self.cell_size
                )

                y2 = (
                    y1
                    + self.cell_size
                )

                # Normal cell or wall
                if (x, y) in self.env.walls:

                    cell_color = "#64748b"

                else:

                    cell_color = "#f1f5f9"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=cell_color,
                    outline="#cbd5e1"
                )

                # Wall label
                if (
                    self.cell_size >= 40
                    and (x, y) in self.env.walls
                ):

                    self.canvas.create_text(
                        x1
                        + self.cell_size / 2,
                        y1
                        + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=(
                            "Arial",
                            8,
                            "bold"
                        )
                    )

        # ---------------------------------------------------------
        # Draw Food
        # ---------------------------------------------------------

        for fx, fy in self.env.food_positions:

            offset = (
                self.cell_size
                * 0.25
            )

            x1 = (
                fx
                * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - fy
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1
                + self.cell_size * 0.5,
                y1
                + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )

        # ---------------------------------------------------------
        # Draw Toxic Traps
        # ---------------------------------------------------------

        for tx, ty in self.env.toxic_traps:

            offset = (
                self.cell_size
                * 0.2
            )

            x1 = (
                tx
                * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - ty
            ) * self.cell_size + offset

            self.canvas.create_polygon(
                x1
                + self.cell_size * 0.3,
                y1,

                x1
                + self.cell_size * 0.6,
                y1
                + self.cell_size * 0.3,

                x1
                + self.cell_size * 0.3,
                y1
                + self.cell_size * 0.6,

                x1,
                y1
                + self.cell_size * 0.3,

                fill="#a855f7",
                outline="#7c3aed"
            )

        # ---------------------------------------------------------
        # Draw Opponents
        # ---------------------------------------------------------

        for ox, oy in self.env.opponents:

            offset = (
                self.cell_size
                * 0.2
            )

            x1 = (
                ox
                * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - oy
            ) * self.cell_size + offset

            self.canvas.create_rectangle(
                x1,
                y1,
                x1
                + self.cell_size * 0.6,
                y1
                + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )

        # ---------------------------------------------------------
        # Draw Agent
        # ---------------------------------------------------------

        ax, ay = self.env.agent_pos

        offset = (
            self.cell_size
            * 0.15
        )

        x1 = (
            ax
            * self.cell_size
            + offset
        )

        y1 = (
            self.env.height
            - 1
            - ay
        ) * self.cell_size + offset

        self.canvas.create_oval(
            x1,
            y1,
            x1
            + self.cell_size * 0.7,
            y1
            + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )

        # ---------------------------------------------------------
        # Display Facing Direction
        # ---------------------------------------------------------

        self.canvas.create_text(
            x1
            + self.cell_size * 0.35,
            y1
            + self.cell_size * 0.35,
            text=self.env.facing[0],
            fill="white",
            font=(
                "Arial",
                10,
                "bold"
            )
        )

    # =============================================================
    # RUN SEARCH SIMULATION
    # =============================================================

    def run_loop(self):

        self.btn.config(
            state="disabled"
        )

        # Import SearchAgent
        from agent import SearchAgent

        # Create search agent
        agent = SearchAgent()

        # ---------------------------------------------------------
        # Choose Algorithm Here
        # ---------------------------------------------------------
        #
        # Change this to:
        #
        # "BFS"
        # "DFS"
        # "UCS"
        #
        # ---------------------------------------------------------

        agent.active_algo = "BFS"

        self.algorithm_label.config(
            text=f"Search Algorithm: {agent.active_algo}"
        )

        def step():

            if not self.env.is_done():

                # Get current global percept
                percept = self.env.get_percept()

                # SearchAgent selects an action
                action = agent.sense_and_act(
                    percept
                )

                # Execute action
                self.env.execute_action(
                    action
                )

                # Redraw GUI
                self.draw_grid()

                # Update status
                self.label.config(
                    text=(
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action} | "
                        f"Food Left: "
                        f"{len(self.env.food_positions)}"
                    )
                )

                # Continue simulation
                self.root.after(
                    250,
                    step
                )

            else:

                if self.env.collision:

                    end_text = (
                        "Collision! Game Over! "
                        f"Final Score: {self.env.score}"
                    )

                elif len(
                    self.env.food_positions
                ) == 0:

                    end_text = (
                        "All Food Collected! "
                        f"Final Score: {self.env.score}"
                    )

                else:

                    end_text = (
                        "Simulation Finished! "
                        f"Final Score: {self.env.score}"
                    )

                self.label.config(
                    text=end_text
                )

                self.btn.config(
                    state="normal"
                )

        step()


# =================================================================
# MAIN
# =================================================================

if __name__ == "__main__":

    root = tk.Tk()

    # 12 x 12 grid
    # 15 food pellets
    # No opponents for search algorithm testing
    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    root.mainloop()