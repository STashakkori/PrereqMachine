#!/usr/bin/python

"""
    dict2mat.py - script that loads a dictionary from a .json file filled with grade data for students. The script then
                  converts that data to a numpy matrix of grades and two lists filled with course data and student
                  dummie id data for reference. The matrix and two lists are saved in memory in the preprocessing
                  directory.
"""

__author__ = 'sina'
__project__ = 'STProject'

import os
import colorama
from termcolor import colored
import cPickle
import numpy
import json
import math
import time
import sys
from collections import OrderedDict
from concurrent import futures

"""
    main - main method of the dict2mat program.
        :param argv: command line argument
        :type argv: string
"""
def main(argv,argv2):
    colorama.init(autoreset=True)
    print(colored("dict2mat","blue"))
    if argv and argv.endswith(".json"):
        studentmap = loadjson(argv)
        activitymap = loadjson(argv2)
        g,d,a = convertdictionariestomatrices(studentmap,activitymap)
        print g.shape
        print len(d)
        print len(a)
        print "============"
        g,d,a = pruneemptycolumns(g,d,a)
        print g.shape
        print len(d)
        print len(a)
        exit(1)
        storenewdatastructuresinmemory(g,d,a,argv)

    else:
        print(colored("dict2mat ==> ERROR --> Bad filename input ~~> .json required","red"))
        exit(1)

"""
    loadjson - method that loads a json object from memory and returns it.
"""
def loadjson(filename):
        f = open(filename,"rb")
        j = json.loads(open(filename).read())
        f.close()
        return j

"""
    convertdictionarytomatrix - method that loops through a dictionary that is indexable by student and generates an
                                equivalent 3 datastructures. Gradematrix is a numpy matrix of all the grades. Dummieidgrid
                                is a 2d list that holds dummie ids. activitygrid is a 2d list that holds course names. Both
                                Dummieidgrid and activitygrid have the same dimensions as gradematrix and have an element
                                to element correspondence.
"""
def convertdictionariestomatrices(studentdictionary,activitydictionary):
    twelvepointgrademap = {"A":12.0,"A-":11.0,"B+":10.0,"B":9.0,"B-":8.0,"C+":7.0,"C":6.0,"C-":5.0,"D+":4.0,"D":3.0,"D-":2.0,"F":0.0}
    rows = len(studentdictionary.keys())
    columns = len(activitydictionary.keys())
    dummieidlabels = studentdictionary.keys()
    dummieidlabels.sort(key=int)
    activitylabels = activitydictionary.keys()
    activitylabels.sort()
    gradematrix = numpy.empty([rows,columns])
    gradematrix[:] = numpy.NAN
    rowindex = 0

    for dummieid in studentdictionary:
        for activity in studentdictionary[dummieid]:
            columnindex = activitylabels.index(activity)
            # Grab the lowest grade out of dictionary entry.
            mingrade = float('inf')
            for value in studentdictionary[dummieid][activity]:
                if activity == "SATV_score" or activity == "SATM_score" or activity == "ACTEng_score" or activity == "ACTMat_score" or activity == "MathPlacement_PLM1_Score" or activity == "MathPlacement_PLM2_Score" or activity == "MathPlacement_PLM3_Score" or activity == "HSGPA":
                    mingrade = value

                elif value in twelvepointgrademap and twelvepointgrademap[value] < mingrade:
                    mingrade = twelvepointgrademap[value]

            if mingrade == float('inf'):
                grade = numpy.NAN
            else:
                grade = mingrade
            gradematrix[rowindex][columnindex] = grade
        rowindex += 1

        numpy.set_printoptions(threshold='nan')
    return gradematrix, dummieidlabels, activitylabels

"""
    createmapfromlabel - method that converts a enumerated map from a list.
"""
def createmapsfromlabels(list):
    map = {}
    for i in range(0,len(list)):
        map[list[i]] = i

    return map

