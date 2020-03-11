#
#List of Functions in LocationTracking_Functions.py
#

# specify_configuration(baited)
# set_scale(poly_stream)
# velocity_calculation(df,scale)
# velocity_plot(x,y,cut)
# velocity_distribution_show(video_dict,data,time,velocity,region_names,config)
# arm_retrieve_show(video_dict,region_names,config)
# arm_retrieve_errors(video_dict,data,region_names)

########################################################################################

import os
import LocationTracking_Functions as lt
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import holoviews as hv
from holoviews import opts
from holoviews import streams
from holoviews.streams import Stream, param
hv.notebook_extension('bokeh')

########################################################################################

def specify_configuration(baited):
    # specify arm configuration
    if baited == "ACDF":
        config = ["ArmA","ArmC","ArmD","ArmF"]
    elif baited == "BDFH":
        config = ["ArmB","ArmD","ArmF","ArmH"]
    elif baited == "BCEG":
        config = ["ArmB","ArmC","ArmE","ArmG"]
    elif baited == "ABFG":
        config = ["ArmA","ArmB","ArmF","ArmG"]
    else:
        print("Error! Check the value you entered for 'baited'!")
    return config


def set_scale(poly_stream):
    vertices = poly_stream.data

    real_distance = 8 * 7.125 * 2.54       #Eight edges, each 7.125 inches
    pixel_distance = 0                     #Find the total pixel length of edges

    n = len(vertices['xs'][0])
    for i in range(n-1):
        dx = vertices['xs'][0][i] - vertices['xs'][0][i+1]
        dy = vertices['ys'][0][i] - vertices['ys'][0][i+1]
        edge = math.sqrt(dx*dx + dy*dy)
        pixel_distance += edge
    pixel_distance += math.sqrt(math.pow((vertices['xs'][0][-1]-vertices['xs'][0][0]),2) + 
                            math.pow((vertices['ys'][0][-1]-vertices['ys'][0][0]),2))

    cm_per_pixel = real_distance / pixel_distance
    print("Conversion:\n",cm_per_pixel,"cm/pixel")

    return cm_per_pixel


def velocity_calculation(df,scale=None):

    arr = df.to_numpy()
    arr_x = arr[:, 9]
    arr_y = arr[:, 10]

    fps = 30.0
    dt = 1.0 / fps
    time = np.arange(0, dt * len(arr_x), dt)                               
    velocity = []

    for i in range(0, len(arr_x) - 1):
        dx = arr_x[i+1] - arr_x[i]
        dy = arr_y[i+1] - arr_y[i]
        movement = math.sqrt(dx * dx + dy * dy) * scale
        velocity.append(movement / dt)

    # add a value to keep len(velocity) consistent with df
    velocity.append(velocity[-1])

    sequences = {}
    sequences['velocity'] = velocity
    sequences['time'] = time

    return sequences


def velocity_plot(x,y,cut):

    plt.figure(figsize=(12,4))                              # plot the original data with an axhline noting the mean level
    plt.subplot(121)
    plt.plot(x, y)
    plt.axhline(cut, color='k')
    plt.title("Velocity-Time")
    plt.xlabel("T/Second")
    plt.ylabel("V/cm_per_second")
    plt.ylim([0,100])
    s = "mean:" + str(cut) + "cm/s"
    plt.text(x=0, y=cut, s=s)

    plt.subplot(122)                                        # plot the sorted velocity sequence to see the distribution
    y_sorted = sorted(y)
    plt.plot(x, y_sorted)
    plt.axhline(cut, color='k')
    plt.title("Velocity Values Distribution")
    plt.xlabel("Index")
    plt.ylabel("V/cm_per_second")
    plt.ylim([0,100])
    plt.text(x=0, y=cut, s=s)
    plt.show()                                              # display and save the results


