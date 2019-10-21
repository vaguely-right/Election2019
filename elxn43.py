'''
Projecting 2019 Canadian Election results riding-by-riding.
This uses a permanence of ratios method to update the results of polling, assuming each riding
deviates from aggregated results (national/regional) by the same amount in 2019 as 2015.
The star independent candidates are ignored for simplicity here, as are the PPC candidates.
Territories polling is scant, so the national averages were used for those regional values.
'''
import pandas as pd
import numpy as np

pd.set_option('display.width',150)
pd.set_option('display.max_columns',16)

#Permanence of ratios updating method
def prupdate(distpoll,distriding,dist2015=[31.9,39.5,19.7,3.5,4.7]):
    distout = []
    for i in range(5):
        if distriding[i] == 0:
            distout = distout + [0.0]
        else:
            distout = distout + [100 / ( 1 + 
                                     (100-distpoll[i])/distpoll[i] * 
                                     (100-distriding[i])/distriding[i] *
                                     dist2015[i]/(100-dist2015[i])
                                     )]
    return distout


#Get the 2015 results data
furl = 'https://elections.ca/res/rep/off/ovr2015app/41/data_donnees/table_tableau12.csv'
df_in = pd.read_csv(furl)
df = df_in[['Province','Electoral District Name/Nom de circonscription','Electoral District Number/Numéro de circonscription',
    'Candidate/Candidat','Votes Obtained/Votes obtenus','Percentage of Votes Obtained /Pourcentage des votes obtenus']]
df.columns = ['Province','ED Name','ED Number','Candidate','Votes','VotePct']

#Get the party names in a separate column
conditions = [(df.Candidate.str.contains('Conservative')),
              (df.Candidate.str.contains('Liberal')),
              (df.Candidate.str.contains('New Democratic')),
              (df.Candidate.str.contains('Green')),
              (df.Candidate.str.contains('Bloc Québécois'))]
choices = ['Conservative','Liberal','NDP','Green','Bloc']
df['Party'] = np.select(conditions,choices,default='Other')

#Add regional names to correspond to polling
conditions = [(df.Province.str.contains('British Columbia/Colombie-Britannique')),
              (df.Province.str.contains('Alberta')),
              (df.Province.str.contains('Manitoba')),
              (df.Province.str.contains('Saskatchewan')),
              (df.Province.str.contains('Ontario')),
              (df.Province.str.contains('Quebec/Québec')),
              (df.Province.str.contains('Newfoundland and Labrador/Terre-Neuve-et-Labrador')),
              (df.Province.str.contains('Prince Edward Island/Île-du-Prince-Édouard')),
              (df.Province.str.contains('Nova Scotia/Nouvelle-Écosse')),
              (df.Province.str.contains('New Brunswick/Nouveau-Brunswick')),
              (df.Province.str.contains('Yukon')),
              (df.Province.str.contains('Northwest Territories/Territoires du Nord-Ouest')),
              (df.Province.str.contains('Nunavut'))]
choices = ['BC','Alberta','Prairies','Prairies','Ontario','Quebec',
           'Atlantic','Atlantic','Atlantic','Atlantic',
           'Territories','Territories','Territories']
df['Region'] = np.select(conditions,choices,default='Other')

#Replace province names with something shorter
df.Province.replace('British Columbia/Colombie-Britannique','BC',inplace=True)
df.Province.replace('Quebec/Québec','Quebec',inplace=True)
df.Province.replace('Newfoundland and Labrador/Terre-Neuve-et-Labrador','Newfoundland',inplace=True)
df.Province.replace('Prince Edward Island/Île-du-Prince-Édouard','PEI',inplace=True)
df.Province.replace('Nova Scotia/Nouvelle-Écosse','Nova Scotia',inplace=True)
df.Province.replace('New Brunswick/Nouveau-Brunswick','New Brunswick',inplace=True)
df.Province.replace('Northwest Territories/Territoires du Nord-Ouest','NWT',inplace=True)

#Pivot the 2015 results by riding
rf = df.pivot_table(values='VotePct',index=['Region','Province','ED Number','ED Name'],columns='Party',aggfunc='sum',fill_value=0.0)
rf = rf[['Conservative','Liberal','NDP','Green','Bloc']]

#Calculate the regional 2015 results
reg = df.pivot_table(values='Votes',index=['Region'],columns='Party',aggfunc='sum',fill_value=0.0)
reg = reg.div(reg.sum(axis=1),axis=0)*100
reg = reg[['Conservative','Liberal','NDP','Green','Bloc']]

#Get a table of the latest polls by region
#Data from https://newsinteractives.cbc.ca/elections/poll-tracker/canada/ on October 21, 2019
poll = reg.copy()
poll.loc['Alberta'] = [60.7,15.4,15.1,4.2,0.0]
poll.loc['Atlantic'] = [26.8,37.1,20.0,12.1,0.0]
poll.loc['BC'] = [30.6,26.5,26.0,13.0,0.0]
poll.loc['Ontario'] = [31.8,38.8,18.8,7.2,0.0]
poll.loc['Prairies'] = [45.5,22.3,22.7,5.6,0.0]
poll.loc['Quebec'] = [14.2,33.2,13.5,6.0,30.2]
poll.loc['Territories'] = [31.6, 32.0, 18.4, 7.5, 0.0]

    
#Running the results with a national 2015 results and 2015 polling
res = pd.DataFrame({'Conservative' : [],
                'Liberal' : [],
                'NDP' : [],
                'Green' : [],
                'Bloc' : []})
dist2015=[31.9,39.5,19.7,3.5,4.7]
distpoll = [31.6, 32.0, 18.4, 7.5, 7.0]
for r in range(338):
    distriding = rf.iloc[r]
    distout = prupdate(distpoll,distriding)
    oot = pd.DataFrame({'Conservative' : [distout[0]],
                    'Liberal' : [distout[1]],
                    'NDP' : [distout[2]],
                    'Green' : [distout[3]],
                    'Bloc' : [distout[4]]})
    res = pd.concat([res,oot])

res.index = rf.index

#Get the winners
res['Winner'] = res.idxmax(axis=1)
res.Winner.value_counts()


    
#Running the results using riding-by-riding 2015 results and 2019 polling
res = pd.DataFrame({'Conservative' : [],
                'Liberal' : [],
                'NDP' : [],
                'Green' : [],
                'Bloc' : []})
for r in range(338):
    region = rf.index[r][0]
    distpoll = poll.loc[region]
    distriding = rf.iloc[r]
    dist2015 = reg.loc[region]
    distout = prupdate(distpoll,distriding,dist2015)
    oot = pd.DataFrame({'Conservative' : [distout[0]],
                    'Liberal' : [distout[1]],
                    'NDP' : [distout[2]],
                    'Green' : [distout[3]],
                    'Bloc' : [distout[4]]})
    res = pd.concat([res,oot])

res.index = rf.index

#Get the winners
res['Winner'] = res.idxmax(axis=1)
res.Winner.value_counts()






















