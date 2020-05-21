#!/usr/bin/env python
# encoding:utf-8
"""
author: liusili
@contact: liusili@unionbigdata.com
@software:
@file: play_table
@time: 2020/4/17
@desc: 
"""
import pandas as pd
import os
import shutil
from tqdm import tqdm
import xml.etree.ElementTree as ET
import numpy as np
import json


class PlayTable(object):
    def __init__(self, table_path, sheet, index_col=0):
        """
        初始化
        :param table_path:
        """
        self.sheet = pd.read_excel(table_path, index_col=index_col, sheet_name=sheet)

    @staticmethod
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
            file_name = df.loc[i]['图片地址']
            if file_name is np.nan:
                continue
            img_name = file_name.split('/')[-1]
            xml_name = os.path.splitext(img_name)[0] + '.xml'

            img_path = os.path.join(sample_root, old_cat, img_name)
            # img_path = os.path.join(sample_root, img_name)
            xml_path = os.path.join(sample_root, old_cat, xml_name)

            new_cat_path = os.path.join(new_path, judge_cat)
            os.makedirs(new_cat_path, exist_ok=True)

            if os.path.isfile(img_path):
                new_img_path = os.path.join(new_cat_path, img_name)
                shutil.copyfile(img_path, new_img_path)

            if os.path.isfile(xml_path):
                new_xml_path = os.path.join(new_cat_path, xml_name)
                shutil.copyfile(xml_path, new_xml_path)

                # 更改xml标签信息
                tree = ET.parse(new_xml_path)
                root = tree.getroot()
                for obj in root.findall('object'):
                    name = self.get_and_check(obj, 'name', 1).text
                    if name == old_cat:
                        self.get_and_check(obj, 'name', 1).text = judge_cat
                tree.write(new_xml_path)

            pbar.set_description('Processing category {}'.format(old_cat))

        print('---End cleaning data---')

    def move_by_condition(self, sample_root, new_path, same=False,  **condition):
        os.makedirs(new_path, exist_ok=False)
        df = self.sheet
        pbar = tqdm(total=len(df))
        for row in df.itertuples():
            img_name = getattr(row, 'image_name')
            product = getattr(row, 'product')
            size = getattr(row, 'size')
            category = getattr(row, 'category')
            inference = getattr(row, 'inference')
            short = getattr(row, 'short')
            score = getattr(row, 'score')

            if img_name is np.nan:
                pbar.update(1)
                continue

            if 'product' in condition:
                if condition['product'] != product:
                    pbar.update(1)
                    continue

            if same:
                if category != inference:
                    pbar.update(1)
                    continue
            else:
                if category == inference:
                    pbar.update(1)
                    continue

            file_name = img_name.split('/')[-1]
            xml_name = os.path.splitext(file_name)[0] + '.xml'

            img_path = os.path.join(sample_root, category, img_name)
            xml_path = os.path.join(sample_root, category, xml_name)

            new_dir = os.path.join(new_path, category)
            os.makedirs(new_dir, exist_ok=True)

            if os.path.isfile(img_path):
                new_img_path = os.path.join(new_dir, img_name)
                shutil.copyfile(img_path, new_img_path)

            if os.path.isfile(xml_path):
                new_xml_path = os.path.join(new_dir, xml_name)
                shutil.copyfile(xml_path, new_xml_path)

            pbar.set_description('Processing image')
            pbar.update(1)

        print('---Finish moving data by condition---')

    def copy_files(self, new_path):
        os.makedirs(new_path, exist_ok=False)
        df = self.sheet
        for row in df.itertuples():
            file_path = row[1]
            file_name = row[2]
            new_file_path = os.path.join(new_path, file_name)
            shutil.copy(file_path, new_file_path)

        print('[FINISH] Files have been copied.')

    def get_confusion_matrix(self, deploy_path, out_path=None, **category_convert):
        category_path = os.path.join(deploy_path, 'classes.txt')
        json_path = os.path.join(deploy_path, 'rule.json')
        category = []
        for line in open(category_path, 'r'):
            temp_line = line.strip()
            if temp_line:
                category.append(temp_line)

        for cate in category_convert.keys():
            if cate in category:
                category.remove(cate)
                category.extend(category_convert[cate])

        category = sorted(list(set(category)))

        with open(json_path, 'r') as f:
            config = json.load(f)

        if config['other_name'] not in category:
            category.append(config['other_name'])

        if config['false_name'] not in category:
            category.append(config['false_name'])

        n = len(category)
        cm_df = pd.DataFrame(np.zeros([n, n], dtype=np.int), index=category, columns=category)

        deploy_df = self.sheet

        for i in deploy_df.index:
            cat = deploy_df.loc[i, 'category']
            predict = deploy_df.loc[i, 'inference']
            if cat not in category:
                continue
            cm_df.loc[cat, predict] += 1

        predict_sum = []
        ori_sum = []
        precision_lst = []
        recall_lst = []
        correct_lst = []

        for i in category:
            predict_cnt = sum(cm_df[i])
            ori_cnt = sum(cm_df.loc[i])
            predict_sum.append(predict_cnt)
            ori_sum.append(ori_cnt)
            correct = cm_df[i][i]
            correct_lst.append(correct)
            precision = round(correct / predict_cnt, 3)
            recall = round(correct / ori_cnt, 3)
            precision_lst.append(precision)
            recall_lst.append(recall)

        cm_df.loc['预测合计'] = predict_sum
        cm_df.loc['准确率'] = precision_lst
        cm_df['判图总量'] = ori_sum + [None] * 2
        cm_df['召回率'] = recall_lst + [None] * 2

        results_columns = ['判图总量', '预测合计', '一致数量', '准确率', '召回率']
        results_df = pd.DataFrame(index=category, columns=results_columns)
        results_df['判图总量'] = ori_sum
        results_df['预测合计'] = predict_sum
        results_df['一致数量'] = correct_lst
        results_df['准确率'] = precision_lst
        results_df['召回率'] = recall_lst

        writer = pd.ExcelWriter(out_path)
        results_df.to_excel(writer, sheet_name='Results')
        cm_df.to_excel(writer, sheet_name='CM')

        writer.save()

        print('[FINISH] Confusion matrix has been writen to path: {}.'.format(out_path))


