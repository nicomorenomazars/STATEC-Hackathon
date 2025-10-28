import pandas as pd



############ Name of the file to be read ############



Wages_File = r'C:\Users\nour.oueghlani\Documents\Hackathon\STATEC-Hackathon\Data\Benefits\Annual wages.xlsx'
Income_File = r'C:\Users\nour.oueghlani\Documents\Hackathon\STATEC-Hackathon\Data\Benefits\Income per year - cleaned_version.xls'
Tableau_Output= pd.

################ Reading the Excel file ############
Income_File_dated_2012 = pd.read_excel(Income_File, header=None)
Income_File
Wages_data_annually = pd.read_excel(Wages_File, header=0)

################ Treatment of the data ############
Wages_data_annually = Wages_data_annually.set_index('Time period')
print(Income_File_dated.head())