from tokenizer import Tokenizer
from pares_tree import ParseTree
from graph import build_graph, Graph
input_regex = "(ab|c)*"

tokenizer = Tokenizer(input_regex)
tokens, valid = tokenizer.tokenize()
if not valid:
    print("Invalid Regex")
else:
    #for token in tokens:
    #    print(token)

    tree = ParseTree()
    tree.build_tree(tokens)
    graph = build_graph(tree.root)

    print(graph.initial_state)
    g = graph.initial_state.draw_graph()
    g.view()

    #print(graph.initial_state.map)
    #print(graph.initial_state.map[0]['#'])
