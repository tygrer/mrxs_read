from openslide import OpenSlide
from PIL import Image, ImageDraw
import os
import cv2
import numpy
import magic
from xml.dom.minidom import parseString
import subprocess

def is_or_not_RGBA(img):
    if img.mode == 'RGBA':
        alpha = img.split()[3]
        bgmask = alpha.point(lambda x: 255 - x)

        img = img.convert('RGB')
        # paste(color, box, mask)
        img.paste((255, 255, 255), None, bgmask)
    else:
        img = img.convert('RGB')
    return img

def draw_rangcle_jpg(file_dir):
    mrxs_lst = []
    if not os.path.isdir(file_dir):
        mrxs_lst[0] = file_dir
    else:
        for i in os.listdir(file_dir):
            if os.path.splitext(i)[-1] == '.mrxs':
                mrxs_lst.append(os.path.join(file_dir, os.path.splitext(i)[0]))
    for mrxs_fille_name in mrxs_lst:
        #mrxs_fille_name = "/home/gytang/medicine/fake/DCB-003"
        osr = OpenSlide(mrxs_fille_name + '.mrxs')
        axis_list = []
        find_file_flag = 0
        file_list = os.listdir(mrxs_fille_name)
        file_list.sort()
        for i in file_list[::-1]:
            a = magic.from_file(os.path.join(mrxs_fille_name, i))
            print("{}: magic tool read file property: {}".format(i, a))
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
                        #print("Can't analysis the {}th line".format(idx))
                        #print(line)
                        res.append(line)
                        continue
                    descript_lst = line.getElementsByTagName('descriptor')
                    for elements in descript_lst:
                        ID = elements.getAttribute('ID')[1:-1]
                        if ID not in ID_name:
                            ID_name.append(ID)
                            flag_lst = line.getElementsByTagName('slide_flag')
                            axis = []
                            sib_lst = line.getElementsByTagName('SimpleBookmark')
                            if sib_lst == []:
                                continue
                            label = sib_lst[0].getAttribute('Caption')
                            detail_label = sib_lst[0].getAttribute('Desc')
                            if label.find("Annotation") == 0 and detail_label != "":
                                #print("alter annotation label.")
                                for node in sib_lst:
                                    node.setAttribute("Caption", detail_label)
                                label = detail_label
                            print("===============================================================================")
                            print("alter_caption :", label)
                            axis.append(flag_lst[0].getAttribute('brLeft'))
                            axis.append(flag_lst[0].getAttribute('brTop'))
                            axis.append(flag_lst[0].getAttribute('brRight'))
                            axis.append(flag_lst[0].getAttribute('brBottom'))
                            axis = [int(i) for i in axis]
                            ww = axis[2] - axis[0]
                            hh = axis[3] - axis[1]
                            w, h = osr.level_dimensions[0]
                            img = osr.read_region((max(axis[0]-100,0), max(axis[1]-100,0)), 0, (min(w,round(ww + 200)), min(h,round(hh + 200))))
                            #img.show()

                            img = is_or_not_RGBA(img)
                            img = numpy.array(img)
                            opencv_image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                            print(100, 100, round(ww),round(hh))

                            opencv_image = cv2.rectangle(opencv_image, (100, 100),(100 + round(ww), 100+round(hh)), (0, 0, 0), 10)
                            #imgdraw.rectangle((round(axis[0]),round(axis[1]),round(ww),round(hh)),None,outline=(0,0,0))
                            ratio = 512 / (ww+200)
                            opencv_image = cv2.resize(opencv_image, (512, int((hh+200) * ratio)))
                            #cv2.imshow("show", opencv_image)
                            #cv2.waitKey(1000)
                            while(1):
                                is_label = input("Is it a label?\n"
                                                 "(Enter means yes, or input 'n' or 'N' means that the box is not label):")
                                #cv2.destroyAllWindows()
                                if is_label == "" or is_label.lower() == "y" or is_label.lower() == "yes":
                                    print("\nfile:",mrxs_fille_name,"axis:", axis, "ID:", ID, "label:", label)
                                    axis_list.append({"axis": axis, "ID": ID, "label": label})
                                    res.append(line)
                                    break
                                elif is_label.lower() == "n" or is_label.lower() == "no":
                                    break
                                else:
                                    print("The format of input is wrong. Please input again.")
                                    continue


                with open(os.path.join(mrxs_fille_name, i), 'w') as fd:
                    if res is not None:
                        res.reverse()
                    for re in res:
                        try:
                            # print("ok:", line[0])
                            line = re.toxml() + '\n'
                            if line.find('<?xml version="1.0" ?>') == 0:
                                line = line.replace('<?xml version="1.0" ?>', '')
                            #print(line)
                            fd.write(line)
                        except:
                            #print("Can't analysis the {}th line")
                            #print(re)
                            fd.write(re)
                            continue

                break

        if find_file_flag == 0:
            print("No .dat label file in mrxs {} which searched by magic tool.".format(mrxs_fille_name))
        osr.close()

    #return axis_list

