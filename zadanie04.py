import sys
import re

class Grammar:
    def __init__(self, grammar):
        self.grammar = grammar
        self.grammar, self.start_non_terminal = self.parse_grammar()

        self.nt = self.fill_nt()
        self.grammar = self.remove_non_nt_from_grammar()

        self.vd = self.fill_vd()
        self.grammar = self.remove_non_vd_from_grammar()

        # self.save_grammar()

    def parse_grammar(self):
        temp_grammar = []
        parsed_grammar = []

        for line in self.grammar:
            line = line.replace("\n", "")
            line = line.replace(" ", "")
            line = re.split('::=|\\|', line)
            start_non_terminals = [line[0] for line in temp_grammar]
            line_start = line[0]

            if line_start not in start_non_terminals:
                temp_grammar.append(line)
            else:
                for already_line in temp_grammar:
                    if already_line[0] == line_start:
                        already_line += line[1:]
        
        for line in temp_grammar:
            parsed_line = []     
            for rule in line:
                parsed_rule = self.parse_rule(rule)
                parsed_line.append(parsed_rule)
            parsed_grammar.append(parsed_line)

        start_nonterminal = parsed_grammar[0][0][0]
        return parsed_grammar, start_nonterminal
    
    def parse_rule(self, rule):
        new_rule = []
        symbol_indexes = []

        for i in range(len(rule)):
            if rule[i] == '<' or rule[i] == '>' or rule[i] == '"':
                symbol_indexes.append(i)

        for i in range(0, len(symbol_indexes), 2):
            start = symbol_indexes[i]
            end = symbol_indexes[i+1] + 1
            symbol = rule[start:end]
            new_rule.append(symbol)

        return new_rule  

    def fill_nt(self):
        nt = set()
        appended = True

        for line in self.grammar:
            for rule in line[1:]:
                for symbol in rule:
                    if len(rule) == 1 and self.is_t(symbol):
                        nt.add(line[0][0])
    
        
        while appended:
            appended = False
            for line in self.grammar:
                for rule in line[1:]:
                    valid_rule = True
                    
                    for symbol in rule:
                        if self.is_non_t(symbol):
                            valid_rule = valid_rule and symbol in nt
                    
                    if valid_rule and line[0][0] not in nt:
                        nt.add(line[0][0])
                        appended = True

        return nt
    
    def remove_non_nt_from_grammar(self):
        new_grammar = []
        all_terminals = [line[0][0] for line in self.grammar]
        terminals_to_remove = [terminal for terminal in all_terminals if terminal not in self.nt]
    
        for line in self.grammar:
            for rule in line[1:]:
                for terminal_to_remove in terminals_to_remove:
                    if terminal_to_remove in rule:
                        line.remove(rule)
                        break

            if line[0][0] not in terminals_to_remove:
                new_grammar.append(line)

        return new_grammar
    
    def fill_vd(self):
        vd = set()
        appended = True

        if len(self.grammar) >= 1:
            vd.add(self.grammar[0][0][0])
 
        while appended:
            appended = False
            for line in self.grammar:
                if line[0][0] in vd:
                    for rule in line[1:]:
                        for symbol in rule:
                            if symbol not in vd:
                                vd.add(symbol)
                                appended = True
                                

        return vd

    def remove_non_vd_from_grammar(self):
        new_grammar = []

        if self.start_non_terminal not in self.vd:
            return new_grammar
        
        for line in self.grammar:
            if line[0][0] in self.vd:
                new_grammar.append(line)

        return new_grammar                  

    def save_grammar(self):
        if self.grammar == []:
            with open(sys.argv[2], "w") as f:
                f.write("PRAZDNY JAZYK")
            return
        
        with open(sys.argv[2], "w") as f:
            for i in range(len(self.grammar)):
                for j in range(len(self.grammar[i])):
                    rule = ''.join(self.grammar[i][j])
                    if j == 0:
                        f.write(f"{rule} ::= ")
                    elif j == len(self.grammar[i]) - 1:
                        f.write(f"{rule}\n")
                    else:
                        f.write(f"{rule} | ")

    def is_t(self, symbol):
        return '"' in symbol
    
    def is_non_t(self, symbol):
        return '>' in symbol
        
text_input = open(sys.argv[1], "r")
text_input = [line for line in text_input.readlines()]
grammar = Grammar(text_input)