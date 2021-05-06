from enum import Enum, auto
import string

class TokenType(Enum):
    Literal = auto()
    TwoOperandOperation = auto()
    SingleOperandOperation = auto()
    LeftParenthesis = auto()
    RightParenthesis = auto()

class Token:
    def __init__(self, token_type, token_value):
        self.type = token_type
        self.value = token_value

    def __str__(self):
        return "Type: " + str(self.type) + " Value: " + self.value

class Tokenizer:
    def __init__(self, regex_string):
        self.regex_string = regex_string
    
    def _is_literal(self, character):
        return character.isalpha() or character.isdigit()

    def _is_operation(self, character):
        return self._is_two_operand_operation(character) or \
            self._is_single_operand_operation(character)

    def _is_two_operand_operation(self, character):
        return character == "|"

    def _is_single_operand_operation(self, character):
        return character in "*+" 

    def _is_left_parenthesis(self, character):
        return character == "("

    def _is_right_parenthesis(self, character):
        return character == ")"

    def _is_range_start(self, character):
        return character == "["

    def _is_range_end(self, character):
        return character == "]"
    
    def _is_range_symbol(self, character):
        return character == "-"

    def _is_range(self, character):
        return character == "="

    def _remove_spaces(self):
        self.regex_string = "".join( self.regex_string.split())

    def _remove_unnecessary_parenthesis(self):
        idx = 1
        while idx < len(self.regex_string):
            if self._is_right_parenthesis(self.regex_string[idx]):
                if self._is_left_parenthesis(self.regex_string[idx - 1]):
                    l = list(self.regex_string)
                    del(l[idx - 1:idx + 1])
                    self.regex_string = "".join(l)
                    idx -= 2
            if self._is_range_end(self.regex_string[idx]):
                if self._is_range_start(self.regex_string[idx - 1]):
                    l = list(self.regex_string)
                    del(l[idx - 1:idx + 1])
                    self.regex_string = "".join(l)
                    idx -= 2
            idx += 1
        
    def _clean_regex_string(self):
        self._remove_spaces()
        self._remove_unnecessary_parenthesis()

    def _is_empty_string(self):
        return not self.regex_string

    def _are_symbols_valid(self):
        # Check that all string characters are valid regex symbols
        valid_symbols = "-[]()*+|"
        for character in self.regex_string:
            if not self._is_literal(character) and character not in valid_symbols:
                return False
        return True

    def _is_there_two_consuctive_operations(self):
        if self._is_operation(self.regex_string[0]):
            return True
        idx = 1
        while idx < len(self.regex_string):
            if self._is_single_operand_operation(self.regex_string[idx]):
                if self._is_operation(self.regex_string[idx - 1]):
                    return True
            if self._is_two_operand_operation(self.regex_string[idx]):    
                if self._is_two_operand_operation(self.regex_string[idx - 1]) or \
                    self._is_left_parenthesis(self.regex_string[idx - 1]):
                    return True
            idx += 1
        return False

    def _are_parenthesis_balanced(self):
        # Check the paranthesis balance
        open_parenthesis = tuple('([')
        close_parenthesis = tuple(')]')
        map = dict(zip(open_parenthesis, close_parenthesis))
        queue = []
        for character in self.regex_string:
            if character in open_parenthesis:
                queue.append(map[character])
            elif character in close_parenthesis:
                if not queue or character != queue.pop():
                    return False
        if queue:
            return False
        return True

    def _validate_regex_string(self):
        return not self._is_empty_string() and \
                self._are_symbols_valid() and \
                not self._is_there_two_consuctive_operations() and \
                self._are_parenthesis_balanced()

    # Add & operator to indicate concatenation
    def _add_concatenation_tokens(self, tokens):
        idx = 1
        while idx < len(tokens):
            if tokens[idx].type == TokenType.Literal or tokens[idx].type == TokenType.LeftParenthesis:
                if tokens[idx - 1].type == TokenType.Literal \
                        or tokens[idx - 1].type == TokenType.RightParenthesis \
                        or tokens[idx - 1].type == TokenType.SingleOperandOperation:
                    tokens.insert(idx, Token(TokenType.TwoOperandOperation, "&"))
                    idx += 1
            idx += 1
        return tokens

    # Reorder single operand operations to be as follows: *a instead of a*
    def _reorder_single_operand_tokens(self, tokens):
        last_left_parenthesis_idx = -1
        queue = []
        for idx in range(len(tokens)):
            if tokens[idx].type == TokenType.LeftParenthesis:
                queue.append(idx)
            elif tokens[idx].type == TokenType.RightParenthesis:
                last_left_parenthesis_idx = queue.pop()
            elif tokens[idx].type == TokenType.SingleOperandOperation:
                if tokens[idx - 1].type == TokenType.RightParenthesis:
                    single_operand_token = tokens.pop(idx)
                    tokens.insert(last_left_parenthesis_idx, single_operand_token)
                else:
                    tokens[idx - 1], tokens[idx] = tokens[idx], tokens[idx - 1]
        return tokens

    def extract_ranges(self):
        ranges = []
        range_buffer = []
        in_range = False
        idx = 0
        while idx < len(self.regex_string):
            if not in_range:  
                if self._is_range_start(self.regex_string[idx]):
                    in_range = True
                    range_buffer.append(self.regex_string[idx])
                    self.regex_string =  self.regex_string[:idx] + self.regex_string[idx+1:]
                    idx -= 1
            else:
                if self._is_range_symbol(self.regex_string[idx]) or self._is_literal(self.regex_string[idx]):
                    range_buffer.append(self.regex_string[idx])
                    self.regex_string =  self.regex_string[:idx] + self.regex_string[idx+1:]
                    idx -= 1
                elif self._is_range_end(self.regex_string[idx]):
                    range_buffer.append(self.regex_string[idx])
                    self.regex_string =  self.regex_string[:idx] + "=" + self.regex_string[idx+1:]
                    in_range = False
                    ranges.append(''.join(range_buffer))                 
                    range_buffer.clear()
                else:
                    return None, False
            idx += 1
        return ranges, True



    def tokenize(self):
        self._clean_regex_string()
        valid_tokens = self._validate_regex_string()

        if not valid_tokens:
            return None, False

        ranges, valid_ranges = self.extract_ranges()
        
        if not valid_ranges:
            return None, False
        
        tokens = []
        for character in self.regex_string:
            if self._is_literal(character):
                tokens.append(Token(TokenType.Literal, character))
            elif self._is_two_operand_operation(character):
                tokens.append(Token(TokenType.TwoOperandOperation, character))
            elif self._is_single_operand_operation(character):
                tokens.append(Token(TokenType.SingleOperandOperation, character))
            elif self._is_left_parenthesis(character):
                tokens.append(Token(TokenType.LeftParenthesis, character))
            elif self._is_right_parenthesis(character):
                tokens.append(Token(TokenType.RightParenthesis, character))
            elif self._is_range(character):
                tokens.append(Token(TokenType.Literal, ranges.pop(0)))
            else:
                return None, False
                
        tokens = self._add_concatenation_tokens(tokens)
        tokens = self._reorder_single_operand_tokens(tokens)
        return  tokens, True