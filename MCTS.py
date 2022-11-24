#Substantial referential and code-use credit to authors at https://ai-boson.github.io/mcts/
import numpy as np
from collections import defaultdict
from Tak import *

class MCTSNode:
    def __init__(self, state_int, parent = None, parent_action = None, agent = PieceColor.WHITE, turn = PieceColor.WHITE):
        self.state_int = state_int
        self.turn = turn
        self.agent_color = agent
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = None
        self._untried_actions = self.untried_actions()
        return 

    def untried_actions(self):
        board = decode_state(self.state_int)
        self._untried_actions = get_moves(board,self.turn)
        return self._untried_actions

    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses

    def n(self):
        return self._number_of_visits

    def expand(self,board):
        action = self._untried_actions.pop()
        next_state = result(board,action)
        child_node = MCTSNode(
            encode_state(next_state), 
            parent=self, 
            parent_action=action, 
            turn = PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE
            )

        self.children.append(child_node)
        return child_node 

    def is_terminal_node(self,board):
        return terminal_test(board, PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE)[0] 
        

    def rollout(self,board):
        end_state = terminal_test(board, PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE)
        while not end_state[0]:   
            
            possible_moves = self._untried_actions
            
            action = self.rollout_policy(possible_moves)
            board = result(board, action)
            end_state = terminal_test(board, PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE)

        return 1 if end_state[1] == self.agent_color else -1

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

    def _tree_policy(self,board):
        current_node = self
        while not current_node.is_terminal_node(board):
            if not current_node.is_fully_expanded():
                return current_node.expand(board)
            else:
                current_node = current_node.best_child()
        return current_node

    def best_action(self):
        simulation_no = 100
        board = decode_state(self.state_int)
	
        for i in range(simulation_no):
            
            v = self._tree_policy(board)
            reward = v.rollout(board)
            v.backpropagate(reward)
        
        return self.best_child(c_param=0.1)

def main():
    initial_state = bits_to_int([1]*GAMESIZE)
    root = MCTSNode(state_int=initial_state)
    selected_node = root.best_action()
    action = selected_node.parent_action
    print(action.piece, action.position)
    return 

if __name__ == "__main__":
    main()