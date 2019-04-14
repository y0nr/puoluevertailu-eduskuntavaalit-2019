import pandas as pd
import re
import pickle

data = pd.read_csv('avoin_data_eduskuntavaalit_2019.csv').replace('-', '3').replace({'1': 1, '2': 2, '3': 3, '4': 4, '5': 5})
data.loc[:, 'puolue'] = data['puolue'].replace({'Suomen Kommunistinen Puolue': 'SKP', 'Kommunistinen Työväenpuolue': 'KTP', 'Kansanliike Suomen Puolesta': 'KSP', 'Seitsemän tähden liike': 'STL', 'Suomen Kansa Ensin': 'SKE'})

constituencies = data['vaalipiiri'].unique().tolist()
constituencies.append('Kaikki vaalipiirit')

basic_questions = data.columns[2:31]

constituency_questions = [q for q in data.columns[81:]]
constituency_numeric_questions = [question for question in constituency_questions if question[-1]!='1']
constituency_numeric_questions_clear = [re.sub(r'^\D*\. ', '', question.replace('\n', '').strip())+' ('+re.search(r'^([\w-]*[\s]{0,1}[\w-]*)\.', question).group(1)+')' for question in constituency_numeric_questions]

database = {}
for constituency in constituencies:
  print(constituency)
  database[constituency] = {}
  if constituency != 'Kaikki vaalipiirit':
    d = data[data['vaalipiiri']==constituency].copy()
  else:
    d = data.copy()
  for question in basic_questions:
    database[constituency][question] = {}
    database[constituency][question]['average'] = d[['puolue', question]].groupby('puolue').agg({question: ['mean', 'median']}).sort_values((question, 'mean'), ascending=False).dropna()
    order = database[constituency][question]['average'].loc[:, (question, 'mean')].index
    database[constituency][question]['absolute'] = pd.crosstab(d[question], d['puolue'])[order]
    database[constituency][question]['percentage'] = pd.crosstab(d[question], d['puolue'], normalize='columns').sort_index()[order]
    database[constituency][question]['percentage'].index = database[constituency][question]['percentage'].index.astype(int)
  d.rename(columns={q: c for q, c in zip(constituency_numeric_questions, constituency_numeric_questions_clear)}, inplace=True)
  if constituency != 'Kaikki vaalipiirit':
    for question in constituency_numeric_questions_clear:
      if len(d[d[question].notnull()]) > 0:
        database[constituency][question] = {}
        database[constituency][question]['average'] = d[['puolue', question]].groupby('puolue').agg({question: ['mean', 'median']}).sort_values((question, 'mean'), ascending=False).dropna()
        order = database[constituency][question]['average'].loc[:, (question, 'mean')].index
        database[constituency][question]['absolute'] = pd.crosstab(d[question], d['puolue'])[order]
        database[constituency][question]['percentage'] = pd.crosstab(d[question], d['puolue'], normalize='columns').sort_index()[order]
        database[constituency][question]['percentage'].index = database[constituency][question]['percentage'].index.astype(int)

with open('database.pkl', 'wb') as f:
	pickle.dump(database, f, pickle.HIGHEST_PROTOCOL)