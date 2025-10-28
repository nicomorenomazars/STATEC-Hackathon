import pandas as pd

############ Name of the file to be read ############
# C'est votre chemin, il est correct
Wages_File = r'C:\Users\nour.oueghlani\Documents\Hackathon\STATEC-Hackathon\Data\Benefits\Annual wages 1990-2024.xlsx'

################ Reading the Excel file ############

df_data = pd.read_excel(Wages_File)