def velocity_distribution_show(video_dict,poly_stream_1,region_names,config,scaling=None):
    
    with open((os.path.splitext(video_dict['fpath'])[0] + '_LocationOutput.csv'), 'r') as csvFile:
        df_1 = pd.read_csv(csvFile)
    
    data = df_1[['Frame','X','Y','Distance','Center','ArmA','ArmB','ArmC','ArmD','ArmE','ArmF','ArmG','ArmH',]]
    data = data*1  
    
    if scaling != None:
        time = velocity_calculation(df=df_1,scale=scaling)['time']
        velocity = velocity_calculation(df=df_1,scale=scaling)['velocity']
    else:
        time = velocity_calculation(df=df_1,scale=None)['time']
        velocity = velocity_calculation(df=df_1,scale=None)['velocity']
    df_v = pd.DataFrame({'Frame':data['Frame'],'Velocity':velocity,'Arm':np.zeros(len(velocity))})

    for a in region_names:
        for i in range(len(data['Frame'])):
            if (data[a][i] == True):
                df_v['Arm'][i] = a
    save_path = os.path.splitext(video_dict['fpath'])[0] + '_VelocityAndArmRetrieval.csv'
    df_v.to_csv(save_path,index=False)
    print('Save results to:'+save_path)
    df_v.head()

    velocity = df_v['Velocity'].to_numpy()

    plt.figure(figsize=(12,6))
    for i in range(len(df_v['Frame'])):
        if df_v['Arm'][i] in config:
            plt.scatter(time[i],velocity[i],c="y",marker=".")
        elif df_v['Arm'][i] == 'Center':
            plt.scatter(time[i],velocity[i],c="b",marker="x")
        else:
            plt.scatter(time[i],velocity[i],c="k",marker=".")

            mean = sum(velocity) / len(velocity)
    plt.axhline(mean, color='k')
    plt.title("Arm Retrieve Performance")
    plt.xlabel("T/Second")
    plt.ylabel("V/cm_per_second")
    s = "mean:" + str('{0:.2f}'.format(mean)) + "cm/s"
    plt.text(x=0, y=max(velocity), s=s, fontweight='bold')
    plt.savefig(video_dict['fpath'][0:-4] + '_ArmRetrieve.png')




def arm_retrieve_show(video_dict,region_names,config):

    with open(((video_dict['fpath'][0:-4]) + '_SummaryStats.csv'), 'r') as csvFile:
        df_2 = pd.read_csv(csvFile)

    summ = df_2[region_names]

    a = np.arange(len(region_names))
    p = summ.values[0]
    plt.title("Percentage of time in Each Arm")
    plt.xticks(a,region_names)

    sum_config = 0
    count = 0

    # draw the bar graph
    for i,v in enumerate(a):
        
        if list(summ.keys())[i] in config:
            # label the bar
            plt.text(i-0.3,p[v]+0.002,str('{0:.2f}'.format(p[v])),color='y',fontweight='bold')
            plt.bar(i,p[i],color='y')
            sum_config += p[v]
            if p[v] >= sorted(p)[-4]:
                count = count + 1
            
        elif list(summ.keys())[i] == 'Center':
            plt.text(i-0.3,p[v]+0.002,str('{0:.2f}'.format(p[v])),color='b',fontweight='bold')  
            plt.bar(i,p[i],color='b')
            
        else:
            plt.text(i-0.3,p[v]+0.002,str('{0:.2f}'.format(p[v])),
                    color='k',fontweight='bold')
            plt.bar(i,p[i],color='k')

    print('Total percentage of time in configured arms: ', sum_config)
    print('Among the top 4 regions, ', count, ' are configured arms.')


