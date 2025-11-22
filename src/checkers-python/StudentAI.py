# from random import randint
from random import choice
from BoardClasses import Move
from BoardClasses import Board
from math import sqrt
from math import log
from copy import deepcopy
# from pickle import load # save/load mcts simulation objects
# from pickle import dump
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

MCTS_num = 1000 # repitions of MCTS per turn (>500)
C = sqrt(2) # exploration factor for UCT (sqrt(2))

class Node():
    def __init__(self, color, parent=None, move=None,
                 wins=0, visits=0):
        self.move = move # Move leading to this node
        self.color = color # 1==B , 2==W -- color of self.move^
        self.wins = wins
        self.visits = visits
        self.parent = parent    # type is Node
        self.unvisited_children = []
        self.children = []      # list of Nodes
    
    def calc_uct(self) -> float:
        if (self.visits == 0): # not fully expanded nodes
            return -1
        if (self.parent == None): # root node
            # (self.parent == None or self.parent.visits == 0)
            return 0
        return (self.wins / self.visits) + (C * sqrt(log(self.parent.visits)/self.visits))
    
    def set_children(self, moves: list[list[Move]]) -> None:
        opposite_color = 1 if self.color == 2 else 2
        for row in moves:
            for col in row:
                self.unvisited_children.append(Node(opposite_color, self, col))
    
    def highest_child(self):
        highest_uct = 0
        res = None
        for child in self.children + self.unvisited_children:
            curr_uct = child.calc_uct()
            if (curr_uct >= highest_uct):
                highest_uct = curr_uct
                res = child
        if (res == None):
            RuntimeError("No moves possible.")
        return res

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.board_copy = None
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2  # 1==B , 2==W, THIS LINE WAS GIVEN

        self.mcts_tree_head = Node(self.opponent[self.color])  # type Node

    def update_head_node(self, move) -> None:
        found = False
        for child in self.mcts_tree_head.children + self.mcts_tree_head.unvisited_children:
            if (child.move == move):
                self.mcts_tree_head = child
                found = True
                break
        if (not found):
            # print("FAAHHHHHH\n")
            self.mcts_tree_head = Node(self.opponent[self.color]) # opponent's color cuz the children of this are gonna be UR moves

    def get_move(self, move):
        # returns a Move
        if len(move) != 0:
            self.board.make_move(move, self.opponent[self.color]) # make ur opponent's move locally on ur Board
            self.update_head_node(move) # update mcts tree
        else: # no move was sent, so that means u go first as black (1)
            self.color = 1 
            self.mcts_tree_head.color = self.opponent[self.color]

        # don't run mcts if there's only 1 move
        moves = self.board.get_all_possible_moves(self.color)
        if (len(moves) == 1 and len(moves[0]) == 1):
            move = moves[0][0]
            self.update_head_node(move) # update tree
            self.board.make_move(move,self.color) # update board
            return move

        # run mcts simulations for current move
        for _ in range(MCTS_num):
            self.mcts()
        self.mcts_tree_head = self.mcts_tree_head.highest_child() # update tree
        move = self.mcts_tree_head.move # RuntimeError if no moves are possible
        self.board.make_move(move,self.color) # update board
        return move

    # ---------------------------------------------------------
    def selection(self) -> Node:
        '''
        returns the Node with the highest UCT value
        '''
        curr_node = self.mcts_tree_head
        res = curr_node
        while (len(curr_node.unvisited_children) == 0 and len(curr_node.children) != 0):
            highest_uct = 0
            res = curr_node.children[0]
            for child in curr_node.children:
                curr_uct = child.calc_uct()
                # if (curr_uct == -1): # nodes that haven't fully been expaned -- update: this is taken care of by 'unvisited_children' attribute
                #     return curr_node
                if (curr_uct > highest_uct):
                    highest_uct = curr_uct
                    res = child
            curr_node = res
            self.board_copy.make_move(curr_node.move, curr_node.color) # update board_copy
        return curr_node

    def expansion(self, node: Node) -> Node: # CHECK THIS -------------------------------
        '''
        node: Node from selection phase
        returns the node that was expanded
        '''
        # adds a new child node for an untried move

        # When the selection phase reaches a leaf node that isn't terminal,
        # the algorithm expands the tree by adding one or more child nodes
        # representing possible actions from that state.

        if (len(node.unvisited_children) == 0):
            if (len(node.children) != 0):
                return choice(node.children)
            # list of Move objects
            moves = self.board_copy.get_all_possible_moves(self.opponent[node.color])
            node.set_children(moves)
        # 'node' was terminal
        if (len(node.unvisited_children) == 0):
            return node
        # random.choice() to select random (unexpanded) node to expand
        res = choice(node.unvisited_children)
        # expanded child, 'res', is no longer unvisited
        node.children.append(res)
        node.unvisited_children.remove(res)
        # update board_copy
        self.board_copy.make_move(res.move, res.color)
        return res

    def simulation(self, node: Node) -> tuple[int, Node]: 
        '''
        node: the expanded node
        returns [-1 (tie) || 1 (black won) || 2 (white won),
                and the terminal node (use for back propagation)]
        '''
        # board = deepcopy(self.board) # -- moved this to be a public attribute, board_copy (we need this for selection and expansion)
        player = node.color
        # play random moves until game ends
        while True:
            # check if game ends + who won, returns is_win
            res = self.board_copy.is_win(player)
                # -1 == tie
                #  0 == no winner yet
                #  1 == black won
                #  2 == white won
            if res != 0:
                return res, node

            # pick random move
            # moves = self.board_copy.get_all_possible_moves(player)
            # if (len(moves) == 0): # terminal
            #     return -1, node # Assume draw if no actions
            # move = choice(choice(moves))
            
            # generate children if necessary
            if (len(node.unvisited_children) == 0 and len(node.children) == 0):
                moves = self.board_copy.get_all_possible_moves(self.opponent[node.color])
                node.set_children(moves)
            # pick random move / update node
            new_node = choice(node.unvisited_children + node.children)
            # change 'unvisited' nodes to 'visited', if applicable
            if (new_node in node.unvisited_children):
                node.children.append(new_node)
                node.unvisited_children.remove(new_node)
            # update board_copy
            self.board_copy.make_move(new_node.move, new_node.color)
            
            node = new_node
            # self.board_copy.make_move(node.move, player)

            # switch players
            player = 1 if player == 2 else 2

    def backpropagation(self, node: Node, won: bool) -> None:
        '''
        Update stats up the tree.
        node = the expanded Node
        won = true if u won, false if u lost
        '''
        while (node.parent != None):
            node.visits += 1
            if (won):
                node.wins += 1
            node = node.parent
        # update parent node
        node.visits += 1
        if (won):
                node.wins += 1

    def mcts(self):
        '''
        plays out one round of mcts
        '''
        self.board_copy = deepcopy(self.board)
        selected_node = self.selection()
        expanded_node = self.expansion(selected_node) # enter non-terminal node
        sim_res, terminal_node = self.simulation(expanded_node)

        if sim_res == -1:
            won = False # consider ties as loss -- let's asian parent this AI
        elif sim_res == self.color: 
            won = True
        else:
            won = False
        self.backpropagation(terminal_node, won)


if __name__ == "__main__":
    col = 7
    row = 7
    p = 2   # num of rows filled with checkers at the start

    # s = StudentAI(col, row, p)
    # head = s.mcts_tree_head
    ## s.mcts()
    # for i in range(10000):
    #     s.mcts()
    # import sys
    # sys.setrecursionlimit(999999999)
    # with open("mcts_data.pkl", 'wb') as file:
    #     dump(head, file)
