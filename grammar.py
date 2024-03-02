"""
COMS W4705 - Natural Language Processing - Fall 2023
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum, isclose

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)

        # assuming lhs symbols of the rules make up the inventory of nonterminals
        self.inventory = list(set(self.lhs_to_rules.keys()))   
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        for lhs_symbol, rules in self.lhs_to_rules.items():
            # checking each rule corresponds to one of the formats permitted in CNF
            for rule in rules:
                if not self.is_rule_valid(rule):
                    return False
            
            # checking all probabilities for the same lhs symbol sum to 1.0
            prob_sum = fsum([rule[2] for rule in self.lhs_to_rules[lhs_symbol]])
            if not isclose(prob_sum, 1.0):
                return False
        return True 
    
    def is_rule_valid(self, rule):
        if len(rule[1]) == 1:
            return True
        elif len(rule[1]) == 2:
            return (rule[1][0] in self.inventory) and (rule[1][1] in self.inventory)
        else:
            return False


if __name__ == "__main__":
    with open(sys.argv[1],'r') as grammar_file:
        grammar = Pcfg(grammar_file)
    # print(grammar.verify_grammar())
        
