import xlrd
import math
import pandas as pd
import json
from ortools.linear_solver import pywraplp

# data loading
datapath = 'SC-Form.xls'
wb = xlrd.open_workbook(datapath)
sheet = wb.sheet_by_index(0)

stage_list = []
for stage_index in range (1, sheet.nrows):
	stage_dict = {'StageId': int(sheet.cell_value(stage_index,0)),\
					'StageName': sheet.cell_value(stage_index,1),\
					'StageType': sheet.cell_value(stage_index,1).split('_')[0],\
					'RelDepth': int(sheet.cell_value(stage_index,2)),\
					'StageCost': float(sheet.cell_value(stage_index,3)),\
					'HoldingCost': float(sheet.cell_value(stage_index,3)),\
					'avgDemand': str(sheet.cell_value(stage_index,4)),\
					'stdDevDemand': str(sheet.cell_value(stage_index,5)),\
					'maxServiceTime': str(sheet.cell_value(stage_index,6)),\
					'ServiceLevel': str(sheet.cell_value(stage_index,7)),\
					'StageTime': str(sheet.cell_value(stage_index,8)).split(';'),\
					'DownstreamStage': str(sheet.cell_value(stage_index,9)),\
					'UpstreamStage': str(sheet.cell_value(stage_index,10))}
	if (len(stage_dict['avgDemand']) > 0):
		stage_dict['avgDemand'] = float(stage_dict['avgDemand'])
	else:
		stage_dict['avgDemand'] = 0
	if (len(stage_dict['stdDevDemand']) > 0):
		stage_dict['stdDevDemand'] = float(stage_dict['stdDevDemand'])
	else:
		stage_dict['stdDevDemand'] = 0
	if (len(stage_dict['maxServiceTime']) > 0):
		stage_dict['maxServiceTime'] = float(stage_dict['maxServiceTime'])
	else:
		stage_dict['maxServiceTime'] = None
	if (len(stage_dict['ServiceLevel']) > 0):
		stage_dict['ServiceLevel'] = float(stage_dict['ServiceLevel'])
	else:
		stage_dict['ServiceLevel'] = 0.95
	for i in range (len(stage_dict['StageTime'])):
		stage_dict['StageTime'][i] = list(map(float,stage_dict['StageTime'][i].split(',')))
	if (len(stage_dict['DownstreamStage']) > 0):
		stage_dict['DownstreamStage'] = list(map(int,list(map(float,stage_dict['DownstreamStage'].split(',')))))
	else:
		stage_dict['DownstreamStage'] = None
	if (len(stage_dict['UpstreamStage']) > 0):
		stage_dict['UpstreamStage'] = list(map(int,list(map(float,stage_dict['UpstreamStage'].split(',')))))
	else:
		stage_dict['UpstreamStage'] = None
	stage_list.append(stage_dict)
#print(stage_list)

# constants
N = len(stage_list) #number of stages
epslion_percent = 0.02
MAX_ITE = 1000
M = 100

# calculate demand
demand_cal_list = []
for j in range (N):
	if (stage_list[j]['UpstreamStage'] is None):
		demand_cal_list.append(j)
while (len(demand_cal_list) != N):
	for j in range (N):
		if ((stage_list[j]['avgDemand'] == 0) or (j in demand_cal_list)):
			continue
		cost_per_sum = 0
		for i in stage_list[j]['UpstreamStage']:
			if (stage_list[i]['StageType'] == 'Manuf'):
				cost_per_sum += 1/stage_list[i]['StageCost']
		for i in stage_list[j]['UpstreamStage']:
			if (stage_list[i]['StageType'] != 'Manuf'):
				stage_list[i]['avgDemand'] += stage_list[j]['avgDemand']
				stage_list[i]['stdDevDemand'] = math.sqrt(stage_list[i]['stdDevDemand']**2+stage_list[j]['stdDevDemand']**2)
			else:
				stage_list[i]['avgDemand'] += stage_list[j]['avgDemand']*(1/stage_list[i]['StageCost']/cost_per_sum)
				stage_list[i]['stdDevDemand'] = math.sqrt(stage_list[i]['stdDevDemand']**2\
					+(stage_list[j]['stdDevDemand']*((1/stage_list[i]['StageCost']/cost_per_sum)**2))**2)
		demand_cal_list.append(j)

