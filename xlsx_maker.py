import pandas as pd

def xlsx_maker(id: str, dataframe: pd.DataFrame):
    dataframe.to_csv(f'c://IOTdata/IOTdata{id}.csv', sep=";", index=False, decimal=',')
    writer = pd.ExcelWriter(f'c://IOTdata/IOTdata{id}.xlsx')
    dataframe.to_excel(writer, index=False)
    writer.save()
