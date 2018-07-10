import pandas as pd
import numpy as np
import time
import tkinter.constants, tkinter.filedialog
import sys
import random

#calculate current schedule total cost time
def schedule_time(M,r,p):
	s,d,D={},{},{}
	v=0

	for i in range(len(r)):
		s[i]=M[p[0]][r[i]]
		d[i]=v
		D[i,p[0]]=v
		v=v+M[p[0]][r[i]]

	for j in range(len(p)):
		D[0,j]=0

	for j in range(1,len(p)):
		for i in range(0,len(r)-1):
			s[i]=s[i]+M[p[j]][r[i]]
			D[i+1,j]=max(0,s[i]+d[i]-s[i+1]-d[i+1])
			d[i+1]=d[i+1]+D[i+1,j]
		
		s[len(r)-1]=s[len(r)-1]+M[p[j]][r[i+1]]

	v=0
	for i in range(len(r)):
		v=v+d[i]
	return v

#list all sequence after every motion 
def permutation(j, V, Q, epsilon):
	vec = j[:]
	Q_temp = [[Q[x][y] for y in range(len(Q[0]))] for x in range(len(Q))]
	for i in j:
		if random.uniform(0, 1) > epsilon: #larger then epsilon repersent choosing by best way
			if j.index(i) == 0: #if it is the first choice, according to V
				temp = V.index(min(float(s) for s in V))
				for k in range(0,len(Q_temp[0])):
					Q_temp[k][temp] = sys.maxsize
				a, b = 0, vec.index(temp)
				vec[b], vec[a] = vec[a], vec[b]
			else: # else according to Q
				temp = Q_temp[i - 1].index(lowest_cost(Q_temp,i - 1))
				for k in range(0,len(Q_temp[0])):
					Q_temp[k][temp] = sys.maxsize
				a, b = i, vec.index(temp)
				vec[b], vec[a] = vec[a], vec[b]
		else: # else by random
			temp = random.choice(vec)
			a, b = i, vec.index(temp)
			vec[b], vec[a] = vec[a], vec[b]
	return vec
	
#get best cost in series sequence
def lowest_cost(Q, r):
	cost = sys.maxsize
	for i in range(0, len(Q[0])):
		if Q[r][i] < cost:
			cost = Q[r][i]
	return cost
	
#update Q
def update_Q(Q, r, cost):
	gamma = 0.8
	alpha = 0.1
	for i in range(0, len(r) - 1):
		Q[r[i]][r[i+1]] = Q[r[i]][r[i+1]] + alpha * (cost + gamma * lowest_cost(Q,r[i]) - Q[r[i]][r[i+1]])
	return Q

#update V
def update_V(V, Q, r, cost):
	gamma = 0.8
	alpha = 0.1
	V[r[0]] = V[r[0]] + alpha * (cost + gamma * lowest_cost(Q,r[0]) - V[r[0]])
	return V
	
#read file and transfer to python list datatype
#    filename = 'C:\\Users\\wu\\Documents\\MEGA\\graduate\\碩一(下)\\作業研究應用\\ORA_project\\final project\\GA\\20x5_flowshop.xlsx'#tkFileDialog.askopenfilename(initialdir = "/",title = "Select file")
filename = 'C:\\Users\\wu\\Documents\\MEGA\\graduate\\碩一(下)\\作業研究應用\\ORA_project\\final project\\GA\\flow_shop.xlsx'#tkFileDialog.askopenfilename(initialdir = "/",title = "Select file")
pt_tmp=pd.read_excel(filename,sheet_name="S1",index_col =[0])
pt = pt_tmp.as_matrix().tolist()

m_sequence = list(range(0,len(pt[0]))) # m_sequence represent machine order in each job
j_sequence = list(range(0,len(pt))) #j_sequence repersent job order
start_sequence = list(range(0,len(pt)))
motion = [] #declare motion
for i in range (0,len(pt)):
	for j in range (i,len(pt)):
		if i != j:
			motion.append([i,j])
time_cost = schedule_time(pt, m_sequence, j_sequence)

s = [] #define final state series
print (time_cost)

#start main function
start_time = time.time()
final_cost = sys.maxsize
final_s = []
final_epoch = 0
for epo in range(0,50):
	epsilon = 1 # random threshold, initial by 1
	#QL main function

	Q = []
	V = []
	for i in range(0,len(pt)):
		Q_temp = []
		V.append(0)
		for j in range(0,len(pt)):
			Q_temp.append(0)
		Q.append(Q_temp)
	for loop_times in range(0,10000):
		epsilon = epsilon*0.999 # after one loop, threshold desend by *0.999999
		r = permutation(j_sequence, V, Q, epsilon)
		cost = schedule_time(pt, m_sequence, r)
		V = update_V(V, Q, r, cost)
		Q = update_Q(Q, r, cost)
	s_result = []
	choose_index = V.index(min(float(s) for s in V))
	s_result.append(choose_index)
	for i in range(0,len(V)):
		Q[i][choose_index] = sys.maxsize
	for i in range(1,len(V)):
		next_index = Q[choose_index].index(min(float(s) for s in Q[choose_index]))
		s_result.append(next_index)
		for j in range(0,len(V)):
			Q[j][next_index] = sys.maxsize
		choose_index = next_index
	now_cost = schedule_time(pt, m_sequence, s_result)
	if final_cost > now_cost:
		final_cost = now_cost
		final_s = s_result
		final_epoch = epo
	print ("The %d epoch result is %s , cost is %d" % (epo, s_result, now_cost))
end_time = time.time()
print ("Ending learning. The best result by learning is %s at number %d epoch, cost is %d" % (final_s, final_epoch, final_cost))
print ("Total time cost: %f s" % (end_time - start_time))