# calculate holding cost
max_depth = 0
for j in range (N):
	if (stage_list[j]['RelDepth'] > max_depth):
		max_depth = stage_list[j]['RelDepth']
current_depth = max_depth - 1
while (current_depth >= 0):
	for j in range (N):
		if ((stage_list[j]['RelDepth'] != current_depth) or (stage_list[j]['UpstreamStage'] is None)):
			continue
		cost_per_sum = 0
		for i in stage_list[j]['UpstreamStage']:
			if (stage_list[i]['StageType'] == 'Manuf'):
				cost_per_sum += 1/stage_list[i]['StageCost']
		for i in stage_list[j]['UpstreamStage']:
			if (stage_list[i]['StageType'] != 'Manuf'):
				stage_list[j]['HoldingCost'] += stage_list[i]['HoldingCost']
			else:
				stage_list[j]['HoldingCost'] += stage_list[i]['HoldingCost']*(1/stage_list[i]['StageCost']/cost_per_sum)
	current_depth -= 1
for j in range (N):
	if (stage_list[j]['StageType'] == 'Part'):
		stage_list[j]['HoldingCost'] = round(stage_list[j]['HoldingCost']*0.05,2)
	elif ((stage_list[j]['StageType'] == 'Manuf') or (stage_list[j]['StageType'] == 'Trans')):
		stage_list[j]['HoldingCost'] = round(stage_list[j]['HoldingCost']*0.1,2)
	elif ((stage_list[j]['StageType'] == 'Retail') or (stage_list[j]['StageType'] == 'Dist')):
		stage_list[j]['HoldingCost'] = round(stage_list[j]['HoldingCost']*0.2,2)
#print(stage_list)

#define objective function
def Phi(j, value):
	phi_sum_t = 0
	for t in range (len(stage_list[j]['StageTime'])):
		phi_sum_t += stage_list[j]['ServiceLevel']*stage_list[j]['stdDevDemand']*stage_list[j]['StageTime'][t][1]\
									*math.sqrt(value+stage_list[j]['StageTime'][t][0])
	return phi_sum_t

# intialization
f_list = [] # element j = [f_r^{j,k}]
alpha_list = [] # element j = [alpha_r^{j,k}]
M_list = [] #element j = [M_r^j]
R = [] #element j = R_j
for j in range (N):
	x_lower_bound = float('inf')
	for t in range (len(stage_list[j]['StageTime'])):
		if (stage_list[j]['StageTime'][t][0] < x_lower_bound):
			x_lower_bound = stage_list[j]['StageTime'][t][0]
	f_list.append([Phi(j,-x_lower_bound), Phi(j,M)])
	alpha_list.append([(Phi(j,M)-Phi(j,-x_lower_bound))/(M+x_lower_bound), 0])
	M_list.append([-x_lower_bound, M])
	R.append(2)
