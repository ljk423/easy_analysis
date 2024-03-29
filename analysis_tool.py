#  Copyright (c) 2019. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
#  Created by LEEJUNKI
#  Copyright © 2019 LEEJUNKI. All rights reserved.
#  github :: https://github.com/ljk423

# easy_analysis_tool
# May 2019
# Free to use
# Can add various machinelearning deeplearning algorithms
# require module : xgboost, pandas, numpy, sklearn, matplotlib, graphviz, sys, seaborn, warnings, fancyimpute

import sys
import time
import warnings
import pandas as pd
import xgboost as xgb
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from fancyimpute import IterativeImputer
warnings.filterwarnings(action='ignore')
%matplotlib inline

def checkTime(func):
    def newFunc(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print('It takes {:.5f} seconds for training and tests.'.format(end - start))
    return newFunc

class dataprep:
    def __init__(self, file):
        self.file = file
    def datainput(self):
        full_data = pd.read_csv(self.file, header=0)
        print('\nMissing values for each columns')
        print(full_data.isnull().sum()) # print # of mssing values
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        df_n = full_data.select_dtypes(include=numerics)
        col_names = list(df_n.columns)
        df_c = full_data.select_dtypes(exclude=numerics)
        ipt = input('\nIs there any missing values? (y/n) : ')
        if ipt == 'y':
            ct = input('Is there any missing values which is not digit? (y/n) : ')
            if ct == 'y':
                full_data.dropna()
            else:
                impute = IterativeImputer()
                df_n = impute.fit_transform(df_n) #process mssing values using imputer
                df_n = pd.DataFrame(df_n)
                df_n.columns = col_names
                full_data = pd.concat([df_n,df_c], axis=1)
            print('\nMissing values after processing')
            print(full_data.isnull().sum())  # print # of missing values
        train, test = train_test_split(full_data, test_size=0.3, shuffle = False) # train,test set split , default = shuffle
        return train, test

class xgboost_anly:
    def __init__(self,train,test,label,*nonnum):
        self.train = train
        self.test = test
        self.target_names = set(test[label])
        if nonnum != ():
            self.nonnumeric_columns = re.sub(' ','',nonnum[0]).split(',')
            le = LabelEncoder()
            for feature in self.nonnumeric_columns:                         #one hot encoding for categorical features
                self.train[feature] = le.fit_transform(self.train[feature])
                self.test[feature] = le.fit_transform(self.test[feature])
        self.train_y = self.train[label]
        self.test_y = self.test[label]
        self.train_x = self.train.drop(label, axis =1)
        self.test_x = self.test.drop(label, axis=1)

    @checkTime
    def classification(self, ntree=100, depth=3, lr=0.05):
        self.gbm = xgb.XGBClassifier(n_estimators=ntree, max_depth=depth, learning_rate=lr).fit(self.train_x, self.train_y)
        self.predictions = self.gbm.predict(self.test_x)
        count_misclassified = (self.test_y != self.predictions).sum()
        print('\nMisclassified samples: {}'.format(count_misclassified))
        accuracy = metrics.accuracy_score(self.test_y, self.predictions)
        print('Accuracy: {:.5f}'.format(accuracy))

    def classifi_plot(self):
        fig = plt.figure(figsize = (19.20,10.80))
        ax1 = fig.add_subplot(224)
        ax2 = fig.add_subplot(211)
        ax3 = fig.add_subplot(223)
        cm = pd.DataFrame(metrics.confusion_matrix(self.test_y, self.predictions), columns=self.target_names, index=self.target_names)
        sns.heatmap(cm, annot=True, ax=ax1)
        xgb.plot_tree(self.gbm, num_trees=0,ax=ax2)
        xgb.plot_importance(self.gbm, ax=ax3)
        plt.show()

    @checkTime
    def regression(self, ntree=100, depth=3, lr=0.05):
        self.gbm = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=ntree, max_depth=depth,
                                    learning_rate=lr).fit(self.train_x, self.train_y)
        self.predictions = self.gbm.predict(self.test_x)
        print('\nMean Absolute Error: ', metrics.mean_absolute_error(self.test_y, self.predictions))
        print('Mean Squared Error: ', metrics.mean_squared_error(self.test_y, self.predictions))
        print("RMSE: ", (np.sqrt(metrics.mean_squared_error(self.test_y, self.predictions))))
        print()

    def reg_plot(self):
        fig = plt.figure(figsize=(19.20, 10.80))
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        x = np.arange(0,len(self.test_y))
        ax1.plot(x,self.test_y, label="Real Value")
        ax1.plot(x,self.predictions, label="Predicted Value")
        ax1.legend(loc=0)
        xgb.plot_importance(self.gbm.get_booster().get_score(importance_type='weight'),ax=ax2)
        plt.show()

