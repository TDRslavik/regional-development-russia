import pandas as pd

pd.set_option('display.max_columns', None)


#DEF ДЛЯ ОЧИСТКИ СТРОК РЕГИОНОВ#
def cleaning_dataframe_regions(dataframe, name_column_after_melt):
    regions_to_remove = ["Тюменская область", "Архангельская область"]
    dataframe['region'] = dataframe['region'].str.strip()
    # Очистка от особенностей учета статистики некоторых регионов.
    dataframe = dataframe[~dataframe['region'].isin(regions_to_remove)]
    dataframe['region'] = dataframe['region'].str.replace('в том числе:', '')
    dataframe['region'] = dataframe['region'].str.replace('\n', '').str.strip()
    dataframe['region'] = dataframe['region'].replace(
        {'в т.ч. Ханты-Мансийский автономный округ-Югра': 'Ханты-Мансийский автономный округ-Югра',
         'Ямало-Ненецкий автономный округ': 'Ямало-Ненецкий автономный округ',
         'в т.ч. Ненецкий авт. округ': 'Ненецкий автономный округ',
         'Архангельская область без Ненецкого авт.округа': 'Архангельская область',
         'Тюменская область (без Ханты-Мансийского авт.округа-Югра и Ямало-Ненецкого авт.округа)': 'Тюменская область',
         'Тюменская область (кроме Ханты-Мансийского автономного округа-Югры и Ямало-Ненецкого автономного округа)': 'Тюменская область',
         'Ханты-Мансийский автономный округ - Югра (Тюменская область)': 'Ханты-Мансийский автономный округ-Югра',
         'Республика Татарстан (Татарстан)': 'Республика Татарстан',
         'Город федерального значения Севастополь': 'г.Севастополь',
         'Архангельская область (кроме Ненецкого автономного округа)': 'Архангельская область',
         'Ямало-Ненецкий автономный округ (Тюменская область)': 'Ямало-Ненецкий автономный округ',
         'Республика Адыгея (Адыгея)': 'Республика Адыгея',
         'Город Санкт-Петербург город федерального значения': 'г.Санкт-Петербург',
         'Ненецкий автономный округ (Архангельская область)': 'Ненецкий автономный округ',
         'Чувашская Республика - Чувашия': 'Чувашская Республика',
         'Город Москва столица Российской Федерации город федерального значения': 'г.Москва',
         'Кемеровская область - Кузбасс': 'Кемеровская область-Кузбасс',
         'Кемеровская область': 'Кемеровская область-Кузбасс',
         'Город Севастополь': 'г.Севастополь',
         'Город Москва': 'г.Москва',
         'Тюменская область (без авт. округов)': 'Тюменская область',
         'Город Санкт-Петербург': 'г.Санкт-Петербург',
         'Ханты-Мансийский автономный округ - Югра': 'Ханты-Мансийский автономный округ-Югра',
         'Архангельская область без  авт. округа': 'Архангельская область'})
    #Федеральные округа не являются регионами России.
    dataframe = dataframe[~dataframe['region'].str.contains('Российская Федерация')]
    dataframe_without_Fed_okrug = dataframe.loc[~dataframe['region'].str.contains('федеральный округ')]
    dataframe_after_clean = dataframe_without_Fed_okrug.melt(id_vars='region', var_name='year',value_name=name_column_after_melt).reset_index(drop=True)
    dataframe_after_clean['year'] = dataframe_after_clean['year'].astype(int)
    dataframe_after_clean = dataframe_after_clean.sort_values(by=['region', 'year']).reset_index(drop=True)
    return dataframe_after_clean


#DEF ДЛЯ РАСЧЁТА ЕЖЕГОДНЫХ ТЕМПОВ РОСТА ПО ПОКАЗАТЕЛЯМ#
def calculate_pct_change(dataframe, value_column, name_column):
    dataframe[name_column] = dataframe.groupby('region')[value_column].pct_change() * 100
    dataframe[name_column] = dataframe[name_column].round(2)
    return dataframe


