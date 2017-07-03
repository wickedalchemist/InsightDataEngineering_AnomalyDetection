import sys
sys.path.append('../../../src/')

import person as Person

p1 = Person.Person(1)
p2 = Person.Person(2)
p3 = Person.Person(3)
p4 = Person.Person(4)
p5 = Person.Person(5)
p6 = Person.Person(6)
p7 = Person.Person(7)
p8 = Person.Person(8)
p9 = Person.Person(9)
p10 = Person.Person(10)

p1.AddFriend(p2)
p1.AddFriend(p3)
p1.AddFriend(p4)

p3.AddFriend(p8)

p4.AddFriend(p5)

p5.AddFriend(p6)
p5.AddFriend(p7)

p6.AddFriend(p8)
p6.AddFriend(p7)
p6.AddFriend(p10)

record = {u'timestamp': u'2017-06-13 11:33:01', u'amount': u'16.83', u'event_type': u'purchase', u'id': u'1'}
record2 = {u'timestamp': u'2017-06-13 11:33:11', u'amount': u'19.83', u'event_type': u'purchase', u'id': u'1'}
p1.AddPurchase(purchase_info=record)
p1.AddPurchase(purchase_info=record2)

if Person.GetNetwork(p1, D=2) != [2,3,4,5]:
    raise ValueError("Seems to be an issue in GetNetwork")

if not Person.FriendOfFriend(p1,p5):
    raise ValueError("FriendofFriend method is faulty")


for i,purchase in enumerate(p1.GetPurchases().values()):
    if i == 0:
        if purchase['amount'] != str(16.83):
            raise ValueError("GetPurchases method seems to be faulty")
    if i == 1:
        if purchase['amount'] != str(19.83):
            raise ValueError("GetPurchases method seems to be faulty")


