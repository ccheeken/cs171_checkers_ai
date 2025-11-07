# from random import randint
from random import choice
from BoardClasses import Move
from BoardClasses import Board
from math import sqrt
from math import log
from copy import deepcopy
from pickle import load # save/load mcts simulation objects
from pickle import dump
#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.

MCTS_num = 1000 # repitions of MCTS per turn (>500)
C = 1.414 # exploration factor for UCT (sqrt(2))

class Node():
    def __init__(self, parent=None, move=None,
                 wins=0, visits=0):
        self.move = move # Move leading to this node
        self.wins = wins
        self.visits = visits
        self.parent = parent    # type is Node
        self.children = []      # list of Nodes
    
    # def __str__(self) -> str:
    #     children = '['
    #     for child in self.children:
    #         children += child.__str__()
    #     children += ']'
    #     res = "Node(" + "PARENT" + ", " + str(self.move) + ", " + \
    #                 str(self.wins) + ", " + str(self.visits) + ", " + children + ")\n"
    #     return res
    
    def calc_uct(self) -> float:
        if (self.visits == 0): # not fully expanded nodes
            return -1
        if (self.parent == None): # root node
            # (self.parent == None or self.parent.visits == 0)
            return 0
        return (self.wins / self.visits) + (C * sqrt(log(self.parent.visits)/self.visits))
    
    def set_children(self, moves: list[list[Move]]) -> None:
        for row in moves:
            for col in row:
                self.children.append(Node(self, col))
    
    def highest_child(self):
        highest_uct = 0
        res = None
        for child in self.children:
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
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2  # 1==B , 2==W

        self.mcts_tree_head = Node()  # type Node

    def update_head_node(self, move) -> None:
        found = False
        for child in self.mcts_tree_head.children:
            if (child.move == move):
                self.mcts_tree_head = child
                found = True
                break
        if (not found):
            self.mcts_tree_head = Node()

    def get_move(self, move):
        # returns a Move
        if len(move) != 0:
            self.board.make_move(move,self.opponent[self.color])
            self.update_head_node(move) # update mcts tree
        else:
            self.color = 1

        #TODO: don't run mcts if there's only 1 move
        # run mcts simulations for current move
        for _ in range(MCTS_num):
            self.mcts()
        self.mcts_tree_head = self.mcts_tree_head.highest_child()
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
        while (curr_node.children != []):
            highest_uct = 0
            res = curr_node.children[0]
            for child in curr_node.children:
                curr_uct = child.calc_uct()
                if (curr_uct == -1): # nodes that haven't fully been expaned
                    return curr_node
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

        if (node.children == []):
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
                # -1 == tie
                #  0 == no winner yet
                #  1 == black won
                #  2 == white won
            if res != 0:
                return res

            # pick random move
            moves = board.get_all_possible_moves(player)
            if (moves == []):
                return res
            move = choice(choice(moves))
            board.make_move(move, player)

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
        selected_node = self.selection()
        expanded_node = self.expansion(selected_node) # enter non-terminal node
        sim_res = self.simulation()

        if sim_res == -1:
            won = False # consider ties as loss -- let's asian parent this AI
        elif sim_res == self.color: 
            won = True
        else:
            won = False
        self.backpropagation(expanded_node, won)


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
