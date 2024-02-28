from typing import List

from PyQt5.QtCore import QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QTreeView


class TreeNode:
    def __init__(self, data, parent: 'TreeNode' = None, children: List['TreeNode'] = None):
        self.data = data
        self.parent = parent
        self.children = children if children is not None else []

    def is_leaf(self) -> bool:
        if len(self.children) == 0:
            return True
        else:
            return False

    def set_children(self, child_list: List['TreeNode']):
        if not child_list:
            self.children = child_list

    def add_child(self, child: 'TreeNode'):
        self.children.append(child)

    def get_node_by_name(self,name:str):
        if self.data.name == name:
            return self
        else:
            for children in self.children:
                node = children.get_node_by_name(name)
                if node:
                    return node
            return None

    def get_non_leaf_nodes(self,data_rst=None, node_rst=None):
        if data_rst is None:
            data_rst = []
        if node_rst is None:
            node_rst = []
        if self.children:
            data_rst.append(self.data)
            node_rst.append(self)
            for child in self.children:
                child.get_non_leaf_nodes(data_rst,node_rst)
        return data_rst,node_rst

    def get_leaf_nodes(self,data_rst=None):
        if data_rst is None:
            data_rst = []
        for child in self.children:
            data_rst.append(child.data)
            child.get_leaf_nodes(data_rst)
        return data_rst

    def has_child(self,child_node:'TreeNode'):
        has_child_flag = False
        if self.children:
            if child_node in self.children:
                has_child_flag = True
            else:
                for child in self.children:
                    if child.has_child(child_node):
                        has_child_flag = True
                        break
        else:
            has_child_flag = False
        return has_child_flag

    def has_child_by_name(self,child_node:'TreeNode'):
        has_child_flag = False
        if self.children:
            for child in self.children:
                if child.data.name == child_node.data.name or child.has_child_by_name(child_node):
                    has_child_flag = True
                    break
        else:
            has_child_flag = False
        return has_child_flag

    @staticmethod
    def get_nodes_between(start_node:'TreeNode',stop_node:'TreeNode',data_rst=None, node_rst=None):
        if data_rst is None:
            data_rst = []
        if node_rst is None:
            node_rst = []
        if start_node.children:
            if start_node.has_child(stop_node):
                data_rst.append(start_node.data)
                node_rst.append(start_node)
                for child in start_node.children:
                    TreeNode.get_nodes_between(child,stop_node,data_rst,node_rst)
        return data_rst,node_rst

    @staticmethod
    def get_nodes_between_by_name(start_node:'TreeNode',stop_node:'TreeNode',data_rst=None, node_rst=None):
        if data_rst is None:
            data_rst = []
        if node_rst is None:
            node_rst = []
        if start_node.children:
            if start_node.has_child_by_name(stop_node):
                data_rst.append(start_node.data)
                node_rst.append(start_node)
                for child in start_node.children:
                    TreeNode.get_nodes_between_by_name(child,stop_node,data_rst,node_rst)
        return data_rst,node_rst

    def print_tree(self, prefix='\t',indent=0)->str:
        # 这里需要拼装更加复杂的字符串
        info_str = self.data.get_scan_str()
        print_str = f'{prefix}{"    " * indent}{indent}-{info_str}\n'
        for child in self.children:
            print_str = print_str + child.print_tree(indent=indent + 1)
        return print_str


def model_to_tree(tree: QTreeView, parent_index: QModelIndex = None) -> TreeNode:
    if parent_index is None:
        parent_index = tree.model.index(0, 0)
    parent_node = TreeNode(tree.indexWidget(parent_index).get_quantity())
    if tree.isExpanded(parent_index):
        # 注意这里需要进行是否展开的判断，保持和UI展开的同步
        for row in range(tree.model.rowCount(parent_index)):
            child_index = tree.model.index(row, 0, parent_index)
            child_node = model_to_tree(tree, child_index)
            child_node.parent = parent_node
            parent_node.children.append(child_node)
    return parent_node
