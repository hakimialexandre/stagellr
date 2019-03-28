#!/usr/bin/env python

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import uproot
from datetime import date
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
        with open(name+'_{}.sub'.format(i), 'w') as script:
            print ('#! /bin/bash',file=script)
            print ('uname -a',file=script)
            print >>script, 'cd', workdir
            print >>script, 'source init_env_polui.sh'
            print ('cd', workdir+'/'+version,file=script)
            print (workdir+'/preprocessing.py -p {0} -b {1} -t {2} -s {3}'.format(path_electrons, batches_elec[i], thr, elec_dir+'/elec_{}'.format(i)),file=script)
            #print >>script, 'touch', name+'_{}.done'.format(i)
            
            
    os.chdir(pions_dir)
    for i in batches_pions:
        os.makedirs('pions_{}'.format(i))
        with open(name+'_{}.sub'.format(i), 'w') as script:
            print ('#! /bin/bash', file=script)
            print ('uname -a',file=script)
            #print >>script, 'cd', workdir
            #print >>script, 'source init_env_polui.sh'
            print ('cd', workdir+'/'+version,file=script)
            print ( workdir+'/preprocessing.py -p {0} -b {1} -t {2} -s {3}'.format(path_pions, batches_pions, thr, pions_dir+'/pion_{}'.format(i)),file=script)
            #print >>script, 'touch', name+'_{}.done'.format(i)
   
    return elec_dir, pions_dir
    

def launch_jobs(elec_dir, pions_dir, batches_elec, batches_pions, name='batch', queue='long', proxy='~/.t3/proxy.cert'):
    print ('Sending {0}+{1} jobs on {2}'.format(len(batches_elec), len(batches_pions), queue+'@llrcms01'))
    print ('===============')
    for i,event in enumerate(events):
        qsub_args = []
        #qsub_args.append('-{}'.format(queue))
        qsub_args.append(elec_dir+'/'+name+'_{}.sub'.format(i))
        #qsub_command = ['/opt/exp_soft/cms/t3/t3submit'] + qsub_args
        print (' '.join(qsub_args))
        subprocess.run(qsub_args)
    print ('===============')
    
    
    
def main(parameters):
    import parameters
    thr= parameters.threshold
    path_electrons=parameters.path_elec
    path_pions=parameters.path_pions
    file_per_batch=parameters.file_per_batch
    
    batches_elec=batch_files(path_electrons, file_per_batch)
    batches_pions=batch_files(path_pions, file_per_batch)
      
    elec_dir, pions_dir=prepare_jobs(path_electrons, path_pions, batches_elec, batches_pions, thr)
    #launch_jobs(elec_dir, pions_dir, batches_elec, batches_pions)
   
    
if __name__=='__main__':
    parameters='parameters'
    main(parameters)
    