#DEF ДЛЯ ФОРМИРОВАНИЯ РЕЙТИНГА ПО ПОКАЗАТЕЛЯМ#
def calculate_region_ratings(dataframe, column_name, lower_is_better=False):
    if lower_is_better is True:
        dataframe = dataframe.groupby('year')[column_name].rank(ascending=True, method='dense')
    else:
        dataframe = dataframe.groupby('year')[column_name].rank(ascending=False, method='dense')
    return dataframe


#РАБОТА С ГРЯЗНЫМ ФАЙЛОМ ВРП РЕГИОНОВ#
regions_df_vrp = pd.read_excel('data/raw/ВРП.xlsx', sheet_name='2', skiprows=2, nrows=96)
regions_df_vrp = regions_df_vrp.rename(columns={'Unnamed: 0': 'region'})
regions_df_vrp = regions_df_vrp[1:]
#Некоторые года в исходном файле имеют лишние знаки. Очищаем названия столбцов
for column in regions_df_vrp.columns:
    column = str(column)
    if column == 'region':
        continue
    else:
        column_short_name_year = column[:4]
        regions_df_vrp.rename(columns={column: column_short_name_year}, inplace=True)
regions_df_vrp_absolute = cleaning_dataframe_regions(regions_df_vrp, 'vrp_absolute_mln_rub')
regions_df_vrp_absolute = regions_df_vrp_absolute[regions_df_vrp_absolute['year'] >= 2018].reset_index(drop=True)
regions_df_vrp_absolute = calculate_pct_change(regions_df_vrp_absolute, 'vrp_absolute_mln_rub', 'vrp_absolute_growth')


##РАБОТА С ГРЯЗНЫМ ФАЙЛОМ ВРП РЕГИОНА НА ДУШУ НАСЕЛЕНИЯ#
regions_df_vrp_on_people_raw = pd.read_excel('data/raw/ВРП на душу.xlsx', sheet_name='Данные', skiprows=2, nrows=101, usecols='B:I')
regions_df_vrp_on_people_raw = regions_df_vrp_on_people_raw.iloc[2:].reset_index(drop=True)
regions_df_vrp_on_people_raw = regions_df_vrp_on_people_raw.rename(columns={'Unnamed: 1': 'region'})
regions_df_vrp_per_capita = cleaning_dataframe_regions(regions_df_vrp_on_people_raw, 'vrp_per_capita_rub')
regions_df_vrp_per_capita = calculate_pct_change(regions_df_vrp_per_capita, 'vrp_per_capita_rub', 'vrp_per_capita_growth')


#РАБОТА С ГРЯЗНЫМ ФАЙЛОМ ОБЪЁМА ИНВЕСТИЦИЙ В АБСОЛЮТНЫХ ЗНАЧЕНИЯХ#
regions_df_investments_raw = pd.read_excel('data/raw/Инвестиции.xlsx', skiprows=2, nrows=97)
regions_df_investments_raw = regions_df_investments_raw.rename(columns={'Unnamed: 0': 'region'}).reset_index(drop=True)
regions_df_investments = cleaning_dataframe_regions(regions_df_investments_raw, 'investments_thousand_rub')
regions_df_investments = calculate_pct_change(regions_df_investments, 'investments_thousand_rub', 'investments_growth')


#РАБОТА С ГРЯЗНЫМ ФАЙЛОМ МЕДИАННОГО СРЕДНЕДУШЕВОГО ДОХОДА#
regions_df_median_per_capita_income_raw = pd.read_excel('data/raw/Медианный доход.xlsx', sheet_name='Данные', skiprows=2, nrows=100)
regions_df_median_per_capita_income_raw = regions_df_median_per_capita_income_raw.rename(columns={'Unnamed: 0': 'region'})
regions_df_median_per_capita_income = cleaning_dataframe_regions(regions_df_median_per_capita_income_raw, 'median_per_capita_income_rub')
regions_df_median_per_capita_income = calculate_pct_change(regions_df_median_per_capita_income, 'median_per_capita_income_rub', 'median_per_capita_income_growth')


