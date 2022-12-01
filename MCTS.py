#Substantial referential and code-use credit to authors at https://ai-boson.github.io/mcts/
from time import *
import numpy as np
from collections import defaultdict
from Tak import *

class Policy(Enum):
    RANDOM,H1 = range(2)

class MCTSNode:
    def __init__(self, state_int, rollout_policy_int = Policy.RANDOM, parent = None, parent_action = None, agent = PieceColor.WHITE):
        self.state_int = state_int
        self.agent_color = agent
        self.rollout_policy_int = rollout_policy_int
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._number_of_visits = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = self.untried_actions()
        return 

    def return_child(self, action, unseen_board):
        #Child has been expanded to by MCTS already (MCTS saw opponents move and has relevant data)
        for child in self.children:
            if action == child.parent_action:
                return child
        #Child has not been seen yet. (MCTS has not seen this move. No data collected yet)
        return MCTSNode(encode_state(unseen_board),parent=self,parent_action=action,agent=self.agent_color)

    def untried_actions(self):
        board = decode_state(self.state_int)
        actions = get_moves(board,self.agent_color)
        return actions

    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses

    def n(self):
        return self._number_of_visits

    def expand(self,board):
        action = self._untried_actions.pop()
        # print(top_board_string(board))
        # print(stacks_string(board))
        # print(f"Expanding on {action}")
        try:
            next_state = result(board,action)
        
            child_node = MCTSNode(
                encode_state(next_state), 
                parent=self, 
                parent_action=action, 
                agent= self.agent_color
            )

            self.children.append(child_node)
            return child_node
        except IndexError:
            f = open("Err.txt","w")
            f.write(f"""Board:\n{top_board_string(board)}
{stacks_string(board)}
Expanding Action: {action}
Self:
\Agent:\t{self.agent_color}
Board:{top_board_string(decode_state(self.state_int))}
{stacks_string(decode_state(self.state_int))}
Untried Actions:{self._untried_actions}""")
            f.close()
            exit()

    def make_node_root(self,color):
        self.parent = None
        self.parent_action = None
        self.agent_color = color
       

    def is_terminal_node(self,board):
        return terminal_test(board, PieceColor.BLACK if self.agent_color == PieceColor.WHITE else PieceColor.WHITE)[0] 
        
    
    def rollout(self):
        board = decode_state(self.state_int)
        color = PieceColor.BLACK if self.agent_color == PieceColor.WHITE else PieceColor.WHITE
        # f.write(top_board_string(board)+'\n')
        score = self.get_score(board)
        end_state = terminal_test(board,self.agent_color)
        i = 0
        while not end_state[0]:   
            
            possible_moves = get_moves(board, color)
            action, score = self.rollout_policy(possible_moves, color, board, score)
            board = result(board, action)
        
            # f.write(top_board_string(board))
            # f.write(stacks_string(board))
            # f.write(f"{action}\n\n")
            end_state = terminal_test(board, color)
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

    def rollout_policy(self, possible_moves, color, board, base_score):
        if self.rollout_policy_int == Policy.RANDOM:
            return self.rand_rollout_policy(possible_moves)
        if self.rollout_policy_int == Policy.H1:
            return self.h1_rollout_policy(possible_moves,color,board,base_score)

    def get_score(self, board):
        if self.rollout_policy_int == Policy.RANDOM:
            return None
        elif self.rollout_policy_int == Policy.H1:
            return h1(board)
        
    def rand_rollout_policy(self, possible_moves:list[Union[PlacementMove,StackMove]])->tuple[Union[PlacementMove,StackMove],None]:
        return (possible_moves[np.random.randint(len(possible_moves))], None)

    def h1_rollout_policy(self, possible_moves:list[Union[PlacementMove,StackMove]],\
        color:PieceColor, board:list[list[deque[Piece]]],\
        base_score:int)->tuple[Union[PlacementMove,StackMove],int]:

        best_score = base_score
        color_factor = 1 if color == PieceColor.WHITE else -1
        best_moves = [possible_moves[np.random.randint(len(possible_moves))]]
        for move in possible_moves:
            curr_score = h1_delta(board,move,base_score)  
            if color_factor*(best_score - curr_score) < 0:
                best_moves.clear()
                best_moves.append(move)
                best_score = curr_score
            elif color_factor*(best_score - curr_score) == 0:
                best_moves.append(move)
        return best_moves[np.random.randint(len(best_moves))], best_score


    def _tree_policy(self,board:list[list[deque[Piece]]]):
        current_node = self
        while not current_node.is_terminal_node(board):
            if not current_node.is_fully_expanded():
                return current_node.expand(board)
            else:
                current_node = current_node.best_child()
                board = decode_state(current_node.state_int)
        return current_node

    def best_action(self):
        sim_total = 0
        board = decode_state(self.state_int)
        sim_goal = max(m.ceil(2 *len(self._untried_actions)),100)
        t_start = time()
        t_curr = t_start
        # t_curr - t_start < 30 and
        while sim_total < sim_goal or t_curr - t_start < 10:
            # f = open(f"simulation{i+1}.txt","w")
            # print("Simulation No.:",sim_total+1,end = ' ')
            v = self._tree_policy(board)
            reward = v.rollout()
            v.backpropagate(reward)
            t_curr = time()
            sim_total +=1
            # f.close()
        
        return self.best_child(c_param=0.1)


