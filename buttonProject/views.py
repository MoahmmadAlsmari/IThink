from __future__ import division
import csv
import os
import shutil
from random import random, seed
import numpy as np
import pandas as pd
import seaborn as sns
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf
from statsmodels.graphics.gofplots import ProbPlot

base_dir = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)).replace("\\", "/"))

imagePathMont = base_dir + '/static/buttonProject/monte.png'
imagePathLin = base_dir + '/static/buttonProject/linear.png'


def index(request):
    return render(request, 'index.html')


def index(request):
    mean = ''
    median = ''
    std = ''

    base_dir = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)).replace("\\", "/"))
    ###########################
    #for deleting the media files before start#
    filemedia = base_dir + "/media"
    folder = filemedia
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception  as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    ###########################
    #reading the file
    if request.method == 'POST':
        uploaded_file = request.FILES['myfile']
        fs = FileSystemStorage()
        up_fileName = os.path.splitext(uploaded_file.name)[0]
        filesaved = fs.save(uploaded_file.name, uploaded_file)
        filename = fs.url(filesaved)
        filepath = base_dir + filename
        print(filepath)
        if os.path.exists(imagePathMont) or os.path.exists(imagePathLin):
            os.remove(imagePathMont)
            os.remove(imagePathLin)
        plt.clf()
        # This arrays are for Grading
        gpa = []
        A = []
        B = []
        C = []
        D = []
        F = []
        zero = []
        # Reading The values from the excel sheet as String
        with open(filepath) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                gpa.append(row[0])
        # Sorting the datacl
        gpa.sort()
        # converting String to floating numbers
        gpa = list(map(float, gpa))
        # This for instring the values to each grade array
        i = 0
        while i < len(gpa):
            if gpa[i] >= 4.5:
                A.append(gpa[i])
            elif gpa[i] >= 3.75:
                B.append(gpa[i])
            elif gpa[i] >= 2.75:
                C.append(gpa[i])
            elif gpa[i] >= 2:
                D.append(gpa[i])
            elif gpa[i] > 0:
                F.append(gpa[i])
            elif gpa[i] == 0:
                zero.append(gpa[i])
            i += 1

        # This is for getting the frequency of each Grade

        total = len(gpa)
        A_Count = len(A)
        B_Count = len(B)
        C_Count = len(C)
        D_Count = len(D)
        F_Count = len(F)
        Zero_count = len(zero)
        countArr = [A_Count, B_Count, C_Count, D_Count, F_Count, Zero_count]

        ############
        #Processing#
        ############

        # This for counting the probability of occurrence
        ProbArr = []

        j = 0
        while j < len(countArr):
            ProbArr.append(countArr[j] / total)
            j += 1
        # This is for calculating cumulative probability
        # CumProbArr= cumulative probability array

        CumProbArr = []
        CumProbArr = np.cumsum(ProbArr)

        # Genrating Random Digit Assignment
        # RandAssignI =Random Digit Assignment I
        # RandAssignJ =Random Digit Assignment j
        ix = 0.00001
        RandAssignI = []
        RandAssignJ = []

        t = 0
        while t < len(CumProbArr) - 1:
            RandAssignI.append(CumProbArr[t] + ix)
            t += 1
        RandAssignI.insert(0, ix)

        t = 0
        while t < len(CumProbArr):
            RandAssignJ.append(CumProbArr[t])
            t += 1

        #############
        #MONTE-CARLO#
        #############

        TestStu = []
        # test values
        for _ in range(400):
            TestStu.append(random())

        TestStu.sort()
        ATest = []
        BTest = []
        CTest = []
        DTest = []
        FTest = []
        ZeroTest = []
        i = 0
        while i < len(TestStu):
            if RandAssignI[0] <= TestStu[i] and RandAssignJ[0] >= TestStu[i]:
                ATest.append('A')
            elif RandAssignI[1] <= TestStu[i] and RandAssignJ[1] >= TestStu[i]:
                BTest.append('B')
            elif RandAssignI[2] <= TestStu[i] and RandAssignJ[2] >= TestStu[i]:
                CTest.append('C')
            elif RandAssignI[3] <= TestStu[i] and RandAssignJ[3] >= TestStu[i]:
                DTest.append('D')
            elif RandAssignI[4] <= TestStu[i] and RandAssignJ[4] >= TestStu[i]:
                FTest.append('F')
            elif RandAssignI[5] <= TestStu[i] and RandAssignJ[5] >= TestStu[i]:
                ZeroTest.append('0')
            i += 1

        ATestLen = len(ATest)
        BTestlen = len(BTest)
        CTestlen = len(CTest)
        DTestlen = len(DTest)
        FTestlen = len(FTest)
        ZeroTestlen = len(ZeroTest)

        CountArrTest = [
            ATestLen, BTestlen, CTestlen, DTestlen, FTestlen, ZeroTestlen
        ]

        # ploting the real values
        plt.plot(countArr)
        #plt.xticks(np.arange(6), ('A', 'B', 'C', 'D', 'F', 'Zero'))

        # ploting the test values

        plt.plot(CountArrTest)
        plt.xticks(np.arange(6), ('A', 'B', 'C', 'D', 'F', 'Zero'))
        plt.title(up_fileName)
        X = np.array(gpa)
        y = np.array(gpa)

        #########################
        #change base on Computer#
        #########################
        plt.savefig(imagePathMont)
        plt.clf()
        #########################
        weight = [6, 5, 4, 3, 2, 1]
        mydata = pd.DataFrame({'weight': weight, 'CountArrTest': CountArrTest})
        model_f = 'CountArrTest~weight'
        model = smf.ols(formula=model_f, data=mydata)
        model_fit = model.fit()

        fitted_values = model_fit.fittedvalues
        plt.scatter(weight, CountArrTest)
        plt.plot(weight, fitted_values, c='r')
        plt.xlabel("weight")
        plt.ylabel("CountArrTest")
        plt.savefig(imagePathLin)
        print(model_fit.summary())
        #########################

        mean = np.mean(gpa)
        median = np.median(gpa)
        std = np.std(gpa)

    return render(request, 'index.html', {
        'mean': mean,
        'median': median,
        'std': std
    })
