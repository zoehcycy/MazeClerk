import os
import numpy as np
import pandas as pd
import holoviews as hv
import lib.LocationTracking_Functions as lt
import lib.VelocityAndArmRetrieval_Functions as va
import smtplib
from email.message import EmailMessage

########################################################################################

def Batch_Process(video_dict,tracking_params,bin_dict,region_names,stretch,crop,poly_stream,poly_stream_1,scaling=None):
    
    #get polygon
    if poly_stream != None:
        lst = []
        for poly in range(len(poly_stream.data['xs'])):
            x = np.array(poly_stream.data['xs'][poly]) #x coordinates
            y = np.array(poly_stream.data['ys'][poly]) #y coordinates
            lst.append( [ (x[vert],y[vert]) for vert in range(len(x)) ] )
        poly = hv.Polygons(lst).opts(fill_alpha=0.1,line_dash='dashed')
    
    heatmaps = []
    
    # exclude 'EmptyBox' video from processing list
    for i in range(len(video_dict['FileNames'])):
        if video_dict['FileNames'][i][-14:-5] == '_EmptyBox':
            del video_dict['FileNames'][i]
    
    # Batch process
    for file in video_dict['FileNames']:
        try:
            video_dict['file'] = file #used both to set the path and to store filenames when saving
            video_dict['fpath'] = os.path.join(os.path.normpath(video_dict['dpath']), file)
            print('Processing File: {f}'.format(f=file),video_dict['fpath'])
            
            # Track location and save a LocationOutput file
            reference = lt.Reference(video_dict,crop,num_frames=100) 
            location = lt.TrackLocation(video_dict,tracking_params,reference,crop)
            if region_names!=None:
                location = lt.ROI_Location(reference,poly_stream,region_names,location)
            location.to_csv(os.path.splitext(video_dict['fpath'])[0] + '_LocationOutput.csv')
            
            # Choices: 'ABFG','BCEG','ACDF','BDFH'
            baited = file.split('_')[4]
            config = va.specify_configuration(baited)
            
            # Scatter plot velocity-time
            va.velocity_distribution_show(video_dict,poly_stream_1,region_names,config,scaling)
            
            referenceMemError,workingMemError = va.arm_retrieve_errors(video_dict,baited)
            
            file_summary = lt.Summarize_Location(location, video_dict, bin_dict=bin_dict, region_names=region_names)
            file_summary.to_csv(os.path.splitext(video_dict['fpath'])[0] + '_SummaryStats.csv')
            

            try: #Add summary info for individual file to larger summary of all files
                summary_all = pd.concat([summary_all,file_summary])
            except NameError: #to be done for first file in list, before summary_all is created
                summary_all = file_summary

            #Plot Heat Map
            image = hv.Image((np.arange(reference.shape[1]), np.arange(reference.shape[0]), reference)).opts(
            width=int(reference.shape[1]*stretch['width']),
            height=int(reference.shape[0]*stretch['height']),
            invert_yaxis=True,cmap='gray',toolbar='below',
            title=file+": Motion Trace")
            points = hv.Scatter(np.array([location['X'],location['Y']]).T).opts(color='navy',alpha=.2)
            heatmaps.append(image*poly*points) if poly_stream!=None else heatmaps.append(image*points)
            
            print('--------------------------')

        except:
            # send an alerting email to zoehcycy@gmail.com
            # credential is stored on local device for safety concerns
            error_msg = '--------' + file + '--------\n'
            send_alerting_email()
            pass
        
    #Write summary data to csv file
    sum_pathout = os.path.join(os.path.normpath(video_dict['dpath']), 'BatchSummary.csv')
    summary_all.to_csv(sum_pathout)
    
    layout = hv.Layout(heatmaps)
    return layout

########################################################################################

def send_alerting_email():

    smtpserver = 'smtp.163.com'
    user = 'NEC_lab@163.com'
    sender = 'NEC_lab<NEC_lab@163.com>' 
    receiver = "zoehcycy@gmail.com;NEC_lab@163.com"
    with open(r'D:\ZOE-STORE-LAPTOP\NEC_lab_163_credential.txt', 'r') as file:
        credential = file.read().replace('\n', '')
        msg = EmailMessage()
        msg.set_content(file.read())
        
    msg['Subject'] = 'NEC_Lab_Unhandled_Exception'
    msg['From'] = 'NEC_lab<NEC_lab@163.com>'  
    msg['To'] = "zoehcycy@gmail.com;NEC_lab@163.com"
    
    smtp = smtplib.SMTP()
    smtp.connect(smtpserver)
    smtp.login(user, credential)
    smtp.send_message(msg)

    smtp.quit()
