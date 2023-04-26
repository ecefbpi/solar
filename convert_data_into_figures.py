import pandas as pd
from datetime import datetime
import plotly.io as pio
import os, zipfile
from os import path
from os import devnull
import shutil
import xlrd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import time
from dash_bootstrap_templates import load_figure_template


pd.set_option('mode.chained_assignment', None)
load_figure_template('DARKLY')


def funcConsCons(x):
    y = x.replace(',', '.')
    return float(y)


def funcHoraCons(x):
    if len(x) == 1:
        y = '0' + x + ':00:00'
    else:
        y = x + ':00:00'
    return y


def loadConsum(file):

    dateparser = lambda x: datetime.strptime(x, '%d/%m/%Y')

    dfCons = pd.read_csv(file, sep=';', parse_dates=['Fecha'],
                         usecols = ['Fecha', 'Hora', 'Consumo_kWh'],
                         converters={'Consumo_kWh': funcConsCons, 'Hora': funcHoraCons},
                         date_parser=dateparser)


    dfCons['fecha'] = dfCons['Fecha'] + pd.to_timedelta(dfCons['Hora']) - pd.to_timedelta(1, unit='h')
    dfCons = dfCons[['fecha', 'Consumo_kWh']]
    dfCons.rename(columns = {'Consumo_kWh':'consumo'}, inplace = True)
    dfConsCalc = dfCons[['fecha', 'consumo']]
    dfCons['mes'] = dfCons['fecha'].apply(lambda x:x.month)
    dfCons['dia'] = dfCons['fecha'].apply(lambda x:x.weekday())
    dfCons['hora'] = dfCons['fecha'].apply(lambda x:x.hour)

    df_per_month = dict()
    for month in dfCons['mes'].unique():
        df_per_month[month] = dfCons[dfCons['mes'] == month]

    dataCons = dict()
    for month in df_per_month.keys():
        dataCons[month] = dict()
        dfweek = df_per_month[month].loc[(df_per_month[month]['dia'] != 5) & (df_per_month[month]['dia'] != 6)]
        dfweekend = df_per_month[month].loc[(df_per_month[month]['dia'] == 5) | (df_per_month[month]['dia'] == 6)]
        dataCons[month]['week_day'] = dfweek.groupby(['hora']).mean().drop(columns=['mes', 'dia'])
        dataCons[month]['weekend_day'] = dfweekend.groupby(['hora']).mean().drop(columns=['mes', 'dia'])
        dataCons[month]['total'] = df_per_month[month].groupby(['hora']).mean().drop(columns=['mes', 'dia'])

    return dataCons, dfConsCalc

