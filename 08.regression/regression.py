from numpy import *

def loadDataSet(fileName):
	numFeat = len(open(fileName).readline().split('\t')) - 1
	dataMat = [];  labelMat = []
	fr = open(fileName)
	for line in fr.readlines():
		lineArr = []
		curLine = line.strip().split('\t')
		for i in range(numFeat):
			lineArr.append(float(curLine[i]))
		dataMat.append(lineArr)
		labelMat.append(float(curLine[-1]))
	return dataMat, labelMat

# 线性回归
def standRegres(xArr, yArr):
	xMat = mat(xArr);  yMat = mat(yArr).T
	xTx = xMat.T * xMat
	if linalg.det(xTx) == 0.0:
		print("This matrix is singular, cannot do inverse")
		return
	ws = xTx.I * (xMat.T * yMat)
	return ws

# 局部加权线性回归
def lwlr(testPoint, xArr, yArr, k=1.0):
	xMat = mat(xArr);  yMat = mat(yArr).T
	m = shape(xMat)[0]
	weights = mat(eye((m)))
	for j in range(m):
		diffMat = testPoint - xMat[j,:]
		weights[j, j] = exp(diffMat * diffMat.T / (-2.0 * k ** 2))
	xTx = xMat.T * (weights * xMat)
	if linalg.det(xTx) == 0.0:
		print("This matrix is singular, cannot do inverse")
		return
	ws = xTx.I * (xMat.T * (weights * yMat))
	return testPoint * ws

def lwlrTest(testArr, xArr, yArr, k=1.0):
	m = shape(testArr)[0]
	yHat = zeros(m)
	for i in range(m):
		yHat[i] = lwlr(testArr[i], xArr, yArr, k)
	return yHat

def rssError(yArr, yHatArr):
	return ((yArr - yHatArr) ** 2).sum()

# 岭回归
def ridgeRegres(xMat, yMat, lam=0.2):
	xTx = xMat.T * xMat
	denom = xTx + eye(shape(xMat)[1]) * lam
	if linalg.det(denom) == 0.0:
		print("This matrix is singular, cannot do inverse")
		return
	ws = denom.I * (xMat.T * yMat)
	return ws

def ridgeTest(xArr, yArr):
	xMat = mat(xArr);  yMat = mat(yArr).T
	yMean = mean(yMat)
	yMat = yMat - yMean
	xMeans = mean(xMat, 0)
	xVar = var(xMat, 0)
	xMat = (xMat - xMeans) / xVar
	numTestPts = 30
	wMat = zeros((numTestPts, shape(xMat)[1]))
	for i in range(numTestPts):
		ws = ridgeRegres(xMat, yMat, exp(i - 10))
		wMat[i, :] = ws.T
	return wMat

def regularize(xMat):#regularize by columns
    inMat = xMat.copy()
    inMeans = mean(inMat,0)   #calc mean then subtract it off
    inVar = var(inMat,0)      #calc variance of Xi then divide by it
    inMat = (inMat - inMeans)/inVar
    return inMat

# 逐步线性回归
def stageWise(xArr, yArr, eps=0.01, numIt=100):
	xMat = mat(xArr);  yMat = mat(yArr).T
	yMean = mean(yMat)
	yMat = yMat - yMean
	xMat = regularize(xMat)
	m,n = shape(xMat)
	returnMat = zeros((numIt, n))
	ws = zeros((n, 1));  wsTest = ws.copy();  wsMax = ws.copy()
	for i in range(numIt):
		print(ws.T)
		lowestError = inf
		for j in range(n):
			for sign in [-1, 1]:
				wsTest = ws.copy()
				wsTest[j] += eps * sign
				yTest = xMat * wsTest
				rssE = rssError(yMat.A, yTest.A)
				if rssE < lowestError:
					lowestError = rssE
					wsMax = wsTest
		ws = wsMax.copy()
		returnMat[i, :] = ws.T
	return returnMat

from time import sleep
import json
import urllib3
def searchForSet(retX, retY, setNum, yr, numPce, origPrc):
	sleep(10)
	myAPIstr = 'get from code.google.com'
	searchURL = 'https://www.googleapis.com/shopping/search/v1/public/products?key=%s&country=US&q=lego+%d&alt=json' % (myAPIstr, setNum)
	http = urllib3.PoolManager()
	pg = http.request('GET', searchURL)
	retDict = json.loads(pg.read())
	for i in range(len(retDict['item'])):
		try:
			currItem = retDict['item'][i]
			if currItem['product']['condition'] == 'new':
				newFlag = 1
			else:	newFlag = 0
			listOfInv = currItem['product']['inventories']
			for item in listOfInv:
				sellingPrice = item['price']
				if sellingPrice > origPrc * 0.5:
					print('%d\t%d\t%d\t%f\t%f' % (yr, numPce, newFlag, origPrc, sellingPrice))
					retX.append([yr, numPce, newFlag, origPrc])
					retY.append(sellingPrice)
		except:
			print('problem with item %d' % i)

def setDataCollect(retX, retY):
	searchForSet(retX, retY, 8288, 2006, 800, 49.99)
	searchForSet(retX, retY, 10030, 2002, 3096, 269.99)
	searchForSet(retX, retY, 10179, 2007, 5195, 499.99)
	searchForSet(retX, retY, 10181, 2007, 3428, 199.99)
	searchForSet(retX, retY, 10189, 2008, 5922, 299.99)
	searchForSet(retX, retY, 10196, 2009, 3263, 249.99)

def crossValidation(xArr,yArr,numVal=10):
    m = len(yArr)                           
    indexList = range(m)
    errorMat = zeros((numVal,30))#create error mat 30columns numVal rows
    for i in range(numVal):
        trainX=[]; trainY=[]
        testX = []; testY = []
        random.shuffle(indexList)
        for j in range(m):#create training set based on first 90% of values in indexList
            if j < m*0.9: 
                trainX.append(xArr[indexList[j]])
                trainY.append(yArr[indexList[j]])
            else:
                testX.append(xArr[indexList[j]])
                testY.append(yArr[indexList[j]])
        wMat = ridgeTest(trainX,trainY)    #get 30 weight vectors from ridge
        for k in range(30):#loop over all of the ridge estimates
            matTestX = mat(testX); matTrainX=mat(trainX)
            meanTrain = mean(matTrainX,0)
            varTrain = var(matTrainX,0)
            matTestX = (matTestX-meanTrain)/varTrain #regularize test with training params
            yEst = matTestX * mat(wMat[k,:]).T + mean(trainY)#test ridge results and store
            errorMat[i,k]=rssError(yEst.T.A,array(testY))
            #print errorMat[i,k]
    meanErrors = mean(errorMat,0)#calc avg performance of the different ridge weight vectors
    minMean = float(min(meanErrors))
    bestWeights = wMat[nonzero(meanErrors==minMean)]
    #can unregularize to get model
    #when we regularized we wrote Xreg = (x-meanX)/var(x)
    #we can now write in terms of x not Xreg:  x*w/var(x) - meanX/var(x) +meanY
    xMat = mat(xArr); yMat=mat(yArr).T
    meanX = mean(xMat,0); varX = var(xMat,0)
    unReg = bestWeights/varX
    print("the best model from Ridge Regression is:\n",unReg)
    print("with constant term: ",-1*sum(multiply(meanX,unReg)) + mean(yMat))




