if __name__ == '__main__':
    # --混淆矩阵-- #
    # table_path = r'D:\Working\Tianma\13902\TEST\0519\deploy_results.xlsx'
    # deploy_path = r'D:\Working\Tianma\13902\deploy\deploy_0519'
    # out_path = r'D:\Working\Tianma\13902\TEST\0519\13902_CM.xlsx'
    #
    # sheet = 'results'
    # category_convert = {'STR02': ['STR02O', 'STR02X'],
    #                     'STR05': ['STR05O', 'STR05X'],
    #                     'STR05B': ['STR05X']}
    #
    # playTable = PlayTable(table_path, sheet)
    # playTable.get_confusion_matrix(deploy_path, out_path, **category_convert)

    # --复制文件-- #
    # table_path = r'D:\Working\Tianma\13902\file\复判数据\13902_vote_2.xlsx'
    # new_path = r'D:\Working\Tianma\13902\data\13902_0426_judge_vote_2\difficult'
    # sheet = 'vote_2'
    # playTable = PlayTable(table_path, sheet)
    # playTable.copy_files(new_path)

    # --根据条件移动文件-- #
    table_path = r'D:\Working\Tianma\13902\TEST\0519\test_4\deploy_results.xlsx'
    sample_root = r'D:\Working\Tianma\13902\TEST\13902_testset'
    new_path = r'D:\Working\Tianma\13902\TEST\13902_testset_655'
    sheet = 'results'
    playTable = PlayTable(table_path, sheet)
    playTable.move_by_condition(sample_root, new_path, product='L3655B0408EB00')