import pandas as pd



############ Name of the file to be read ############
<<<<<<< HEAD
=======
# C'est votre chemin, il est correct
Wages_File = '.\Data\Benefits\Annual wages 1990-2024.xlsx'
>>>>>>> e6dd2e995303f7a080a4c09c7c10b5c0c4f8e80a



Wages_File = r'C:\Users\nour.oueghlani\Documents\Hackathon\STATEC-Hackathon\Data\Benefits\Annual wages.xlsx'
Income_File = r'C:\Users\nour.oueghlani\Documents\Hackathon\STATEC-Hackathon\Data\Benefits\Income per year - cleaned_version.xls'
list_years = list(range(1990,2025))
list_ages = list(range(15,66))
Tableau_Output = pd.DataFrame()
Ratio_dict = {}
################ Reading the Excel file ############
Income_File_dated_2012 = pd.read_excel(Income_File, header=None)
tous_les_onglets = pd.read_excel(Income_File, sheet_name=None)
Wages_data_annually = pd.read_excel(Wages_File, header=0)
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
print(Wages_data_annually['2012'])        
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
print(Tableau_Output)