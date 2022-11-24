#Substantial referential and code-use credit to authors at https://ai-boson.github.io/mcts/
from time import *
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
        
    # TODO: Error here. Right now this rollout logic plays black's turns only. I.e. no white moves happen.
    def rollout(self):
        board = decode_state(self.state_int)
        color = self.turn
        # f.write(top_board_string(board)+'\n')
        end_state = terminal_test(board, PieceColor.BLACK if self.turn == PieceColor.WHITE else PieceColor.WHITE)
        i = 0
        while not end_state[0]:   
            
            possible_moves = get_moves(board, color)
            action = self.rollout_policy(possible_moves)
            board = result(board, action)
            # f.write(top_board_string(board))
            # f.write(stacks_string(board))
            # f.write(f"{action}\n\n")
            end_state = terminal_test(board, PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE)
            color = PieceColor.BLACK if color == PieceColor.WHITE else PieceColor.WHITE
            i+=1
        # f.seek(0) 
        # f.write(f"Winner: {end_state[1]}\nMoves: {i}") 
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
        sim_goal = 100
        sim_total = 0
        board = decode_state(self.state_int)
        t_start = time()
        t_curr = t_start
        while t_curr - t_start < 30 and sim_total <= sim_goal :
            # f = open(f"simulation{i+1}.txt","w")
            print("Simulation No.:",sim_total+1,end = ' ')
            v = self._tree_policy(board)
            reward = v.rollout()
            v.backpropagate(reward)
            t_curr = time()
            sim_total +=1
            # f.close()
        
        return self.best_child(c_param=0.1)

def main():
    initial_state = bits_to_int([1]*GAMESIZE)
    game = TakGame(decode_state(initial_state))
    root = MCTSNode(state_int=initial_state)
    while not root.is_terminal_node(decode_state(root.state_int)):
        selected_node = root.best_action()
        action = selected_node.parent_action
        print(f"Root won {root._results[1]} out of {root._number_of_visits} games")
        print(f"{action} won {selected_node._results[1]} out of {selected_node._number_of_visits} games")
        make_move(game,action)
        print(top_board_string(game.board))
        root = selected_node


    print("\nSelected Action: ", action.position, action.piece,"\nWins",selected_node._results[1], " out of ", selected_node._results[1]+selected_node._results[-1], " games")
    print("\nRoot saw ", root.agent_color, " win ", root._results[1], " out of ", root._results[1] + root._results[-1]," games")
    return 

if __name__ == "__main__":
    main()