class randomForest_anly:
    def __init__(self,train,test,label,*nonnum):
        self.train = train
        self.test = test
        self.target_names = set(test[label])
        if nonnum != ():
            self.nonnumeric_columns = re.sub(' ','',nonnum[0]).split(',')
            le = LabelEncoder()
            for feature in self.nonnumeric_columns:  # one hot encoding for categorical features
                self.train[feature] = le.fit_transform(self.train[feature])
                self.test[feature] = le.fit_transform(self.test[feature])
        self.train_y = self.train[label]
        self.test_y = self.test[label]
        self.train_x = self.train.drop(label, axis=1)
        self.test_x = self.test.drop(label, axis=1)

    @checkTime
    def classification(self, ntree=100):
        self.rfm = RandomForestClassifier(n_estimators=ntree).fit(self.train_x,self.train_y)
        self.predictions = self.rfm.predict(self.test_x)
        count_misclassified = (self.test_y != self.predictions).sum()
        print('\nMisclassified samples: {}'.format(count_misclassified))
        accuracy = metrics.accuracy_score(self.test_y, self.predictions)
        print('Accuracy: {:.5f}'.format(accuracy))

    def classifi_plot(self):
        fig = plt.figure(figsize=(19.20, 10.80))
        ax1 = fig.add_subplot(122)
        cm = pd.DataFrame(metrics.confusion_matrix(self.test_y, self.predictions), columns=self.target_names,index=self.target_names)
        sns.heatmap(cm, annot=True, ax=ax1)
        feature_list = list(self.train_x.columns)
        importances = self.rfm.feature_importances_
        indices = np.argsort(importances)
        plt.style.use('fivethirtyeight')
        plt.subplot(121)
        plt.barh(range(len(indices)), importances[indices], height=0.3)
        plt.yticks(range(len(indices)), [feature_list[i] for i in indices])
        plt.xlabel('Importance');
        plt.title('Variable Importances');
        plt.show()

    @checkTime
    def regression(self, ntree=100):
        self.rfm = RandomForestRegressor(n_estimators=ntree).fit(self.train_x,self.train_y)
        self.predictions = self.rfm.predict(self.test_x)
        print('\nMean Absolute Error: ', metrics.mean_absolute_error(self.test_y, self.predictions))
        print('Mean Squared Error: ', metrics.mean_squared_error(self.test_y, self.predictions))
        print("RMSE: ", (np.sqrt(metrics.mean_squared_error(self.test_y, self.predictions))))
        print()

    def reg_plot(self):
        plt.figure(figsize=(19.20, 10.80))
        plt.subplot(211)
        x = np.arange(0, len(self.test_y))
        plt.plot(x, self.test_y, label='Real Value')
        plt.plot(x, self.predictions, label='Predicted Value')
        plt.legend(loc=0)
        feature_list = list(self.train_x.columns)
        importances = self.rfm.feature_importances_
        indices = np.argsort(importances)
        plt.style.use('fivethirtyeight')
        plt.subplot(212)
        plt.barh(range(len(indices)), importances[indices], height=0.3)
        plt.yticks(range(len(indices)), [feature_list[i] for i in indices], size=9)
        plt.xlabel('Importance', size=10);
        plt.title('Variable Importances', size=10);
        plt.show()
        plt.close()