"""
    pruneemptycolumns - method that removes columns that are populated entirely with NAN's
"""
def pruneemptycolumns(gradematrix, dummieidlabels, activitylabels):
    validgradereference = numpy.zeros([gradematrix.shape[1],1])
    print "TESTING *****"
    print len(validgradereference)
    print len(activitylabels)
    for i in range(0,gradematrix.shape[0]):
        for j in range(0,gradematrix.shape[1]):
            if not math.isnan(gradematrix[i][j]):
                validgradereference[j] = validgradereference[j] + 1

    zerolist,nonzerobool = numpy.where(validgradereference == 0)
    gradematrix = numpy.delete(gradematrix,zerolist,1)

    activitylabels = numpy.array(activitylabels)
    numpy.delete(activitylabels,zerolist,1)

    """
    for index in zerolist:
        del activitylabels[index]
        zerolist = zerolist - 1
    """
    return gradematrix, dummieidlabels, activitylabels

"""
    transpose - method that transposes a 2d list datastructure.
"""
def transpose(grid):
    return zip(*grid)

"""
    removeblankrows - method that removes empty rows from a 2d list datastructure.
"""
def removeblankrows(grid):
    return [list(row) for row in grid if any(row)]

"""
    storematrixandlistsinmemory - method that stores gradematrix, dummieidgrid, and activitygrid into memory.
"""
def storenewdatastructuresinmemory(gradematrix, dummieidlabels, activitylabels, filename):
        gradematrixname = os.path.splitext(filename)[0].replace("_studentdict","") + "_grademat.npy"
        dummieidlabelsname = os.path.splitext(filename)[0].replace("_studentdict","") + "_dummieidlabels.cPickle"
        activitylabelsname = os.path.splitext(filename)[0].replace("_studentdict","") + "_activitylabels.cPickle"
        dummieidlabelsmapname = os.path.splitext(filename)[0].replace("_studentdict","") + "_activityindexmap.json"
        activitylabelsmapname = os.path.splitext(filename)[0].replace("_studentdict","") + "_studentindexmap.json"

        numpy.save(gradematrixname,gradematrix)
        print(colored("dict2mat ==> SUCCESS --> " + gradematrixname + " file written to the preprocessing directory..","cyan"))

        file = open(dummieidlabelsname, "wb")
        cPickle.dump(dummieidlabels,file,protocol=2)
        file.close()
        print(colored("dict2mat ==> SUCCESS --> " + dummieidlabelsname + " file written to the preprocessing directory..","cyan"))

        file = open(activitylabelsname, "wb")
        cPickle.dump(activitylabels,file,protocol=2)
        file.close()
        print(colored("dict2mat ==> SUCCESS --> " + activitylabelsname + " file written to the preprocessing directory..","cyan"))
        """
        file = open("preprocessing/" + filename, "wb")
        json.dump(dummieidlabelsmapname,file)
        file.close()
        print(colored("csv2dict ==> SUCCESS --> " + dummieidlabelsmapname + " file written to the preprocessing directory.","cyan"))

        file = open("preprocessing/" + activitylabelsmapname, "wb")
        json.dump(dummieidlabelsmapname,file)
        file.close()
        print(colored("csv2dict ==> SUCCESS --> " + activitylabelsmapname + " file written to the preprocessing directory.","cyan"))
        """

if __name__ == "__main__":
    usage = colored("dict2mat ==> ERROR --> Improper command line arguments ~~> Usage : python dict2mat.py <dictionary.json> ","red")
    if len(sys.argv) > 3:
        print usage
        exit(-1)

    try:
        t0 = time.time()
        input_filename = sys.argv[1]
        input_filename2 = sys.argv[2]
        main(input_filename,input_filename2) # main("preprocessing/CSDataFile_ForParry_2014Nov26_studentdict.json","preprocessing/CSDataFile_ForParry_2014Nov26_activitydict.json)
        t1 = time.time()
        totaltime = t1 - t0
        print(colored("dict2mat ~=> " + str(totaltime) + " seconds.","yellow"))
    except IOError as e:
        print usage
        print e.strerror
        exit(-1)