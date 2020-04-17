#!/usr/bin/env python
# encoding:utf-8
"""
author: liusili
@contact: liusili@unionbigdata.com
@software:
@file: PlayTable
@time: 2020/4/17
@desc: 
"""
import pandas as pd
import os
import shutil
from tqdm import tqdm


class PlayTable(object):
    def __init__(self, table_path, sheet, index_col=0):
        """
        初始化
        :param table_path:
        """
        self.sheet = pd.read_excel(table_path, index_col=index_col, sheet_name=sheet)

    def move_judge(self, sample_root, dir_name='judge_correct'):
        """
        对复判完成后结果进行整理，与原类别不同的图片以及标签移动到对应新的目录中
        :param dir_name:
        :param sample_root:
        :return:
        """
        sample_root = sample_root.rstrip('\\')
        new_path = sample_root + '_' + dir_name
        os.makedirs(new_path, exist_ok=False)
        df = self.sheet
        print('---Start cleaning data---')
        pbar = tqdm(df.index)
        for i in pbar:
            old_cat = df.loc[i]['Auto Code']
            judge_cat = df.loc[i]['Manual Code']
            tmp_path = df.loc[i]['图片地址']
            img_name = tmp_path.split('/')[-1]
            xml_name = os.path.splitext(img_name)[0] + '.xml'

            img_path = os.path.join(sample_root, old_cat, img_name)
            xml_path = os.path.join(sample_root, old_cat, xml_name)

            new_cat_path = os.path.join(new_path, judge_cat)
            os.makedirs(new_cat_path, exist_ok=True)

            if os.path.isfile(img_path):
                new_img_path = os.path.join(new_cat_path, img_name)
                shutil.copyfile(img_path, new_img_path)

            if os.path.isfile(xml_path):
                new_xml_path = os.path.join(new_cat_path, xml_name)
                shutil.copyfile(xml_path, new_xml_path)

            pbar.set_description('Processing category {}'.format(old_cat))

        print('---End cleaning data---')

if __name__ == '__main__':
    table_path = r'D:\Working\Tianma\13902\file\复判数据\13902_0417复判结果.xlsx'
    sample_root = r'D:\Working\Tianma\13902\data\13902_0414_复判'
    sheet = '数据'
    playTable = PlayTable(table_path, sheet)
    playTable.move_judge(sample_root)
