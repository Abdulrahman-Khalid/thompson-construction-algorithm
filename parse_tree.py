from enum import Enum, auto
from tokenizer import TokenType

class NodeType(Enum):
    Token = auto()
    Subtree = auto()

class TreeNode:
    def __init__(self, value, node_type=NodeType.Token):
        self.left = None
        self.right = None
        self.value = value
        self.type = node_type

    def __repr__(self):
        if self.type == NodeType.Token:
            return str(self.value.value)
        elif self.type == NodeType.Subtree:
            return "SubTree"

    def _is_single_operand_operation(self):
        return self.type == NodeType.Token and self.value.type == TokenType.SingleOperandOperation
    
    def _is_not_single_operand_operation(self):
        return self.type == NodeType.Token and self.value.type != TokenType.SingleOperandOperation

    def _is_and_operation(self):
        return self.type == NodeType.Token and self.value.value == "&"
    
    def _is_not_and_operation(self):
        return self.type == NodeType.Token and self.value.value != "&"

class ParseTree:
    def __init__(self):
        self.root = TreeNode(None)
    
    @staticmethod
    def _print_tree(node, level=0):
        s = "\t" * level + repr(node) + "\n"
        if node.left is not None:
            s += ParseTree._print_tree(node.left, level + 1)
        if node.right is not None:
             s += ParseTree._print_tree(node.right, level + 1)
        return s

    def __str__(self):
        return ParseTree._print_tree(self.root)

    def _find_empty_node(self, node, new_node):
        if node.left is None:
            node.left = new_node
        elif node.right is None and node._is_not_single_operand_operation():
            node.right = new_node
        elif node.right is None and node._is_single_operand_operation():
            self._find_empty_node(node.left, new_node)
        else:
            self._find_empty_node(node.right, new_node)
    
    def _right_rotate(self, node):
        left_node = node.left
        right_node = left_node.right
        left_node.right = node
        node.left = right_node
        return left_node

    def _insert_literal(self, value):
        new_node = TreeNode(value)
        self._find_empty_node(self.root, new_node)

    def _insert_two_operand_operator(self, value):
        if self.root.value is not None:
            new_node = TreeNode(value)
            new_node.left = self.root
            self.root = new_node
            if new_node._is_and_operation() and \
                new_node.left._is_not_and_operation() and \
                new_node.left._is_not_single_operand_operation():
                self.root = self._right_rotate(new_node)
        else:
            self.root.value = value


    def _insert_subtree(self, root):
        new_node = TreeNode(root, NodeType.Subtree)
        self._find_empty_node(self.root, new_node)

    def _insert_single_operand_operator(self, value):
        if self.root.value is not None:
            new_node = TreeNode(value)
            self._find_empty_node(self.root, new_node)
        else:
            self.root.value = value

    def build_tree(self, tokens, start_index=0):
        if len(tokens) == 0:
            return
        new_idx = -1
        for idx in range(start_index, len(tokens)):
            if idx < new_idx:
                continue
            if tokens[idx].type == TokenType.Literal:
                self._insert_literal(tokens[idx])
            elif tokens[idx].type == TokenType.SingleOperandOperation:
                self._insert_single_operand_operator(tokens[idx])
            elif tokens[idx].type == TokenType.TwoOperandOperation:
                self._insert_two_operand_operator(tokens[idx])
            elif tokens[idx].type == TokenType.LeftParenthesis:
                subtree = ParseTree()
                new_idx = subtree.build_tree(tokens, idx + 1)
                self._insert_subtree(subtree.root)
            elif tokens[idx].type == TokenType.RightParenthesis:
                if self.root.value is None:
                    self.root = self.root.left
                return idx + 1

        if self.root.value is None:
            self.root = self.root.left
