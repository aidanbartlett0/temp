'''
aidanb04_KInARow.py
Authors: Aidan Bartlett

An agent for playing "K-in-a-Row with Forbidden Squares" and related games.
CSE 415, University of Washington

THIS IS A TEMPLATE WITH STUBS FOR THE REQUIRED FUNCTIONS.
YOU CAN ADD WHATEVER ADDITIONAL FUNCTIONS YOU NEED IN ORDER
TO PROVIDE A GOOD STRUCTURE FOR YOUR IMPLEMENTATION.

'''

from agent_base import KAgent
from game_types import State, Game_Type
from static_eval import static_eval_scoring
import time

AUTHORS = 'Aidan Bartlett' 
UWNETIDS = ['aidanb04'] # The first UWNetID here should
# match the one in the file name, e.g., janiesmith99_KInARow.py.

import time # You'll probably need this to avoid losing a
# game due to exceeding a time limit.
import random

# Create your own type of agent by subclassing KAgent:

class OurAgent(KAgent):  # Keep the class name "OurAgent" so a game master
    # knows how to instantiate your agent class.

    def __init__(self, twin=False):
        self.twin=twin
        self.nickname = 'Jesse'
        if twin: self.nickname += '2'
        self.long_name = 'Jesse Pinkman'
        if twin: self.long_name += ' II'
        self.persona = 'bland'
        self.voice_info = {'Chrome': 10, 'Firefox': 2, 'other': 0}
        self.playing = "don't know yet" # e.g., "X" or "O".
        self.alpha_beta_cutoffs_this_turn = -1
        self.num_static_evals_this_turn = -1
        self.zobrist_table_num_entries_this_turn = -1
        self.zobrist_table_num_hits_this_turn = -1
        self.alpha_beta_cutoffs = -1
        self.num_static_evals = -1
        self.zobrist_table_num_entries = -1
        self.zobrist_table_num_hits = -1

        self.current_game_type = None
        self.playing_mode = KAgent.DEMO

    def introduce(self):
        intro = '\nMy name is Jesse Pinkman, yo.\n'+\
            '"I am a game-playing agent made by Aidan Bartlett (aidanb04)\n'+\
            'I\'m definitely gonna win, bitch!\n'
        if self.twin: intro += "This is crazy! Am I like a clone or something? I think I'm like my own evil twin, yo.\n"
        return intro

    # Receive and acknowledge information about the game from
    # the game master:
    def prepare(
        self,
        game_type,
        what_side_to_play,
        opponent_nickname,
        expected_time_per_move = 0.1, # Time limits can be
                                      # changed mid-game by the game master.

        utterances_matter=True):      # If False, just return 'OK' for each utterance,
                                      # or something simple and quick to compute
                                      # and do not import any LLM or special APIs.
                                      # During the tournament, this will be False..
        if utterances_matter:
            self.utterances_matter = True
        else:
            self.utterances_matter = False
           # Optionally, import your LLM API here.
           # Then you can use it to help create utterances.
        self.game_type = game_type
        self.what_side_to_play = what_side_to_play
        self.opponent_nickname = opponent_nickname
        self.expected_time_per_move = expected_time_per_move

        self.zobrist_table = {}
        self.transposition_table = {}

       # Write code to save the relevant information in variables
       # local to this instance of the agent.
       # Game-type info can be in global variables.
    #    print("Change this to return 'OK' when ready to test the method.")
        for row in range(game_type.n):
            for col in range(game_type.m):
                for piece in ['X', 'O']:  # ignore blocked '-'
                    self.zobrist_table[(row, col, piece)] = random.getrandbits(64)

        return "OK"

    def compute_zobrist_hash(self, state):
        h = 0
        for row in range(self.game_type.n):
            for col in range(self.game_type.m):
                piece = state.board[row][col]
                if piece in ('X', 'O'):
                    h ^= self.zobrist_table[(row, col, piece)]
        return h

    def update_zobrist_hash(self, current_hash, move, piece):
        return current_hash ^ self.zobrist_table[(move[0], move[1], piece)]

    # The core of your agent's ability should be implemented here:             
    def make_move(self, current_state, current_remark, time_limit=1000,
                  use_alpha_beta=False,
                  use_zobrist_hashing=False, max_ply=3,
                  special_static_eval_fn=None, 
                  return_game_stats=True):
        print("make_move has been called")
        self.alpha_beta_cutoffs_this_turn = 0
        self.num_static_evals_this_turn = 0
        self.zobrist_table_num_entries_this_turn = 0
        self.zobrist_table_num_hits_this_turn = 0

        if use_zobrist_hashing:
            current_hash = self.compute_zobrist_hash(current_state)
        else:
            current_hash = None
        minimax_result = self.minimax(current_state, pruning=use_alpha_beta, depth_remaining=max_ply,
                                      use_zobrist_hashing=use_zobrist_hashing, current_hash=current_hash)
        new_move = minimax_result[1]

        if self.utterances_matter:
            if current_state.whose_move == 'X':
                if minimax_result[0] > 0:
                    remark = 'O is going down'
                else:
                    remark = 'Oh man, oh man, I dont know what to do, yo!'
            else:
                if minimax_result[0] < 0:
                    remark = 'X is going down'
                else:
                    remark = 'This is bad, man!'
        else:
            remark = 'OK'

        next_state = State(old=current_state)
        next_state.board[new_move[0]][new_move[1]] = next_state.whose_move
        next_state.change_turn()

        self.alpha_beta_cutoffs += self.alpha_beta_cutoffs_this_turn
        self.num_static_evals += self.num_static_evals_this_turn
        self.zobrist_table_num_entries += self.zobrist_table_num_entries_this_turn
        self.zobrist_table_num_hits += self.zobrist_table_num_hits_this_turn

        turn_stats = [self.alpha_beta_cutoffs_this_turn,
                        self.num_static_evals_this_turn,
                        self.zobrist_table_num_entries_this_turn,
                        self.zobrist_table_num_hits_this_turn]
        if return_game_stats:
            game_stats = [self.alpha_beta_cutoffs,
                            self.num_static_evals,
                            self.zobrist_table_num_entries,
                            self.zobrist_table_num_hits]
        # if we want to do evaluations end-of-game
            stats = turn_stats + game_stats
        else:
            stats = turn_stats


        print("Returning from make_move")
        return [[new_move, next_state] + stats, remark]

    # The main adversarial search function:
    def minimax(self,
            state,
            depth_remaining,
            pruning=False,
            alpha=None,
            beta=None, 
            use_zobrist_hashing=False,
            current_hash=None):

        if use_zobrist_hashing and current_hash is not None:
            # Combine current board hash with whose turn it is
            player_turn = hash(state.whose_move) & ((1 << 64) - 1)
            current_player_full = current_hash ^ player_turn
        else:
            current_player_full = None

        if use_zobrist_hashing and current_hash is not None:
            player_turn_hash = hash(state.whose_move) & ((1 << 64) - 1)
            current_player_full = current_hash ^ player_turn_hash
        else:
            current_player_full = None

        if use_zobrist_hashing and current_player_full is not None:
            if current_player_full in self.transposition_table:
                self.zobrist_table_num_hits_this_turn += 1
                return self.transposition_table[current_player_full]

        if depth_remaining == 0:
            if use_zobrist_hashing and current_player_full is not None and current_player_full in self.transposition_table:
                self.zobrist_table_num_hits_this_turn += 1
                return self.transposition_table[current_player_full]
            score = self.static_eval(state, self.game_type)
            self.num_static_evals_this_turn += 1

            if use_zobrist_hashing and current_player_full is not None:
                self.transposition_table[current_player_full] = [score, None]
                self.zobrist_table_num_entries_this_turn += 1
            return [score, None]

        if state.whose_move == 'X':
            best_x_score_move = [-9999999, None]
            possible_moves = False
            for row in range(len(state.board)):
                for col in range(len(state.board[0])):
                    move = (row, col)
                    if state.board[row][col] not in ('X', '-', 'O'):
                        possible_moves = True
                        next_state = State(old=state)
                        next_state.board[row][col] = next_state.whose_move
                        next_state.change_turn()

                        if use_zobrist_hashing and current_player_full is not None:
                            board_hash_after_move = self.update_zobrist_hash(current_player_full, move, state.whose_move)

                            next_player_turn = hash(next_state.whose_move) & ((1 << 64) - 1)
                            next_hash = board_hash_after_move ^ next_player_turn
                        else:
                            next_hash = None

                        next_branch_score = self.minimax(next_state, depth_remaining-1, pruning, alpha, beta, 
                                                        use_zobrist_hashing, current_hash=next_hash)
                        child_score, _, = next_branch_score
                        if child_score > best_x_score_move[0]:
                            best_x_score_move = [child_score, move]
                        if pruning:
                            if alpha is None or best_x_score_move[0] > alpha:
                                alpha = best_x_score_move[0]
                            if beta is not None and beta <= alpha:
                                self.alpha_beta_cutoffs_this_turn += 1
                                break
                if pruning and alpha is not None and beta is not None and beta <= alpha:
                    self.alpha_beta_cutoffs_this_turn += 1
                    break
            if not possible_moves:
                score = self.static_eval(state, self.game_type)
                self.num_static_evals_this_turn += 1
                if use_zobrist_hashing and current_player_full is not None:
                    if current_player_full not in self.transposition_table:
                        self.transposition_table[current_player_full] = [score, None]
                        self.zobrist_table_num_entries_this_turn += 1
                return [score, None]
            if use_zobrist_hashing and current_player_full is not None:
                if current_player_full not in self.transposition_table:
                    self.transposition_table[current_player_full] = best_x_score_move
                    self.zobrist_table_num_entries_this_turn += 1
            return best_x_score_move

        else:
            best_o_score_move = [9999999, None]
            possible_moves = False
            for row in range(len(state.board)):
                for col in range(len(state.board[0])):
                    move = (row, col)
                    if state.board[row][col] not in ('X', '-', 'O'):
                        possible_moves = True
                        next_state = State(old=state)
                        next_state.board[row][col] = next_state.whose_move
                        next_state.change_turn()

                        if use_zobrist_hashing and current_player_full is not None:
                            board_hash_after_move = self.update_zobrist_hash(current_player_full, move, state.whose_move)

                            next_player_turn = hash(next_state.whose_move) & ((1 << 64) - 1)
                            next_hash = board_hash_after_move ^ next_player_turn
                        else:
                            next_hash = None

                        next_branch_score = self.minimax(next_state, depth_remaining-1, pruning, alpha, beta, 
                                                        use_zobrist_hashing, current_hash=next_hash)
                        child_score, _, = next_branch_score
                        if child_score < best_o_score_move[0]:
                            best_o_score_move = [child_score, move]
                        if pruning:
                            if beta is None or best_o_score_move[0] < beta:
                                beta = best_o_score_move[0]
                            if alpha is not None and beta <= alpha:
                                self.alpha_beta_cutoffs_this_turn += 1
                                break
                if pruning and alpha is not None and beta is not None and beta <= alpha:
                    self.alpha_beta_cutoffs_this_turn += 1
                    break

            if not possible_moves:
                score = self.static_eval(state, self.game_type)
                self.num_static_evals_this_turn += 1
                if use_zobrist_hashing and current_player_full is not None:
                    if current_player_full not in self.transposition_table:
                        self.transposition_table[current_player_full] = [score, None]
                        self.zobrist_table_num_entries_this_turn += 1
                return [score, None]
            if use_zobrist_hashing and current_player_full is not None:
                if current_player_full not in self.transposition_table:
                    self.transposition_table[current_player_full] = best_o_score_move
                    self.zobrist_table_num_entries_this_turn += 1
            return best_o_score_move

        # Only the score is required here but other stuff can be returned
        # in the list, after the score, in case you want to pass info
        # back from recursive calls that might be used in your utterances,
        # etc.

    def static_eval(self, state, game_type=None):
        if not game_type:
            game_type = self.game_type
        start_time = time.perf_counter() 
        print('calling static_eval...')
        score = static_eval_scoring(state, k=game_type.k, n=game_type.n, m=game_type.m)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f'score: {score} in {elapsed_time:.4f} secs')
        return score

# OPTIONAL THINGS TO KEEP TRACK OF:

#  WHO_MY_OPPONENT_PLAYS = other(WHO_I_PLAY)
#  MY_PAST_UTTERANCES = []
#  OPPONENT_PAST_UTTERANCES = []
#  UTTERANCE_COUNT = 0
#  REPEAT_COUNT = 0 or a table of these if you are reusing different utterances