def loadProdReal(file):

    dateparserReal = lambda x: datetime.strptime(x, '%m/%d/%Y %H:%M')

    dfReal1 = pd.read_csv(file, parse_dates=[0],
                          usecols=[0, 1], names=['fecha', 'prod'],
                          header=0, date_parser=dateparserReal)

    dfReal1.set_index('fecha', inplace= True)
    dfReal2 = dfReal1.resample('H').sum()
    dfReal2.reset_index(inplace=True)

    dfReal2['mes'] = dfReal2['fecha'].apply(lambda x:x.month)
    dfReal2['hora'] = dfReal2['fecha'].apply(lambda x:x.hour)

    dfRealCalcTmp = dfReal2[['fecha', 'prod']]
    dfRealCalcTmp['prod'] = dfRealCalcTmp['prod'].apply(lambda x:x/1000)
    dfRealCalcTmp.rename(columns = {'prod':'prod5'}, inplace = True)
    dfRealCalcTmp['fecha'] = dfRealCalcTmp['fecha'].apply(lambda x: x.replace(year=2022) if x.year == 2023 else x.replace(year=x.year))
    dfRealCalcTmp.sort_values(by='fecha', inplace=True)
    dfRealCalcTmp['mes'] = dfRealCalcTmp['fecha'].apply(lambda x: x.month)
    dfRealCalcTmp['dia'] = dfRealCalcTmp['fecha'].apply(lambda x: x.day)
    dfRealCalcTmp['hora'] = dfRealCalcTmp['fecha'].apply(lambda x: x.hour)
    dfMarMay = dfRealCalcTmp.loc[(dfRealCalcTmp['mes'] == 3) | (dfRealCalcTmp['mes'] == 5)]
    MarMayAvg = dfMarMay.groupby(['hora']).mean()['prod5']
    fecha = pd.date_range(start='2022-03-30 00:00:00', end='2022-05-15 23:00:00', freq='H')
    dftmp = pd.DataFrame(data=fecha, columns=['fecha'])
    dftmp['prod5'] = dftmp['fecha'].apply(lambda x: MarMayAvg[x.hour])
    dftmp['mes'] = dftmp['fecha'].apply(lambda x: x.month)
    dftmp['dia'] = dftmp['fecha'].apply(lambda x: x.day)
    dftmp['hora'] = dftmp['fecha'].apply(lambda x: x.hour)
    dfRealCalc = pd.concat([dfRealCalcTmp, dftmp], ignore_index=True)
    dfRealCalc.sort_values(by='fecha', inplace=True)
    dfRealCalc['prod1'] = dfRealCalc['prod5'].apply(lambda x: x / 5)
    dfRealCalc['prod2'] = dfRealCalc['prod1'].apply(lambda x: x * 2)
    dfRealCalc['prod3'] = dfRealCalc['prod1'].apply(lambda x: x * 3)
    dfRealCalc['prod4'] = dfRealCalc['prod1'].apply(lambda x: x * 4)
    dfRealCalc.drop(columns=['mes', 'dia', 'hora'], inplace=True)

    df_per_month_prodReal5 = dict()
    df_per_month_prodReal1 = dict()
    df_per_month_prodReal2 = dict()
    df_per_month_prodReal3 = dict()
    df_per_month_prodReal4 = dict()
    for month in dfReal2['mes'].unique():
        df_per_month_prodReal5[month] = dfReal2[dfReal2['mes'] == month]
        df_per_month_prodReal1[month] = dfReal2[dfReal2['mes'] == month]
        df_per_month_prodReal2[month] = dfReal2[dfReal2['mes'] == month]
        df_per_month_prodReal3[month] = dfReal2[dfReal2['mes'] == month]
        df_per_month_prodReal4[month] = dfReal2[dfReal2['mes'] == month]

    dataProdReal5 = dict()
    dataProdReal1 = dict()
    dataProdReal2 = dict()
    dataProdReal3 = dict()
    dataProdReal4 = dict()
    for month in df_per_month_prodReal5.keys():
        dataProdReal5[month] = dict()
        dataProdReal5[month] = df_per_month_prodReal5[month].groupby(['hora']).mean().drop(columns=['mes'])
    for month in df_per_month_prodReal1.keys():
        dataProdReal1[month] = dict()
        dataProdReal1[month] = df_per_month_prodReal1[month].groupby(['hora']).mean().drop(columns=['mes'])
    for month in df_per_month_prodReal2.keys():
        dataProdReal2[month] = dict()
        dataProdReal2[month] = df_per_month_prodReal2[month].groupby(['hora']).mean().drop(columns=['mes'])
    for month in df_per_month_prodReal3.keys():
        dataProdReal3[month] = dict()
        dataProdReal3[month] = df_per_month_prodReal3[month].groupby(['hora']).mean().drop(columns=['mes'])
    for month in df_per_month_prodReal4.keys():
        dataProdReal4[month] = dict()
        dataProdReal4[month] = df_per_month_prodReal4[month].groupby(['hora']).mean().drop(columns=['mes'])

    dataProdReal5[4] = pd.concat([dataProdReal5[3], dataProdReal5[5]], axis=1)
    dataProdReal5[4]['mean'] = dataProdReal5[4].mean(axis=1)
    dataProdReal5[4].drop(columns=['prod','prod'], inplace = True)
    dataProdReal5[4].rename(columns = {'mean':'prod'}, inplace = True)

    dataProdReal1[4] = pd.concat([dataProdReal1[3], dataProdReal1[5]], axis=1)
    dataProdReal1[4]['mean'] = dataProdReal1[4].mean(axis=1)
    dataProdReal1[4].drop(columns=['prod','prod'], inplace = True)
    dataProdReal1[4].rename(columns = {'mean':'prod'}, inplace = True)

    dataProdReal2[4] = pd.concat([dataProdReal2[3], dataProdReal2[5]], axis=1)
    dataProdReal2[4]['mean'] = dataProdReal2[4].mean(axis=1)
    dataProdReal2[4].drop(columns=['prod','prod'], inplace = True)
    dataProdReal2[4].rename(columns = {'mean':'prod'}, inplace = True)

    dataProdReal3[4] = pd.concat([dataProdReal3[3], dataProdReal3[5]], axis=1)
    dataProdReal3[4]['mean'] = dataProdReal3[4].mean(axis=1)
    dataProdReal3[4].drop(columns=['prod','prod'], inplace = True)
    dataProdReal3[4].rename(columns = {'mean':'prod'}, inplace = True)

    dataProdReal4[4] = pd.concat([dataProdReal4[3], dataProdReal4[5]], axis=1)
    dataProdReal4[4]['mean'] = dataProdReal4[4].mean(axis=1)
    dataProdReal4[4].drop(columns=['prod','prod'], inplace = True)
    dataProdReal4[4].rename(columns = {'mean':'prod'}, inplace = True)

    for month in dataProdReal5.keys():
        dataProdReal5[month]['prod'] = dataProdReal5[month]['prod'].apply(lambda x: x/1000)

    for month in dataProdReal1.keys():
        dataProdReal1[month]['prod'] = dataProdReal5[month]['prod'].apply(lambda x: x/5)

    for month in dataProdReal2.keys():
        dataProdReal2[month]['prod'] = dataProdReal1[month]['prod'].apply(lambda x: x*2)

    for month in dataProdReal3.keys():
        dataProdReal3[month]['prod'] = dataProdReal1[month]['prod'].apply(lambda x: x*3)

    for month in dataProdReal4.keys():
        dataProdReal4[month]['prod'] = dataProdReal1[month]['prod'].apply(lambda x: x*4)

    #return_dict = {'dataProdReal1': dataProdReal1, 'dataProdReal2': dataProdReal2, 'dataProdReal3': dataProdReal3,
    #               'dataProdReal4': dataProdReal4, 'dataProdReal5': dataProdReal5, 'dfRealCalc': dfRealCalc}
    return_list = [dataProdReal1, dataProdReal2, dataProdReal3, dataProdReal4, dataProdReal5]
    return return_list, dfRealCalc


