import json
from collections import OrderedDict
import os
import time, datetime
import numpy as np
import person as Person

def float_formatter(n, number):
    string = "%."+str(n)+"f"
    tmp = lambda x: string % x
    return tmp(number)

class EventProcessor(object):
    def __init__(self, json_dict):
        self.json_dict = json_dict
        self.event_type = json_dict['event_type']
        if self.event_type == 'purchase':
            self.amount = self.json_dict['amount']
            self.user_id = self.json_dict['id']
        if ( (self.event_type == 'befriend') | (self.event_type == 'unfriend') ):
            self.user_id = self.json_dict['id1']

    def Purchase(self, users):
        self.amount = self.json_dict['amount']
        self.user_id = (self.json_dict['id'])
        self.timestamp = self.json_dict['timestamp']
        users[(self.user_id)].AddPurchase(purchase_info=self.json_dict)

    def MakeFriend(self, users):
        self.user_id = (self.json_dict['id1'])
        users[self.user_id].AddFriend(users[self.json_dict['id2']])
        
    def UnFriend(self, users):
        self.user_id = (self.json_dict['id1'])
        users[self.user_id].DeFriend(users[self.json_dict['id2']])

    def HandleIt(self, usrs=False):
        if self.event_type == 'purchase':
            self.Purchase(usrs)
        if self.event_type == 'befriend':
             self.MakeFriend(usrs)
        if self.event_type == 'unfriend':
            self.UnFriend(usrs)

def DefUsers(batch_file_path):
    batch_file = open(batch_file_path)
    l=0
    users = {}
    for i,line in enumerate(batch_file.readlines()):
        json_dict = json.loads(line, object_pairs_hook=OrderedDict)
        if l > 1:
            if json_dict['event_type']=='purchase':
                if (json_dict['id']) not in users.keys():
                    users[(json_dict['id'])] = Person.Person((json_dict['id']))
            if json_dict['event_type']=='befriend':
                if (json_dict['id1']) not in users.keys():
                    users[(json_dict['id1'])] = Person.Person((json_dict['id1']))
                if (json_dict['id2']) not in users.keys():
                    users[(json_dict['id2'])] = Person.Person((json_dict['id2']))
            if json_dict['event_type']=='unfriend':
                if json_dict['id1'] not in users.keys():
                    users[json_dict['id1']] = Person.Person(json_dict['id1'])
                if json_dict['id2'] not in users.keys():
                    users[json_dict['id2']] = Person.Person(json_dict['id2'])

        l+=1

    batch_file.close()

    return users

def InitiateEvents(batch_file_path, users):
    #Goes through each transaction in batch file, and alters the friend list/purchase history for each user
    batch_file = open(batch_file_path)
    for i,line in enumerate(batch_file.readlines()):
        json_dict = json.loads(line, object_pairs_hook=OrderedDict)
        if i == 0:
            #Degrees of connection and number of transaction set here
            D = float(json_dict['D'])
            T = float(json_dict['T'])
        if i > 0:
            event = EventProcessor(json_dict)
            event.HandleIt(usrs=users)
        
    batch_file.close()
    return users, D, T

def PurchaseInNetwork(usr, network, T=False):
    #Get all purchases from all users in a given user's network (defined by the degrees of connection) -> network if found in GetNetwork method of Person class
    #Before returning network purchases, cut the list of purchases to the defined transaction limit, if the number of purchases within the network is above this threshold
    network_purchases = []
    
    for friend_id in network:
        times, amounts = [], []
        if not users[friend_id].GetPurchases():
            #In theory, we should never reach this place - all users should be defined in initialization of database
            raise ValueError('User '+str(users[friend_id].unique_id)+' does not exist in database')
        network_purchases.append(users[friend_id].GetPurchases())
        friends_buys = users[friend_id].GetPurchases()
        buys = friends_buys.values()
        tmoney = [thisbuy['amount'] for thisbuy in buys]
        ttime = [time.mktime(datetime.datetime.strptime(thisbuy['timestamp'], "%Y-%m-%d %H:%M:%S").timetuple()) for thisbuy in buys]
        amounts = amounts + tmoney
        times = times + ttime

    #need to have at least 2 transactions
    leng_amounts = len(amounts)   
    if leng_amounts > 1:
        amounts = np.array(amounts,dtype=float)
        times = np.array(times, dtype=float)
        sortby = np.argsort(times)
        times = times[sortby]
        amounts = amounts[sortby]
        high = np.min([float(leng_amounts), T])
        return amounts[:high], times[:high]
    else:
        return [],[]

def FindAnomaly(json_dict, users, T=False):
    #Determine if a given purchase is an outlier within the user's network
    amounts, times = PurchaseInNetwork(usr, network, T=T)
    if len(amounts) > 1:
        if (float(event.amount) > np.mean(amounts)+3*np.std(amounts)) & (np.std(amounts)>0):
            return json_dict, np.mean(amounts), np.std(amounts)
    return np.nan, np.nan, np.nan


### INITIALIZE PARAMETERS
batch_file_path = '/home/tahlia/Documents/Insight/anomaly_demaio/log_input/batch_log.json'
stream_file_path = '/home/tahlia/Documents/Insight/anomaly_demaio/log_input/stream_log.json'
n=10000

start = time.time()
#DEFINE USERS FROM BATCH LOG
users = DefUsers(batch_file_path)
#print "HAVE IDENTIFIED ALL USERS"
#PROCESS TRANSACTIONS IN BATCH_FILE, ADJUSTING PARMETERS FOR EACH USER AS NEEDED
users, D, T = InitiateEvents(batch_file_path, users)
#print "HAVE PROCESSED ALL INITIAL TRANSACTIONS AND ASSIGNED TO RESPECTIVE USER"

#GO THROUGH TRANSACTIONS AGAIN, ONE BY ONE, FINDING NETWORK PURCHASE HISTORY FOR EACH
stream_file = open(stream_file_path)
batch_file = open(batch_file_path)
flagged_file_path = './log_output/flagged_purchases.json'

if os.access(flagged_file_path, os.F_OK)==True: os.system('rm '+flagged_file_path)
with open(flagged_file_path, 'a') as outfile:
    for i, line in enumerate(stream_file.readlines()):
        json_dict = json.loads(line, object_pairs_hook=OrderedDict)
        event = EventProcessor(json_dict)
        if event.user_id not in users.keys():
            #again, should never be an issue, all users defined upon initialization
            raise ValueError('User '+str(event.user_id)+' does not exist in database')
        #Process each transaction, adding it to user history
        event.HandleIt(usrs=users)
        if event.event_type == 'purchase':
            #Evaluate if this purchase is an outlier
            usr = users[event.user_id]
            network = Person.GetNetwork(usr, D=D)
            if network:
                threesig, mean, std = FindAnomaly(json_dict, users, T=T)
                if np.isfinite(mean):
                    json_dict['mean']=float_formatter(2,mean)
                    json_dict['sd']=float_formatter(2,std)
                    json.dump(json_dict, outfile)
                    outfile.write('\n')


batch_file.close()
stream_file.close()

#print (time.time()-start)/60.
