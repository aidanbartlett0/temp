# state1 = \
#        [[' ','O',' ',' '],
#         [' ','X','X',' '],
#         [' ',' ','X',' '],
#         [' ',' ','X',' ']]
# state2 = \
#        [[['O','X'],
#         [' ','X']], 2]

# state3 = \
#        [['O','X','X'],
#         [' ',' ','-'],
#         [' ','-',' ']]
# state5 = \
#        [['O',' ',' '],
#         ['-','X',' ']]
'''
Save the coordinate, value, direction, and current length
'''


def check_direction(found_direction, dir_name):
    opposites = {
        'left': 'right', 'right': 'left',
        'up': 'down', 'down': 'up',
        'up-left': 'down-right', 'down-right': 'up-left',
        'up-right': 'down-left', 'down-left': 'up-right'
    }
    return opposites[found_direction] == dir_name or found_direction == dir_name


def judge_neighbor(grid, start_coord, neighbor_coord, direction, player_lines, empty_links):
    player_opposites = {'X': 'O', 'O': 'X'}

    start_player = grid[start_coord[0]][start_coord[1]]
    neighbor_value = grid[neighbor_coord[0]][neighbor_coord[1]]

    # CASE 1: neighbor has the same symbol → extend existing line or create new line
    if neighbor_value == start_player:
        # Find an existing line that includes start_coord in this direction
        existing_line = None
        for line in player_lines[start_player]:
            if check_direction(line['direction'], direction) and \
                    line['coords'] & {start_coord, neighbor_coord}:  # any overlap
                existing_line = line
                break

        if existing_line:
            # Add the neighbor to this line
            existing_line['coords'].add(neighbor_coord)
            # print(f'Found an existing line to extend between{start_coord} and {neighbor_coord} going {direction}')

        else:
            # Create a new line in this direction
            player_lines[start_player].append({
                'coords': set([start_coord, neighbor_coord]),
                'direction': direction
            })
            # print(f'Creating a len 2 line between{start_coord} and {neighbor_coord} going {direction}')
            for empty_coord in empty_links:
                for player in [start_player]:
                    for line_ref in empty_links[empty_coord][player]:
                        if check_direction(line_ref['direction'], direction) and \
                                (start_coord in line_ref['coords'] or neighbor_coord in line_ref['coords']):
                            line_ref['coords'].add(neighbor_coord)


    # CASE 2: neighbor is empty → associate as potential extension
    elif neighbor_value not in (player_opposites[start_player], '-'):
        if neighbor_coord not in empty_links:
            empty_links[neighbor_coord] = {'X': [], 'O': []}

        # Find all lines of start_player that include start_coord in this direction
        associated_lines = [
            line for line in player_lines[start_player]
            if check_direction(line['direction'], direction) and
            (start_coord in line['coords'] or neighbor_coord in line['coords'])
        ]

        # If no line yet, create a new mini-line
        if not associated_lines:
            new_line = {'coords': set([start_coord]), 'direction': direction}
            player_lines[start_player].append(new_line)
            associated_lines = [new_line]

        # Register this empty neighbor for all relevant lines
        for line in associated_lines:
            if line not in empty_links[neighbor_coord][start_player]:
                empty_links[neighbor_coord][start_player].append(line)

    # CASE 3: blocked or opponent → do nothing
    else:
        return player_lines, empty_links
    return player_lines, empty_links


def judge_lines(grid, player_lines, k, n, m):
    player_opposites = {'X': 'O', 'O': 'X'}
    directions = {
        (-1, -1): 'up-left',
        (-1, 0): 'up',
        (-1, 1): 'up-right',
        (0, -1): 'left',
        (1, 0): 'down',
        (1, -1): 'down-left',
        (0, 1): 'right',
        (1, 1): 'down-right'
    }

    dir_lookup = {v: d for d, v in directions.items()}

    def in_bounds(r, c):
        return 0 <= r < n and 0 <= c < m

    viable_lines = {'X': [], 'O': []}
    unviable_lines = {'X': [], 'O': []}

    for player, lines in player_lines.items():
        for line in lines:
            coords = sorted(list(line['coords']))
            direction = line['direction']
            dr, dc = dir_lookup[direction]

            # Find endpoints — assumes coords are sorted in correct traversal order
            start_r, start_c = coords[0]
            end_r, end_c = coords[-1]

            total_space = len(coords)

            # Extend backward from start
            r, c = start_r - dr, start_c - dc
            while in_bounds(r, c) and grid[r][c] not in (player_opposites[player], '-'):
                total_space += 1
                r -= dr
                c -= dc

            # Extend forward from end
            r, c = end_r + dr, end_c + dc
            while in_bounds(r, c) and grid[r][c] not in (player_opposites[player], '-'):
                total_space += 1
                r += dr
                c += dc

            # Keep the line if it can still potentially reach k length
            if total_space >= k:
                viable_lines[player].append(line)
            else:
                unviable_lines[player].append(line)

    return viable_lines, unviable_lines


