#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import uproot
from datetime import date
import optparse


workdir=os.getcwd()
algo_name=['T23', 'S', 'S0', 'S10', 'S20', 'T', 'T0', 'T10', 'T20']


def deltar(df):
    df['deta']=df['cl3d_eta']-df['genpart_exeta']
    df['dphi']=np.abs(df['cl3d_phi']-df['genpart_exphi'])
    sel=df['dphi']>np.pi
    df['dphi']-=sel*(2*np.pi)
    return(np.sqrt(df['dphi']*df['dphi']+df['deta']*df['deta']))
    
def matching(event):
    return event.cl3d_pt==event.cl3d_pt.max()

def openroot(path, files):
    os.chdir(path)
    algo={}
    branches_gen=['event','genpart_pid','genpart_exphi', 'genpart_exeta','genpart_gen','genpart_reachedEE', 'genpart_pt', 'genpart_energy','genpart_fbrem']
    branches_cl3d=['event','cl3d_pt','cl3d_eta','cl3d_phi','cl3d_showerlength','cl3d_coreshowerlength','cl3d_firstlayer','cl3d_maxlayer','cl3d_seetot','cl3d_spptot','cl3d_szz', 'cl3d_srrtot', 'cl3d_srrmean']
    branches_T23=branches_cl3d+['cl3d_bdteg','cl3d_quality']
    
    for i,filename in enumerate(files,1):
        if i==1:
            gen=uproot.open(filename)['Floatingpoint8ThresholdRef2dRef3dGenclustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_gen,flatten=True)
            algo[0]=uproot.open(filename)['Floatingpoint8ThresholdRef2dRef3dGenclustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_T23,flatten=True)
            algo[1]=uproot.open(filename)['Floatingpoint8SupertriggercellDummyHistomaxClustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)
            algo[2]=uproot.open(filename)['Floatingpoint8SupertriggercellDummyHistomaxvardrth0Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)
            algo[3]=uproot.open(filename)['Floatingpoint8SupertriggercellDummyHistomaxvardrth10Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)
            algo[4]=uproot.open(filename)['Floatingpoint8SupertriggercellDummyHistomaxvardrth20Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)
            algo[5]=uproot.open(filename)['Floatingpoint8ThresholdDummyHistomaxClustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)
            algo[6]=uproot.open(filename)['Floatingpoint8ThresholdDummyHistomaxvardrth0Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)
            algo[7]=uproot.open(filename)['Floatingpoint8ThresholdDummyHistomaxvardrth10Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)
            algo[8]=uproot.open(filename)['Floatingpoint8ThresholdDummyHistomaxvardrth20Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)
        
        else:
            gen=pd.concat([gen,uproot.open(filename)['Floatingpoint8ThresholdRef2dRef3dGenclustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_gen,flatten=True)])
            algo[0]=pd.concat([algo[0],uproot.open(filename)['Floatingpoint8ThresholdRef2dRef3dGenclustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_T23,flatten=True)])
            algo[1]=pd.concat([algo[1],uproot.open(filename)['Floatingpoint8SupertriggercellDummyHistomaxClustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)])
            algo[2]=pd.concat([algo[2],uproot.open(filename)['Floatingpoint8SupertriggercellDummyHistomaxvardrth0Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)])
            algo[3]=pd.concat([algo[3],uproot.open(filename)['Floatingpoint8SupertriggercellDummyHistomaxvardrth10Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)])
            algo[4]=pd.concat([algo[4],uproot.open(filename)['Floatingpoint8SupertriggercellDummyHistomaxvardrth20Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)])
            algo[5]=pd.concat([algo[5],uproot.open(filename)['Floatingpoint8ThresholdDummyHistomaxClustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)])
            algo[6]=pd.concat([algo[6],uproot.open(filename)['Floatingpoint8ThresholdDummyHistomaxvardrth0Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)])
            algo[7]=pd.concat([algo[7],uproot.open(filename)['Floatingpoint8ThresholdDummyHistomaxvardrth10Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)])
            algo[8]=pd.concat([algo[8],uproot.open(filename)['Floatingpoint8ThresholdDummyHistomaxvardrth20Clustersntuple;1/HGCalTriggerNtuple'].pandas.df(branches_cl3d,flatten=True)])
        
    return(gen, algo)

def preprocessing(path, files, savedir,  thr):
    
    gen,algo=openroot(path, files)
    n_rec={}
    algo_clean={}
    
    
    
    #clean gen from particles that are not the originals or didn't reach endcap
    sel=gen['genpart_reachedEE']==2 
    gen_clean=gen[sel]
    sel=gen_clean['genpart_gen']!=-1
    gen_clean=gen_clean[sel]

    #split df_gen_clean in two by eta sign
    sel1=gen_clean['genpart_exeta']<=0
    sel2=gen_clean['genpart_exeta']>0
    gen_neg=gen_clean[sel1]
    gen_pos=gen_clean[sel2]

    gen_pos.set_index('event', inplace=True)
    gen_neg.set_index('event', inplace=True)
    
    for i in algo:
        #split clusters in two by eta sign
        sel1=algo[i]['cl3d_eta']<=0
        sel2=algo[i]['cl3d_eta']>0
        algo_neg=algo[i][sel1]
        algo_pos=algo[i][sel2]
        #set the indices
        algo_pos.set_index('event', inplace=True)
        algo_neg.set_index('event', inplace=True)
        #merging
        algo_pos_merged=gen_pos.join(algo_pos, how='left', rsuffix='_algo')
        algo_neg_merged=gen_neg.join(algo_neg, how='left', rsuffix='_algo')
        #calculate deltar
        algo_pos_merged['deltar']=deltar(algo_pos_merged)
        algo_neg_merged['deltar']=deltar(algo_neg_merged)
        
        #keep the unreconstructed values (NaN)
        sel=pd.isna(algo_pos_merged['deltar']) 
        unmatched_pos=algo_pos_merged[sel]
        sel=pd.isna(algo_neg_merged['deltar'])  
        unmatched_neg=algo_neg_merged[sel]
        unmatched_pos['matches']=False
        unmatched_neg['matches']=False
        
        #select deltar under thr
        sel=algo_pos_merged['deltar']<=thr
        algo_pos_merged=algo_pos_merged[sel]
        sel=algo_neg_merged['deltar']<=thr
        algo_neg_merged=algo_neg_merged[sel]
        
        #matching
        group=algo_pos_merged.groupby('event')
        n_rec_pos=group['cl3d_pt'].size()
        algo_pos_merged['best_match']=group.apply(matching).array
        group=algo_neg_merged.groupby('event')
        n_rec_neg=group['cl3d_pt'].size()
        algo_neg_merged['best_match']=group.apply(matching).array
        
        #keep only matched clusters 
        sel=algo_pos_merged['best_match']==True
        algo_pos_merged=algo_pos_merged[sel]
    
        sel=algo_neg_merged['best_match']==True
        algo_neg_merged=algo_neg_merged[sel]
    
        #remerge with NaN values
        algo_pos_merged=pd.concat([algo_pos_merged, unmatched_pos], sort=False).sort_values('event') 
        algo_neg_merged=pd.concat([algo_neg_merged, unmatched_neg], sort=False).sort_values('event')
        
        n_rec[i]=n_rec_pos.append(n_rec_neg)
        algo_clean[i]=pd.concat([algo_neg_merged,algo_pos_merged], sort=False).sort_values('event')

        algo_clean[i]['matches']=algo_clean[i]['matches'].replace(np.nan, True)
        algo_clean[i].drop(columns=['best_match'], inplace=True)

        #save files to savedir
    os.chdir(savedir)   
    gen_clean.to_csv('gen_clean.csv')
    for i in algo:
        algo_clean[i].to_csv('{}.csv'.format(algo_name[i]))
        
        
if __name__=='__main__':
    parser = optparse.OptionParser()
    parser.add_option("-f","--file",type="string", dest="param_file", help="select the path to the parameters file")
   
    (opt, args) = parser.parse_args()
    os.chdir(opt.param_file)

    import param
    path=param.path
    files=param.files
    thr=param.thr
    savedir=param.savedir
    
    preprocessing(path, files, savedir, thr)

