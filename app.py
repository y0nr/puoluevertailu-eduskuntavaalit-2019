# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import pickle

def load_file():
	with open('database.pkl', 'rb') as f:
		return pickle.load(f)

def formatNumber(num):
  if num % 1 == 0:
    return int(num)
  else:
    return round(num, 2)

data = load_file()
color_list = ['#E66101', '#FDB863', '#DDDDDD', '#92C5DE', '#0571B0']

constituencies = list(data.keys())
constituencies.remove('Kaikki vaalipiirit')
constituencies.sort()
constituencies.insert(0, 'Kaikki vaalipiirit')

basic_questions = list(data[constituencies[0]].keys())
basic_questions_explanation = {
	5: 'Täysin samaa mieltä',
	4: '',
	3: 'En osaa sanoa',
	2: '',
	1: 'Täysin eri mieltä'
}

def create_line_trace(x, y, name):
	return go.Scatter(x=x ,y=y, mode='lines', name=name)

def create_bar_trace(x, y, name, response, orientation='v'):
	return go.Bar(x=x ,y=y, name=name, marker={'color': color_list[response-1]}, orientation=orientation)

def create_bar_figure(constituency, data, question):
	d = data[constituency][question]
	return {
		'data': [create_bar_trace(y=d['percentage'].loc[response].index, x=d['percentage'].loc[response].values*100, name=label, response=response, orientation='h') for response, label in zip(d['percentage'].index, [str(i).replace(str(i), basic_questions_explanation[i]) for i in d['percentage'].index])],
		'layout': {
			'barmode': 'stack',
			'yaxis': {
				'automargin': True,
				'fixedrange': True,
			},
			'xaxis': {
				'automargin': True,
				'fixedrange': True,
				'tickvals': [0, 20, 40, 60, 80, 100],
				'ticksuffix': '%',
				'fontweight': 'bold'
			},
			'showlegend': False,
			'margin': {
				't': 0,
				'r': 0,
				'b': 50,
				'pad': 5
			},
			'annotations': [{'x': 100, 'y': y, 'yref': 'y', 'xanchor': 'left', 'text': str('{:.2f}'.format(round(mean, 2))) + ' <b>|</b> ' + str(formatNumber(median)), 'showarrow': False, 'align': 'center'} for y, mean, median in zip(d['average'].loc[:, (question, 'mean')].index, d['average'].loc[:, (question, 'mean')], d['average'].loc[:, (question, 'median')])]+[{'x': 100, 'y': len(d['average']), 'yref': 'y', 'xanchor': 'left', 'text': 'ka.   <b>|</b> Md.', 'showarrow': False, 'align': 'center'}]
		}
	}

app = dash.Dash(__name__)
app.title='Puoluevertailu by Mapple'
app.config['suppress_callback_exceptions']=True

