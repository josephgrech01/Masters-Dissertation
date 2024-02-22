import pandas as pd
import os

files = ['Route22ByHour.csv','Route43ByHour.csv']
folder = os.path.join('singapore','demand')

for file in files:
    print("File: ", file)
    
    df = pd.read_csv(os.path.join(folder,file))
    df.dropna(subset=['Alighting Stop'], inplace=True)

    removeRows = df[df['Boarding Stop'] == df['Alighting Stop']].index
    df.drop(removeRows, inplace=True)

    if file == 'Route22ByHour.csv':
        name = 'route22.csv'
    else:
        name = 'route43.csv'

    for i in range(6,22):
        print("Hour: ", i)
        temp = df[df['Hour'] == i]
       
        path = os.path.join(folder, 'byHour', 'hour'+str(i))
        os.makedirs(path, exist_ok=True)
        
        if len(temp.index) != 0:
            temp.to_csv(os.path.join(path, name), index=False)
        else:
            print("Empty dataframe for {} Hour {}".format(name, i))

    
        
        