import random
import sys
import argparse
from collections import defaultdict

#To play the game in the command line, run python sudoku_final.py --game
#To simply create & see a puzzle solve itself, run python sudoku_final.py without any arguments

### VARIABLES WE WILL USE LATER ON
ROWS = "ABCDEFGHI"
COLS = "123456789"

grid_dict_max = {0: 2, 1: 2, 2: 2, 3: 5, 4: 5, 5: 5, 6: 8, 7: 8, 8: 8} #example: mini grid max for 9th number (index 8) is at index 8
grid_dict_min = {0: 0, 1: 0, 2: 0, 3: 3, 4: 3, 5: 3, 6: 6, 7: 6, 8: 6} #example: mini grid min for 9th number (index 8) is at index 6


SQUARES = [r + c for r  in ROWS for c in COLS]

### PRINTING FUNCTIONS

def print_grid(mygrid):
    """
    print grid mygrid (represented as a string of length 81) in the form of 
    a 9x9 grid     
    """
    final_rep = ""
    idx = 1
    for v in mygrid: 
        final_rep += v + ' '
        if idx != 81 and idx % 27 == 0:
            final_rep += "\n"
            final_rep += "-" * 22
            final_rep += "\n"            
        elif idx % 9 == 0:
            final_rep += "\n"
        elif idx % 3 == 0:
            final_rep += "| "
        idx += 1
    return final_rep

def print_grid_from_vals(poss_vals):
    """
    print grid from dictionary of poss_vals (key:value = square name: possible values for that square)
    """
    final_rep = ""
    idx = 1
    for r in ROWS:
        for c in COLS:
            current = r+c
            if len(poss_vals[current]) == 1:
                final_rep += str(poss_vals[current][0]) + ' '
            else:
                final_rep += '. '
            if idx != 81 and idx % 27 == 0:
                final_rep += "\n"
                final_rep += "-" * 21
                final_rep += "\n"            
            elif idx % 9 == 0:
                final_rep += "\n"
            elif idx % 3 == 0:
                final_rep += "| "
            idx += 1
    return final_rep

def print_guide():
    """
    print a grid guide of A1 to I9 to show where each square name resides
    """
    final_rep = ""
    idx = 1
    for s in SQUARES:
        final_rep += str(s) + ' '
        if idx != 81 and idx % 27 == 0:
            final_rep += "\n"
            final_rep += "-" * 30
            final_rep += "\n"            
        elif idx % 9 == 0:
            final_rep += "\n"
        elif idx % 3 == 0:
            final_rep += "| "
        idx += 1 
    return final_rep

### FUNCTIONS NEEDED TO ASSIGN VALUES

def find_neighbors(target_square):
    """
    return a list of the square names that are in the same minigrid, row and column
    for example, find_neighbors(A1) would return: 
        ['A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1']
    """
    neighbors = []
    row = target_square[0]
    col = target_square[1]
    #add all squares in same row to neighbors
    for c in COLS:
        potential_square = row + c
        if potential_square != target_square and potential_square not in neighbors:
            neighbors.append(potential_square)
    #add all squares in same column to neighbors
    for r in ROWS:
        potential_square = r + col
        if potential_square != target_square and potential_square not in neighbors:
            neighbors.append(potential_square)
    #add all squares in same mini grid to neighbors
    row_idx = ROWS.index(target_square[0])
    col_idx = COLS.index(target_square[1])
    for h in xrange(grid_dict_min[row_idx], grid_dict_max[row_idx] + 1):
        for s in xrange(grid_dict_min[col_idx], grid_dict_max[col_idx] + 1):
            potential_square = ROWS[h] + COLS[s]
            if potential_square != target_square and potential_square not in neighbors:
                neighbors.append(potential_square)
    return neighbors

def assign_value(poss_values, target_square, myguess):
    """
    poss_values is a value dictionary of all squares & their current valid possible values
    This method attempts to assign a value, myguess, to the target_square, remove all other possibilities from poss_values[target_square] 
    except myguess. Then return updated poss_values. If not a valid guess, return False.
    """
    #if the guessed value is not in possible values for the target square, return false
    if myguess not in poss_values[target_square]:
        return False
    elif poss_values[target_square] == myguess:
        return poss_values
    else:
        # try to remove all other values except myguess from possible values for target square; if not possible, return False
        values_to_remove = poss_values[target_square].replace(myguess, '')
        for v in values_to_remove:
            if not remove_poss(poss_values, target_square, v):
                return False
    return poss_values