def funcPVPC(x):
    y = round(float(x)/1000, 3)
    return float(y)

def funcHoraPVPC(x):
    y = str(int(x))
    if len(y) == 1:
        z = '0' + y + ':00:00'
    else:
        z = y + ':00:00'
    return z


def loadPVPC(file):

    working_dir = './tmp'

    if path.exists(working_dir):
        shutil.rmtree(working_dir)
    os.mkdir(working_dir)

    file_name = os.path.abspath(file) # get full path of files
    zip_ref = zipfile.ZipFile(file_name) # create zipfile object
    zip_ref.extractall(working_dir) # extract file to dir
    zip_ref.close() # close file

    files = os.listdir(working_dir)

    pvpcDfs = list()
    for file in files:
        wb = xlrd.open_workbook(working_dir + '/' + file, logfile=open(devnull, 'w'))
        df = pd.read_excel(wb,
                       skiprows= 4, usecols= [0, 1, 4],
                       names= ['fecha', 'hora', 'pvpc'],
                       converters={'pvpc': funcPVPC, 'hora': funcHoraPVPC},
                       engine='xlrd')
        df['fecha2'] = df['fecha'] + pd.to_timedelta(df['hora']) - pd.to_timedelta(1, unit='h')
        df.dropna(inplace= True)
        df = df[['fecha2', 'pvpc']]
        df.rename(columns = {'fecha2':'fecha'}, inplace = True)
        pvpcDfs.append(df)
        dfPVPCtmp = pd.concat(pvpcDfs, ignore_index=True)
        dfPVPCtmp.sort_values(by='fecha', inplace=True)
        dfPVPCtmp['pvpc'] = dfPVPCtmp['pvpc'].astype(float)

    if path.exists(working_dir):
        shutil.rmtree(working_dir)

    dataPVPC = dfPVPCtmp

    return dataPVPC


