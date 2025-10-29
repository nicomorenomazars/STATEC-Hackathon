import pandas as pd




def Wages_Calculation(Wages_data_annually, tous_les_onglets):
    list_years = list(range(1990,2051))
    list_ages = list(range(15,66))
    Tableau_Output = pd.DataFrame()
    Ratio_dict = {}
    ################ Reading the Excel file ############
    for year in list_years:
        for age in list_ages:
            if str(year) in tous_les_onglets.keys():
                df_int={'Year':[year],
                'Age': [age],
                'Income_per_year': [tous_les_onglets[str(year)].loc[tous_les_onglets[str(year)]['Age']==age,'Total'].values[0]]}
                Tableau_Output=pd.concat([Tableau_Output,pd.DataFrame(df_int)])
            else:
                df_int=pd.DataFrame({'Year':[year],
                        'Age': [age],
                        'Income_per_year': [0]})
                Tableau_Output=pd.concat([Tableau_Output,df_int])     
    ################ Treatment of the data ############
    for year in tous_les_onglets.keys():
        Annual_Price=Wages_data_annually[year].values[0]
        liste_wage=list(tous_les_onglets[year]['Total']/Annual_Price)
        Ratio_dict[year]=liste_wage
    Ration_dict=pd.DataFrame(Ratio_dict)
    Ratio_moyen=list(Ration_dict.mean(axis=1))
    for year in list_years:
        for age in list_ages:
            Annual_Price=Wages_data_annually[str(year)].values[0]
            Tableau_Output.loc[(Tableau_Output['Year']==year) & (Tableau_Output['Age']==age),'Income_per_year']=Ratio_moyen[age-15]*(Annual_Price)
    return Tableau_Output

def Reval_avg_An_wages(adapt_salaire_data, Wages_data_annually):
    #Adapt the actual wages data to  revalorisation factor
    returns_list_historical =[]
    last_wage=Wages_data_annually['1990'].values[0]
    for year in Wages_data_annually.columns.drop(['Time period','1990']):
        returns_list_historical.append(Wages_data_annually[year].values[0]/last_wage)
        last_wage=Wages_data_annually[year].values[0]
    return_moyen_historical = sum(returns_list_historical)/len(returns_list_historical)
    ##############Projection for the future years##############
    for year in range(2024, 2051):
        Wages_data_annually[str(year)] = Wages_data_annually[str(year-1)] * (return_moyen_historical)
        
    return Wages_data_annually
     