def alter_capption_main(file_dir):
    mrxs_lst = []
    if not os.path.isdir(file_dir):
        mrxs_lst[0] = file_dir
    else:
        for i in os.listdir(file_dir):
            if os.path.splitext(i)[-1] == '.mrxs':
                print(os.path.join(file_dir, os.path.splitext(i)[0]))
                mrxs_lst.append(os.path.join(file_dir, os.path.splitext(i)[0]))
    for mrxs_fille_name in mrxs_lst:
        #mrxs_fille_name = "/home/gytang/medicine/fake/DCB-003"
        osr = OpenSlide(mrxs_fille_name + '.mrxs')
        axis_list = []
        find_file_flag = 0
        file_list = os.listdir(mrxs_fille_name)
        file_list.sort()
        for i in file_list[::-1]:
            a = magic.from_file(os.path.join(mrxs_fille_name, i))
            print("{}: magic tool read file property: {}".format(i, a))
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
                        #print("Can't analysis the {}th line".format(idx))
                        #print(line)
                        res.append(line)
                        continue
                    descript_lst = line.getElementsByTagName('descriptor')
                    for elements in descript_lst:
                        ID = elements.getAttribute('ID')[1:-1]
                        if ID not in ID_name:
                            ID_name.append(ID)
                            flag_lst = line.getElementsByTagName('slide_flag')
                            axis = []
                            sib_lst = line.getElementsByTagName('SimpleBookmark')
                            if sib_lst == []:
                                continue
                            label = sib_lst[0].getAttribute('Caption')
                            detail_label = sib_lst[0].getAttribute('Desc')
                            if label.find("Annotation") == 0 and detail_label != "":
                                #print("alter annotation label.")
                                for node in sib_lst:
                                    node.setAttribute("Caption", detail_label)
                                label = detail_label
                            print("===============================================================================")
                            print("alter_caption :", label)
                            axis.append(flag_lst[0].getAttribute('brLeft'))
                            axis.append(flag_lst[0].getAttribute('brTop'))
                            axis.append(flag_lst[0].getAttribute('brRight'))
                            axis.append(flag_lst[0].getAttribute('brBottom'))
                            axis = [int(i) for i in axis]
                            ww = axis[2] - axis[0]
                            hh = axis[3] - axis[1]
                            print("\nfile:", mrxs_fille_name, "axis:", axis, "ID:", ID, "label:", label)
                            axis_list.append({"axis": axis, "ID": ID, "label": label})
                            res.append(line)
                            w, h = osr.level_dimensions[0]
                            img = osr.read_region((max(axis[0]-100,0), max(axis[1]-100,0)), 0, (min(w,round(ww + 200)), min(h,round(hh + 200))))
                            #img.show()

                            img = is_or_not_RGBA(img)
                            img = numpy.array(img)
                            opencv_image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                            print(100, 100, round(ww),round(hh))

                            opencv_image = cv2.rectangle(opencv_image, (100, 100),(100 + round(ww), 100+round(hh)), (0, 0, 0), 10)
                            #imgdraw.rectangle((round(axis[0]),round(axis[1]),round(ww),round(hh)),None,outline=(0,0,0))
                            ratio = 512 / (ww+200)
                            opencv_image = cv2.resize(opencv_image, (512, int((hh+200) * ratio)))
                            cv2.imshow("show", opencv_image)
                            cv2.waitKey(1000)
                            while(1):
                                is_label = input("Is it a label?\n"
                                                 "(Enter means yes, or input 'n' or 'N' means that the box is not label):")
                                #cv2.destroyAllWindows()
                                if is_label == "" or is_label.lower() == "y" or is_label.lower() == "yes":
                                    print("\nfile:",mrxs_fille_name,"axis:", axis, "ID:", ID, "label:", label)
                                    axis_list.append({"axis": axis, "ID": ID, "label": label})
                                    res.append(line)
                                    break
                                elif is_label.lower() == "n" or is_label.lower() == "no":
                                    break
                                else:
                                    print("The format of input is wrong. Please input again.")
                                    continue

                with open(os.path.join(mrxs_fille_name, i), 'w') as fd:
                    if res is not None:
                        res.reverse()
                    for re in res:
                        try:
                            # print("ok:", line[0])
                            line = re.toxml() + '\n'
                            if line.find('<?xml version="1.0" ?>') == 0:
                                line = line.replace('<?xml version="1.0" ?>', '')
                            #print(line)
                            fd.write(line)
                        except:
                            #print("Can't analysis the {}th line")
                            #print(re)
                            fd.write(re)
                            continue

                break

        if find_file_flag == 0:
            print("No .dat label file in mrxs {} which searched by magic tool.".format(mrxs_fille_name))
        osr.close()

    #return axis_list

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file_dir', type=str, help="The location of the mrxs file directory, as: /home/gytang/medicine/annotion/anotation-test-image/SHE .")
    args = parser.parse_args()
    #draw_rangcle_jpg(args.file_dir)
    alter_capption_main(args.file_dir)
    #alter_caption_main("/home/gytang/Downloads/res/other/")