def funcHoraExc(x):
    # 2022-01-01T00:00:00+01:00
    return x.split('+')[0]


def funcPrecExc(x):
    # 145.16
    return float(x) / 1000


def loadExc(file):

    dfPrecExcTmp = pd.read_csv(file, sep=';',
                               usecols=[4, 5], names=['precioExced', 'fecha'],
                               header=0, converters={'fecha': funcHoraExc, 'precioExced': funcPrecExc})

    dfPrecExcTmp['fecha'] = pd.to_datetime(dfPrecExcTmp['fecha'], format='%Y-%m-%dT%H:%M:%S')
    dfPrecExc = dfPrecExcTmp[['fecha', 'precioExced']]

    return dfPrecExc


def plotData(dataCons, dataProd, maxRange, legendName):
    kw_str = legendName.split('_')[1].rstrip('kw')
    # CALCULO DE PORCENTAJES DE CONSUMO
    # SOBRE EL TOTAL DE PRODUCCION
    # =================================

    # Prepare invisible line for fill trick
    porcentaje = dict()

    for row, month in enumerate(dataCons.keys()):
        porcentaje[month] = dict()
        consumo_total = dataCons[month]['total']['consumo'].tolist()
        produccion = dataProd[month]['prod'].tolist()

        consumido_total = [p if c >= p else c for c, p in zip(consumo_total, produccion)]

        porcentaje[month]['total'] = round((sum(consumido_total) / sum(produccion)) * 100, 1)

    # VISUALIZACION
    # =============
    plots_titles = [MONTH_STR[x] for x in MONTH_STR.keys()]

    figDict = dict()
    cols = px.colors.qualitative.Dark24

    # Prepare invisible line for fill trick
    y_inv_total_month = dict()

    for row, month in enumerate(dataCons.keys()):
        figDict[month] = go.Figure()
        x_prod = dataProd[month].index.tolist()
        y_prod = dataProd[month]['prod'].tolist()
        xtot = dataCons[month]['total'].index.tolist()
        ytot = dataCons[month]['total']['consumo'].tolist()
        y_inv_total = [b if a >= b else a for a, b in zip(ytot, y_prod)]

        # consumption
        figDict[month].add_trace(go.Scatter(
            x=xtot,
            y=ytot,
            line=dict(width=2, color=cols[0]),
            showlegend=True,
            legendgroup='consumo',
            name="cons"
            )
        )
        # invisible line
        figDict[month].add_trace(go.Scatter(
            x=xtot,
            y=y_inv_total,
            line_color="rgba(0,0,0,0)",
            showlegend=False,
            legendgroup='produccion',
            fill='tozeroy',
            fillcolor='red'
            )
        )
        # production
        figDict[month].add_trace(go.Scatter(
            x=x_prod,
            y=y_prod,
            line=dict(width=2, color='red'),
            showlegend=True,
            legendgroup='produccion',
            name=legendName
            )
        )
        figDict[month].update_xaxes(title_text="Day's hour")
        figDict[month].update_yaxes(title_text="kWh")
        # add annotation
        figDict[month].add_annotation(xref='x domain',
                           yref='y domain',
                           x=0.95,
                           y=0.9,
                           text=str(porcentaje[month]['total']) + '%',
                           font={'size': 16,
                                 'color': 'red'},
                           showarrow=False,
                           )

        figDict[month].update_yaxes(range=[-0.1, maxRange + 0.3])

        text_title = "Production vs Consumption Curves (" + kw_str + "kw)<br><b>- " +  MONTH_STR[month] + " -</b>"
        figDict[month]['layout'].update(
                             title={
                                 'text': text_title,
                                 'font_size': 18,
                                 'x': 0.5,
                                 'xanchor': 'center',
                                 'yanchor': 'top'}
                             )


    return figDict


