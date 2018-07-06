# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 15:15:09 2018

Author: cheng-man wu
LinkedIn: www.linkedin.com/in/chengmanwu
Github: https://github.com/wurmen
"""

import pandas as pd
import numpy as np
import time
import sys
import pickle


pt_tmp=pd.read_excel(flow_shop.xlsx,sheet_name="S1",index_col =[0])
pt = pt_tmp.as_matrix().tolist()
j_num=len(pt)
m_num=5
m_sequence=[i for i in range(m_num)]

EPSILON = 0.2   # greedy police
ALPHA = 0.4   # learning rate
GAMMA = 0.8    # discount factor
MAX_EPISODES = 10000



#calculate current schedule total cost time
def schedule_time(M,r,p):
#    if len(p) != j_num:
#        reward=v=0
#    else:
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
    reward=1/v
        
    return v,reward


def action(state, q_table,j_sequence):
    state_actions_value = [q_table[tuple(state)][i] for i in state]
#    print(state)
    if (np.random.uniform() > EPSILON) or (all(i == 0 for i in state_actions_value)):
        action_job=int(np.random.choice(state, 1, replace=False))
    else:
        action_job=state[state_actions_value.index(max(state_actions_value))]
    
#    print(state,action_job)
    next_state=state[:]
    next_state.remove(action_job)
#    print(next_state)
    j_sequence.append(action_job)
    return next_state,action_job,j_sequence


def check_state(state,q_table,key_cont):
    key_name=tuple(state)
    if key_name not in q_table.keys():
        q_table[key_name] = q_table.pop(key_cont)
        key_cont+=1
    
    return q_table,key_cont

def rl():
    key_cont=0
    # generate Q table
    state_num=2**j_num
    q_table={key:[0 for i in range(j_num)] for key in range(state_num) }
    v_table=[sys.maxsize for i in range(j_num)]
    best_sol=sys.maxsize
    ep_count=0
    for episode in range(MAX_EPISODES):
        s=[i for i in range(j_num)]
        j_sequence=[]
#        print(s)
        q_table,key_cont=check_state(s,q_table,key_cont)
#        print('check')
        
        while not s==[]:
            next_state,action_job,j_sequence=action(s,q_table,j_sequence)
#            print(next_state)
            q_table,key_cont=check_state(next_state,q_table,key_cont)
            v,r=schedule_time(pt,m_sequence, j_sequence)
#            print(v,r)
            q_predict = q_table[tuple(s)][action_job]
            q_target = r + GAMMA * max(q_table[tuple(next_state)][:])
            q_table[tuple(s)][action_job] += ALPHA * (q_target - q_predict)
#            print(s)
            s=next_state
        ep_count+=1
        if v_table[j_sequence[0]]> v:
            v_table[j_sequence[0]]=v
        if ep_count%100==0:
            write_qtable = open('q_table.txt', 'wb')
            pickle.dump(q_table, write_qtable)
        if v < best_sol:
            best_sol=v
            best_seq=j_sequence[:]


    return best_sol,best_seq,q_table,v_table

def action_by_q_table(q_table):
    
    state=[i for i in range(j_num)]
    j_sequence=[]
    while not state==[]:
        state_actions_value = [q_table[tuple(state)][i] for i in state]
        action_job=state[state_actions_value.index(max(state_actions_value))]
        state.remove(action_job)
        next_state=state[:]
        j_sequence.append(action_job)
        state=next_state
    v,r=schedule_time(pt,m_sequence, j_sequence)
    
    return j_sequence,v

#def action_by_q_table(q_table):
#    
#    state=[]
#    j_sequence=[]
#    while len(state)!=j_num:
#        all_job=[ i for i in range(j_num)]
#        if state!=[]:
#            for j in state:
#                all_job.remove(j)
#        Remaining_job=all_job[:]
#        state_actions_value = [q_table[tuple(state)][i] for i in Remaining_job]
#        action_job=Remaining_job[state_actions_value.index(max(state_actions_value))]
#        state.append(action_job)
#        state.sort()
#        next_state=state[:]
#        j_sequence.append(action_job)
#        state=next_state
#        
#    j_sequence.reverse()
#    v,r=schedule_time(pt,m_sequence, j_sequence)
#    
#    return j_sequence,v
#

#read_qtable  = open('q_table.txt', 'rb') 
#q_table2 = pickle.loads(read_qtable.read())

start_time = time.time()        
if __name__ == "__main__":
    best_sol,best_seq,q_table,v_talbe= rl()
    j_seq_by_qtable,v=action_by_q_table(q_table)
    print(best_seq)
    print(best_sol)
    print(j_seq_by_qtable)
    print(v)
    print('the elapsed time:%s'% (time.time() - start_time))
