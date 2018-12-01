from xml.etree.ElementTree import ElementTree, Element
from xml.dom.minidom import parseString

import os
def read_xml(file_dir):
    """
    parse the .dat file of the mrxs file. Find the annotation info in the mrxs file.
    Use magic tool to show the .dat file property, the file which shows 'ASCII text, with very long lines,
    with CRLF line terminators' contains label information. Other file of property are not satisfied this requirment.
    :param file_dir: the dir path of the mrxs info which only contains .dat source files.
    :return: axis_list: a dist {label:list,'ID',ID}, label is the label name. list is the axis of the bbox in the image.
    """
    tree = ElementTree()
    tree.parse(file_dir)
    return tree

def write_xml(tree, out_path):
    tree.write(out_path, encoding="utf-8",xml_declaration=True)

def read_tree(file_dir):
    #tree = read_xml(file_dir)

    with open(file_dir) as f:
        lines = f.readlines()
        root = Element("data")
        for idx, line in enumerate(lines):
            line = parseString(line)
            root.append(line)
            for attr in line:


        #tree = Element('data')

    pretty(tree)
    write_xml(tree, file_dir)

def pretty(e,level=0):
    if len(e)>0:
        e.text = '\n' + '\t'(level+1)
        for child in e:
            pretty(child, level+1)
        child.tail = child.tail[:-1]
    e.tail = '\n' + '\t'*level


if __name__ == "__main__":
    read_tree("/home/gytang/new 2.txt")