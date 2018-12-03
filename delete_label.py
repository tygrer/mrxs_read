from openslide import OpenSlide
from PIL import Image, ImageDraw
import os
import cv2
import numpy
import magic
from xml.dom.minidom import parseString
import subprocess
def delete_label_annotion(file_dir):
    mrxs_lst = []
    is_label = input("Please input mrxs filename and ID of its delete label:\n"
                     "For example, mrxs_file1:ID1 (DD10:UENFI10JD-DKKEMIJD-19DNK937,DD11:JFD73JF-2KD93-DKV10)\n")
    # cv2.destroyAllWindows()
    label_lst = is_label.split(",")
    label_dict = {}
    if label_lst != ['']:
        for li in label_lst:
            if label_dict.get(li.split(":")[0]) is not None:
                label_dict[li.split(":")[0]].append(li.split(":")[1])
            else:
                label_dict[li.split(":")[0]] = [li.split(":")[1]]

    if not os.path.isdir(file_dir):
        mrxs_lst[0] = file_dir
    else:
        for i in os.listdir(file_dir):
            if os.path.splitext(i)[-1] == '.mrxs':
                print("===============================================================================")
                print(os.path.join(file_dir, os.path.splitext(i)[0]))
                mrxs_lst.append(os.path.join(file_dir, os.path.splitext(i)[0]))
    for mrxs_fille_name in mrxs_lst:
        # mrxs_fille_name = "/home/gytang/medicine/fake/DCB-003"
        osr = OpenSlide(mrxs_fille_name + '.mrxs')
        axis_list = []
        find_file_flag = 0
        file_list = os.listdir(mrxs_fille_name)
        file_list.sort()
        delete_label = None
        if label_dict.get(os.path.basename(mrxs_fille_name)) is not None:
            delete_label = label_dict.get(os.path.basename(mrxs_fille_name))
        for i in file_list[::-1]:
            a = magic.from_file(os.path.join(mrxs_fille_name, i))
            #print("{}: magic tool read file property: {}".format(i, a))
            if a.find("ASCII text") != -1 or a.find("UTF-8 Unicode") != -1:
                with open(os.path.join(mrxs_fille_name, i)) as f:
                    lines = f.readlines()
                lines.reverse()
                if lines[-1].find("<attributes>") == -1:
                    continue
                if find_file_flag == 1:
                    print("There are already exsited a .dat label config file. The mrxs is not as normal as we occured.")
                find_file_flag = 1
                ID_name = []
                res = []
                for idx, line in enumerate(lines):
                    try:
                        line = parseString(line)
                        # print("ok:", line[0])
                    except:
                        # print("Can't analysis the {}th line".format(idx))
                        # print(line)
                        res.append(line)
                        continue
                    descript_lst = line.getElementsByTagName('descriptor')
                    for elements in descript_lst:
                        ID = elements.getAttribute('ID')[1:-1]
                        if ID not in ID_name:
                            ID_name.append(ID)
                            if delete_label is not None:
                                if ID in delete_label:
                                    continue
                            sib_lst = line.getElementsByTagName('SimpleBookmark')
                            if sib_lst == []:
                                continue
                            label = sib_lst[0].getAttribute('Caption')
                            detail_label = sib_lst[0].getAttribute('Desc')
                            if label.find("Annotation") == 0 and detail_label != "":
                                # print("alter annotation label.")
                                for node in sib_lst:
                                    node.setAttribute("Caption", detail_label)
                        res.append(line)

                with open(os.path.join(mrxs_fille_name, i), 'w') as fd:
                    if res is not None:
                        res.reverse()
                    for re in res:
                        try:
                            # print("ok:", line[0])
                            line = re.toxml() + '\n'
                            if line.find('<?xml version="1.0" ?>') == 0:
                                line = line.replace('<?xml version="1.0" ?>', '')
                            # print(line)
                            fd.write(line)
                        except:
                            # print("Can't analysis the {}th line")
                            # print(re)
                            fd.write(re)
                            continue

                break

        if find_file_flag == 0:
            print("No .dat label file in mrxs {} which searched by magic tool.".format(mrxs_fille_name))
        osr.close()

    # return axis_list

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file_dir', type=str, help="The location of the mrxs file directory, as: /home/gytang/medicine/annotion/anotation-test-image/SHE .")
    args = parser.parse_args()
    #draw_rangcle_jpg(args.file_dir)
    delete_label_annotion(args.file_dir)
    #save_label_alter_caption_main(args.file_dir)
    #alter_caption_main("/home/gytang/Downloads/res/other/")
