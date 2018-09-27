#!/usr/bin/env python
#-*- coding: utf8 -*-



from pprint import pprint
from RI_precision1 import *
from paser import *
result=zeros((1,9))

LogSigDataPath=['./Sca/zoo/','./Sca/pro/','./Sca/bgl/','./Sca/hdfs/','./Sca/hpc/']

dataName=['zoo','pro','bgl','hdfs','hpc']
logNamedata=['rawlogzoo.log','rawlogpro.log','rawlogbgl.log','rawloghdfs.log','rawloghpc.log']

curData=4
for i in range(0,1,1):
	print ('the ', i+1, 'th experiment starts here!')
	path = './data/'
	removeColdata = [[0,1,2,3,4,5],[0,1,2,3,4],[0,1,2,3,4,5],[0,1,2,3,4],[0]]
	
	st = 0.5
	rexdata=[[('(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', 'IPAddandPortID')],[],[('core\.[0-9]*', 'coreNum')], 
	[('blk_(|-)[0-9]+', 'blkID'), ('(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', 'IPAddandPortID')], 
	[('([0-9]+\.){3}[0-9]','IPAdd'),('node-[0-9]+', 'nodeNum')]]
	
	removeCol=removeColdata[curData]
	rex=rexdata[curData]
	freseq=[]
	logName = logNamedata[curData]
	parserPara = Para(path=path, st=st, removeCol=removeCol,logName=logName)
	print (parserPara.path,parserPara.st,parserPara.removeCol)
	myParser = Simplelogparser(parserPara)
	time=myParser.mainProcess()
	parameters=prePara(groundTruthDataPath=LogSigDataPath[curData],logName=logName)
	TP,FP,TN,FN,p,r,f,RI=process(parameters)
	result[i,:]=TP,FP,TN,FN,p,r,f,RI,time
	pprint(result)
	savetxt('10experiment_withRE'+dataName[curData]+'.csv',result,delimiter=',')
