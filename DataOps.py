__author__ = 'sina'

import cPickle
import pickle
import json
import re

class loadergetter:

    studentdict = {}
    activitydict = {}
    gradelist = []
    graderegex = re.compile('^((\*?[A-DFSIWU][+-]?) ?)?(NG|XG|NR|WB|WF|AU|XP|XC|CV|CR|WC|IE)*$')
    traditionalgraderegex = re.compile('^\*?[A-DFSIWU][+-]?$')
    gradenumericsmap = {"A":4.0,"A-":3.7,"B+":3.3,"B":3.0,"B-":2.7,"C+":2.3, "C":2.0,"C-":1.7,"D+":1.3,"D":1.0,"D-":0.7,"F":0.0}

    def __init__(self):
        self.studentdict = self.load_json("preprocessing/studentdictionary.json")
        self.activitydict =self.load_json("preprocessing/activitydictionary.json")
        print "DataOps -> datastructures loaded"

    def get_results(self,string):
        dummieidregex = re.compile('^[0-9]{7}')

        if dummieidregex.search(string):
            if string in self.studentdict:
                return self.studentdict[string]

            else:
                print ":: NOT A VALID DUMMIEID ::"

        else:
            if string in self.activitydict:
                return self.activitydict[string]

            else:
                print ":: NOT A VALID ACTIVITY ::"

    def load_cpickle(self,filename):
        f = open(filename,"rb")
        cp = cPickle.load(f)
        f.close()
        return cp

    def load_pickle(self,filename):
        f = open(filename,"rb")
        p = pickle.load(f)
        f.close()
        return p

    def load_json(self,filename):
        f = open(filename,"rb")
        j = json.loads(open(filename).read())
        f.close()
        return j

    def grademerger(self,studentmap):
        for k, v in studentmap.iteritems():
            if isinstance(v,dict):
                self.grademerger(v)
            else:
                for value in v:
                    if self.graderegex.search(value):
                        self.gradelist.append(value)

    def countsmapper(self,list):
        from collections import OrderedDict
        countmap = OrderedDict([("A",0),("A-",0),("B+",0),("B",0),("B-",0),("C+",0),("C",0),("C-",0),("D+",0),("D",0),("D-",0),("F",0),("I",0),("S",0),("U",0),("W",0),("*F",0),("Other",0)])
        for item in list:
            if self.traditionalgraderegex.search(item):
                countmap[item] = countmap.setdefault(item,0) + 1
            else:
                countmap["Other"] = countmap.setdefault("Other",0) + 1

        return countmap

    def gradehistogrammer(self,list):
        import matplotlib.pyplot as plt
        import numpy
        X = numpy.arange(len(list))
        plt.bar(X,list.values(),align='center',width=0.5)
        plt.xticks(X,list.keys())
        ymax=max(list.values()) + 1
        plt.ylim(0,ymax)
        plt.autoscale(enable=True,axis=u'x',tight=None)
        plt.title("Letter Grade Histogram of All Students That Have Taken a CS Class")
        plt.show()

    def calculatelettergrademean(self,list):
        sum = 0.0
        count = 0.0
        for grade in list:
            if grade in self.gradenumericsmap:
                sum = sum + self.gradenumericsmap[grade]
                count = count + 1.0
        return sum/count

    def calculatelettergrademedian(self,list):
        return list[len(list)/2]

    def calculatelettergrademode(self,countsmap):
        import operator
        return max(countsmap.iteritems(), key=operator.itemgetter(1))[0]