#РАБОТА С ГРЯЗНЫМ ФАЙЛОМ УРОВНЯ БЕДНОСТИ#
regions_df_poverty_rate_raw = pd.read_excel('data/raw/уровень бедности.xlsx', skiprows=2, nrows=97)
regions_df_poverty_rate_raw = regions_df_poverty_rate_raw.rename(columns={'Unnamed: 0': 'region'})
regions_df_poverty_rate = cleaning_dataframe_regions(regions_df_poverty_rate_raw, 'poverty_rate')
regions_df_poverty_rate = calculate_pct_change(regions_df_poverty_rate, 'poverty_rate', 'poverty_rate_growth')


#РАБОТА С ГРЯЗНЫМ ФАЙЛОМ АБСОЛЮТНОГО ЧИСЛА БЕДНЫХ#
regions_df_population_poverty_absolute_raw = pd.read_excel('data/raw/абсолютное число бедных.xlsx', sheet_name='по РФ и субъектам РФ 2013-2025',skiprows=2, nrows=97, usecols='A:N')
regions_df_population_poverty_absolute_raw = regions_df_population_poverty_absolute_raw.rename(columns={'Unnamed: 0': 'region'})
regions_df_population_poverty_absolute = cleaning_dataframe_regions(regions_df_population_poverty_absolute_raw, 'population_poverty_thousands')
regions_df_population_poverty_absolute = regions_df_population_poverty_absolute[(regions_df_population_poverty_absolute['year'] >= 2018) & (regions_df_population_poverty_absolute['year'] < 2025)].reset_index(drop=True)
regions_df_population_poverty_absolute = calculate_pct_change(regions_df_population_poverty_absolute, 'population_poverty_thousands', 'population_poverty_growth')


#РАБОТА С ГРЯЗНЫМ ФАЙЛОМ УРОВНЯ БЕЗРАБОТИЦЫ#
regions_df_unemployment_rate_raw = pd.read_excel('data/raw/безработица.xlsx', skiprows=2, nrows=97, usecols='B:I')
regions_df_unemployment_rate_raw = regions_df_unemployment_rate_raw.rename(columns={'Unnamed: 1': 'region'})
regions_df_unemployment_rate = cleaning_dataframe_regions(regions_df_unemployment_rate_raw, 'unemployment_rate')
regions_df_unemployment_rate = calculate_pct_change(regions_df_unemployment_rate, 'unemployment_rate', 'unemployment_rate_growth')


#РАБОТА С ГРЯЗНЫМ ФАЙЛОМ ЧИСЛЕННОСТИ НАСЕЛЕНИЯ#
regions_df_population_raw = pd.read_excel('data/raw/население.xlsx', skiprows=2, nrows=100)
regions_df_population_raw = regions_df_population_raw.rename(columns={'Unnamed: 0': 'region'})
regions_df_population = cleaning_dataframe_regions(regions_df_population_raw, 'population')
regions_df_population = calculate_pct_change(regions_df_population, 'population', 'population_growth')


#СОЗДАНИЕ ДАТАФРЕЙМА С ИНФОРМАЦИЕЙ О КОЛИЧЕСТВЕ ИНВЕСТИЦИЙ НА 1 ЧЕЛОВЕКА В РЕГИОНЕ ИЗ ИМЕЮЩИХСЯ ДАННЫХ#
dataframe_investment_per_capita_raw = pd.merge(regions_df_population, regions_df_investments, how='inner', on=['region', 'year'])[['region', 'year', 'population', 'investments_thousand_rub']]
dataframe_investment_per_capita_raw['investments_per_capita_thousand_rub'] = (dataframe_investment_per_capita_raw['investments_thousand_rub'] / dataframe_investment_per_capita_raw['population']).round(2)
dataframe_investment_per_capita = calculate_pct_change(dataframe_investment_per_capita_raw, 'investments_per_capita_thousand_rub', 'investments_per_capita_growth')
dataframe_investment_per_capita = dataframe_investment_per_capita[['region', 'year', 'investments_per_capita_thousand_rub', 'investments_per_capita_growth']]


