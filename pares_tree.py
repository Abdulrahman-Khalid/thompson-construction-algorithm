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

    def __str__(self, level=0):
        ret = "\t" * level + repr(self) + "\n"
        if self.left is not None:
            ret += self.left.__str__(level + 1)
        if self.right is not None:
            ret += self.right.__str__(level + 1)
        return ret

    def __repr__(self):
        if self.type == NodeType.Token:
            return str(self.value.value)
        elif self.type == NodeType.Subtree:
            return "SubTree"


class ParseTree:
    def __init__(self):
        self.root = TreeNode(None)

    def _fill_empty_node(self, node, new_node):
        if node.left is None:
            node.left = new_node
        elif node.right is None and \
        (node.type == NodeType.Token and node.value.type != TokenType.SingleOperandOperation):
            node.right = new_node
        elif node.right is None and \
        (node.type == NodeType.Token and node.value.type == TokenType.SingleOperandOperation):
            self._fill_empty_node(node.left, new_node)
        else:
            self._fill_empty_node(node.right, new_node)

    def _insert_literal(self, value):
        new_node = TreeNode(value)
        self._fill_empty_node(self.root, new_node)

    def _right_rotate(self, node):
        left_node = node.left
        right_node = left_node.right
        left_node.right = node
        node.left = right_node
        return left_node

    def _insert_two_operand_operator(self, value):
        if self.root.value is not None:
            new_node = TreeNode(value)
            new_node.left = self.root
            self.root = new_node
            if value.value == '&' and \
            new_node.left.value.value != '&' and \
            (new_node.left.type == NodeType.Token and \
            new_node.left.value.type != TokenType.SingleOperandOperation):
                self.root = self._right_rotate(new_node)
        else:
            self.root.value = value


    def _insert_subtree(self, root):
        new_node = TreeNode(root, NodeType.Subtree)
        self._fill_empty_node(self.root, new_node)

    def _insert_single_operand_operator(self, value):
        if self.root.value is not None:
            self._insert_literal(value)
        else:
            self.root.value = value

    def build_tree(self, tokens, start_index=0):
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
            elif tokens[idx].type == TokenType.Left_Parenthesis:
                subtree = ParseTree()
                new_idx = subtree.build_tree(tokens, idx + 1)
                self._insert_subtree(subtree.root)
            elif tokens[idx].type == TokenType.Right_Parenthesis:
                return idx + 1
  



