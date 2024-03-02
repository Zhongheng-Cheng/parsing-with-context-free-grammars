"""
COMS W4705 - Natural Language Processing - Fall 2023
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False

        Implementation of the CKY Algorithm
        """
        def find_lhs(symbol_list1, symbol_list2):
            res = []
            for symbol1 in symbol_list1:
                for symbol2 in symbol_list2:
                    res += [rule[0] for rule in self.grammar.rhs_to_rules[(symbol1, symbol2)]]
            return res

        n = len(tokens)
        pi_table = [[[] for _ in range(n + 1)] for _ in range(n + 1)]
        
        # initialization
        for i in range(n):
            pi_table[i][i + 1] = [rule[0] for rule in self.grammar.rhs_to_rules[(tokens[i],)]]
            
        # main loop
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                for k in range(i + 1, j):
                    lhs_symbols = find_lhs(pi_table[i][k], pi_table[k][j])
                    pi_table[i][j] += lhs_symbols
        
        # get result
        if pi_table[0][-1]:
            return True
        return False
    
       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.

        Modification of CKY Algorithm from is_in_language(), and use (and return) specific data structures.
        """

        table= {}
        probs = {}
        n = len(tokens)

        # initialization
        for i in range(n):
            table[(i, i + 1)] = {}
            probs[(i, i + 1)] = {}
            for rule in self.grammar.rhs_to_rules[(tokens[i],)]:
                if (rule[0] not in table[(i, i + 1)]) or \
                    (rule[0] in table[(i, i + 1)] and math.log(rule[2]) > probs[(i, i + 1)][rule[0]]):
                    table[(i, i + 1)][rule[0]] = tokens[i]
                    probs[(i, i + 1)][rule[0]] = math.log(rule[2])

        # main loop
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length
                table[(i, j)] = {}
                probs[(i, j)] = {}
                for k in range(i + 1, j):
                    # maintain the backpointers with highest probability
                    for symbol1 in table[(i, k)]:
                        for symbol2 in table[(k, j)]:
                            for rule in self.grammar.rhs_to_rules[(symbol1, symbol2)]:
                                prob = math.log(rule[2]) + probs[(i, k)][symbol1] + probs[(k, j)][symbol2]
                                if (rule[0] not in table[(i, j)]) or \
                                    (rule[0] in table[(i, j)] and prob > probs[(i, j)][rule[0]]):
                                        table[(i, j)][rule[0]] = ((symbol1, i, k), (symbol2, k, j))
                                        probs[(i, j)][rule[0]] = prob

        # get result
        return table, probs


def get_tree(chart, i, j, nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    if isinstance(chart[(i, j)][nt], str):
        return (nt, chart[(i, j)][nt])
    nt_left, i_left, j_left = chart[(i, j)][nt][0]
    nt_right, i_right, j_right = chart[(i, j)][nt][1]
    return (nt, get_tree(chart, i_left, j_left, nt_left), get_tree(chart, i_right, j_right, nt_right))
 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        # toks =['miami', 'flights','cleveland', 'from', 'to','.']
        # print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
        print(get_tree(table, 0, len(toks), grammar.startsymbol))
        