#ОБЪЕДИНЯЕМ В БОЛЬШОЙ ОБЩИЙ ДАТАФРЕЙМЫ#
dataframe_regions_all_statics = regions_df_vrp_absolute.merge(regions_df_vrp_per_capita, how='inner', on=['region', 'year'])
dataframe_regions_all_statics = dataframe_regions_all_statics.merge(regions_df_investments, how='inner', on=['region', 'year'])
dataframe_regions_all_statics = dataframe_regions_all_statics.merge(regions_df_median_per_capita_income, how='inner', on=['region', 'year'])
dataframe_regions_all_statics = dataframe_regions_all_statics.merge(regions_df_poverty_rate, how='inner', on=['region', 'year'])
dataframe_regions_all_statics = dataframe_regions_all_statics.merge(regions_df_population_poverty_absolute, how='inner', on=['region', 'year'])
dataframe_regions_all_statics = dataframe_regions_all_statics.merge(regions_df_unemployment_rate, how='inner', on=['region', 'year'])
dataframe_regions_all_statics = dataframe_regions_all_statics.merge(regions_df_population, how='inner', on=['region', 'year'])
dataframe_regions_all_statics = dataframe_regions_all_statics.merge(dataframe_investment_per_capita, how='inner', on=['region', 'year'])
dataframe_regions_all_statics.to_csv('data/processed/regions_all_statics.csv', index=False)


#ОТДЕЛЬНЫЙ ДАТАФРЕЙМ ДЛЯ ОТСЛЕЖИВАНИЯ АБСОЛЮТНЫХ ИЗМЕНЕНИЙ РЯДА ПОКАЗАТЕЛЕЙ 2018-2024#
region_summary_df = dataframe_regions_all_statics.loc[(dataframe_regions_all_statics['year'] == 2018) | (dataframe_regions_all_statics['year'] == 2024)] #оставляем 2018 и 2024 года для отслеживания изменения
region_summary_df = region_summary_df.loc[:, ~region_summary_df.columns.str.contains('growth')]
region_summary_df = region_summary_df.sort_values(['region', 'year'])
region_summary_df_changes = pd.DataFrame()
region_summary_df_changes['region'] = region_summary_df['region']
indicator_columns = list(region_summary_df.columns)
indicator_columns.remove('region')
indicator_columns.remove('year')
for column in indicator_columns:
    column_name_absolute_change = column + '_absolute_change'
    column_name_pct_change = column + '_pct_change'
    region_summary_df_changes[column_name_absolute_change] = region_summary_df.groupby('region')[column].diff()
    region_summary_df_changes[column_name_pct_change] = (region_summary_df.groupby('region')[column].pct_change() * 100).round(2)
region_summary_df_changes = region_summary_df_changes.dropna().reset_index(drop=True).rename(columns={'poverty_rate_absolute_change': 'poverty_rate_change_pp', 'unemployment_rate_absolute_change' : 'unemployment_rate_change_pp'})
region_summary_df_changes.to_csv('data/processed/region_summary_changes.csv', index=False)

#ДАТАФРЕЙМ ПО ПОКАЗАТЕЛЯМ В КАЖДОМ ИЗ ГОДОВ#
regions_dataframe_all_rank_raw = dataframe_regions_all_statics.copy()
clear_absolute_value = ['vrp_absolute_mln_rub', 'investments_thousand_rub', 'population_poverty_thousands', 'population']
regions_dataframe_all_rank_raw = regions_dataframe_all_rank_raw.loc[:, ~regions_dataframe_all_rank_raw.columns.isin(clear_absolute_value)]
regions_dataframe_all_rank_raw = regions_dataframe_all_rank_raw.loc[:, ~regions_dataframe_all_rank_raw.columns.str.contains('growth')]
columns_need_rating = list(regions_dataframe_all_rank_raw.columns)
columns_need_rating.remove('region')
columns_need_rating.remove('year')
lower_is_better_for_rating = ['poverty_rate', 'unemployment_rate']
for column in columns_need_rating:
    column_name_new_rating = column + '_rank'
    if column in lower_is_better_for_rating:
        regions_dataframe_all_rank_raw[column_name_new_rating] = calculate_region_ratings(regions_dataframe_all_rank_raw[['region', 'year', column]], column, lower_is_better=True)
    else:
        regions_dataframe_all_rank_raw[column_name_new_rating] = calculate_region_ratings(regions_dataframe_all_rank_raw[['region', 'year', column]], column)