def remove_poss(poss_values, target_square, unwanted):
    """
    Remove unwanted value from poss_values (the value dictionary of possible values for each square) for the target_square. 
    If removing this value would result in only one possible remaining value for the target square, itterate through
    the target square's neighbors to see if it is possible to remove that remaining value from each neighbor's possible values.
    Then iterate through each of target square's neighbors to see if any neighbors have only one possible value left, and 
    if so, try to assign that last value to that square. If this is not successful, return false.
    If the function is able to go through all steps successfully, return value dictionary (poss_values). Otherwise, it would
    have returned false already if one of the earlier steps had failed.
    """
    #if the guessed value has already been removed from possible values for the target square, return poss_values
    if unwanted not in poss_values[target_square]:
        return poss_values
    elif poss_values[target_square] == unwanted:
        return False #cannot remove this value; it is the only remaining possible value for this square
    #remove myguess from poss_values for target square
    poss_values[target_square] = poss_values[target_square].replace(unwanted, '')
    if len(poss_values[target_square]) == 1:
        # if removing myguess from poss_values for target_square leads to just one possible value, guess2, 
        # check if it's possible to eliminate guess2 from all neighboring squares because this is equivalent to
        # assigning guess2 value for target_square
        guess2 = poss_values[target_square]
        for n in find_neighbors(target_square):
            if not remove_poss(poss_values, n, guess2):
                return False # not a valid move because we cannot remove guess2 from neighboring squares
    #now check neighbors to see if they only have one possible value left
    for n in find_neighbors(target_square):
        if len(poss_values[n]) == 1:
            the_value = poss_values[n]
            # if a neighboring square n is left with only one possible value, try assigning that value to square n 
            # and return False if not possible
            if not assign_value(poss_values, n, the_value):
                return False
    return poss_values


### CREATE INITIAL PUZZLE

def create_puzzle():
    """
    Create initial puzzle with at least 17 spaces filled in. Returns a tuple. First item in tuple is
    grid represented as a string with '.' indicating an empty space, going from A1, A2, A3...I8, I9. 
    Second item is a dictionary of possible values for each square (key is square name, e.g. "A1" 
    and value is possible values for that square represented as a string of digits, e.g. '123456789'
    """
    #initialize value_dict with all possible values '123456789' for all squares
    value_dict = dict((s, COLS) for s in SQUARES)
    assigned = []
    digits_to_assign = '123456789'
    final_rep = ""
    #Sudoku puzzle needs at least 17 squares filled in (OK to have > 17 squares filled in) to have a unique solution
    #also we want to assign all numbers 1-9 to lower the possibility of multiple solutions
    while len(assigned) < 17 and len(digits_to_assign) > 0: 
        target_square = random.choice(SQUARES)
        if target_square not in assigned:
            value_to_assign = random.choice(value_dict[target_square])
            if assign_value(value_dict, target_square, value_to_assign):
                assigned.append(target_square)
                digits_to_assign.replace(value_to_assign, '')
    for square in SQUARES:
        if square in assigned:
            final_rep += value_dict[square]
        else:
            final_rep += '.'                    
    return (final_rep, generate_value_dict(final_rep))


def generate_value_dict(mygrid):
    """
    Given the initial grid, mygrid, in the form of an 81-character string, with empty spaces represented with '.',
    return a dictionary in the form of Key: square name. Value: possible valid values for that square.
    """
    value_dict = dict()
    #each square starts off with all possible values 1 through 9
    for s in SQUARES:
        value_dict[s] = ''.join(str(x) for x in range(1, 10))
    for i in range(len(mygrid)):
        #if square has been assigned, remove that assigned value from neighboring squares' possible values
        if mygrid[i] != '.':
            value_dict[SQUARES[i]] = mygrid[i]
            for n in find_neighbors(SQUARES[i]):
                value_dict[n] = value_dict[n].replace(mygrid[i], '')
    return value_dict

def generate_grid(poss_values):
    mygrid = ''
    for s in SQUARES:
        if len(poss_values[s]) == 1:
            mygrid += poss_values[s]
        else:
            mygrid += '.'
    return mygrid
#A1 is idx 0
#B1 is idx 9
#C1 is idx 18


### SOLVE PUZZLE

