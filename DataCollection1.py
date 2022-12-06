from Tak import *
from MCTS import *

def setup_agent_game(black, white, game):
    initial_state = bits_to_int([1]*GAMESIZE)
    white_root = MCTSNode(state_int=initial_state, rollout_policy_int= white)
    white_selected_node = white_root.best_action()
    white_action = white_selected_node.parent_action
    # print(f"{white_root.agent_color} won {white_root._results[1]} out of {white_root._number_of_visits} games")
    # print(f"{white_action} won {white_selected_node._results[1]} out of {white_selected_node._number_of_visits} games")
    white_action = white_selected_node.parent_action
    make_move(game, white_action)
    # print(top_board_string(game.board))
    return MCTSNode(state_int=encode_state(game.board), rollout_policy_int= black ,agent = PieceColor.BLACK), white_selected_node


game_count = 100
f = None
while game_count < 200:
    turns = 0.5
    game = TakGame(blank_board())
    if game_count < 50:
        if game_count == 0:
            f = open("WH1 vs. BRand.txt","w")
            black_wins = 0
            white_wins = 0
            total_turns = 0
            total_time = 0
        black_root,white_selected_node = setup_agent_game(white = Policy.H1, black = Policy.RANDOM, game=game)
    elif game_count < 100:
        if game_count == 50:
            if isinstance(f, FILE):
	        f.close()
            f = open("WRand vs. BH1.txt","w")
            black_wins = 0
            white_wins = 0
            total_turns = 0
            total_time = 0
        black_root,white_selected_node = setup_agent_game(white = Policy.RANDOM, black=Policy.H1, game=game)
    elif game_count < 150:
        if game_count == 100:
          	if f:
			f.close()
            f = open("Wrand vs. Brand.txt","w")
            black_wins = 0
            white_wins = 0
            total_turns = 0
            total_time = 0
        black_root,white_selected_node = setup_agent_game(white = Policy.RANDOM, black=Policy.RANDOM, game=game)
    elif game_count < 200:
        if game_count == 150:
            f.close()
            f = open("WH1 vs. BH1.txt","w")
            black_wins = 0
            white_wins = 0
            total_turns = 0
            total_time = 0
        black_root,white_selected_node = setup_agent_game(white = Policy.H1, black=Policy.H1, game=game)
    f2 = open(f"Game {game_count}.txt", "w")
    t_start = time()
    while True:
        f2.write(f"Simulating {len(black_root._untried_actions)} moves\n")
        black_selected_node = black_root.best_action()
        black_action = black_selected_node.parent_action
    
        f2.write(f"{black_root.agent_color} won {black_root._results[1]} out of {black_root._number_of_visits} games\n")
        f2.write(f"{black_action} won  {black_selected_node._results[1]} out of  {black_selected_node._number_of_visits} games\n")
        
        make_move(game,black_action)
        turns += .5
        f2.write(top_board_string(game.board)+"\n")
        f2.write(stacks_string(game.board)+"\n")
        res = terminal_test(game.board, PieceColor.BLACK)
        if res[0]:
            game_time = time() - t_start
            total_time += game_time
            total_turns += turns
            if res[1] == PieceColor.WHITE:
                white_wins += 1  
            else: 
                black_wins += 1  
            f2.write(f"Winner: {res[1]}; Turns: {turns}; Time: {game_time} seconds\n")
            f.write(f"{res[1]} won game #{game_count % 50 + 1} in {turns} turns, the game took {game_time} seconds!\n White W/L Record: {white_wins}/{game_count % 50 + 1} | Black W/L Record: {black_wins}/{game_count % 50 + 1} | Avg. Turns Per Game: {total_turns/(game_count % 50 + 1)} | Avg. Time Per Game: {total_time /(game_count % 50 + 1)} seconds\n\n")
            break
        
        white_root = white_selected_node.return_child(black_action,game.board)
        white_root.make_node_root(PieceColor.WHITE)
        
        f2.write(f"Simulating {len(white_root._untried_actions)} moves\n")
        white_selected_node = white_root.best_action()
        white_action = white_selected_node.parent_action
        f2.write(f"{white_root.agent_color} won {white_root._results[1]} out of {white_root._number_of_visits} games\n")
        f2.write(f"{white_action} won {white_selected_node._results[1]} out of {white_selected_node._number_of_visits} games\n")
        
        make_move(game,white_action)
        turns += 0.5
        f2.write(top_board_string(game.board) + "\n")
        f2.write(stacks_string(game.board) + "\n")
        res = terminal_test(game.board, PieceColor.WHITE)
        if res[0]:
            game_time = time() - t_start
            total_time += game_time
            total_turns += turns
            if res[1] == PieceColor.WHITE:
                white_wins += 1  
            else: 
                black_wins += 1  
            f2.write(f"Winner: {res[1]}; Turns: {turns}; Time: {game_time} seconds\n")
            f.write(f"{res[1]} won game #{game_count % 50 + 1} in {turns} turns, the game took {game_time} seconds!\n White W/L Record: {white_wins}/{game_count % 50 + 1} | Black W/L Record: {black_wins}/{game_count % 50 + 1} | Avg. Turns Per Game: {total_turns/(game_count % 50 + 1)} | Avg. Time Per Game: {total_time /(game_count % 50 + 1)} seconds\n\n")
            break
        
        black_root = black_selected_node.return_child(white_action,game.board)
        black_root.make_node_root(PieceColor.BLACK)
    
    f2.close()
    game_count += 1

f.close()
     
