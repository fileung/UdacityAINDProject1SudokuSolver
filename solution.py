
from utils import *
import time


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
diagonal_units = [[], []]

# diagonal top-left -> bottom-right 
for d1 in range (0, len(rows)):
    diagonal_units[0].append(rows[d1]+cols[d1])

# diagonal bottom-left -> top-right 
rows_reversed = list(reversed(rows))
for d2 in range (0, len(rows_reversed)):
    diagonal_units[1].append((rows_reversed[d2]+cols[d2]))

unitlist = unitlist + diagonal_units


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    # TODO: Implement this function!
        
    # 1. get all boxes with 2 possible values
    boxes_2 = [key for key in values.keys() if(len(values[key]) == 2)]
    boxes_2.sort()    
    
    # 2. get all units for each unsolved box with two possible values
    for box_2 in boxes_2:
        box_2_units = units[box_2]
        box_2_value = values[box_2]
        
        # for each unit
        # check if there are two or more unallocated boxes matching the naked twin value
        # if found, remove the value from other boxes in the same unit
        for unit in box_2_units:            
            # check if there is another box match the value, which result a pair of naked twin found
            twins = [box for box in unit if(values[box] == box_2_value)]
                
            # if there are twins found in current unit, then remove twin value from other unallocated boxes
            if(len(twins) >= 2):
                # the unallocated boxes except the twin boxes
                twin_peers = [box for box in unit if(values[box] != box_2_value)]
                
                for pr in twin_peers:
                    # remove twin value one by one from peer. e.g. 47 = remove 4 first, then 7
                    for v in box_2_value:
                        # only remove if twin value is found on peers in the unit
                        if(v in values[pr]):
                            original_value = values[pr] + '' # use copy, not ref
                            values[pr] = values[pr].replace(v, '')
                            
                            # if the change result duplicate digit on another unit, revert to original
                            box_changed_units = units[pr]
                            if is_duplicate_digit_in_units(box_changed_units, values, debug=False) == True:
                                values[pr] = original_value
    
    return values

def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    # TODO: Copy your code from the classroom to complete this function
    
    # get all boxes with only one digit, the solved boxes
    solved_boxes = [box for box in values.keys() if len(values[box]) == 1]
            
    for solved_box in solved_boxes:
        solved_digit = values[solved_box]
        
        # get peers of solved box
        solved_box_peers = peers[solved_box]
        
        # remove solved boxes from peers - unneccessary really
        solved_box_peers = [p for p in solved_box_peers if(len(values[p]) > 1)]
        
        for peer in solved_box_peers:
            if(solved_digit in values[peer]):
                original_value = values[peer]
                values[peer] = values[peer].replace(solved_digit, '')
                
                # if the change result duplicate digit on another unit, revert to original
                peer_units = units[peer]
                if is_duplicate_digit_in_units(peer_units, values) == True:
                    values[peer] = original_value            
    
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    # TODO: Copy your code from the classroom to complete this function
    
    # loop units, the complete rows, cols, 3x3 boxes, and diagonal
    for unit in unitlist:
        # loop 1-9, which is cols
        for d in cols:
            # get the boxes with the next digit d
            # d = 1, 2, 3 etc
            # box = A1, A2, B1 etc
            # each unit have the nine boxes from 1-9 e.g. [A1, A2, A3, A4, A5, A6, A7, A8, A9]
            boxes_with_d = [box for box in unit if d in values[box]]
            
            # if the digit d is only appears inside one of the nine boxes in the current unit
            if(len(boxes_with_d) == 1):
                # then the only choice is to assign that box with the digit d
                box_target = boxes_with_d[0]
                original_value = values[box_target] + '' # +'' to make a copy of the str, not using ref
                values[box_target] = d
              
                # if the changed result duplicate digit on another unit, revert to original
                box_changed_units = units[box_target]
                if is_duplicate_digit_in_units(box_changed_units, values) == True:
                    values[box_target] = original_value
        
    return values

