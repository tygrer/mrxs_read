from xml.etree.ElementTree import ElementTree, Element
import magic
import os
def read_xml(file_dir):
    """
    parse the .dat file of the mrxs file. Find the annotation info in the mrxs file.
    Use magic tool to show the .dat file property, the file which shows 'ASCII text, with very long lines,
    with CRLF line terminators' contains label information. Other file of property are not satisfied this requirment.
    :param file_dir: the dir path of the mrxs info which only contains .dat source files.
    :return: axis_list: a dist {label:list,'ID',ID}, label is the label name. list is the axis of the bbox in the image.
    """
    import magic
    tree = ElementTree()
    tree.parse(file_dir)
    return tree
def write_xml(tree, out_path):
    tree.write(out_path)

def get_node_by_keyvalue(nodelist):
    result_nodes = []
    for node in nodelist:
        caption_label = node.attrib.get("Caption")
        desc_label = node.attrib.get("desc")
        if caption_label.find("Annotation") != -1 and desc_label != "":
            node.set("Caption", caption_label)
            #result_nodes.append(node)
    #return result_nodes

def find_nodes(tree, path):
    return tree.findall(path)

def alter_capption_main(file_dir):

    axis_list = []
    find_file_flag = 0
    file_list = os.listdir(file_dir)
    file_list.sort()
    for i in file_list[::-1]:
        a = magic.from_file(os.path.join(file_dir, i))
        print("{}: magic tool read file property: {}".format(i, a))
        if a.find("ASCII text") != -1 or a.find("UTF-8 Unicode") != -1:
            with open(os.path.join(file_dir, i)) as f:
                lines = f.readlines()
            lines.reverse()
            if lines[-1].find("<attributes>") == -1:
                continue
            if find_file_flag == 1:
                print("There are already exsited a .dat label config file. The mrxs is not as normal as we occured.")
            find_file_flag = 1
            ID_name = []
            tree = read_xml(os.path.join(file_dir, i))
            node_list = find_nodes(tree, "data/slide_flag_data/SimpleBookmark")
            get_node_by_keyvalue(node_list)
            write_xml(tree,"./out.dat")

    if find_file_flag == 0:
        print("No .dat label file in mrxs {} which searched by magic tool.".format(file_dir))


if __name__ == "__main__":
    axis_list = alter_capption_main("/home/gytang/medicine/annotion/anotation-test-image/SHE/")
    print(axis_list)