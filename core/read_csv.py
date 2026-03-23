"""游戏文本CSV读取模块"""
import pandas as pd
import os
from .text_classifier import TextClassifier


def read_csv(with_classification=True):
    """
    读取游戏文本CSV文件

    Args:
        with_classification: 是否添加文本分类信息

    Returns:
        DataFrame: 包含游戏文本的数据框
    """
    # 动态获取游戏路径和CSV文件路径
    from config import Config
    game_path = Config.get_game_path()

    if not game_path:
        columns = ['Offset_start', 'ZH_CN']
        if with_classification:
            columns.extend(['Category', 'Category_Name'])
        return pd.DataFrame(columns=columns)

    # 获取用户DAT文件夹下的CSV文件路径
    file_path = Config.get_extracted_texts_csv(game_path)

    # 如果文件不存在，返回空的DataFrame
    if not os.path.exists(file_path):
        columns = ['Offset_start', 'ZH_CN']
        if with_classification:
            columns.extend(['Category', 'Category_Name'])
        return pd.DataFrame(columns=columns)

    # CSV文件实际有9列，最后一列是行号
    df = pd.read_csv(
        file_path,
        usecols=['Offset_start', 'ZH_CN'],
        encoding='utf-8',
        names=["id_текста", "Offset_start", "JPN", "US", "ZH_CN", "ZH_TW", "KO", "ES", ""],
        header=0
    )

    # 按偏移量排序
    df = df.sort_values(by='Offset_start')

    # 添加分类信息
    if with_classification:
        df['Category'] = df['ZH_CN'].apply(TextClassifier.classify)
        df['Category_Name'] = df['Category'].apply(TextClassifier.get_category_name)
        df = df[['Offset_start', 'ZH_CN', 'Category', 'Category_Name']]
    else:
        df = df[['Offset_start', 'ZH_CN']]

    return df


if __name__ == '__main__':
    print(read_csv())
