#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import uproot
from datetime import date
from datetime import datetime
import subprocess
import time
import optparse

workdir=os.getcwd()

def job_version(workdir):
    version_date = "v_1_"+str(date.today())
    if os.path.isdir(workdir):
        dirs= [f for f in os.listdir(workdir) if os.path.isdir(os.path.join(workdir,f)) and f[:2]=='v_']
        version_max = 0
        for d in dirs:
            version = int(d.split("_")[1])
            if version > version_max: version_max = version
        version_date = "v_"+str(version_max+1)+"_"+str(date.today())
    return version_date

def batch_files(path, file_per_batch):
    #n_files=len(os.listdir(path))
    batches={}
    j=0
    batches[j]=[]
    for i, filename in enumerate(os.listdir(path),1):
        batches[j].append(filename)
        if i%file_per_batch == 0:
            j+=1
            batches[j]=[]
    return batches
        
        

        
def prepare_jobs(path_electrons, path_pions, batches_elec, batches_pions,thr, name='batch', local=True):
    version=job_version(workdir)
    os.chdir(workdir)
    os.makedirs(version)
    os.makedirs(version+'/electrons')
    os.makedirs(version+'/pions')
    elec_dir=workdir+'/'+version+'/electrons'
    pions_dir=workdir+'/'+version+'/pions'
    
    
    os.chdir(elec_dir)
    for i in batches_elec:
        os.makedirs('elec_{}'.format(i))
        with open('elec_{}/param.py'.format(i), 'w') as param:
            print('path="{}"\n'.format(path_electrons), file=param)
            print('files={}\n'.format(batches_elec[i]), file=param)
            print('thr={}\n'.format(thr), file=param)
            print('savedir="'+elec_dir+'/elec_{}"'.format(i), file=param)
            st=os.stat('elec_{}/param.py'.format(i))
            os.chmod('elec_{}/param.py'.format(i), st.st_mode | 0o744)

        with open(name+'_{}.sub'.format(i), 'w') as script:
            
            print ('#! /bin/bash',file=script)
            print ('uname -a',file=script)
            #print >>script, 'cd', workdir
            #print >>script, 'source init_env_polui.sh'
            print ('cd', workdir+'/'+version,file=script)
            print ( 'python -W ignore '+workdir+'/preprocessing.py -f '+elec_dir+'/elec_{}'.format(i),file=script)
            #print >>script, 'touch', name+'_{}.done'.format(i)
            file=name+'_{}.sub'.format(i)
            st=os.stat(file)
            os.chmod(file, st.st_mode | 0o744)
            
            
            
    os.chdir(pions_dir)
    for i in batches_pions:
        os.makedirs('pions_{}'.format(i))
        with open('pions_{}/param.py'.format(i), 'w') as param:
            print('path="{}"\n'.format(path_pions), file=param)
            print('files={}\n'.format(batches_pions[i]), file=param)
            print('thr={}\n'.format(thr), file=param)
            print('savedir="'+pions_dir+'/pions_{}"'.format(i), file=param)
            st=os.stat('pions_{}/param.py'.format(i))
            os.chmod('pions_{}/param.py'.format(i), st.st_mode | 0o744)
        with open(name+'_{}.sub'.format(i), 'w') as script:
            print ('#! /bin/bash', file=script)
            print ('uname -a',file=script)
            print ( 'cd', workdir, file=script)
            if local == False:
                print('source init_env_polui.sh', file=script)
            print ('cd', workdir+'/'+version,file=script)
            print ( 'python -W ignore '+workdir+'/preprocessing.py -f '+pions_dir+'/pions_{}'.format(i),file=script)
            #print >>script, 'touch', name+'_{}.done'.format(i)
            file=name+'_{}.sub'.format(i)
            st=os.stat(file)
            os.chmod(file, st.st_mode | 0o744)
        
   
    return elec_dir, pions_dir, version
    

def launch_jobs(elec_dir, pions_dir, batches_elec, batches_pions,version,  name='batch', queue='long', proxy='~/.t3/proxy.cert',stop=False, local=True):
    if local == True:
        machine='llruicms01'
    else:
        machine='llrt3'

    print ('Sending {0}+{1} jobs on {2}'.format(len(batches_elec), len(batches_pions), queue+'@{}'.format(machine)))
    print ('===============')
    with open(workdir+'/'+version+'/log.txt','a') as log:
        print('Number of electrons batches: {}\nNumber of pions batches: {}\n ========== '.format(len(batches_elec), len(batches_pions)),file=log)
    
    for i,batch in enumerate(batches_elec):
        with open(workdir+'/'+version+'/log.txt','a') as log:
            qsub_args = []
            if local==False:
                qsub_args.append('-{}'.format(queue))

            qsub_args.append(elec_dir+'/'+name+'_{}.sub'.format(i))
            
            if local==False:
                qsub_command = ['/opt/exp_soft/cms/t3/t3submit']+ qsub_args
            if local==True:
                qsub_command = qsub_args
            #print('qsub_command=', qsub_command)
            print (str(datetime.now()),' '.join(qsub_command))
            print(str(datetime.now()),':elec_batch_{} start'.format(i),file=log)
            start=time.time()
            status=subprocess.run(qsub_command, capture_output=False)
           
            if status.returncode==0:
                duration=time.time()-start
                print(str(datetime.now()),':elec_batch_{} done in {}s'.format(i, duration),file=log)
            else:
                print(':elec_batch_{}: failed'.format(i),file=log)
            print ('===============')
        if stop==True:
            
            break

    for i,batch in enumerate(batches_pions):
        with open(workdir+'/'+version+'/log.txt','a') as log:
            qsub_args = []
            if local == False:
                qsub_args.append('-{}'.format(queue))

            qsub_args.append(pions_dir+'/'+name+'_{}.sub'.format(i))
            if local==False:
                qsub_command = ['/opt/exp_soft/cms/t3/t3submit']+ qsub_args
            if local==True:
                qsub_command = qsub_args
            print (str(datetime.now()),' '.join(qsub_command))
            print(str(datetime.now()),':pion_batch_{} start'.format(i),file=log)
            start=time.time()
            status=subprocess.run(qsub_command, capture_output=False)
            
            if status.returncode==0:
                duration=time.time()-start
                print(str(datetime.now()),':pion_batch_{} done in {}s'.format(i, duration),file=log)
            else:
                print(':pion_batch_{}: failed'.format(i),file=log)
            print ('===============')
        if stop==True:
            print('Test ended')
            with open(workdir+'/'+version+'/log.txt','a') as log:
                print('Test ended', file=log)
            break
    
        
    
    
    
    
def main(parameters_file):
    import importlib
    parameters=importlib.import_module(parameters_file)
    thr= parameters.threshold
    path_electrons=parameters.path_elec
    path_pions=parameters.path_pions
    file_per_batch_elec=parameters.file_per_batch_elec
    file_per_batch_pion=parameters.file_per_batch_pion
    stop=parameters.stop
    local=parameters.local
    
    batches_elec=batch_files(path_electrons, file_per_batch_elec)
    batches_pions=batch_files(path_pions, file_per_batch_pion)
      
    elec_dir, pions_dir, version=prepare_jobs(path_electrons, path_pions, batches_elec, batches_pions, thr,local=local)
    os.chdir(workdir)
    launch_jobs(elec_dir, pions_dir, batches_elec, batches_pions, version, stop=stop, local=local)
   
    
if __name__=='__main__':

    parser = optparse.OptionParser()
    parser.add_option("-p","--param",type="string", dest="param_file", help="select the parameter file")
    (opt, args) = parser.parse_args()

    parameters=opt.param_file
    main(parameters)
    






