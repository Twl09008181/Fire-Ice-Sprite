from PIL import Image
import os
 
dir_img = "./origin-Left/" 
#待处理的图片地址
dir_save = "./Right/"
#水平镜像翻转后保存的地址
 
list_img = os.listdir(dir_img)
 
for img_name in list_img:
    pri_image = Image.open(dir_img+img_name)
    tmppath = dir_save + img_name
    pri_image.transpose(Image.FLIP_LEFT_RIGHT).save(tmppath)