# iteration
iteration_index = 1
while (1):
	# optimization
	solver = pywraplp.Solver.CreateSolver('SCIP')
	# variables
	u = []
	z = []
	X = []
	SI = []
	S = []
	for j in range (N):
		u_r = []
		z_r = []
		for r in range (R[j]-1):
			u_r.append(solver.IntVar(0.0, solver.infinity(), 'u'+str(j)+str(r)))
			z_r.append(solver.NumVar(-solver.infinity(), solver.infinity(), 'z'+str(j)+str(r)))
			solver.Add(u_r[r] <= 1)
		u.append(u_r)
		z.append(z_r)
	for j in range (N):
		X.append(solver.NumVar(-solver.infinity(), solver.infinity(), 'X'+str(j)))
		SI.append(solver.NumVar(0.0, solver.infinity(), 'SI'+str(j)))
		S.append(solver.NumVar(0.0, solver.infinity(), 'S'+str(j)))
	# constraints
	for j in range(N):
		for t in range (len(stage_list[j]['StageTime'])):
			solver.Add(X[j] + stage_list[j]['StageTime'][t][0] >= 0)
		sum_z = 0
		sum_u = 0
		for r in range (R[j]-1):
			sum_z += z[j][r]
			sum_u += u[j][r]
		solver.Add(sum_z == X[j])
		solver.Add(sum_u == 1)
		solver.Add(X[j] == SI[j] - S[j])
		if (stage_list[j]['DownstreamStage'] is not None):
			for i in stage_list[j]['DownstreamStage']:
				solver.Add(SI[i] - S[j] >= 0)
		if (stage_list[j]['UpstreamStage'] is None):
			solver.Add(SI[j] == 0)
		for r in range (R[j]-1):
			solver.Add(z[j][r] <= M_list[j][r+1] * u[j][r])
			solver.Add(z[j][r] >= M_list[j][r] * u[j][r])
		if (stage_list[j]['maxServiceTime'] is not None):
			solver.Add(S[j] <= stage_list[j]['maxServiceTime'])
	# objective
	obj = 0
	for j in range (N):
		for r in range (R[j]-1):
			obj += stage_list[j]['HoldingCost']*(f_list[j][r]*u[j][r]+alpha_list[j][r]*z[j][r]-alpha_list[j][r]*M_list[j][0]*u[j][r])
	solver.Minimize(obj)
	# solve the problem
	status = solver.Solve()
	print(solver.Objective().Value())
	if status == pywraplp.Solver.OPTIMAL:
		print('Solution:')
		print('Objective value =', solver.Objective().Value())
	else:
		print('The problem does not have an optimal solution.')
	print('\nAdvanced usage:')
	print('Problem solved in %f milliseconds' % solver.wall_time())
	print('Problem solved in %d iterations' % solver.iterations())
	print('Problem solved in %d branch-and-bound nodes' % solver.nodes())

	# termination criterion
	flag = 0
	phi_sum = 0
	for j in range (N):
		phi_sum += stage_list[j]['HoldingCost']*Phi(j,round(X[j].solution_value(),2))
	for j in range (N):
		phi_temp = 0
		for r in range (R[j]-1):
			phi_temp += f_list[j][r]*u[j][r].solution_value()+alpha_list[j][r]*z[j][r].solution_value()-\
									alpha_list[j][r]*M_list[j][0]*u[j][r].solution_value()
		if ((stage_list[j]['HoldingCost']*abs(Phi(j,round(X[j].solution_value(),2))-phi_temp)) > (epslion_percent*phi_sum/N)):
			flag = 1
			break
	if ((flag == 0) or (iteration_index >= MAX_ITE)):
		break
	
	#update R, f, alpha, M for each j
	for j in range (N):
		n = R[j]
		for n_temp in range (R[j]-1):
			if ((round(X[j].solution_value(),2) >= M_list[j][n_temp]) and (round(X[j].solution_value(),2) < M_list[j][n_temp+1])):
				n = n_temp
				break
		if (n == R[j]):
			print("the pre-determined M is too small!")
		if (round(X[j].solution_value(),2) == M_list[j][n]):
			continue
		
		alpha_list[j].append(alpha_list[j][R[j]-1])
		f_list[j].append(f_list[j][R[j]-1])
		for n_temp in range (R[j]-n-2):
			alpha_list[j][R[j]-n_temp-1] = alpha_list[j][R[j]-n_temp-2]
			f_list[j][R[j]-n_temp-1] = f_list[j][R[j]-n_temp-2]
		alpha_list[j][n] = (Phi(j,round(X[j].solution_value(),2))-Phi(j,M_list[j][n]))/(round(X[j].solution_value(),2)-M_list[j][n])
		f_list[j][n] = Phi(j,round(X[j].solution_value(),2))-alpha_list[j][n]*(round(X[j].solution_value(),2)-M_list[j][0])
		alpha_list[j][n+1] = (Phi(j,M_list[j][n+1])-Phi(j,round(X[j].solution_value(),2)))/(M_list[j][n+1]-round(X[j].solution_value(),2))
		f_list[j][n+1] = Phi(j,M_list[j][n+1])-alpha_list[j][n+1]*(M_list[j][n+1]-M_list[j][0])
		
		R[j] += 1

		M_list[j].append(0)
		for n_temp in range (R[j]-n-2):
			M_list[j][R[j]-n_temp-1] = M_list[j][R[j]-n_temp-2]
		M_list[j][n+1] = round(X[j].solution_value(),2)

	iteration_index += 1

