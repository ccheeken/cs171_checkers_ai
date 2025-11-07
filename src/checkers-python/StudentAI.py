from random import randint
from random import choice
from BoardClasses import Move
from BoardClasses import Board
from math import sqrt
from math import log
from copy import deepcopy
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

C = 1 # exploration factor for UCT

class Node():
    def __init__(self, parent=None, move=None):
        self.move = None # Move leading to this node
        self.wins = 0
        self.visits = 0
        self.parent = parent # type is Node
        self.children = []   # list of Nodes
    
    def calc_uct(self) -> float:
        if (self.parent == None):
            return 0
        return (self.wins / self.visits) + (C * sqrt(log(self.parent.visits)/self.visits))
    
    def set_children(self, moves: list[Move]) -> None:
        for move in moves:
            self.children.append(Node(self, move))

class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2  # 1==B , 2==W

        self.mcts_tree_head = Node()  # type Node

    def get_move(self, move):
        # returns a Move
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1

        '''
        moves = self.board.get_all_possible_moves(self.color)
        index = randint(0,len(moves)-1)
        inner_index =  randint(0,len(moves[index])-1)
        move = moves[index][inner_index]
        self.board.make_move(move,self.color)
        return move
        '''
    # ---------------------------------------------------------

    def selection(self) -> Node:
        '''
        returns the Node with the highest UCT value
        '''
        curr_node = self.mcts_tree_head
        while (curr_node.children != []):
            highest_uct = 0
            res = curr_node.children[0]
            for child in curr_node.children:
                curr_uct = child.calc_uct()
                if (curr_uct > highest_uct):
                    highest_uct = curr_uct
                    res = child
            curr_node = res
        return res

    def expansion(self, node: Node) -> Node:
        '''
        node: **selected** Node from selection phase
            - assumes node isn't terminal
        returns the node that was expanded
        '''
        # adds a new child node for an untried move

        # When the selection phase reaches a leaf node that isn't terminal,
        # the algorithm expands the tree by adding one or more child nodes
        # representing possible actions from that state.

        # list of Move objects
        moves = self.board.get_all_possible_moves(self.color)
        node.set_children(moves)
        # random.choice() to select random (unexpanded) node to expand
        return choice(node.children)

    def simulation(self) -> int:
        '''
        returns -1 (tie), 1 (black won), 2 (white won)
        '''
        board = deepcopy(self.board)
        player = self.color
        # play random moves until game ends
        while True:
            # check if game ends + who won, returns is_win
            res = board.is_win(player)
            if res != 0:
                return res

            # pick random move
            moves = board.get_all_possible_moves(player)
            move = choice(moves)
            # makes move 
            board.make_move(move,player)

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

    def mcts(self):
        '''
        plays out one round of mcts
        '''
        selected_node = self.selection()
        self.board.is_win(self.color)
            # -1 == tie
            #  0 == no winner yet
            #  1 == black won
            #  2 == white won
        expanded_node = self.expansion(selected_node) # enter non-terminal node
        sim_res = self.simulation()
        self.backpropagation(expanded_node, sim_res)


if __name__ == "__main__":
    pass
