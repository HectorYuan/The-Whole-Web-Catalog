#%% 导入必要库
import pandas as pd
import datetime

#%% 进行转换处理
def csv2df(file_path):

    '''将带有网址信息的csv文件进行初步处理，并转换为dataframe对象'''
    columns = ['名称', '介绍', '地址', '场景', '形态', '推荐','标签', 
        '网站质量', '访问方式','排名']

    df = pd.read_csv(file_path,usecols=columns)
    df['名称'] =  df.apply(lambda x: '['+ str(x['名称']) + '](' + str(x['地址'])+r') | `'+ str(x['推荐']) + r'` | `' + str(x['网站质量'])+'`', axis=1)
    df['标签'] = df.apply(lambda x: str(x['标签']) +', '+ str(x['访问方式']) ,axis=1)
    df = df.sort_values(['排名','访问方式'],ascending=True).drop(columns=['排名','地址','推荐','网站质量','访问方式'])

    return df

def df2dict(df, string):    

    '''将dataframe对象变为字典对象'''
    df_info = df[string].value_counts().to_dict()
    df = df.fillna(f'`ToBeDone`')
    dfs = {key:df[df[string] == key].drop(columns=[string]) for key in df_info.keys()}

    for value in dfs.values():
        value = value.to_dict('records')

    dfs_dict = {key: value.to_dict('records') for key, value in dfs.items()}

    return [dfs_dict,dfs,df_info]

def main_writer(file_path):
    '''整合以上函数，将数据文件最终变为md文件'''

    now_time = datetime.datetime.now().strftime('%Y%m%d%H')
    file_name = file_path.split(' ')[0] + now_time

    base = csv2df(file_path)
    base_dfs_dict = df2dict(base, '场景')[0]
    base_dfs= df2dict(base, '场景')[1]
    base_info = df2dict(base, '场景')[2]

    extend_dicts = {key: df2dict(value, '形态')[0] for key,value in base_dfs.items()}
    extend_infos = {key: df2dict(value, '形态')[2] for key,value in base_dfs.items()}

    with open(f'{file_name}.md','w', encoding='utf-8') as f:
        f.write('# 互联网漫游指南\n\n')
        f.write('{:toc}\n\n')
        f.write(f'## 场景概况\n\n')
        for key, value in base_info.items():
            f.write(f'> [{key}]({key}场景汇总.md) --- 共计 {value}\n\n')

    def two_layer(dicts = extend_dicts):
        for key_1, dictsets in dicts.items():
            with open(f'{key_1}场景汇总.md','w',encoding='utf-8') as f:
                f.write(f'# {key_1}场景网站列表\n\n')
                f.write(f'\n## 类别概况\n\n')
                for info_key,info_value in extend_infos[key_1].items():
                    f.write(f'> {info_key} --- 共计 {info_value}\n\n')
                for key_2, value_2 in dictsets.items():
                    f.write(f'\n## {key_2}类\n\n')
                    for dict in value_2:
                        for key, value in dict.items():
                            if key == '名称':
                                f.write(f'\n\n### {value}\n')
                            elif key == '介绍':
                                f.write(f'\n> {value}\n')
                            elif key == '标签':
                                list = [f'`{i}`' for i in value.split(', ')]
                                value = '  '.join(list)
                                f.write(f'\n主要特性: {value}\n')
                            else:
                                f.write(f'\n{key}: {value}\n')
                        f.write(f'\n---')

    two_layer()           

    return extend_dicts, extend_infos

file_path = r'互联网漫游指南 1e6e510f75aa4cd9a80191e68fccccff.csv'
extend_dicts, extend_infos = main_writer(file_path)
