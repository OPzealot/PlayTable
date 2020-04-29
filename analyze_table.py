#!/usr/bin/env python
# encoding:utf-8
"""
author: liusili
@contact: liusili@unionbigdata.com
@software:
@file: analyze_table
@time: 2020/4/29
@desc: 
"""
import pandas as pd
import numpy as np


def analyze_vote_2(vote_2_path):
    df = pd.read_excel(vote_2_path, index_col=0, sheet_name='vote_2')
    for i in df.index:
        origin = df.loc[i]['origin']
        judge_1 = df.loc[i]['judge_1']
        judge_2 = df.loc[i]['judge_2']
        judge_3 = df.loc[i]['judge_3']
        judge_1 = judge_1 if judge_1 is not np.nan else origin
        judge_2 = judge_2 if judge_2 is not np.nan else origin
        judge_3 = judge_3 if judge_3 is not np.nan else origin
        if judge_1 == judge_2:
            final_judge = judge_1
        else:
            final_judge = judge_3
        df.loc[i, 'final_judge'] = final_judge
    print('Finish.')
    return df


if __name__ == '__main__':
    vote_2_path = r'D:\Working\Tianma\13902\file\复判数据\13902_vote_2.xlsx'
    out_path = r'D:\Working\Tianma\13902\file\复判数据\13902_vote_2_final_judge.xlsx'
    df = analyze_vote_2(vote_2_path)
    df.to_excel(out_path, sheet_name='vote_2')
