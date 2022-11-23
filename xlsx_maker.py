import pandas as pd


def xlsx_maker(id: str, dataframe: pd.DataFrame, directory: str, d_start, d_finish):
    id_dataframe = dataframe[(dataframe['carid'] == id) & (dataframe['mdate_time'].between(d_start, d_finish))]
    id_dataframe.to_csv(f'{directory}/IOTdata{id}.csv', sep=";", index=False, decimal=',')
    writer = pd.ExcelWriter(f'{directory}/IOTdata{id}.xlsx')
    id_dataframe.to_excel(writer, index=False)
    writer.save()
