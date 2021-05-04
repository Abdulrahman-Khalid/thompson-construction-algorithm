from tokenizer import Tokenizer
from pares_tree import ParseTree

input_regex = "()((abc)*[a-z]|    []  (abc)|  ()   [1-9]+e*)"

tokenizer = Tokenizer(input_regex)
tokens, valid = tokenizer.tokenize()
if not valid:
    print("Invalid Regex")
else:
    #for token in tokens:
    #    print(token)

    tree = ParseTree()
    tree.build_tree(tokens)
    #print(tree.root)