def solve_puzzle(orig_grid, myvals):
    """
    Argument: grid, mygrid, in the form of an 81-character string, with empty spaces represented with '.'
    Generate a list of values based on the grid and iterate through the squares to find the square with fewest poss_values. 
    Try assigning each value; if it returns False, move on to next value. Continue until only one possible value 
    is left for each square. Return the grid as a string.
    """
    if myvals is False:
        return solve_puzzle(orig_grid, generate_value_dict(orig_grid))
    if max(len(myvals[s]) for s in SQUARES) == 1:
        return myvals
    #make a copy of myvals (dictionary of possible values for each square) before we start modifying it
    vals_copy = myvals.copy()
    the_min = 9
    min_squares = []
    for k, v in vals_copy.items():
        # check if square has been filled in; if it has, it is not a valid choice
        # we want to find the unassigned square with the minimum number of possible values
        if len(v) != 1:
            if len(v) == the_min:
                min_squares.append(k)
            elif len(v) < the_min:
                min_squares = [k]
                the_min = len(v)
    # if length of min_squares is greater than one, choose one randomly
    if len(min_squares) > 1:
        selection = random.choice(min_squares)
    else:
        selection = min_squares[0]
    vals_temp = vals_copy.copy()
    # randomly choose a value, value_is, to assign to the selected square, selection
    value_is = random.choice(vals_temp[selection])
    #before trying to assign values, save a copy of current value_dict
    # if we are unsuccessful in assigning value_is to selection, remove it as a possibility from selection's current possible values
    if not assign_value(vals_copy, selection, value_is):
        remove_poss(vals_temp, selection, value_is)
        #call solve_puzzl() again using the vals_temp dictionary, not the vals_copy one we unsuccessfully modified.
        return solve_puzzle(orig_grid, vals_temp)
    else:
        # if we are successful at assigning value_is to selection square, call solve_puzzle() again using the updated value dict, vals_copy 
        return solve_puzzle(orig_grid, vals_copy)

### FUNCTIONS FOR GAME PLAY  

def fill_in_random(current_grid):
    """Input: current grid as a string. Return a random square that has not already been filled in"""
    random_square = random.choice(SQUARES)
    if current_grid[SQUARES.index(random_square)] == '.':
        return random_square
    else:
        return fill_in_random(current_grid)

def find_num_assigned(current_grid):
    num_assigned = 0
    for i in range(len(current_grid)):
        if current_grid[i] != '.':
            num_assigned += 1
    return num_assigned

def play_game():
    print "Welcome to your Sudoku game! Here is your guide: "
    print print_guide() 
    new_puzzle = create_puzzle()
    new_puzzle_dict = new_puzzle[1]  
    print "\n"
    print "And here is your puzzle: "
    print print_grid(new_puzzle[0])
    original_squares = []
    for s in range(len(new_puzzle)):
        if new_puzzle[s] != '.':
            original_squares.append(SQUARES[s])
    solved_dict = solve_puzzle(new_puzzle[0], new_puzzle_dict)
    in_play = True
    while in_play:
        response = raw_input('please enter a square, and the value you\'d like to fill in that square, separated by a comma (e.g. A1,5 with no space between), or "HELP" in all caps, for help, or "GUIDE" in all caps to see the grid guide, or "SOLVE" to quit and see solved puzzle ')
        current_dict = generate_value_dict(new_puzzle[0])
        if response == "HELP":
            #choose a random square to fill, called fill_square
            fill_square = fill_in_random(new_puzzle[0])
            #fill in the square that was randomly chosen, by consulting the solved_dict
            new_puzzle_dict[fill_square] = solved_dict[fill_square]
            print "We filled in square ", fill_square, " for you. Here is the updated sudoku grid: \n"
            print print_grid_from_vals(new_puzzle_dict)
        elif response == "GUIDE":
            print print_guide()
        elif response == "SOLVE":
            print print_grid_from_vals(solved_dict)
            break
        else:
            try:
                next_square, next_value = response.split(',')
                next_square.strip()
                next_value.strip()
            except ValueError:
                print "please try again"
                break
            print "you've selected ", next_square, "as the square you'd like to fill in."
            print "checking if value is valid for that square..."
            if next_square in original_squares:
                print "please enter an empty square that is not part of the original puzzle "
            try: 
                if solved_dict[next_square] != next_value:
                    print "this is not the correct value for that square. Enter 'HELP' if you need a hint. "
                else:
                    print "Awesome possum. Your guess of", next_value, "in square ", next_square, " was successful. Here is the updated sudoku grid: \n"
                    new_puzzle_dict[next_square] = next_value
                    print print_grid_from_vals(new_puzzle_dict)
                    print "and here is your guide to square names: \n"
                    print print_guide() 
            except KeyError:
                break
            if max(len(new_puzzle_dict[s]) for s in SQUARES) == 1:
                print "Congratulations! Puzzle is solved!"
                in_play = False
    return new_puzzle_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A simple Sudoku game/solver')
    parser.add_argument("--game", required=False, help="If you want to play, add --game argument", action="store_true")
    args = parser.parse_args()
    if args.game:
        play_game()
    else:
        mygrid = create_puzzle()
        print "We generated this random Sudoku puzzle:"
        print print_grid_from_vals(mygrid[1])
        solved = solve_puzzle(mygrid[0], mygrid[1])
        print "Puzzle solution:"
        print print_grid_from_vals(solved)


