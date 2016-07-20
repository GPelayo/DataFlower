import json
import os
import random

BRANCH_ID_FIELD_NAME = 'fields__pk'
CHILDREN_ID_FIELD_NAME = 'fields__child'

INPUT_FILEPATH = "data.json"
OUTPUT_DIRECTORY = "javascripts"
OUTPUT_FILENAME = "constants.js"

RANDOMIZE = True
RANDOM_ENTRY_SIZE = 10

data_file = open(INPUT_FILEPATH, "r")
data_obj = json.load(data_file)


class DataNode:
    not_used = None
    children = None
    node_id = None
    parent_id = None

    def __init__(self, node_id):
        self.node_id = node_id
        self.children = []

    def add_child(self, child_id):
        self.children.append(child_id)


class JSONDataBuilder:
    node_map = None
    used_key_list = None

    def __init__(self):
        self.node_map = dict()

    def add_node(self, node_id, child_id):
        self.node_map.setdefault(node_id, DataNode(node_id)).add_child(child_id)

    def connect_parents(self):
        for node in self.node_map.values():
            for child_id in node.children:
                child_node = self.node_map.get(child_id)
                if child_node:
                    child_node.parent_id = child_id

    def build_json(self):
        self.connect_parents()
        self.used_key_list = []
        output_json_str_list = []

        if RANDOMIZE:
            self.randomize(output_json_str_list)
        else:
            for node_id in self.node_map.keys():
                if node_id not in self.used_key_list and not self.node_map[node_id].parent_id:
                    output_json_str_list.append(self._build_json_node(self.node_map[node_id]))
        return [json.dumps(output_json, sort_keys=True) for output_json in output_json_str_list]

    def _build_json_node(self, node):
        child_node_list = []

        for child_id in node.children:
            if child_id in self.node_map.keys():
                child_node_list.append(self._build_json_node(self.node_map[child_id]))
            else:
                child_node_list.append(self.create_node_dict(child_id))

        new_node_dict = self.create_node_dict(node.node_id, children=child_node_list)

        return new_node_dict

    def create_node_dict(self, node_id, children=None):
        node_dict = dict()
        node_dict['name'] = node_id
        node_dict['size'] = 100

        if children:
            node_dict['children'] = children

        self.used_key_list.append(node_id)
        return node_dict

    def randomize(self, output_json):
        offset = 0
        for i, node_id in enumerate(self.node_map.keys()):
            if not self.node_map[node_id].parent_id:
                output_json.append(self._build_json_node(self.node_map[node_id]))
                break

        end_offset = offset + RANDOM_ENTRY_SIZE
        keys = list(self.node_map.keys())
        for node_id in keys[offset: end_offset]:
            if node_id not in self.used_key_list and not self.node_map[node_id].parent_id:
                self.traverse_dict(output_json, node_id)

    def traverse_dict(self, curr_json, node_id):
        if isinstance(curr_json, list):
            rando_dict = curr_json[0]
        else:
            rando_dict = curr_json

        if "children" in rando_dict.keys():
            children_size = len(rando_dict["children"])
            rando_index = random.randint(0, children_size)
        else:
            children_size = rando_index = 0

        if rando_index == children_size:
            new_dict = self._build_json_node(self.node_map[node_id])
            rando_dict.setdefault('children', []).append(new_dict)
        else:
            rando_dict = rando_dict["children"][rando_index]
            self.traverse_dict(rando_dict, node_id)

tree = JSONDataBuilder()

for entry in data_obj:
    node_value = entry
    children_values = entry

    for node_dict_key in BRANCH_ID_FIELD_NAME.split('__'):
        node_value = node_value[node_dict_key]

    for child_dict_ley in CHILDREN_ID_FIELD_NAME.split('__'):
        children_values = children_values[child_dict_ley]

    tree.add_node(node_value, children_values)

json_string = tree.build_json()[0]

with open(os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILENAME), 'w') as constant_js_file:
    constant_js_file.write("var json_data = '{}';".format(json_string))