app.layout = html.Div(
	id='app',
	children=[

	html.Div(
		id='bar-top',
		children=[
			html.H1(children=['Puoluevertailu', html.Span(children=['by', html.A('Mapple', href='https://mapple.io/', style={'marginLeft': '5px'})], style={'fontSize': '12px', 'marginLeft': '5px'})]),
			html.Div('YLEn vaalikonevastausten vertailua puolueittain.', style={'fontSize': '13px'}),
			html.Button(id='info-button', children='i'),
			html.Div(
				id='info-wrapper',
				style={'display': 'none'},
				children=[
					html.Div(
						id='info', children= [
							html.H2('Puoluevertailu.'),
							html.Button(id='info-close', children='x'),
							html.Div(
								id='info-content',
								children=[
									html.P('Tällä työkalulla voit vertailla puolueiden vuoden 2019 eduskuntavaalien YLEn vaalikonevastausten jakautumista koko maassa sekä vaalipiireittäin viisiportaisten kysymysten (täysin samaa mieltä - täysin eri mieltä) osalta.'),
									html.P('Palveluissa näytetään puolueittain vastausten suhteellinen jakautuminen valitussa vaalipiirissä (tai niissä kaikissa). Puolueet näytetään graafeissa vastausten keskiarvojen mukaisessa järjestyksessä, jotka näkyvät myös graafien oikeassa reunassa (ka.). Tämän vieressä näkyy myös vastausten mediaani (Md.).'),
									html.P('Puolueiden nimiä on lyhennetty alkuperäisestä datasta seuraavanlaisesti: Suomen Kommunistinen Puolue = SKP, Kommunistinen Työväenpuolue = KTP, Kansanliike Suomen Puolesta = KSP, Seitsemän tähden liike = STL, Suomen Kansa Ensin = SKE.'),
									html.P(children=['Visualisoinnin takana on Joona Repo / ', html.A('Mapple', href='https://mapple.io/'), '.']),
									html.P(children=['Aineisto on ladattu avoimena datana ', html.A('YLEn sivuilta', href='https://yle.fi/uutiset/3-10725384'), '.'])
							])
						])
				]
			)
		]
	),

	html.Div(
		id='constituency-radio-buttons-wrapper',
		style={'display': 'none'},
		children=[
			dcc.RadioItems(
				id='constituency-radio-buttons',
				options=[{'label': constituency, 'value': constituency} for constituency in constituencies],
				value=constituencies[0]
			)
		]
	),

	html.Div(
		id='main',
		children=[
			dcc.Dropdown(
				id='basic-questions-dropdown',
				options=[{'label': str(i+1).zfill(2)+') '+question, 'value': question} for i, question in enumerate(basic_questions)],
				value=basic_questions[0],
				clearable=False,
				searchable=False
			),
			html.Div(id='legend'),
			html.Div(
				id='basic-questions',
				children=[
					html.Div(
						id='basic-question',
						children=[
							dcc.Graph(
								id='basic-question-graph',
								config={
									'displayModeBar': False
								}
							)
						]
					)
				]
			),
			dcc.Tabs(
				id="tabs",
				value='graph',
				children=[
					dcc.Tab(label='Graafi', value='graph', style={'padding': '10px'}, selected_style={'padding': '10px', 'fontWeight': 'bold'}),
					dcc.Tab(id='constituency-tab', label='Vaalipiiri(t): Kaikki vaalipiirit', value='constituency', style={'padding': '10px'}, selected_style={'padding': '10px', 'fontWeight': 'bold'}),
			])
		])

])

@app.callback(
	Output('constituency-radio-buttons-wrapper', 'style'),
  [Input('tabs', 'value')]
	)
def render_content(tab):
		if tab == 'graph':
			constituency_display = {'display': 'none'}
		elif tab == 'constituency':
			constituency_display = {'display': 'block	'}
		return constituency_display

@app.callback(
	[Output('basic-questions-dropdown', 'options'),
	Output('basic-questions-dropdown', 'value')],
	[Input('constituency-radio-buttons', 'value')],
	[State('basic-questions-dropdown', 'value')]
)
def update_question_options(constituency, previous_question):
	available_questions = list(data[constituency].keys())
	if previous_question in available_questions:
		updated_question = previous_question
	else:
		updated_question = available_questions[0]
	return [{'label': str(i+1).zfill(2)+') '+question, 'value': question} for i, question in enumerate(available_questions)], updated_question


@app.callback(
    [Output(component_id='basic-question-graph', component_property='figure'),
		Output('constituency-tab', 'label'),
		Output('legend', 'children')],
		[Input(component_id='basic-questions-dropdown', component_property='value'),
		Input(component_id='constituency-radio-buttons', component_property='value')]
)
def update_output_div(question, constituency):
	legend =	[
		html.Div(id='legend-row-1', children=basic_questions_explanation[3]),
		html.Div(
			id='legend-row-2',
			children=[html.Div(className='ls', children=basic_questions_explanation[1]), html.Div(className='lv'), html.Div(id='l1', children='1'), html.Div(className='lv'), html.Div(id='l2', children='2'), html.Div(className='lv'), html.Div(id='l3', children='3'), html.Div(className='lv'), html.Div(id='l4', children='4'), html.Div(className='lv'), html.Div(id='l5', children='5'), html.Div(className='lv'), html.Div(className='ls', children=basic_questions_explanation[5])]
		)
	]
	return create_bar_figure(constituency, data, question), 'Vaalipiiri(t): '+constituency, legend

@app.callback(
	Output('info-wrapper', 'style'),
  [Input('info-button', 'n_clicks'),
	Input('info-close', 'n_clicks')]
)
def open_info(open_event, close_event):
	if open_event != None:
		if close_event != None:
			if close_event-open_event>=0:
				return {'display': 'none'}
		return {'display': 'block'}	
	return {'display': 'none'}
		

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')