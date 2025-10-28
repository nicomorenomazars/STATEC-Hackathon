import pandas as pd

############ Name of the file to be read ############
# C'est votre chemin, il est correct
Wages_File = '.\Data\Benefits\Annual wages 1990-2024.xlsx'

################ Reading the Excel file ############

df_data = pd.read_excel(Wages_File)