def pipeline():
    tool = input('\nChoose a tool for analysis (xgboost, randomforest) : ')
    if tool == 'xgboost':
        meth = input('classfication problem? (y/n) : ')
        if meth == 'y':
            print('\nProcessing classification problem.')
            label_name = input('\nEnter name of label(target) : ')
            nonnum = input('Enter the name of categorical features(except y, if none press enter) : ')
            if nonnum == '':
                anly = xgboost_anly(train, test, label_name)
                param = input("\nWant to setting Hyperparameter?(y/n)\n**If not, it will use default settings. : ")
                if param == 'y':
                    print("\n******Parameter input start******")
                    ntree = int(input("Enter the number of tree(default = 100) : "))
                    depth = int(input("Enter the maximum depth(default = 3) : "))
                    lr = float(input("Enter learning rate(default = 0.05) : "))
                    anly.classification(ntree, depth, lr)
                    anly.classifi_plot()
                else:
                    anly.classification()
                    anly.classifi_plot()
            else:
                anly = xgboost_anly(train, test, label_name, nonnum)
                param = input("\nWant to setting Hyperparameter?(y/n)\n**If not, it will use default settings. : ")
                if param == 'y':
                    print("\n******Parameter input start******")
                    ntree = int(input("Enter the number of tree(default = 100) : "))
                    depth = int(input("Enter the maximum depth(default = 3) : "))
                    lr = float(input("Enter learning rate(default = 0.05) : "))
                    anly.classification(ntree, depth, lr)
                    anly.classifi_plot()
                else:
                    anly.classification()
                    anly.classifi_plot()
        elif meth == 'n':
            print('\nProcessing regression problem.')
            label_name = input('\nEnter name of label(target) : ')
            nonnum = input('Enter the name of categorical features(except y, if none press enter) : ')
            if nonnum == '':
                anly = xgboost_anly(train, test, label_name)
                param = input("\nWant to setting Hyperparameter?(y/n)\n**If not, it will use default settings. : ")
                if param == 'y':
                    print("\n******Parameter input start******")
                    ntree = int(input("Enter the number of tree(default = 100) : "))
                    depth = int(input("Enter the maximum depth(default = 3) : "))
                    lr = float(input("Enter learning rate(default = 0.05) : "))
                    anly.regression(ntree, depth, lr)
                    anly.reg_plot()
                else:
                    anly.regression()
                    anly.reg_plot()
            else:
                anly = xgboost_anly(train, test, label_name, nonnum)
                param = input("Want to setting Hyperparameter?(y/n)\n**If not, it will use default settings. : ")
                if param == 'y':
                    print("\n******Parameter input start******")
                    ntree = int(input("Enter the number of tree(default = 100) : "))
                    depth = int(input("Enter the maximum depth(default = 3) : "))
                    lr = float(input("Enter learning rate(default = 0.05) : "))
                    anly.regression(ntree, depth, lr)
                    anly.reg_plot()
                else:
                    anly.regression()
                    anly.reg_plot()
        else:
            raise KeyError
    elif tool =='randomforest':
        meth = input('classfication problem? (y/n) : ')
        if meth == 'y':
            print('\nProcessing classification problem.')
            label_name = input('\nEnter name of label(target) : ')
            nonnum = input('Enter the name of categorical features(except y, if none press enter) : ')
            if nonnum == '':
                anly = randomForest_anly(train, test, label_name)
                param = input("\nWant to setting Hyperparameter?(y/n)\n**If not, it will use default settings. : ")
                if param == 'y':
                    print("\n******Parameter input start******")
                    ntree = int(input("Enter the number of tree(default = 100) : "))
                    anly.classification(ntree)
                    anly.classifi_plot()
                else:
                    anly.classification()
                    anly.classifi_plot()
            else:
                anly = randomForest_anly(train, test, label_name, nonnum)
                param = input("\nWant to setting Hyperparameter?(y/n)\n**If not, it will use default settings. : ")
                if param == 'y':
                    print("\n******Parameter input start******")
                    ntree = int(input("Enter the number of tree(default = 100) : "))
                    anly.classification(ntree)
                    anly.classifi_plot()
                else:
                    anly.classification()
                    anly.classifi_plot()
        elif meth == 'n':
            print('\nProcessing regression problem.')
            label_name = input('\nEnter name of label(target) : ')
            nonnum = input('Enter the name of categorical features(except y, if none press enter) : ')
            if nonnum == '':
                anly = randomForest_anly(train, test, label_name)
                param = input("\nWant to setting Hyperparameter?(y/n)\n**If not, it will use default settings. : ")
                if param == 'y':
                    print("\n******Parameter input start******")
                    ntree = int(input("Enter the number of tree(default = 100) : "))
                    anly.regression(ntree)
                    anly.reg_plot()
                else:
                    anly.regression()
                    anly.reg_plot()
            else:
                anly = randomForest_anly(train, test, label_name, nonnum)
                param = input("\nWant to setting Hyperparameter?(y/n)\n**If not, it will use default settings. : ")
                if param == 'y':
                    print("\n******Parameter input start******")
                    ntree = int(input("Enter the number of tree(default = 100) : "))
                    anly.regression(ntree)
                    anly.reg_plot()
                else:
                    anly.regression()
                    anly.reg_plot()
        else:
            raise KeyError
    else: print('There is no such tool.')

if __name__ == "__main__":

    file = input('Enter the file path (ex: /Users/Desktop/file.csv) : ')
    prep = dataprep(file)
    try:
        train, test = prep.datainput()
    except TypeError:
        print('\nThere is data format problem.')
    except FileNotFoundError:
        print('\nCheck the path again.')
        sys.exit()

    flag = True
    while flag:
        try:
            pipeline()
        except KeyError:
            print('Wrong input or Wrong feature named.')
        except TypeError:
            print('It is not proper tools for that label type.')
        finally :
            keep = input('\nWant to analyize again? (y/n) : ')
        if keep == 'y':
            continue
        else :
            flag = False
            sys.exit('Analysis System End')
