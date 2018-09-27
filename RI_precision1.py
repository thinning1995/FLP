#!/usr/bin/env python
#-*- coding: utf-8 -*-
'''
import sys
reload(sys)
sys.setdefaultencoding('utf8')
'''
from numpy import *
import re
from glob import *
import math

#************************************************************************
#参数计算方法参考： http://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-clustering-1.html
#************************************************************************************
class prePara:
	def __init__(self,groundTruthDataPath='',logName='',groundTruthTempName='templates.txt',
	groundTruthGroupNamePat='template',geneDataPath='./results/',geneTempName='logTemplates.txt',geneGroupNamePat='template',beta=1):
		self.groundTruthDataPath=groundTruthDataPath
		self.groundTruthDataPath=groundTruthDataPath
		self.logName=logName
		self.groundTruthTempName=groundTruthTempName
		self.groundTruthGroupNamePat=groundTruthGroupNamePat
		self.geneDataPath=geneDataPath
		self.geneTempName=geneTempName
		self.geneGroupNamePat=geneGroupNamePat
		self.beta=beta
		#print Para.path+Para.logname
		
def process(prePara):
	logNum=0
	with open(prePara.groundTruthDataPath+prePara.logName) as lines:
		for line in lines:
			logNum+=1
		#print logNum
	print(prePara.groundTruthDataPath+prePara.logName)
	
	gtLogLabel=-1*ones((logNum,1))   #全1矩阵
	gtfilepath=prePara.groundTruthDataPath+prePara.groundTruthGroupNamePat
	gtfileNum=len(glob(gtfilepath+'[0-9]*.txt'))
	print u'真实数据一共有',gtfileNum, u'个日志事件'
	gtLogNumOfEachGroup=zeros((gtfileNum,1))
	getGtLabel(gtfilepath,gtLogLabel,gtfileNum,gtLogNumOfEachGroup)

	#处理由算法生成的组
	
	geneFilePath=prePara.geneDataPath+prePara.geneGroupNamePat
	fileNum=len(glob(geneFilePath+'[0-9]*.txt'))
	geneClusterLabel=list()  
	#geneClusterLabel存了很多字典，键为事件ID的，值为日志在生成事件与真实数据均在一个事件里的数量。
	geneLogNumOfEachGroup=zeros((fileNum,1))
	
	print("*******************")
	print '生成算法一共有',fileNum, '个日志事件'
	#生成模板中的日志，计算模板日志文件数，不同标签的日志
	for i in range(fileNum):
		filename=geneFilePath+str(i+1)+'.txt'
		labelDict=dict()
		count=0
		with open(filename) as lines:
			for line in lines:
				count+=1
   				#int(line.split('\t')[0])
				ID =int(round(float(line.split(' ')[0])))
				#print ID
				label=int(gtLogLabel[ID-1])
				if label not in labelDict:
					labelDict[label]=1
				else:
					labelDict[label]+=1
			geneLogNumOfEachGroup[i]=count
		geneClusterLabel.append(labelDict)
		#print geneClusterLabel

	TP_FP=0
	for i in range(fileNum):
		if geneLogNumOfEachGroup[i]>1:
			TP_FP+=nCr(geneLogNumOfEachGroup[i],2)

	TP_FN=0
	for i in range(gtfileNum):
		if gtLogNumOfEachGroup[i]>1:
			TP_FN+=nCr(gtLogNumOfEachGroup[i],2)
   

	TP=0
	for i in range(len(geneClusterLabel)):
		labelD=geneClusterLabel[i]
		for key,value in labelD.items():
			if value>1:
				TP+=nCr(value,2)

	TP_FP_TN_FN=nCr(logNum,2)
	FN=TP_FN-TP
	FP=TP_FP-TP
	TN=TP_FP_TN_FN-TP_FP-FN
	print "*****"+str(len(geneClusterLabel))+"*********"
	print 'TP,FP,TN,FN 分别为:',TP,FP,TN,FN
	precision=float(TP)/(TP_FP)
	recall=float(TP)/(TP_FN)
	b=prePara.beta
	F_measure=float(b*b+1)*precision*recall/(b*b*precision+recall)
	RI=float(TP+TN)/TP_FP_TN_FN
	print 'precision 为 %.4f'%(precision)
	print 'recall 为 %.4f'%(recall)
	print 'F measure 为 %.4f'%(F_measure)
	print 'RI 为 %.4f'%(RI)
	return TP,FP,TN,FN,precision,recall,F_measure,RI

#打开真实数据使用模板序号给日志建立标签
def getGtLabel(filePath,gtLogLabel,fileNum,gtLogNumOfEachGroup):
	for i in range(fileNum):
		count=0
		filename=filePath+str(i+1)+'.txt'
		#print filename
		with open(filename) as lines:
			label=i+1
			for line in lines:
				count+=1
				ID =  int(line.split('\t')[0])
    
				#ID =int(round(float(line.split(' ')[0])))
				#print ID
				gtLogLabel[ID-1]=label
		gtLogNumOfEachGroup[i]=count
		#print gtLogNumOfEachGroup[20]

#J计算 C(n,r)
def nCr(n,r):
	result = 1
	denominator = r
	numerator = n
	for i in range(r):
		result *= float(numerator)/denominator
		denominator -= 1
		numerator -= 1
	return result
