from parse_tree import ParseTree, NodeType
from tokenizer import TokenType
from graphviz import Digraph
import json

class State:
    previously_printed = []
    def __init__(self, value):
        self.value = value
        self.output_states = []
        self.is_terminal_state = False
        
    def add_output_edge(self, edge_value, output_state):
        self.output_states.append({edge_value: output_state})

    def value_string(self):
        return "S" + str(self.value)
    
class Graph:
    last_state_value = 0
    
    def __init__(self):
        self.initial_state = self.create_state()
        self.last_state = self.create_state()
        self.last_state.is_terminal_state = True
    
    def create_state(self):
        state = State(Graph.last_state_value)
        Graph.last_state_value += 1
        return state

    @staticmethod
    def _print_graph(state, previously_printed, level=0):
        s = "\t" * level + state.value_string() + "\n"
        previously_printed.append(state.value)
        for output_state in state.output_states:
            for output_edge in output_state:
                if output_state[output_edge].value in previously_printed:
                    s += "\t" * level + output_edge + " --> " + "\n" + "\t" * (level+1) + output_state[output_edge].value_string() + "\n"
                else:
                    s += "\t" * level + output_edge + " --> " + "\n" + Graph._print_graph(output_state[output_edge], previously_printed, level + 1) + "\n"
                    previously_printed.append(output_state[output_edge].value) 
        return s

    def __str__(self):
        previously_printed = []
        return Graph._print_graph(self.initial_state, previously_printed)
        
    def to_json(self, filename):
        json_data = {}
        json_data["startingState"] = self.initial_state.value_string()
        
        Graph.to_json_helper(self.initial_state, json_data)

        with open(filename+'.json', 'w') as outfile:
            json.dump(json_data, outfile, indent=4)
        
    @staticmethod
    def to_json_helper(state, json_data):
        if state.value_string() not in json_data:
            json_data[state.value_string()] = {}
            json_data[state.value_string()]["isTerminatingState"] = state.is_terminal_state
            
        for output_state in state.output_states:
            for output_edge in output_state:  
                edge_string = "Epsilon" if output_edge == "\u03b5" else output_edge
                if edge_string not in json_data[state.value_string()]:
                    json_data[state.value_string()][edge_string] = [output_state[output_edge].value_string()]
                else:
                    json_data[state.value_string()][edge_string].append(output_state[output_edge].value_string())

                if output_state[output_edge].value_string() not in json_data:
                    Graph.to_json_helper(output_state[output_edge], json_data)
            
    def draw_graph(self, filename):
        previously_drawn = []

        graph = Digraph('G', filename=filename, format='png')
        graph.attr(rankdir='LR', size='6,5')
        graph.attr('node', shape='circle')
        
        Graph._draw_graph_helper(self.initial_state, graph, previously_drawn)

        return graph

    @staticmethod
    def _draw_graph_helper(state, graph, previously_drawn):
        previously_drawn.append(state.value)
        
        for output_state in state.output_states:
            for output_edge in output_state:
                if output_state[output_edge].is_terminal_state:
                    graph.attr('node', shape='doublecircle')
                    graph.node("S" + str(output_state[output_edge].value))
                    graph.attr('node', shape='circle')
            
                graph.edge("S" + str(state.value), "S" + str(output_state[output_edge].value), label=output_edge)

                if output_state[output_edge].value not in previously_drawn:
                    previously_drawn.append(output_state[output_edge].value)
                    Graph._draw_graph_helper(output_state[output_edge], graph, previously_drawn) 


def create_literal_graph(literal):
    literal_graph = Graph()

    literal_graph.initial_state.add_output_edge(literal, literal_graph.last_state)
    
    return literal_graph

def create_and_graph(fisrst_graph, second_graph):
    fisrst_graph.last_state.add_output_edge("\u03B5", second_graph.initial_state)
    fisrst_graph.last_state.is_terminal_state = False
    fisrst_graph.last_state = second_graph.last_state
    
    return fisrst_graph

def create_or_graph(fisrst_graph, second_graph):
    or_graph = Graph()

    or_graph.initial_state.add_output_edge("\u03B5", fisrst_graph.initial_state)
    or_graph.initial_state.add_output_edge("\u03B5", second_graph.initial_state)
    
    fisrst_graph.last_state.is_terminal_state = False
    second_graph.last_state.is_terminal_state = False

    fisrst_graph.last_state.add_output_edge("\u03B5", or_graph.last_state)
    second_graph.last_state.add_output_edge("\u03B5", or_graph.last_state)
    
    return or_graph

def create_asterisk_graph(initial_graph):
    asterisk_graph = Graph()


    asterisk_graph.initial_state.add_output_edge("\u03B5", initial_graph.initial_state)
    asterisk_graph.initial_state.add_output_edge("\u03B5", asterisk_graph.last_state)
    
    initial_graph.last_state.is_terminal_state = False

    initial_graph.last_state.add_output_edge("\u03B5", asterisk_graph.last_state)
    initial_graph.last_state.add_output_edge("\u03B5", asterisk_graph.initial_state)

    return asterisk_graph

def create_plus_graph(initial_graph):
    plus_graph = Graph()

    plus_graph.initial_state.add_output_edge("\u03B5", initial_graph.initial_state)
    
    initial_graph.last_state.is_terminal_state = False

    initial_graph.last_state.add_output_edge("\u03B5", plus_graph.last_state)
    initial_graph.last_state.add_output_edge("\u03B5", plus_graph.initial_state)

    return plus_graph


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
