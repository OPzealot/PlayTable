#!/usr/bin/env python
# encoding:utf-8
"""
author: liusili
@contact: liusili@unionbigdata.com
@software:
@file: create_table
@time: 2020/4/24
@desc: 
"""
import os
import pandas as pd
from tqdm import tqdm


def create_table(sample_root, img_format='.jpg'):
    columns = ['path', 'file_name', 'origin']
    df = pd.DataFrame(columns=columns)
    id = 0
    pbar = tqdm(os.walk(sample_root))
    for root, _, file_lst in pbar:
        if len(file_lst) > 0:
            category = root.split(sample_root + '\\')[-1]
            for file in file_lst:
                if os.path.splitext(file)[-1] == img_format:
                    img_path = os.path.join(sample_root, file)
                    id += 1
                    df.loc[id] = [img_path, file, category]
            pbar.set_description('Processing category [{}]:'.format(category))

    print('[FINISH] Table has been created.')
    return df


def add_judge(dataframe, judge_path, judge='judge'):
    df = dataframe
    judge_df = pd.read_excel(judge_path, index_col=0, sheet_name='数据')
    for row in judge_df.itertuples():
        judge_code = row[5]
        judge_path = row[6]
        file_name = judge_path.split('/')[-1]
        df.loc[df['file_name'] == file_name, judge] = judge_code
    print('[FINISH] Judge result has been added.')
    return df


def add_change(dataframe, judge_list=None):
    df = dataframe
    index_lst = 0
    for judge in judge_list:
        index_lst = index_lst | df[judge].notnull()
    df_change = df[index_lst]
    print('[FINISH] Change result has been added.')
    return df_change


def add_logic(dataframe, mode='all_different'):
    df = dataframe
    if mode == 'all_different':
        index_lst = (df['judge_1'] != df['judge_2']) & (df['judge_1'] != df['judge_3']) \
                    & (df['judge_2'] != df['judge_3']) & \
                    ((df['judge_1'].notnull() & df['judge_2'].notnull())
                     | (df['judge_1'].notnull() & df['judge_3'].notnull())
                     | (df['judge_2'].notnull() & df['judge_3'].notnull()))
    if mode == 'all_same':
        index_lst = (df['judge_1'] == df['judge_3']) & (df['judge_1'] == df['judge_3']) \
                    & (df['judge_2'] == df['judge_3'])
    if mode == 'vote_2':
        index_lst = (df['judge_1'] == df['judge_2']) | (df['judge_1'] == df['judge_3']) \
                    | (df['judge_2'] == df['judge_3']) \
                    | (df['judge_1'].isnull() & df['judge_2'].isnull()) \
                    | (df['judge_1'].isnull() & df['judge_3'].isnull()) \
                    | (df['judge_2'].isnull() & df['judge_3'].isnull())
    df = df[index_lst]
    return df

if __name__ == '__main__':
    sample_root = r'D:\Working\Tianma\13902\data\13902_0414_judge'
    judge_path = r'D:\Working\Tianma\13902\file\复判数据\13902_3.xlsx'
    table_path = r'D:\Working\Tianma\13902\file\复判数据\13902_change.xlsx'
    out_path = r'D:\Working\Tianma\13902\file\复判数据\13902_vote_2.xlsx'
    # df = create_table(sample_root)
    df = pd.read_excel(table_path, index_col=0, sheet_name='change')
    df = add_logic(df, mode='vote_2')
    # df = add_judge(df, judge_path, judge='judge_3')
    judge_list = ['judge_1', 'judge_2', 'judge_3']
    # df = add_change(df, judge_list)
    df.to_excel(out_path, sheet_name='vote_2')