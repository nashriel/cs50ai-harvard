import math
import random
import time


class Nim:
    """
    A class representing the game of Nim.
    Contains game logic and methods for gameplay management.
    """

    def __init__(self, initial=None):
        """
        Initialize the game board.
        Args:
            initial (list): Initial configuration of piles. Defaults to [1, 3, 5, 7].
        """
        if initial is None:
            initial = [1, 3, 5, 7]
        self.piles = initial.copy()
        self.player = 0
        self.winner = None

    @classmethod
    def available_actions(cls, piles):
        """
        Compute all available actions for the current state.
        Args:
            piles (list): Current state of piles.
        Returns:
            set: All valid actions as (pile_index, count) tuples.
        """
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player):
        """
        Determine the opponent player.
        Args:
            player (int): Current player (0 or 1).
        Returns:
            int: Opponent player (1 or 0).
        """
        return 0 if player == 1 else 1

    def switch_player(self):
        """
        Switch turn to the other player.
        """
        self.player = Nim.other_player(self.player)

    def move(self, action):
        """
        Execute a move for the current player.
        Args:
            action (tuple): A tuple (pile_index, count) representing the move.
        Raises:
            Exception: If the move is invalid or the game is already won.
        """
        pile, count = action

        # Validate move
        if self.winner is not None:
            raise Exception("Game already won")
        if pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile")
        if count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects")

        # Apply move
        self.piles[pile] -= count
        self.switch_player()

        # Check for a winner
        if all(pile == 0 for pile in self.piles):
            self.winner = self.player


class NimAI:
    """
    A class representing an AI agent for the game of Nim.
    Implements Q-learning for decision-making.
    """

    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize the AI agent.
        Args:
            alpha (float): Learning rate.
            epsilon (float): Exploration rate.
        """
        self.q = {}
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        """
        Update the Q-value for a given state-action pair.
        Args:
            old_state (list): Previous state.
            action (tuple): Action taken.
            new_state (list): Resulting state.
            reward (float): Reward received.
        """
        old_q = self.get_q_value(old_state, action)
        future_rewards = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old_q, reward, future_rewards)

    def get_q_value(self, state, action):
        """
        Get the Q-value for a given state-action pair.
        Args:
            state (list): Current state.
            action (tuple): Action taken.
        Returns:
            float: Q-value of the state-action pair, defaulting to 0.
        """
        return self.q.get((tuple(state), action), 0)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update the Q-value using the Q-learning formula.
        Args:
            state (list): Current state.
            action (tuple): Action taken.
            old_q (float): Old Q-value.
            reward (float): Reward received.
            future_rewards (float): Estimated future rewards.
        """
        new_q = old_q + self.alpha * (reward + future_rewards - old_q)
        self.q[(tuple(state), action)] = new_q

    def best_future_reward(self, state):
        """
        Compute the maximum future reward for a given state.
        Args:
            state (list): Current state.
        Returns:
            float: Maximum future reward.
        """
        return max(
            (self.get_q_value(state, action) for action in Nim.available_actions(state)),
            default=0
        )

    def choose_action(self, state, epsilon=True):
        """
        Choose an action based on the current state.
        Args:
            state (list): Current state.
            epsilon (bool): Whether to use epsilon-greedy exploration.
        Returns:
            tuple: Chosen action.
        """
        actions = list(Nim.available_actions(state))
        if epsilon and random.random() < self.epsilon:
            return random.choice(actions)

        # Greedy choice
        return max(actions, key=lambda action: self.get_q_value(state, action), default=random.choice(actions))


def train(n):
    """
    Train the AI by playing games against itself.
    Args:
        n (int): Number of training games.
    Returns:
        NimAI: Trained AI instance.
    """
    ai = NimAI()

    for i in range(n):
        game = Nim()
        last = {0: {"state": None, "action": None}, 1: {"state": None, "action": None}}

        while game.winner is None:
            state = game.piles.copy()
            action = ai.choose_action(state)

            last[game.player]["state"] = state
            last[game.player]["action"] = action

            game.move(action)
            new_state = game.piles.copy()

            if game.winner is not None:
                ai.update(state, action, new_state, -1)
                ai.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    1
                )
            elif last[game.player]["state"] is not None:
                ai.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    0
                )
    return ai


def play(ai, human_player=None):
    """
    Play a game against the trained AI.
    Args:
        ai (NimAI): Trained AI instance.
        human_player (int): Human player order (0 or 1). Random if None.
    """
    human_player = human_player if human_player is not None else random.randint(0, 1)
    game = Nim()

    while game.winner is None:
        print("\nPiles:")
        for i, pile in enumerate(game.piles):
            print(f"Pile {i}: {pile}")
        print()

        if game.player == human_player:
            print("Your Turn")
            while True:
                pile = int(input("Choose Pile: "))
                count = int(input("Choose Count: "))
                if (pile, count) in Nim.available_actions(game.piles):
                    break
                print("Invalid move, try again.")
        else:
            print("AI's Turn")
            pile, count = ai.choose_action(game.piles, epsilon=False)
            print(f"AI chose to take {count} from pile {pile}.")

        game.move((pile, count))

        if game.winner is not None:
            print("\nGAME OVER")
            print(f"Winner is {'Human' if game.winner == human_player else 'AI'}")
