from xml.dom.minidom import parseString
import magic
import os


def read_label(file_dir):
    axis_list = []
    for i in os.listdir(file_dir):
        a = magic.from_file(os.path.join(file_dir, i))

        if a == "ASCII text, with very long lines, with CRLF line terminators":
            with open(os.path.join(file_dir, i)) as f:
                lines = f.readlines()
            ID_name = []
            for idx, line in enumerate(lines[1:]):
                try:
                    line = parseString(line)
                except:
                    print("Can't analysis the {}th line".format(idx))
                    continue
                descript_lst = line.getElementsByTagName('descriptor')
                print('annotation_{}'.format(idx))
                for elements in descript_lst:
                    ID = elements.getAttribute('ID')
                    print('id_{}'.format(ID))
                    if ID not in ID_name:
                        ID_name.append(ID)
                        flag_lst = line.getElementsByTagName('slide_flag')
                        print('x1: {}, y1:{} ,x2:{}, y2:{}'.format(flag_lst[0].getAttribute('brLeft'), flag_lst[0].getAttribute('brTop'),
                              flag_lst[0].getAttribute('brRight'), flag_lst[0].getAttribute('brBottom')))
                        axis = []
                        axis.append(flag_lst[0].getAttribute('brLeft'))
                        axis.append(flag_lst[0].getAttribute('brTop'))
                        axis.append(flag_lst[0].getAttribute('brRight'))
                        axis.append(flag_lst[0].getAttribute('brBottom'))
                        axis_list.append({ID:axis})

                print('====================================================')
    return axis_list
