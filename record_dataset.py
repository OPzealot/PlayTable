#!/usr/bin/env python
# encoding:utf-8
"""
author: liusili
@contact: liusili@unionbigdata.com
@software:
@file: record_dataset
@time: 2020/5/8
@desc: 
"""
import xml.etree.ElementTree as ET
import os
import pandas as pd
from tqdm import tqdm


def get_and_check(root, name, length):
    """
    :param root: Element-tree 根节点
    :param name: 需要返回的子节点名称
    :param length: 确认子节点长度
    """
    var_lst = root.findall(name)
    if len(var_lst) == 0:
        raise NotImplementedError('Can not find %s in %s.' % (name, root.tag))
    if (length > 0) and (len(var_lst) != length):
        raise NotImplementedError('The size of %s is supposed to be %d, but is %d.'
                                  % (name, length, len(var_lst)))
    if length == 1:
        var_lst = var_lst[0]
    return var_lst


def get_info_from_xml(xml_path, mode='max_area'):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    area = 0

    category = None
    bbox_out =None

    for obj in root.findall('object'):
        bbox = get_and_check(obj, 'bndbox', 1)
        xmin = int(get_and_check(bbox, 'xmin', 1).text)
        ymin = int(get_and_check(bbox, 'ymin', 1).text)
        xmax = int(get_and_check(bbox, 'xmax', 1).text)
        ymax = int(get_and_check(bbox, 'ymax', 1).text)
        bbox_area = (xmax - xmin + 1) * (ymax - ymin + 1)
        if mode == 'max_area':
            if bbox_area > area:
                area = bbox_area
                category = get_and_check(obj, 'name', 1).text
                bbox_out = [xmin, ymin, xmax, ymax]

    return category, bbox_out


def record_dataset(sample_root, img_format='.jpg'):
    columns = ['file_name', 'category', 'bbox']
    df = pd.DataFrame(columns=columns)
    id = 0
    for root, _, file_lst in os.walk(sample_root):
        if len(file_lst) > 0:
            pbar = tqdm(file_lst)
            for file in pbar:
                if os.path.splitext(file)[-1] == img_format:
                    img_file = file
                    file_name = os.path.splitext(file)[0]
                    xml_path = os.path.join(root, file_name + '.xml')
                    if os.path.isfile(xml_path):
                        category, bbox = get_info_from_xml(xml_path)
                        id += 1
                        df.loc[id] = [img_file, category, bbox]
                pbar.set_description('Processing cateogry [{}]'.format(category))

    record_path = sample_root + '_record.xlsx'
    df.to_excel(record_path, sheet_name='data')
    print('[FINISH] Dataset has been recorded.')


def record_product(sample_root, img_format='.jpg'):
    columns = ['image_name', 'product', 'category']
    df = pd.DataFrame(columns=columns)
    id = 0
    for root, _, file_lst in os.walk(sample_root):
        if len(file_lst) > 0:
            pbar = tqdm(file_lst)
            for file in pbar:
                if os.path.splitext(file)[-1] == img_format:
                    info_lst = root.split('\\')
                    product = info_lst[-3]
                    cat = info_lst[-1]
                    category = cat.split('-')[-1]
                    id += 1
                    df.loc[id] = [file, product, category]
                    pbar.set_description('Processing cateogry [{}]'.format(category))

    product_path = sample_root + '_product.xlsx'
    df.to_excel(product_path, sheet_name='product')
    print('[FINISH] Product information has been recorded.')


if __name__ == '__main__':
    sample_root = r'D:\Working\Tianma\13902\TEST\13902_testset'
    record_dataset(sample_root)
