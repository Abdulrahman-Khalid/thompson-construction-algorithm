from parse_tree import ParseTree, NodeType
from tokenizer import TokenType
from graphviz import Digraph
import json

class State:
    previously_printed = []
    def __init__(self, value):
        self.value = value
        self.map = []
        
    def add_output_edge(self, edge_value, output_state):
        self.map.append({edge_value: output_state})
    
    def __str__(self, level=0):
        s = "\t" * level + "State " + chr(self.value) + "\n"
        State.previously_printed.append(self.value)
        for output in self.map:
            for key in output:
                if output[key].value in State.previously_printed:
                    s += "\t" * level + key + " --> " + "\n" + "\t" * (level+1) + "State " + chr(output[key].value) + "\n"
                else:
                    s += "\t" * level + key + " --> " + "\n" + output[key].__str__(level + 1) + "\n"
                    State.previously_printed.append(output[key].value) 
            
        return s

    def draw_graph(self, filename):
        State.previously_printed = []
        graph = Digraph('G', filename=filename, format='png')
        graph.attr(rankdir='LR', size='6,5')
        graph.attr('node', shape='circle')
        data = {}
        data["startingState"] = chr(self.value)
        self.draw_graph_helper(graph, data)
        with open(filename+'.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
        return graph

    def json_add_keyvalue(self, data, output, key):
        state = chr(self.value)
        if state not in data:
            data[state] = {}
        if key == "\u03b5":
            newKey = "Epsilon"
        else:
            newKey = key
        outState = chr(output[key].value)
        if newKey not in data[state]:
            data[state][newKey] = list(outState)
        else:
            data[state][newKey].append(outState)

    def draw_graph_helper(self, graph, data):
        State.previously_printed.append(self.value)
        if chr(self.value) not in data:
            data[chr(self.value)] = {}
        data[chr(self.value)]["isTerminatingState"] = len(self.map) == 0
            
        for output in self.map:
            for key in output:
                self.json_add_keyvalue(data, output, key)
                if len(output[key].map) == 0:
                    graph.attr('node', shape='doublecircle')
                    graph.node(chr(output[key].value))
                    graph.attr('node', shape='circle')
                    graph.edge(chr(self.value), chr(output[key].value), label=key)
                else:
                    graph.edge(chr(self.value), chr(output[key].value), label=key)
                if output[key].value not in State.previously_printed:
                    State.previously_printed.append(output[key].value) 
                    output[key].draw_graph_helper(graph, data)


class Graph:
    last_state_value = 65
    def __init__(self):
        self.initial_state = None
        self.last_state = None

def create_literal_graph(literal):
    literal_graph = Graph()
    literal_graph.initial_state = State(Graph.last_state_value)
    Graph.last_state_value += 1
    literal_graph.last_state = State(Graph.last_state_value)
    Graph.last_state_value += 1
    
    literal_graph.initial_state.add_output_edge(literal, literal_graph.last_state)
    return literal_graph

def create_and_graph(fisrst_graph, second_graph):
    fisrst_graph.last_state.add_output_edge("\u03B5", second_graph.initial_state)
    fisrst_graph.last_state = second_graph.last_state
    return fisrst_graph

def create_or_graph(fisrst_graph, second_graph):
    or_graph = Graph()
    or_graph.initial_state = State(Graph.last_state_value)
    Graph.last_state_value += 1
    or_graph.last_state = State(Graph.last_state_value)
    Graph.last_state_value += 1

    or_graph.initial_state.add_output_edge("\u03B5", fisrst_graph.initial_state)
    or_graph.initial_state.add_output_edge("\u03B5", second_graph.initial_state)

    fisrst_graph.last_state.add_output_edge("\u03B5", or_graph.last_state)
    second_graph.last_state.add_output_edge("\u03B5", or_graph.last_state)
    return or_graph

def create_asterisk_graph(initial_graph):
    asterisk_graph = Graph()
    asterisk_graph.initial_state = State(Graph.last_state_value)
    Graph.last_state_value += 1
    asterisk_graph.last_state = State(Graph.last_state_value)
    Graph.last_state_value += 1

    asterisk_graph.initial_state.add_output_edge("\u03B5", initial_graph.initial_state)

    asterisk_graph.initial_state.add_output_edge("\u03B5", asterisk_graph.last_state)

    initial_graph.last_state.add_output_edge("\u03B5", asterisk_graph.last_state)
    
    initial_graph.last_state.add_output_edge("\u03B5", asterisk_graph.initial_state)

    return asterisk_graph

def create_plus_graph(initial_graph):
    asterisk_graph = Graph()
    asterisk_graph.initial_state = State(Graph.last_state_value)
    Graph.last_state_value += 1
    asterisk_graph.last_state = State(Graph.last_state_value)
    Graph.last_state_value += 1

    asterisk_graph.initial_state.add_output_edge("\u03B5", initial_graph.initial_state)
 
    initial_graph.last_state.add_output_edge("\u03B5", asterisk_graph.last_state)
    
    initial_graph.last_state.add_output_edge("\u03B5", asterisk_graph.initial_state)

    return asterisk_graph


def build_graph(parse_tree):
    if parse_tree.type == NodeType.Subtree:
        return build_graph(parse_tree.value)

    if parse_tree.value.type == TokenType.Literal:
        return create_literal_graph(parse_tree.value.value)

    if parse_tree.value.value == "&":
        return create_and_graph(build_graph(parse_tree.left), build_graph(parse_tree.right))

    if parse_tree.value.value == "|":
        return create_or_graph(build_graph(parse_tree.left), build_graph(parse_tree.right))

    if parse_tree.value.value == "*":
        return create_asterisk_graph(build_graph(parse_tree.left))

    if parse_tree.value.value == "+":
        return create_plus_graph(build_graph(parse_tree.left))

    