# output result to csv: Excel Data + SI, S, obj, real obj value, number of iterations
for j in range (N):
	stage_list[j]['InboundServiceTime'] = round(SI[j].solution_value())
	stage_list[j]['OutboundServiceTime'] = round(S[j].solution_value())
	stage_list[j]['SafetyInventoryCost'] = stage_list[j]['HoldingCost']*Phi(j,round(X[j].solution_value(),2))
	phi_temp = 0
	for r in range (R[j]-1):
		phi_temp += f_list[j][r]*u[j][r].solution_value()+alpha_list[j][r]*z[j][r].solution_value()\
								-alpha_list[j][r]*M_list[j][0]*u[j][r].solution_value()
	stage_list[j]['ApproxObjValue'] = stage_list[j]['HoldingCost']*phi_temp
	stage_list[j]['ObjValueGap'] = stage_list[j]['HoldingCost']*(Phi(j,round(X[j].solution_value(),2))-phi_temp)
	stage_list[j]['IteNum'] = iteration_index
df = pd.DataFrame(stage_list)
df.to_csv(datapath.split('.')[0].split('-')[0]+"-Result.csv")

# export to json
jsdata = {'results': [{'columns':['user', 'entity'],'data':[{'graph': {'nodes':[],'relationships':[]}}]}],'errors':[]}
for j in range (N):
	if (stage_list[j]['DownstreamStage'] is None):
		jsdata['results'][0]['data'][0]['graph']['nodes'].append({'id': str(j),
																															'labels': [stage_list[j]['StageType']],
																															'properties': {
																																'Stage Name': stage_list[j]['StageName'],
																																'Holding Cost': round(stage_list[j]['HoldingCost']),
																																'Average Demand': round(stage_list[j]['avgDemand'],2),
																																'Demand Std Dev.': round(stage_list[j]['stdDevDemand'],2),
																																'Max Service Time': stage_list[j]['maxServiceTime'],
																																'Service Level': stage_list[j]['ServiceLevel'],
																																'Lead Time': stage_list[j]['StageTime'],
																																'Safety Inventory Cost': round(stage_list[j]['SafetyInventoryCost'],2)
																															}
																															})
	else:
		jsdata['results'][0]['data'][0]['graph']['nodes'].append({'id': str(j),
																															'labels': [stage_list[j]['StageType']],
																															'properties': {
																																'Stage Name': stage_list[j]['StageName'],
																																'Holding Cost': round(stage_list[j]['HoldingCost']),
																																'Average Demand': round(stage_list[j]['avgDemand'],2),
																																'Demand Std Dev.': round(stage_list[j]['stdDevDemand'],2),
																																'Lead Time': stage_list[j]['StageTime'],
																																'Safety Inventory Cost': round(stage_list[j]['SafetyInventoryCost'],2)
																															}
																															})

rela_index = 0
for j in range (N):
	if (stage_list[j]['DownstreamStage'] is None):
		continue
	for i in stage_list[j]['DownstreamStage']:
		jsdata['results'][0]['data'][0]['graph']['relationships'].append({'id': str(rela_index),
																	'type': str(round(stage_list[j]['OutboundServiceTime'])),
																	'startNode': str(j),
																	'endNode': str(i),
																	'properties': {'Outbound Service Time '+str(j)+' -> '+str(i): round(stage_list[j]['OutboundServiceTime'])}
																	})
		rela_index += 1

with open('Visualization/docs/json/neo4jData.json', 'w') as json_file:
  json.dump(jsdata, json_file, indent=2)
