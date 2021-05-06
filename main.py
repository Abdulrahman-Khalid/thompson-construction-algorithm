from tokenizer import Tokenizer
from parse_tree import ParseTree
from graph import build_graph, Graph
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--regex', type=str, required=True, default='', 
                                help='input regex string => valid symbols: ' \
                                '\'AB\' AND operation, ' \
                                '\'A|B\' OR operation, ' \
                                '\'A*\' Repetition (0 or more), ' \
                                '\'A+\' Repetition (1 or more), ' \
                                '() are supported for subregex expressions, ' \
                                '[] are supported for range expressions, ' \
                                'a-z, A-Z, 0-9 are all valid, '
                                'no other symbols are valid, '
                                'example: \'(ab)*|c+\'')
parser.add_argument('--graph', type=str, required=False, default='graph', 
                                help='graph filename')
args = parser.parse_args()

# Tokenization
tokenizer = Tokenizer(args.regex)
tokens, valid = tokenizer.tokenize()

if not valid:
    print("Invalid Regex Expression")
else:
    # Construct Parse tree
    tree = ParseTree()
    tree.build_tree(tokens)

    # Construct NFA Graph
    graph = build_graph(tree.root)
    graph.to_json(args.graph)
    g = graph.draw_graph(args.graph)
    g.view()
