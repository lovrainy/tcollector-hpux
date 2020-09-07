#!/usr/bin/env python
import os
import collections
import ConfigParser as configparser

base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.realpath(base_dir))
root_path = root_dir + '/etc'

def gen_config(name, path):
    config_file = os.path.join(root_path, path)
    config = configparser.ConfigParser()
    config.read(config_file)

    sections = config.sections()
    settings = collections.namedtuple(name, sections)

    setting_map = {s: "" for s in sections}

    for section in sections:
        ops = config.options(section)
        if not ops:
            raise KeyError("Configuration %s is not allowed to be empty" % section)
        np = collections.namedtuple(section, ops)
        op_list = []
        for op in ops:
            op_v = config.get(section, op)
            if op_v in ["false", "False"]:
                op_v = False
            if op_v in ["true", "True"]:
                op_v = True
            if isinstance(op_v, str):
                if "," in op_v:
                    op_v = op_v.split(",")
            if op_v == "none":
                op_v = None
            if op_v == "":
                op_v = []
            op_list.append(op_v)
        setting_map[section] = np._make(op_list)

    return settings._make([setting_map[section] for section in sections])