def gastoReal(row):
    return row.consumo * row.pvpc


def gastoProd1(row):
    if row.prod1 <= row.consumo:
        return (row.consumo - row.prod1) * row.pvpc
    else:
        return -((row.prod1 - row.consumo) * row.precioExced)


def gastoProd2(row):
    if row.prod2 <= row.consumo:
        return (row.consumo - row.prod2) * row.pvpc
    else:
        return -((row.prod2 - row.consumo) * row.precioExced)


def gastoProd3(row):
    if row.prod3 <= row.consumo:
        return (row.consumo - row.prod3) * row.pvpc
    else:
        return -((row.prod3 - row.consumo) * row.precioExced)


def gastoProd4(row):
    if row.prod4 <= row.consumo:
        return (row.consumo - row.prod4) * row.pvpc
    else:
        return -((row.prod4 - row.consumo) * row.precioExced)


def gastoProd5(row):
    if row.prod5 <= row.consumo:
        return (row.consumo - row.prod5) * row.pvpc
    else:
        return -((row.prod5 - row.consumo) * row.precioExced)


def excedentes1(row):
    if row['prod1'] <= row['consumo']:
        return 0
    else:
        return round(row['prod1'] - row['consumo'], 2)


def excedentes2(row):
    if row['prod2'] <= row['consumo']:
        return 0
    else:
        return round(row['prod2'] - row['consumo'], 2)


def excedentes3(row):
    if row['prod3'] <= row['consumo']:
        return 0
    else:
        return round(row['prod3'] - row['consumo'], 2)


def excedentes4(row):
    if row['prod4'] <= row['consumo']:
        return 0
    else:
        return round(row['prod4'] - row['consumo'], 2)


def excedentes5(row):
    if row['prod5'] <= row['consumo']:
        return 0
    else:
        return round(row['prod5'] - row['consumo'], 2)


