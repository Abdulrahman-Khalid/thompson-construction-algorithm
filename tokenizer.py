from enum import Enum, auto
import string

class TokenType(Enum):
    Literal = auto()
    TwoOperandOperation = auto()
    SingleOperandOperation = auto()
    Left_Parenthesis = auto()
    Right_Parenthesis = auto()

class Token:
    def __init__(self, token_type, token_value):
        self.type = token_type
        self.value = token_value

    def __str__(self):
        return "Type: " + str(self.type) + " Value: " + self.value

    
class Tokenizer:
    def __init__(self, regex_string):
        self.regex_string = regex_string

    def _clean_regex_string(self):
        self.regex_string = "".join( self.regex_string.split())

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


    def _validate_regex_string(self):
        if not self.regex_string:
            return False

        valid_symbols = "-[]()*+|"
        for character in self.regex_string:
            if not self._is_literal(character) and character not in valid_symbols:
                return False

        idx = 1
        single_opernad_operations = "+*"
        two_opernad_operations = "|"
        while idx < len(self.regex_string):
            if self.regex_string[idx] in single_opernad_operations:
                if self.regex_string[idx - 1] in single_opernad_operations or \
                    self.regex_string[idx - 1] in two_opernad_operations:
                    return False
            if self.regex_string[idx] in two_opernad_operations:    
                if self.regex_string[idx - 1] in two_opernad_operations:
                    return False
            idx += 1


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

    def _is_literal(self, character):
        return character.isalpha() or character.isdigit()

    def _is_two_operand_operation(self, character):
        return character == "|"

    def _is_single_operand_operation(self, character):
        return character == "*" or character == "+"

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

    def _add_concatenation_tokens(self, tokens):
        idx = 1
        while idx < len(tokens):
            if tokens[idx].type == TokenType.Literal or tokens[idx].type == TokenType.Left_Parenthesis:
                if tokens[idx - 1].type == TokenType.Literal \
                        or tokens[idx - 1].type == TokenType.Right_Parenthesis \
                        or tokens[idx - 1].type == TokenType.SingleOperandOperation:
                    tokens.insert(idx, Token(TokenType.TwoOperandOperation, "&"))
                    idx += 1
            idx += 1
        return tokens


    def _reorder_single_operand_tokens(self, tokens):
        last_left_parenthesis_idx = -1
        for idx in range(len(tokens)):
            if tokens[idx].type == TokenType.Left_Parenthesis:
                last_left_parenthesis_idx = idx
            elif tokens[idx].type == TokenType.SingleOperandOperation:
                if tokens[idx - 1].type == TokenType.Right_Parenthesis:
                    single_operand_token = tokens.pop(idx)
                    tokens.insert(last_left_parenthesis_idx, single_operand_token)
                else:
                    tokens[idx - 1], tokens[idx] = tokens[idx], tokens[idx - 1]
        return tokens

    def tokenize(self):
        self._clean_regex_string()
        valid_token = self._validate_regex_string()
        if not valid_token:
            return None, False

        tokens = []
        range_buffer = []
        in_range = False
        for character in self.regex_string:
            if not in_range:
                if self._is_range_start(character):
                    in_range = True
                    range_buffer.append(character)
                if self._is_literal(character):
                    tokens.append(Token(TokenType.Literal, character))
                elif self._is_two_operand_operation(character):
                    tokens.append(Token(TokenType.TwoOperandOperation, character))
                elif self._is_single_operand_operation(character):
                    tokens.append(Token(TokenType.SingleOperandOperation, character))
                elif self._is_left_parenthesis(character):
                    tokens.append(Token(TokenType.Left_Parenthesis, character))
                elif self._is_right_parenthesis(character):
                    tokens.append(Token(TokenType.Right_Parenthesis, character))
            else:
                if self._is_range_symbol(character) or self._is_literal(character):
                    range_buffer.append(character)
                elif self._is_range_end(character):
                    in_range = False
                    range_buffer.append(character)
                    tokens.append(Token(TokenType.Literal, ''.join(range_buffer)))
                    range_buffer.clear()
    
        tokens = self._add_concatenation_tokens(tokens)
        tokens = self._reorder_single_operand_tokens(tokens)
        return  tokens, True