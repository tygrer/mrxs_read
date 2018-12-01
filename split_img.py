from openslide import OpenSlide
from PIL import Image
from PIL import ImageDraw
import time

from read_label import read_label
import numpy as np
import random
import math
import os

def split_whole_img(max_length,firname):
    osr = OpenSlide(firname)
    props = osr.properties
    w, h = osr.level_dimensions[0]
    start_time = time.time()

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
    overlap_ratio = 100
    nums = round(w / max_length)
    overlap = round(max_length/overlap_ratio)

    def crop_image(nums,osr,w,h,max_length):
        image_info = {}
        image_list = []
        for i in range(nums):
            x1 = max(0, i * round(w / nums) - overlap)
            y1 = max(0, i * round(h / nums) - overlap)
            ww = min(w - (i * round(w / nums)), max_length + 2 * overlap)

            hh = min(h - (i * round(h / nums)), max_length + 2 * overlap)
            #print("ww:", ww)
            #print("hh:", hh)
            x2 = x1 + min(w - (i * round(w / nums)), max_length + 2 * overlap)
            y2 = y1 + min(h - (i * round(h / nums)), max_length + 2 * overlap)
            ww_ratio = max_length/float(ww)
            hh_ratio = max_length/float(hh)
            img = osr.read_region((x1, y1), 0, (round(ww), round(hh)))

            img = is_or_not_RGBA(img)
            thumb = img.resize((max_length, max_length), Image.ANTIALIAS)
            image_list.append(thumb)
            image_info = {"idex": i, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "w_ratio": ww_ratio, "h_ratio": hh_ratio}
            thumb.save("/home/gytang/img_split_result/" + str(i) + ".jpg", quality=100)
            npimage = np.array(thumb)
        return image_info, image_list

    image_info, image_list = crop_image(nums, osr, w, h, max_length)
    end_time = time.time() - start_time
    return image_list

def diff_to_jpeg(path, image_list):
    import cv2
    for ii in range(len(os.listdir(path))):
        if len(os.listdir(path)) != len(image_list):
            print("some thing wrong!")
        print(os.path.join(path, str(ii))+'.jpg')
        value_jpg = []
        value = []
        k = 0
        v = 0
        jjpeg = cv2.imread(os.path.join(path, str(ii))+'.jpg')
        print(np.array(image_list[ii]).shape)
        print(jjpeg.shape)
        for i in range(jjpeg.shape[0]):
            for j in range(jjpeg.shape[1]):
                if (jjpeg[i,j] != np.array(image_list[ii])[i,j]).any():
                    print("Not same!!!!!!!!!!")


def conver_axis_to_large_mrxs(xmin,ymin,xmax,ymax,mrxs_filename,image,index):
    overlap_ratio = 10
    osr = OpenSlide(mrxs_filename)
    props = osr.properties
    w, h = osr.level_dimensions[0]
    nums = round(w / image.shape(1))

    xmin_change = xmin/ww_ratio
    ymin_change = ymin/hh_ratio
    xmax_change = xmax/ww_ratio
    ymax_change = ymax/hh_ratio

    [x1+xmin_change, y1+ymin_change, x2+xmax_change, y2+ymax_change]
    return xmin,ymin,xmax,ymax


def split_region_around(max_length,image_num,file_dir):
    osr = OpenSlide(file_dir + '.mrxs')
    props = osr.properties
    axis_list = read_label(file_dir)

    for ID, axis in axis_list:
        print("axis:", axis)
        width = float(axis[2]) - float(axis[0])
        height = float(axis[3]) - float(axis[1])
        print("width:", width, ",height:", height)
        label_list = []
        for i in range(image_num):
            #print(props)
            radioX = random.uniform(0, 1 - width / max_length)
            radioY = random.uniform(0, 1 - height / max_length)
            crop_xl = math.floor(max(float(axis[0]) - max_length * radioX, 0))
            crop_yl = math.floor(max(float(axis[1]) - max_length * radioY, 0))
            crop_xr = crop_xl + max_length
            crop_yr = crop_yl + max_length
            #print("crop_xl:", crop_xl)
            img = osr.read_region((crop_xl, crop_yl), 0,
                                  (max_length, max_length)).convert("RGB")
            #draw = ImageDraw.Draw(img)
            #draw.rectangle((radioX * max_length, radioY * max_length, width, height), None, "red")
            labelxmin = math.floor(radioX*max_length)
            labelymin = math.floor(radioY*max_length)
            labelxmax = math.floor(radioX*max_length + width)
            labelymax = math.floor(radioY*max_length + height)
            label_list.append([labelxmin, labelymin, labelxmax, labelymax])
            for ID_other, axis_other in axis_list:
                width_other = float(axis_other[2]) - float(axis_other[0])
                height_other = float(axis_other[3]) - float(axis_other[1])
                labelxmin_other = max(math.floor(axis_other[0]), crop_xl)
                labelymin_other = max(math.floor(axis_other[1]), crop_yl)
                labelxmax_other = min(math.floor(axis_other[2]), crop_xr)
                labelymax_other = min(math.floor(axis_other[3]), crop_yr)
                if labelxmin_other == labelxmin and labelymin_other == labelymin and labelxmax_other == labelxmax \
                        and labelymax_other == labelymax:
                    continue
                if width_other > max_length or height_other > max_length:
                    logger.error("The label box is too large, its width or height is bigger than the crop max /"
                                 "length {}".format(max_length))
                    continue
                label_list.append([labelxmin_other, labelymin_other, labelxmax_other, labelymax_other])

            #img.show()
            #img.save("/home/gytang/img_split_result/" + ID + str(i) + ".jpg", quality=100)


if __name__ == "__main__":
    #split_whole_img()
    file_dir = "/home/gytang/medicine/annotion/anotation-test-image/SHE.mrxs"
    image_list = split_whole_img(1000, file_dir)
    diff_to_jpeg('/home/gytang/img_split_result/', image_list)
    #split_region_around(3000, 200, file_dir)

# if (labelxmax>axis_other[0]>labelxmin and labelymax>axis_other[1]>labelymin):
#
# elif(labelxmax>(axis_other[2])>labelxmin and labelymax>axis_other[1]>labelymin):
#
# elif(labelxmax>(axis_other[0])>labelxmin and labelymax>axis_other[3]>labelymin):
#
# elif(labelxmax>(axis_other[2])>labelxmin and labelymax>axis_other[3]>labelymin):
#     example = tf.train.Example(features=tf.train.Features(
#         feature={
#             'image/encoded': _bytes_feature(img_raw),
#             'image/format': _bytes_feature(img_format),
#             'image/label': _int64_feature(0),
#             'image/height': _int64_feature(height),
#             'image/width': _int64_feature(width),
#             'image/channel': _int64_feature(channel),
#             'bbox/xmin': _int64_feature(xmin),
#             'bbox/ymin': _int64_feature(ymin),
#             'bbox/xmax': _int64_feature(xmax),
#             'bbox/ymax': _int64_feature(ymax),
#             'difficult': _int64_feature(0),
#             'truncated': _int64_feature(0)
#         }))