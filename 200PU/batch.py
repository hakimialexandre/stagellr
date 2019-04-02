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
    n_files=len(os.listdir(path))
    batches={}
    j=0
    batches[j]=[]
    for i, filename in enumerate(os.listdir(path),1):
        batches[j].append(filename)
        if i%file_per_batch == 0:
            j+=1
            batches[j]=[]
    return batches
        
        

        
def prepare_jobs(path_electrons, path_pions, batches_elec, batches_pions,thr, name='batch'):
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
            print ( workdir+'/preprocessing.py -f '+elec_dir+'/elec_{}'.format(i),file=script)
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
            print('savedir="'+pions_dir+'/pion_{}"'.format(i), file=param)
            st=os.stat('pions_{}/param.py'.format(i))
            os.chmod('pions_{}/param.py'.format(i), st.st_mode | 0o744)
        with open(name+'_{}.sub'.format(i), 'w') as script:
            print ('#! /bin/bash', file=script)
            print ('uname -a',file=script)
            #print >>script, 'cd', workdir
            #print >>script, 'source init_env_polui.sh'
            print ('cd', workdir+'/'+version,file=script)
            print ( workdir+'/preprocessing.py -f '+pions_dir+'/pions_{}'.format(i),file=script)
            #print >>script, 'touch', name+'_{}.done'.format(i)
            file=name+'_{}.sub'.format(i)
            st=os.stat(file)
            os.chmod(file, st.st_mode | 0o744)
        
   
    return elec_dir, pions_dir, version
    

def launch_jobs(elec_dir, pions_dir, batches_elec, batches_pions,version,  name='batch', queue='long', proxy='~/.t3/proxy.cert'):
    print ('Sending {0}+{1} jobs on {2}'.format(len(batches_elec), len(batches_pions), queue+'@llrcms01'))
    print ('===============')
    with open(workdir+'/'+version+'/log.txt','w') as log:
        for i,batch in enumerate(batches_elec):
            qsub_args = []
            #qsub_args.append('-{}'.format(queue))

            qsub_args.append(elec_dir+'/'+name+'_{}.sub'.format(i))
            #qsub_command = ['/opt/exp_soft/cms/t3/t3submit'] + qsub_args
            print (str(datetime.now()),' '.join(qsub_args))
            print(str(datetime.now()),':elec_batch_{} start\n'.format(i),file=log)
            status=subprocess.run(qsub_args, capture_output=False)
            print(str(datetime.now()), status.returncode, file=log)
            if status.returncode==0:
                print(':elec_batch_{} done\n'.format(i),file=log)

            for i,batch in enumerate(batches_pions):
            qsub_args = []
            #qsub_args.append('-{}'.format(queue))

            qsub_args.append(pions_dir+'/'+name+'_{}.sub'.format(i))
            #qsub_command = ['/opt/exp_soft/cms/t3/t3submit'] + qsub_args
            print (str(datetime.now()),' '.join(qsub_args))
            print(str(datetime.now()),':pion_batch_{} start\n'.format(i),file=log)
            status=subprocess.run(qsub_args, capture_output=False)
            print(str(datetime.now()), status.returncode, file =log)
            if status.returncode==0:
                print(':pion_batch_{} done\n'.format(i),file=log)
        
        
    print ('===============')
    
    
    
def main(parameters):
    import parameters
    thr= parameters.threshold
    path_electrons=parameters.path_elec
    path_pions=parameters.path_pions
    file_per_batch=parameters.file_per_batch
    
    batches_elec=batch_files(path_electrons, file_per_batch)
    batches_pions=batch_files(path_pions, file_per_batch)
      
    elec_dir, pions_dir, version=prepare_jobs(path_electrons, path_pions, batches_elec, batches_pions, thr)
    os.chdir(workdir)
    launch_jobs(elec_dir, pions_dir, batches_elec, batches_pions, version)
   
    
if __name__=='__main__':
    parameters='parameters'
    main(parameters)
    






