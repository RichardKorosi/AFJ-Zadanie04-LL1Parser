import sys
import re

class Grammar:
    def __init__(self, grammar, texts):
        self.grammar = grammar
        self.texts = texts
        self.firsts = {}
        self.follows = {}
        self.predict = {}
        self.reduce_table = {}

        # Reduce grammar
        self.grammar, self.start_non_terminal = self.parse_grammar()

        self.nt = self.fill_nt()
        self.grammar = self.remove_non_nt_from_grammar()

        self.vd = self.fill_vd()
        self.grammar = self.remove_non_vd_from_grammar()

        # Firsts  
        self.init_first()
        self.terminals_first()
        self.epsilon_first()
        self.loop_first()
        
        # Follow
        self.init_follow()
        self.loop_follow()

        # Predict
        self.init_predict()
        self.loop_predict()

        # Reduce table
        self.terminals = set()
        self.non_terminals = set()
        self.init_reduce_table()
        self.loop_reduce_table()

        # Check if LL(1) and find derivations
        if self.check_if_ll1():
            self.parse_texts()
            self.find_derivations()

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

    def is_t(self, symbol):
        return '"' in symbol
    
    def is_non_t(self, symbol):
        return '>' in symbol

    def init_first(self):
        for line in self.grammar:
            self.firsts[line[0][0]] = set()
    
    def terminals_first(self):
        for line in self.grammar:
            for rule in line[1:]:
                if self.is_t(rule[0]) and rule[0] != '""':
                    self.firsts[line[0][0]].add(rule[0])

    def epsilon_first(self):
        n_epsilon = []
        appended = True

        for line in self.grammar:
            for rule in line[1:]:
                if rule == ['""']:
                    n_epsilon.append(line[0][0])

        
        while appended:
            appended = False
            for line in self.grammar:
                if line[0][0] not in n_epsilon:
                    for rule in line[1:]:
                        valid_rule = True

                        for symbol in rule:
                            if self.is_non_t(symbol):
                                valid_rule = valid_rule and symbol in n_epsilon
                            if self.is_t(symbol) and symbol != '""':
                                valid_rule = False

                        if valid_rule:
                            n_epsilon.append(line[0][0])
                            appended = True
        
        for valid_nt in n_epsilon:
            self.firsts[valid_nt].add('""')
                        
    def loop_first(self):
        appended = True

        while appended:
            appended = False
            for line in self.grammar:
                curr = line[0][0]
                for rule in line[1:]: 
                    for symbol in rule:      
                        if self.is_t(symbol):
                            if symbol != '""' and symbol not in self.firsts[curr]:
                                self.firsts[curr].add(symbol)
                                appended = True
                            break

                        if self.is_non_t(symbol):
                            had_epsilon = '""' in self.firsts[curr]
                            len_before = len(self.firsts[curr])
                            self.firsts[curr] = self.firsts[curr].union(self.firsts[symbol])
                            
                            if not had_epsilon and '""' in self.firsts[curr]:
                                self.firsts[curr].remove('""')

                            len_after = len(self.firsts[curr])
                            
                            if len_before != len_after:
                                appended = True
                            
                            if '""' not in self.firsts[symbol]:
                                break
    
    def init_follow(self):
        start = True
        for line in self.grammar:
            self.follows[line[0][0]] = set()
            if start:
                self.follows[line[0][0]].add('""')
                start = False

    def loop_follow(self):
        appended = True

        while appended:
            appended = False
            for line in self.grammar:
                for rule in line[1:]:
                    for i in range(len(rule)):
                        symbol = rule[i]
                        if self.is_non_t(symbol):
                            iSmb = 1
                            while True:
                                next_symbol = rule[i+iSmb] if i+iSmb < len(rule) else None
                                len_before = len(self.follows[symbol])

                                if next_symbol == None or next_symbol == '""':
                                    self.follows[symbol] = self.follows[symbol].union(self.follows[line[0][0]])
                                    break

                                elif self.is_t(next_symbol) and next_symbol != '""':
                                    self.follows[symbol].add(next_symbol)
                                    break

                                elif self.is_non_t(next_symbol):
                                    had_epsilon = '""' in self.follows[symbol]
                                    self.follows[symbol] = self.follows[symbol].union(self.firsts[next_symbol])
                                    if not had_epsilon and '""' in self.follows[symbol]:
                                        self.follows[symbol].remove('""')
                                    if '""' not in self.firsts[next_symbol]:
                                        break
                                    else:
                                        iSmb += 1

                            len_after = len(self.follows[symbol])
                            appended = appended or len_before != len_after                        

    def init_predict(self):
        for line in self.grammar:
            for rule in line[1:]:
                self.predict[(line[0][0], "".join(rule))] = set()

    def loop_predict(self):
        for line in self.grammar:
            for rule in line[1:]:
                for symbol in rule:

                    if self.is_t(symbol) and symbol != '""':
                        self.predict[(line[0][0], "".join(rule))].add(symbol)
                        break

                    elif symbol == '""':
                        self.predict[(line[0][0], "".join(rule))] = self.predict[(line[0][0], "".join(rule))].union(self.follows[line[0][0]])
                        # if '""' in self.predict[(line[0][0], "".join(rule))]:
                        #     self.predict[(line[0][0], "".join(rule))].remove('""')
                        break

                    elif self.is_non_t(symbol):
                        if '""' in self.firsts[symbol]:
                            had_epsilon = '""' in self.predict[(line[0][0], "".join(rule))]
                            self.predict[(line[0][0], "".join(rule))] = self.predict[(line[0][0], "".join(rule))].union(self.firsts[symbol])
                            if not had_epsilon and '""' in self.predict[(line[0][0], "".join(rule))]:
                                self.predict[(line[0][0], "".join(rule))].remove('""')
                        else:
                            self.predict[(line[0][0], "".join(rule))] = self.predict[(line[0][0], "".join(rule))].union(self.firsts[symbol])
                            # if '""' in self.predict[(line[0][0], "".join(rule))]:
                            #     self.predict[(line[0][0], "".join(rule))].remove('""')
                            break

    def init_reduce_table(self):
        for line in self.grammar:
            for rule in line[1:]:
                for symbol in rule:
                    if self.is_t(symbol):
                        self.terminals.add(symbol)

        for line in self.grammar:
            self.non_terminals.add(line[0][0])

        for non_terminal in self.non_terminals:
            for terminal in self.terminals:
                self.reduce_table[(non_terminal, terminal)] = list()

    def loop_reduce_table(self):
        for row in self.reduce_table:
            non_t = row[0]
            t = row[1]
            for row2 in self.predict:
                if row2[0] == non_t and t in self.predict[row2]:
                    self.reduce_table[row].append(row2)
                    break

    def check_if_ll1(self):
        for row in self.reduce_table:
            if len(self.reduce_table[row]) > 1:
                print("Gramatika NIE je LL(1)-gramatikou.")
                return False
        print("Gramatika je LL(1)-gramatikou.")
        return True
    
    def parse_texts(self):
        new_texts = []
        for line in self.texts[1:]:
            new_line = []
            line = line.replace("\n", "")
            line = re.split(" ", line)
            for symbol in line:
                symbol = '"' + symbol + '"'
                new_line.append(symbol)
            new_texts.append(new_line)
        self.texts = new_texts

    def find_derivations(self):
        for text in self.texts[:]:
            print("*" * 50)
            print("Retazec:", (" ".join(text)).replace('"', ""))
            stack = [self.start_non_terminal]
            result = []
            is_correct = True
            while True:
                if len(stack) == 0 and len(text) == 0:
                    is_correct = True
                    break

                if len(stack) == 0 and len(text) != 0:
                    is_correct = False
                    break

                if len(stack) != 0 and len(text) == 0:
                    is_correct = False
                    break

                if self.is_non_t(stack[0]):
                    try:
                        new = self.reduce_table[(stack[0], text[0])][0][1]
                        result.append(self.reduce_table[(stack[0], text[0])][0])
                        stack = self.parse_rule(new) + stack[1:]

                        if stack[0] == '""':
                            stack = stack[1:]
    
                    except:
                        is_correct = False
                        break
                
                elif self.is_t(stack[0]):
                    if stack[0] == text[0]:
                        stack = stack[1:]
                        text = text[1:]
                    else:
                        is_correct = False
                        break

            if is_correct:
                print("Retazec ma derivaciu.")
                print("Postupnost pravidiel pre lavu derivaciu:")
                for tupl in result:
                    print("".join(tupl[0]), "::=", "".join(tupl[1]))
            else:
                print("Retazec nema derivaciu.")
            

def main():
    grammar_input = open(sys.argv[1], "r")
    texts_input = open(sys.argv[2], "r")
    grammar_input = [line for line in grammar_input.readlines()]
    texts_input = [line for line in texts_input.readlines()]
    grammar = Grammar(grammar_input, texts_input)

if __name__ == "__main__":
    main()