def arm_retrieve_errors(video_dict,baited):
    #Output the number of working and reference memory errors for the given trial.  This information
    #is to be entered into the MATLAB GUI

    with open(((video_dict['fpath'][0:-4]) + '_LocationOutput.csv'), 'r') as csvFile:
        df = pd.read_csv(csvFile)
        
    data = df[['ArmA','ArmB','ArmC','ArmD','ArmE','ArmF','ArmG','ArmH',]]
    r = ['ArmA','ArmB','ArmC','ArmD','ArmE','ArmF','ArmG','ArmH',]
    data = data*1
    
    singleData = data[r].loc[(data[r].shift() != data[r]).any(axis=1)]

    A = singleData['ArmA']
    B = singleData['ArmB']
    C = singleData['ArmC']
    D = singleData['ArmD']
    E = singleData['ArmE']
    F = singleData['ArmF']
    G = singleData['ArmG']
    H = singleData['ArmH']

    ACDF = list(zip(*[A,C,D,F]))
    BDFH = list(zip(*[B,D,F,H]))
    BEGH = list(zip(*[B,E,G,H]))
    BCEG = list(zip(*[B,C,E,G]))
    ABFG = list(zip(*[A,B,F,G]))
    ADFH = list(zip(*[A,D,F,H]))
    CDEH = list(zip(*[C,D,E,H]))
    ACEG = list(zip(*[A,C,E,G]))

    lst = list();

    if sum(A) > 0:
        lst.append(1)
    else:
        lst.append(0)
    if sum(B) > 0:
        lst.append(1)
    else:
        lst.append(0)
    if sum(C) > 0:
        lst.append(1)
    else:
        lst.append(0)
    if sum(D) > 0:
        lst.append(1)
    else:
        lst.append(0)
    if sum(E) > 0:
        lst.append(1)
    else:
        lst.append(0)
    if sum(F) > 0:
        lst.append(1)
    else:
        lst.append(0)
    if sum(G) > 0:
        lst.append(1)
    else:
        lst.append(0)
    if sum(H) > 0:
        lst.append(1)
    else:
        lst.append(0)
    A_ent = lst[0]
    B_ent = lst[1]
    C_ent = lst[2]
    D_ent = lst[3]
    E_ent = lst[4]
    F_ent = lst[5]
    G_ent = lst[6]
    H_ent = lst[7]

    if baited == "ACDF":
        workingMemErrors = (np.sum(np.sum(ACDF, axis=0)-[A_ent,C_ent,D_ent,F_ent]) + np.sum(np.sum(BEGH, axis=0)-[B_ent,E_ent,G_ent,H_ent])) 
        referenceMemErrors = np.sum(np.sum(BEGH, axis=0))
        print("The number of reference memory errors was " + str(referenceMemErrors))
        print("The number of working memory errors was " + str(workingMemErrors))
    elif baited == "BDFH":
        workingMemErrors = (np.sum(np.sum(BDFH, axis=0)-[B_ent,D_ent,F_ent,H_ent]) + np.sum(np.sum(ACEG, axis=0)-[A_ent,C_ent,E_ent,G_ent])) 
        referenceMemErrors = np.sum(np.sum(ACEG, axis=0))
        print("The number of reference memory errors was " + str(referenceMemErrors))
        print("The number of working memory errors was " + str(workingMemErrors))
    elif baited == "BCEG":
        workingMemErrors = (np.sum(np.sum(BCEG, axis=0)-[B_ent,C_ent,E_ent,G_ent]) + np.sum(np.sum(ADFH, axis=0)-[A_ent,D_ent,F_ent,H_ent])) 
        referenceMemErrors = np.sum(np.sum(ADFH, axis=0))
        print("The number of reference memory errors was " + str(referenceMemErrors))
        print("The number of working memory errors was " + str(workingMemErrors))
    elif baited == "ABFG":
        workingMemErrors = (np.sum(np.sum(ABFG, axis=0)-[A_ent,B_ent,F_ent,G_ent]) + np.sum(np.sum(CDEH, axis=0)-[C_ent,D_ent,E_ent,H_ent])) 
        referenceMemErrors = np.sum(np.sum(CDEH, axis=0))
        print("The number of reference memory errors was " + str(referenceMemErrors))
        print("The number of working memory errors was " + str(workingMemErrors))
    else:
        print("Error! Check the value you entered for 'baited'!")
    
    return referenceMemErrors,workingMemErrors