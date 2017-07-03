# Table of Contents
1. [Challenge Summary](README.md#code-challenge-summary)
2. [Details of Implementation](README.md#details-of-implementation)
3. [Dependencies](README.md#dependencies)
4. [Run Instructions](README.md#run-instructions)
 
 
# Code Challenge Summary
 
Challenge: Given a log of all transactions at an e-commerce company with a social network, determine if a given transaction is anomalously high within a user's friend network. 
See <https://github.com/InsightDataScience/anomaly_detection> for full description and requirements of code challenge.
 
A user's network is defined by a degrees of connection parameter, D. 
D=1 considers only direct friends of a user as that user's network.
D=2 considers friends of the user's friends as a part of the network.
D=3 considers the friends of the friends of the user's friends as the network.
etc.
Given D, an anomalous purchase is one that is 3 sigma above the mean of the user's network's average purchase.
To further customize this algorithm, the number of transaction to track within a user's network can be set. 
Purchases from the stream of transactions are evaluated and flagged purchases are recorded, along with the mean and standard deviation of the user's network purchases (within the last T transactions).
 
# Details of Implementation
To address this challenge I consider the following scenario:
 
1. An initial log of transaction is available from which I build a record of all transactions (friending, unfriending, purchases) for a given user. 
The variables D (degree of connection) and T (number of transaction) are defined in the first line of this log.
Using this batch log I create a 'database' of users. 
The direct friends and purchase history of each user is reflected in this database.
All subsequent transactions can change this database, depending on the event type. (e.g. a purchase gets added to the purchase log, an unfriending removes a friend from the user's list).
After processing the batch log the users database is 'primed' for the streaming feed. 
 
2. A 'real-time' stream of transaction is contained in a separate log. 
Each of these transactions is evaluated and updates the database of users, as generated above. 
For example, if a new friendship is made that connection is reflected for both friends and their respective networks.
A reminder, a user's network is a flexible parameter that depends on the degree of connection, D. 
For a purchase in the streaming log I first collect all purchases made within a user's network.
Then, taking the last T transaction, I find the mean and standard deviation of these purchases.
If anomalous (3 sigma above the mean), the purchase is flagged and recorded in an output log.
Anomalous purchases are not removed, they are incorporated into the purchase history of that network and would be considered part of the baseline if future purchases were made within that network.
 
# Dependencies 
 
This code is written in Python, tested with version 2.7.13 on an Ubuntu 14.01 machine. It requires the Python packages numpy, json, collections, time, datetime, and os.
 
# Run Instructions
Simply execute run.sh in the top directory of this repo.
The default behavior is to use log_input/batch_log.json and log_input/stream_log.json as the input logs, however this can be changed by editing the file path specified in run.sh.
The output log of anomalous purchases is always recorded in log_output/flagged_purchases.json
 
 
 
