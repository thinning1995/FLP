#coding:utf-8
import re
import os
import time
import numpy as np
import gc
	
class Para:
	def __init__(self, rex=None, path=r'C:\Users\YaYa\Desktop\flp', st=0.4, logName='rawloghdfs.log',removable=True,removeCol=None,savePath='./results/',saveFileName='template', saveTempFileName='logTemplates.txt'):
		self.path = path
		self.st = st
		self.logName = logName
		self.removable = removable
		self.removeCol = removeCol
		self.savePath = savePath
		self.saveFileName = saveFileName
		self.saveTempFileName = saveTempFileName
		if rex is None:
			rex = []
		self.rex = rex	

	
	
class Simplelogparser:
	def __init__(self, para):
		self.para = para


	def hasNumbers(self, s):
		return any(char.isdigit() for char in s)


	def getTemplate(self, seq1, seq2):
		assert len(seq1) == len(seq2)
		retVal = []

		iffff = 0
		for word in seq1:
			if word == seq2[iffff]:
				retVal.append(word)
			else:
				retVal.append('*')

			iffff += 1

		return retVal	
		
	def SeqDist(self, seq1, seq2):
		assert len(seq1) == len(seq2)
		simTokens = 0
		numOfPar = 0

		for token1, token2 in zip(seq1, seq2):
			if self.hasNumbers(token2):
				numOfPar += 1
				continue
			if token1 == token2:
				simTokens += 1 

		retVal = (float(simTokens)+float(numOfPar)) / len(seq1)

		return retVal, numOfPar
	

	def outputResult(self, logTemplateall,logIdLall):
		writeTemplate = open(self.para.savePath + self.para.saveTempFileName, 'w')

		idx = 1
		for logTemplate in logTemplateall:
			writeTemplate.write(' '.join(logTemplate) + '\n')
			writeID = open(self.para.savePath + self.para.saveFileName + str(idx) + '.txt', 'w')
			logIdL = logIdLall[idx-1]
			for logID in logIdL:
				writeID.write(str(logID) + '\n')
			writeID.close()
			idx += 1

		writeTemplate.close()
	def deleteAllFiles(self, dirPath):
		fileList = os.listdir(dirPath)
		for fileName in fileList:
	 		os.remove(dirPath+fileName)
	
	
	
	def mainProcess(self):

		t1 = time.time()
		featureVall=None
		logTemplateall=[]
		weekdata=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
		monthdata=['Jan','Feb','Mar','Apr','May','Jun','Jul','Ags','Sep','Oct','Nov','Dec']
			


		with open(self.para.path+self.para.logName) as lines:
			count = 0

			for line in lines:
				logmessageL1=[]
				logID = int(line.split('\t')[0])
				logmessageL = line.strip().split('\t')[1].split()
				logmessageL = [word for ixxx, word in enumerate(logmessageL) if ixxx not in self.para.removeCol]
				
				featureV =[]
				#print (featureVall)
				
				for term in logmessageL:
					if not term.startswith('('):
						if not term.endswith(')'):
							logmessageL1.append(term)
				logmessageL=logmessageL1
				#print (logmessageL)
				messageLen = len(logmessageL)
				featureV.append(messageLen)
				cookedLine1 = ' '.join(logmessageL)				
				for currentRex in self.para.rex:
                    
					if re.match(currentRex[0],cookedLine1,0):
						logmessageL[0]=currentRex[1]
						
				i1=0
				firstterm = logmessageL[i1]
				flagdot='.' in firstterm 
				flagweek=firstterm in weekdata
				flagmonth=firstterm in monthdata
				boolFirstterm = self.hasNumbers(firstterm)
				while boolFirstterm or flagdot or flagweek or flagmonth :
					if (messageLen-i1) <= 1:
						firstterm=logmessageL[i1]
						break
					else:					
						i1 = i1+1
						firstterm = logmessageL[i1]
						boolFirstterm = self.hasNumbers(firstterm)
						flagdot='.' in firstterm
						flagweek=firstterm in weekdata
						flagmonth=firstterm in monthdata
				featureV.append(firstterm)	
				i2 = -1
				lastterm = logmessageL[i2]
				boolLastterm = self.hasNumbers(lastterm)
				#or ':' in lastterm
				flagdot='.' in lastterm 
				flagweek=lastterm in weekdata
				flagmonth=lastterm in monthdata
				#considering the case where the tail term is a variable. If there is with a number, jump to the term before it.
				while boolLastterm or flagdot or flagweek or flagmonth :
					if (i2+messageLen) <= 0:
						lastterm='None'
						break
					else:
						
						i2 = i2-1
						lastterm = logmessageL[i2]
						boolLastterm = self.hasNumbers(lastterm)
						flagdot='.' in lastterm
						flagweek=lastterm in weekdata
						flagmonth=lastterm in monthdata
				featureV.append(lastterm)
	
				

				cookedLine = ' '.join(logmessageL)

				for currentRex in self.para.rex:
					cookedLine = re.sub(currentRex[0], currentRex[1], cookedLine)
				logmessageL = cookedLine.split()


				#Search and construction of feature table
				
				#if the coming log  is  the  first  log  in log  file, then
				if featureVall == None:
					featureVall=[]
					i=0   #a flag for indexing the log  event
					featureV.append(i)
					featureVall.append(featureV)
					logIdLall=[]
					for j in range (0,10000):
						logIdLall.append([])
					logIdL = logIdLall[i]	
					logIdL.append(logID) #add the log id  into this log event 
					logTemplateall.append(logmessageL) # the first valid part of the log as the event template for the first event
					#print (featureVall)
					#print (logIdLall)
					#print (logIdL)
				else:
					flagl=100
					low = 0
					high=len(featureVall) - 1
					#Mathch the featureV[0]
					while(low <= high):
						mid = int((low + high) / 2)
						featureVcur = featureVall[mid]
						midval = featureVcur[0]
						if midval < featureV[0]:
							low = mid+1
							flagl = 1
						elif midval > featureV[0]:
							high = mid -1
							flagl = 0
						# If the length is matched, continue to find the first token.
						# Similarly, if it is not found, we treat it as a new event
						else :
							flagl=100
							flagf=100
							while  mid <=len(featureVall)-1 and mid >=0 and (featureVall[mid])[0] == featureV[0] :
								featureVcur = featureVall[mid]
								if featureV[1] > featureVcur[1]:
									if flagf ==0:#Prevent entry into an infinite loop
										mid = mid +1
										break
									else:
										mid = mid + 1
								
										flagf=1
								elif featureV[1] < featureVcur[1]:
									if flagf == 1:
										break
									else :
										if featureVall[mid-1][0] == featureV[0]:
											mid = mid -1
											flagf = 0
										else:
											flagf = 0
											break
								
								#If the featureV[1] is matched, then match  featureV[2]. It is the same as the featureV[1] , with the flags for flag.
								else:
									flagf =100
									flags=100
									#midfirstval=(featureVall[mid])[1]
									while mid <=len(featureVall)-1 and mid >=0 and (featureVall[mid])[1] == featureV[1] and (featureVall[mid])[0] == featureV[0] :
										featureVcur = featureVall[mid]
										if featureV[2] > featureVcur[2]:
											if flags ==0:#防止进入死循环
												mid = mid+1
												break
											else:								
												mid = mid + 1
												flags=1	
										elif featureV[2] < featureVcur[2]:
											if featureVall[mid - 1][1] == featureV[1] and featureVall[mid - 1][0] == featureV[0] :
												mid = mid - 1
												flags = 0
											else:
												flags = 0
												break
										#Calculate maximum similarity,if it is bigger than the similarity threshold st, add this log message into the log group where the max similarity is.
										else:
											flags=100
											maxSim = -1
											maxNumOfPara = -1
											#flag3 =100
											#midlastval=(featureVall[mid])[2]
											mid2 = mid
											#midlastval2=(featureVall[mid2])[2]
											while mid <=len(featureVall)-1 and mid >=0  and(featureVall[mid])[2] == featureV[2]and (featureVall[mid])[1] == featureV[1] and(featureVall[mid])[0] == featureV[0]   :
												featureVcur = featureVall[mid]
												flag = featureVcur[3]
												curSim, curNumOfPara = self.SeqDist(logTemplateall[flag], logmessageL)
												if curSim>maxSim or (curSim==maxSim and curNumOfPara>maxNumOfPara):
													maxSim = curSim
													maxNumOfPara = curNumOfPara
													s =  flag
													#flag3=0
												mid = mid + 1
												#midlastval=(featureVall[mid])[2]
												
						
											while mid2 <=len(featureVall)-1 and mid2 >=0 and (featureVall[mid2])[2] == featureV[2] and (featureVall[mid2])[1] == featureV[1] and (featureVall[mid2])[0] == featureV[0]:
												featureVcur = featureVall[mid2]
												flag = featureVcur[3]
												curSim, curNumOfPara = self.SeqDist(logTemplateall[flag], logmessageL)
												if curSim>maxSim or (curSim==maxSim and curNumOfPara>maxNumOfPara):
													maxSim = curSim
													maxNumOfPara = curNumOfPara
													s =  flag
													#flag3=1
												mid2 = mid2 - 1
												#midlastval=(featureVall[mid2])[2]
												
				
											if maxSim >= self.para.st:
												logIdL = logIdLall[s]	
												logIdL.append(logID)
												newTemplate = self.getTemplate(logmessageL, logTemplateall[s])
												logTemplateall[s]=newTemplate
												break
												
											#If thesimilarity on the match is less than the threshold, it is considered a new event
											else:
												i = i + 1
												featureV.append(i)
												featureVall.insert(mid,featureV)
												logIdL = logIdLall[i]	
												logIdL.append(logID)
												logTemplateall.insert(i,logmessageL)
												break
												
												
			
									if flags != 100:
										i = i + 1
										featureV.append(i)
										featureVall.insert(mid,featureV)
										logIdL = logIdLall[i]	
										logIdL.append(logID)
										logTemplateall.insert(i,logmessageL)
									break
							
							if flagf != 100:
								i = i + 1
								featureV.append(i)
								featureVall.insert(mid,featureV)
								logIdL = logIdLall[i]	
								logIdL.append(logID)
								logTemplateall.insert(i,logmessageL)
							break
							
									
				
					if flagl == 0:
						i=i+1
						featureV.append(i)
						featureVall.insert(mid,featureV)
						logIdL = logIdLall[i]	
						logIdL.append(logID)
						logTemplateall.insert(i,logmessageL)
						
					elif flagl == 1:
						i=i+1
						featureV.append(i)
						mid =  mid + 1
						featureVall.insert(mid,featureV)
						logIdL = logIdLall[i]	
						logIdL.append(logID)
						logTemplateall.insert(i,logmessageL)
					count += 1
					if count%5000 == 0:
						print (count)
		#print (logIdLall)
		#print (featureVall)
		#for llll in logTemplateall:
		
			
        #print (llll)
		t2 = time.time()			
		if not os.path.exists(self.para.savePath):
			os.makedirs(self.para.savePath)
		else:
			self.deleteAllFiles(self.para.savePath)

		self.outputResult(logTemplateall,logIdLall)
		

		print('this process takes',t2-t1)
		print('*********************************************')
		gc.collect()
		
  
	print ('******')
		
# HDFS parameters for example

path = './'
removeCol = [0,1,2,3,4,5] #[] for HDFS
st = 0.5
rex = [('core\.[0-9]*', 'coreNum')]
logName = "bgltest1000000.txt"
'''
parserPara = Para(path=path, st=st, removeCol=removeCol, rex=rex,logName=logName)
myParser = Simplelogparser(parserPara)
myParser.mainProcess()

'''

'''
path = './'
removeCol = [] #[] for HDFS
st = 0.3
rex = []
logName = "testth.log"

parserPara = Para(path=path, st=st, removeCol=removeCol, rex=rex,logName=logName)
myParser = Simplelogparser(parserPara)
myParser.mainProcess()
'''