columns_avg_rating = ['vrp_per_capita_rub_rank', 'median_per_capita_income_rub_rank', 'poverty_rate_rank', 'unemployment_rate_rank', 'investments_per_capita_thousand_rub_rank']
regions_dataframe_all_rank_raw['avg_rating'] = regions_dataframe_all_rank_raw[columns_avg_rating].mean(axis=1).round(5)
regions_dataframe_all_rank_clear = regions_dataframe_all_rank_raw[['region', 'year', 'avg_rating']]
regions_dataframe_all_rank_clear['region_rank'] = regions_dataframe_all_rank_clear.groupby('year')['avg_rating'].rank(ascending=True, method='min')
regions_dataframe_all_rank_clear = regions_dataframe_all_rank_clear.sort_values(['region_rank', 'region', 'year'])
regions_dataframe_all_rank_clear.to_csv('data/processed/regions_custom_rank.csv', index=False)


#РАСЧЁТ РЕЙТИНГА РЕГИОНОВ НА ОСНОВАНИИ ИХ ДИНАМИКИ ПО РЯДУ ПОКАЗАТЕЛЕЙ ЗА 2018-2024
regional_dynamics_df_raw = dataframe_regions_all_statics.copy()
regional_dynamics_df_raw = regional_dynamics_df_raw.loc[:, ~regional_dynamics_df_raw.columns.str.contains('growth')]
regional_dynamics_df_raw = regional_dynamics_df_raw[(regional_dynamics_df_raw['year'] == 2018) | (regional_dynamics_df_raw['year'] == 2024)]
columns_need_rating_with_absolute = list(regional_dynamics_df_raw.columns)
columns_need_rating_with_absolute.remove('region')
columns_need_rating_with_absolute.remove('year')
columns_need_rating_with_absolute_change = list()
for column in columns_need_rating_with_absolute:
    column_name_change = column + '_pct_change'
    columns_need_rating_with_absolute_change.append(column_name_change)
    regional_dynamics_df_raw = calculate_pct_change(regional_dynamics_df_raw, column, column_name_change)
    del regional_dynamics_df_raw[column]
regional_dynamics_df_raw = regional_dynamics_df_raw.loc[regional_dynamics_df_raw['year'] == 2024]

lower_is_better_for_rating_with_absolute = ['poverty_rate', 'population_poverty_thousands', 'unemployment_rate']
for column in columns_need_rating_with_absolute_change:
    column_name_rating = column[:-10] + 'rank'
    if column[:-10] in lower_is_better_for_rating_with_absolute:
        regional_dynamics_df_raw[column_name_rating] = calculate_region_ratings(regional_dynamics_df_raw[['region', 'year', column]], column, lower_is_better=True) #для динамики отрицательное изменение является положительным результатом
    else:
        regional_dynamics_df_raw[column_name_rating] = calculate_region_ratings(regional_dynamics_df_raw[['region', 'year', column]], column)
regional_dynamics_df_raw = regional_dynamics_df_raw.reset_index(drop=True)
del regional_dynamics_df_raw['year']
regional_dynamics_df_clear = regional_dynamics_df_raw.loc[:, ~regional_dynamics_df_raw.columns.str.contains('change')]
regional_dynamics_df_clear.to_csv('data/processed/rank_of_dynamics.csv', index=False)
#Из Python выгружаешь 4 итоговых DataFrame в CSV:dataframe_regions_all_statics region_summary_df_changes regions_dataframe_all_rank_clear regional_dynamics_df_clear

