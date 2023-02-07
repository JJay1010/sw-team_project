import glob
from PIL import ImageFile
from PIL import Image
import numpy as np
import shutil
from tqdm import tqdm
import cv2
import json

ImageFile.LOAD_TRUNCATED_IMAGES = True
classes = ['Ch01','Ch02', 'Ch04', 'Ch05', 'Ch06', 'Ch07']

# classes = ['Ch03']
data_dir = glob.glob('Validation/raw' + '/*.*')
label_dir = glob.glob('Validation/label/*/*.*')
# print(len(label_dir))
# print(len(data_dir))
for c in tqdm(classes):
    x, y = [], []
    for data_name in tqdm(data_dir[:-1]):
        name_split = data_name.split('_')
        status = name_split[5]
        disease_name = name_split[6]
        json_name = 'Validation/label/' + disease_name + '/'  + data_name[15:-4] + '.json'
        # print(json_name)
        with open(json_name, 'r', encoding='utf-8') as j:
            metadata = json.load(j)
            position = metadata['metadata']['Position']
            # print(position)
            if position == 'Lateral' and c == disease_name:
                try:
                    img = cv2.imread(data_name)
                    h, w, _ = img.shape
                    margin = [np.abs(w - h) // 2 , np.abs(w - h) // 2]
                    if w > h:
                        margin_list = [margin, [0,0]]
                    else:
                        margin_list = [[0,0], margin]
                        
                    if len(img.shape) == 3:
                        margin_list.append([0,0])
                    
                    output = np.pad(img, margin_list, mode='constant')
                    output = cv2.resize(output, (224,224))
                    x.append(output)
                    if status == 'NOR':
                        y.append(0)
                    else:
                        y.append(1)
                except:
                    continue
                
    x = np.array(x)
    y = np.array(y)
    # print(c, x.shape)
    # np.save(c + '_x_lateral', x)
    # np.save(c + '_y_lateral', y)
    np.save(c + '_x_Valid', x)
    np.save(c + '_y_Valid', y)
    
        # print(output.shape)
        # # print(disease_name, status, data_name[13:])
        # to = 'Validation/raw' + '/' + disease_name + '/' + status + '/' + data_name[13:]
        # # print(to)
        # cv2.imwrite(to, output)