def prune_empty_links(empty_links, viable_lines):
    updated_empty_links = {}
    for coord, player_dict in empty_links.items():
        updated_empty_links[coord] = {'X': [], 'O': []}
        for player in ['X', 'O']:
            filtered_lines = [
                line for line in player_dict[player]
                if line in viable_lines[player]
            ]
            updated_empty_links[coord][player] = filtered_lines
    return updated_empty_links


def traverse_grid(grid, k, n, m):
    player_lines = {'X': [], 'O': []}
    empty_links = {}

    directions = {
        (-1, -1): 'up-left',
        (-1, 0): 'up',
        (-1, 1): 'up-right',
        (0, -1): 'left',
        (1, 0): 'down',
        (1, -1): 'down-left',
        (0, 1): 'right',
        (1, 1): 'down-right'
    }

    for i in range(n):
        for j in range(m):
            if grid[i][j] not in ('X', 'O'):
                continue
            for dx, dy in directions.keys():
                new_i, new_j = i + dx, j + dy
                if 0 <= new_i < n and 0 <= new_j < m:
                    player_lines, empty_links = judge_neighbor(grid, (i, j), (new_i, new_j), directions[(dx, dy)], player_lines, empty_links)
                else:  # out of bounds
                    continue
    viable_lines, unviable_lines = judge_lines(grid, player_lines, k, n, m)
    updated_empty_links = prune_empty_links(empty_links, viable_lines)

    # print('viable:', viable_lines)
    # print('unviable:', unviable_lines)
    return viable_lines, updated_empty_links


def static_eval_scoring(state, k, n, m, verbose=False):
    '''
    Each line will add a weight to the players score proportional to the goal k length (*100)

    Each potential line will add a weight to the players score by exsiting_length proportional to the goal k length (*30)

    The empty links reward open spaces that can help the player in some way, but they shouldnt be worth equal or more than actually playing moves, otherwise, the algorithm would just make moves that would benefit the next move, and never actually make the big move. 
    They do however, need to be high enough to influence decision making because if they're too low, then 
    '''
    print(state)
    grid = state.board
    player_lines, empty_links = traverse_grid(grid, k, n, m)

    if verbose:
        print("Player lines:")
    scores = {'X': 0, 'O': 0}
    for player in player_lines:
        if verbose:
            print(player)
        for line in player_lines[player]:
            if verbose:
                print(line)
            length = len(line['coords'])
            if player == 'X' and length == k:
                print('FOUND A WINNER')
                return float('inf')
            if player == 'O' and length == k:
                return -float('inf')

            score = (length / k) * 100
            scores[player] += score

    if verbose:
        print("\nEmpty links:")
    for coord in empty_links:
        if verbose:
            print(coord, empty_links[coord])
        for player in empty_links[coord]:
            if len(empty_links[coord][player]) == 0:
                scores[player] += 0
            else:
                for existing_line in empty_links[coord][player]:
                    length = len(existing_line['coords'])
                    score = (length / k) * 30
                    scores[player] += score
    if verbose:
        print_grid(grid)
    return scores['X'] - scores['O']


def print_grid(grid):
    for i in grid:
        print(i, '\n')


# x = static_eval_scoring(state5, 2, 2, 3, verbose=True)
# print('score:', x)

# x = static_eval_scoring(state1, 4, 4, 4, verbose=True)
# print('score:', x)

# x = static_eval_scoring(state3, 3, 3, 3, verbose=True)
# print('score:', x)


# Need to implement a check if the game is unwinnable or if the game is won by a player