def calculateSaving(dfCons, dfProd, dfPVPC, dfExec):
    month_str = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
                 12: 'December'}
    dftmp1 = dfCons.merge(dfProd, on='fecha', how='inner')
    dftmp2 = dftmp1.merge(dfPVPC, on='fecha', how='inner')
    dftmp3 = dftmp2.merge(dfExec, on='fecha', how='inner')

    dftmp3['gasto_real'] = dftmp3.apply(gastoReal, axis=1)
    dftmp3['gasto_prod1'] = dftmp3.apply(gastoProd1, axis=1)
    dftmp3['gasto_prod2'] = dftmp3.apply(gastoProd2, axis=1)
    dftmp3['gasto_prod3'] = dftmp3.apply(gastoProd3, axis=1)
    dftmp3['gasto_prod4'] = dftmp3.apply(gastoProd4, axis=1)
    dftmp3['gasto_prod5'] = dftmp3.apply(gastoProd5, axis=1)
    dftmp3['excedentes1'] = dftmp3.apply(excedentes1, axis=1)
    dftmp3['excedentes2'] = dftmp3.apply(excedentes2, axis=1)
    dftmp3['excedentes3'] = dftmp3.apply(excedentes3, axis=1)
    dftmp3['excedentes4'] = dftmp3.apply(excedentes4, axis=1)
    dftmp3['excedentes5'] = dftmp3.apply(excedentes5, axis=1)

    dftmp3.set_index('fecha', inplace= True)
    dfSavingsM = dftmp3.resample('M').sum().round(2)
    dfSavingsY = dftmp3.resample('A').sum().round(2)
    dfAvgPricesM = dftmp3.resample('M').mean().round(2)
    dfAvgPricesY = dftmp3.resample('Y').mean().round(2)
    dftmp3.reset_index(inplace=True)
    dfSavingsM.reset_index(inplace=True)
    dfSavingsY.reset_index(inplace=True)
    dfAvgPricesM.reset_index(inplace=True)
    dfAvgPricesY.reset_index(inplace=True)

    dfAvgPricesM.drop(columns=['consumo', 'prod1', 'prod2', 'prod3', 'prod4', 'prod5',
                               'gasto_real', 'gasto_prod1', 'gasto_prod2', 'gasto_prod3',
                               'gasto_prod4', 'gasto_prod5', 'excedentes1', 'excedentes2',
                               'excedentes3', 'excedentes4', 'excedentes5'], inplace=True)
    dfAvgPricesY.drop(columns=['consumo', 'prod1', 'prod2', 'prod3', 'prod4', 'prod5',
                               'gasto_real', 'gasto_prod1', 'gasto_prod2', 'gasto_prod3',
                               'gasto_prod4', 'gasto_prod5', 'excedentes1', 'excedentes2',
                               'excedentes3', 'excedentes4', 'excedentes5'], inplace=True)

    dfFig1M = dfAvgPricesM.merge(dfSavingsM[['fecha', 'consumo', 'prod1', 'excedentes1', 'gasto_real', 'gasto_prod1']], on='fecha', how='inner')
    dfFig1Y = dfAvgPricesY.merge(dfSavingsY[['fecha', 'consumo', 'prod1', 'excedentes1', 'gasto_real', 'gasto_prod1']], on='fecha', how='inner')
    dfFig1M.rename(columns={'prod1': 'prod', 'gasto_prod1': 'gasto_prod', 'excedentes1': 'excedentes'}, inplace=True)
    dfFig1Y.rename(columns={'prod1': 'prod', 'gasto_prod1': 'gasto_prod', 'excedentes1': 'excedentes'}, inplace=True)
    dfFig1M['mes'] = dfFig1M['fecha'].apply(lambda row: month_str[row.month])
    dfFig1M.drop(columns=['fecha'], inplace=True)
    dfFig1Y['año'] = dfFig1Y['fecha'].apply(lambda row: row.year)
    dfFig1Y.drop(columns=['fecha'], inplace=True)
    dfFig1M = dfFig1M[['mes', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]
    dfFig1Y = dfFig1Y[['año', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]

    dfFig2M = dfAvgPricesM.merge(dfSavingsM[['fecha', 'consumo', 'prod2', 'excedentes2', 'gasto_real', 'gasto_prod2']], on='fecha', how='inner')
    dfFig2Y = dfAvgPricesY.merge(dfSavingsY[['fecha', 'consumo', 'prod2', 'excedentes2', 'gasto_real', 'gasto_prod2']], on='fecha', how='inner')
    dfFig2M.rename(columns={'prod2': 'prod', 'gasto_prod2': 'gasto_prod', 'excedentes2': 'excedentes'}, inplace=True)
    dfFig2Y.rename(columns={'prod2': 'prod', 'gasto_prod2': 'gasto_prod', 'excedentes2': 'excedentes'}, inplace=True)
    dfFig2M['mes'] = dfFig2M['fecha'].apply(lambda row: month_str[row.month])
    dfFig2M.drop(columns=['fecha'], inplace=True)
    dfFig2Y['año'] = dfFig2Y['fecha'].apply(lambda row: row.year)
    dfFig2Y.drop(columns=['fecha'], inplace=True)
    dfFig2M = dfFig2M[['mes', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]
    dfFig2Y = dfFig2Y[['año', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]

    dfFig3M = dfAvgPricesM.merge(dfSavingsM[['fecha', 'consumo', 'prod3', 'excedentes3', 'gasto_real', 'gasto_prod3']], on='fecha', how='inner')
    dfFig3Y = dfAvgPricesY.merge(dfSavingsY[['fecha', 'consumo', 'prod3', 'excedentes3', 'gasto_real', 'gasto_prod3']], on='fecha', how='inner')
    dfFig3M.rename(columns={'prod3': 'prod', 'gasto_prod3': 'gasto_prod', 'excedentes3': 'excedentes'}, inplace=True)
    dfFig3Y.rename(columns={'prod3': 'prod', 'gasto_prod3': 'gasto_prod', 'excedentes3': 'excedentes'}, inplace=True)
    dfFig3M['mes'] = dfFig3M['fecha'].apply(lambda row: month_str[row.month])
    dfFig3M.drop(columns=['fecha'], inplace=True)
    dfFig3Y['año'] = dfFig3Y['fecha'].apply(lambda row: row.year)
    dfFig3Y.drop(columns=['fecha'], inplace=True)
    dfFig3M = dfFig3M[['mes', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]
    dfFig3Y = dfFig3Y[['año', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]

    dfFig4M = dfAvgPricesM.merge(dfSavingsM[['fecha', 'consumo', 'prod4', 'excedentes4', 'gasto_real', 'gasto_prod4']], on='fecha', how='inner')
    dfFig4Y = dfAvgPricesY.merge(dfSavingsY[['fecha', 'consumo', 'prod4', 'excedentes4', 'gasto_real', 'gasto_prod4']], on='fecha', how='inner')
    dfFig4M.rename(columns={'prod4': 'prod', 'gasto_prod4': 'gasto_prod', 'excedentes4': 'excedentes'}, inplace=True)
    dfFig4Y.rename(columns={'prod4': 'prod', 'gasto_prod4': 'gasto_prod', 'excedentes4': 'excedentes'}, inplace=True)
    dfFig4M['mes'] = dfFig4M['fecha'].apply(lambda row: month_str[row.month])
    dfFig4M.drop(columns=['fecha'], inplace=True)
    dfFig4Y['año'] = dfFig4Y['fecha'].apply(lambda row: row.year)
    dfFig4Y.drop(columns=['fecha'], inplace=True)
    dfFig4M = dfFig4M[['mes', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]
    dfFig4Y = dfFig4Y[['año', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]

    dfFig5M = dfAvgPricesM.merge(dfSavingsM[['fecha', 'consumo', 'prod5', 'excedentes5', 'gasto_real', 'gasto_prod5']], on='fecha', how='inner')
    dfFig5Y = dfAvgPricesY.merge(dfSavingsY[['fecha', 'consumo', 'prod5', 'excedentes5', 'gasto_real', 'gasto_prod5']], on='fecha', how='inner')
    dfFig5M.rename(columns={'prod5': 'prod', 'gasto_prod5': 'gasto_prod', 'excedentes5': 'excedentes'}, inplace=True)
    dfFig5Y.rename(columns={'prod5': 'prod', 'gasto_prod5': 'gasto_prod', 'excedentes5': 'excedentes'}, inplace=True)
    dfFig5M['mes'] = dfFig5M['fecha'].apply(lambda row: month_str[row.month])
    dfFig5M.drop(columns=['fecha'], inplace=True)
    dfFig5Y['año'] = dfFig5Y['fecha'].apply(lambda row: row.year)
    dfFig5Y.drop(columns=['fecha'], inplace=True)
    dfFig5M = dfFig5M[['mes', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]
    dfFig5Y = dfFig5Y[['año', 'consumo', 'prod', 'excedentes', 'pvpc', 'precioExced', 'gasto_real', 'gasto_prod']]

    dfFig1M.columns = ['Month', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig1Y.columns = ['Year', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig2M.columns = ['Month', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig2Y.columns = ['Year', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig3M.columns = ['Month', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig3Y.columns = ['Year', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig4M.columns = ['Month', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig4Y.columns = ['Year', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig5M.columns = ['Month', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']
    dfFig5Y.columns = ['Year', 'Cons(kwh)', 'Prod(kwh)', 'Excess(kwh)', 'Kwh Price(€)', 'Exc kwh Price(€)', 'Billed', 'Simulated Bill']

    return [dfFig1M, dfFig2M, dfFig3M, dfFig4M, dfFig5M], [dfFig1Y, dfFig2Y, dfFig3Y, dfFig4Y, dfFig5Y]


if __name__ == "__main__":
    MAXCONSUMO = 0
    MAXTOTAL = 0
    MAXTOTALReal = [0, 0, 0, 0, 0]
    MAXPRODUCCION = 0
    MAXPRODUCCIONReal = [0, 0, 0, 0, 0]
    MONTH_STR = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November',
                 12: 'December'}

    # CARGA DATOS CONSUMO
    # ===================
    st = time.time()
    print('Loading consumption data...', end= '')
    fileCons = 'original_data/consumo_2022.csv'
    dataCons, dfConsCalc = loadConsum(fileCons)

    for month in dataCons.keys():
        if max(dataCons[month]['week_day']['consumo'].tolist()) > MAXCONSUMO:
            MAXCONSUMO = max(dataCons[month]['week_day']['consumo'].tolist())
        elif max(dataCons[month]['weekend_day']['consumo'].tolist()) > MAXCONSUMO:
            MAXCONSUMO = max(dataCons[month]['weekend_day']['consumo'].tolist())
        elif max(dataCons[month]['total']['consumo'].tolist()) > MAXCONSUMO:
            MAXCONSUMO = max(dataCons[month]['total']['consumo'].tolist())

    et = time.time()
    delta = round(et - st, 1)
    print(" in " + str(delta) + " seconds.")
    
    # CARGA DATOS PRODUCCION REAL
    # DATOS PARA 1KW a 5KW
    # ===========================
    et = time.time()
    print('Loading real production example data...', end='')
    fileProdReal = 'original_data/ejemplo_generacion_real.csv'
    dataProdRealList, dfRealCalc = loadProdReal(fileProdReal)

    for i, df in enumerate(dataProdRealList):
        for month in df.keys():
            if max(df[month]['prod'].tolist()) > MAXPRODUCCIONReal[i]:
                MAXPRODUCCIONReal[i] = max(df[month]['prod'].tolist())


    for i, value in enumerate(MAXPRODUCCIONReal):
        if value >= MAXCONSUMO:
            MAXTOTALReal[i] = value
        else:
            MAXTOTALReal[i] = MAXCONSUMO

    et = time.time()
    delta = round(et - st, 1)
    print(" in " + str(delta) + " seconds.")

    # CARGA DATOS PVPC
    # ================
    st = time.time()
    print('Loading PVPC price data...', end='')
    filePVPC = 'original_data/pvpc_2022.zip'
    dfPVPCCalc = loadPVPC(filePVPC)

    et = time.time()
    delta = round(et - st, 1)
    print(" in " + str(delta) + " seconds.")

    # CARGA DATOS PRECIO EXCEDENTES
    # =============================
    st = time.time()
    print('Loading excess compensation price data...', end='')
    fileExc = 'original_data/precio_excedentes_2022.csv'
    dfExcCalc = loadExc(fileExc)

    et = time.time()
    delta = round(et - st, 1)
    print(" in " + str(delta) + " seconds.")

    # GENERAR FIGURAS Y ALAMACENARLAS
    # ===============================
    st = time.time()

    print('\nGenerating plots and data tables...')
    figProdReal = list()
    for i in range(5):
        figProdReal.append(plotData(dataCons, dataProdRealList[i], MAXTOTALReal[i], 'prod_{}kw'.format(i+1)))

    figTablaM, figTablaY = calculateSaving(dfConsCalc, dfRealCalc, dfPVPCCalc, dfExcCalc)

    for j in range(12):
        for i in range(5):
            fig_json = pio.to_json(figProdReal[i][j+1], validate=False, pretty=False, engine='auto')
            with open('figure_data_month/figProdReal{}kw_{}.json'.format(i+1,MONTH_STR[j+1]), 'w') as outfile:
                outfile.write(fig_json)

    for i in range(5):
        figTablaM[i].to_json('figure_data_month/dfTableM{}kw.json'.format(i+1))
        figTablaY[i].to_json('figure_data_month/dfTableY{}kw.json'.format(i+1))
