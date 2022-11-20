#Substantial referential and code-use credit to authors at https://ai-boson.github.io/mcts/
import numpy as np
from collections import defaultdict
import TakGame

class Node:
    def __init__(self, state, parent = None, parent_action = None):
        self.state = state
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._visit_count = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        return 

    def untried_actions(self):
        self._untried_actions = None    # TODO: Find a way to use __get_moves() here...
                                        # might need to generalize __get_moves() and a 
                                        # lot of the Tak class to work outside of a game 
                                        # instance for structure and memory purposes
        return self._untried_actions

    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses

    def n(self):
        return self._number_of_visits

    def expand(self):
        action = self._untried_actions.pop()
        next_state = None   # TODO: generalize TakGame.Tak.result() to work
                            # outside of game instance. Modify result to return
                            # encoded state. 
        child_node = Node(
            next_state, parent=self, parent_action=action)

        self.children.append(child_node)
        return child_node 

    def is_terminal_node(self):
        return TakGame.terminal_state(self.state)  
        # TODO: generalize terminal_states(self.state) to take encoded state, 
        # return (bool, 1 or 0 or -1 indicate w/notdone/l)

    def rollout(self):
        current_rollout_state = self.state
    
        while not TakGame.terminal_state(self.state):   # TODO: See is_terminal_node
        
            possible_moves = None   # TODO: See untried_actions(),
                                    # should be all legal moves from self.state
            
            action = self.rollout_policy(possible_moves)
            current_rollout_state = None    # TODO: See expand(),
                                            # should be result(self.state)

        return None  # TODO: implement function that accepts a terminal state
                     # and returns 1/-1 for win or loss for moving player.

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)
    
    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def best_child(self, c_param=0.1):  
        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]

    def _tree_policy(self):
        current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

    def best_action(self):
        simulation_no = 100
	
	
        for i in range(simulation_no):
            
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        
        return self.best_child(c_param=0.1)