def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    # TODO: Copy your code from the classroom and modify it to complete this function
    
    stalled = False
    
    # while there is still progress
    while not stalled:
        
        # get nunber of solved boxes - before current run
        number_of_1_poss_before = len([key for key in values.keys() if (len(values[key]) == 1)])
        number_of_2_poss_before = len([key for key in values.keys() if (len(values[key]) == 2)])
        number_of_3_poss_before = len([key for key in values.keys() if (len(values[key]) == 3)])
        number_of_4_poss_before = len([key for key in values.keys() if (len(values[key]) == 4)])
        number_of_5_poss_before = len([key for key in values.keys() if (len(values[key]) == 5)])
        number_of_6_poss_before = len([key for key in values.keys() if (len(values[key]) == 6)])
        number_of_7_poss_before = len([key for key in values.keys() if (len(values[key]) == 7)])
        number_of_8_poss_before = len([key for key in values.keys() if (len(values[key]) == 8)])
    
        # solve more boxes with three implemented methods
        
        values_before_eliminate = values.copy()
        values = eliminate(values)
        
        values_before_only_choice = values.copy()
        values = only_choice(values)

        values_before_naked_twins = values.copy()
        values = naked_twins(values)
        
        values_after_three_methods = values.copy()
        
        # get nunber of solved boxes - after current run
        number_of_1_poss_after = len([key for key in values.keys() if (len(values[key]) == 1)])
        number_of_2_poss_after = len([key for key in values.keys() if (len(values[key]) == 2)])
        number_of_3_poss_after = len([key for key in values.keys() if (len(values[key]) == 3)])
        number_of_4_poss_after = len([key for key in values.keys() if (len(values[key]) == 4)])
        number_of_5_poss_after = len([key for key in values.keys() if (len(values[key]) == 5)])
        number_of_6_poss_after = len([key for key in values.keys() if (len(values[key]) == 6)])
        number_of_7_poss_after = len([key for key in values.keys() if (len(values[key]) == 7)])
        number_of_8_poss_after = len([key for key in values.keys() if (len(values[key]) == 8)])
        
        if(number_of_1_poss_before == number_of_1_poss_after
           and number_of_2_poss_before == number_of_2_poss_after
           and number_of_3_poss_before == number_of_3_poss_after
           and number_of_4_poss_before == number_of_4_poss_after
           and number_of_5_poss_before == number_of_5_poss_after
           and number_of_6_poss_before == number_of_6_poss_after
           and number_of_7_poss_before == number_of_7_poss_after
           and number_of_8_poss_before == number_of_8_poss_after):
            stalled = True
        else:
            stalled = False
            
        # sanity check 1 - detect box with zero available values
        if len([key for key in values.keys() if (len(values[key]) == 0)]):
            return False

        # sanity check 2 - make sure the solved boxes in each unit have unique digits
        if is_duplicate_digit_in_units(unitlist, values, debug=False) == True:
            print ('reduce_puzzle > found duplicate digit, but should be already handled in the three functions')
            
            print ('\n---values_before_eliminate---')
            display(values_before_eliminate)
            
            print ('\n---values_before_only_choice---')
            display(values_before_only_choice)
            
            print ('\n---values_before_naked_twins---')
            display(values_before_naked_twins)
            
            print ('\n---values_after_three_methods---')
            display(values_after_three_methods)
            
            return False
    
    return values

def is_duplicate_digit_in_units(units, values, debug=False):
    for u in units:
        solved_digit_concat = ''
        for b in u:
            if (len(values[b]) == 1):
                solved_digit_concat += values[b]
        
            # sort string to asc order - for view only
            solved_digit_concat_sorted = ''.join(sorted(solved_digit_concat))
    
            # check for duplicate digit
            for d in solved_digit_concat_sorted:
                count = solved_digit_concat.count(d)
                if count > 1:
                    if debug:
                        print ('\nduplicate value=', d, '\nfound in unit=', u, '\nvalues=', solved_digit_concat)
                        display(values)
                    return True

    return False # no duplicate digit


import random
def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # TODO: Copy your code from the classroom to complete this function
        
    values = reduce_puzzle(values)

    # if the values is not False by sanity check
    if(values is False):
        return False
        # 3. check if the puzzle already solved by reduce_puzzle, as it is possble for an easy sudoku
    
    solved_boxes = [key for key in values.keys() if (len(values[key]) == 1)]

    if(len(solved_boxes) == len(values.keys())):
        if is_duplicate_digit_in_units(unitlist, values, debug=False) == True:
            print ('***NOT SOLVED***')
            display(values)
            return False
        else:
            print ('***SOLVED***')
            display(values)
            return values
        
    lowest_value_length = 9
    
    for box in boxes:
        value_length = len(values[box])
        if(value_length > 1 and value_length < lowest_value_length):
            lowest_value_length = value_length

    boxes_with_lowest_value_length = [b for b in boxes if(len(values[b]) == lowest_value_length)]

    box_chosen = boxes_with_lowest_value_length[0]
    for next_possible_value in values[box_chosen]:
        #create a new sudoku and assign the value then try to solve it
        sudoku_copy = values.copy()
        original_value = sudoku_copy[box_chosen] + ''
        sudoku_copy[box_chosen] = next_possible_value
                    
        # if the change result duplicate digit on another unit, revert to original
        box_chosen_units = units[box_chosen]
        
        if is_duplicate_digit_in_units(box_chosen_units, sudoku_copy, debug=False) == True:
            sudoku_copy[box_chosen] = original_value            
#            continue
        else:            
            try_solve_sudoku = search(sudoku_copy)
            if(try_solve_sudoku):
                return try_solve_sudoku

        
def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    
    start_time = time.time()
    values = search(values)
    end_time = time.time()
    diff_time = end_time - start_time
    print ('%s seconds' % diff_time)
    
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
