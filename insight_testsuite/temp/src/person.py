
"""
Adapted from http://pythonfiddle.com/friend-of-friends/
(Because transparency is more important than ego.)
"""

class Person(object):
  npurchase=0

  def __init__(self, unique_id, friends=None, purchase_info=None):
    self.unique_id = unique_id
    #self.name = name
    if friends:
      self.friends = friends
    else:
      self.friends = {}

    if purchase_info:
      self.purchases = self.AddPurchase(purchase_info)
    else:
      self.purchases = {}
        
  def GetFriends(self):
    return self.friends
        
  def GetID(self):
    return self.unique_id
   
  def GetPurchases(self):
    return self.purchases

  #def GetName(self):
  #  return self.Name

  def AddPurchase(self, purchase_info):
    #self.purchases[purchase_info['timestamp']]={'amount':purchase_info['amount']}
    self.purchases[self.npurchase]={'amount':purchase_info['amount'], 'timestamp':purchase_info['timestamp']}
    self.npurchase += 1
    return

  def AddFriend(self, person):
    self.friends[person.GetID()] = person    
    if self.unique_id not in person.GetFriends():
    	person.AddFriend(self)
    return

  def DeFriend(self, person):
    del self.friends[person.GetID()]
    del person.GetFriends()[self.unique_id ]
    return
    
  def IsFriend(self, person):
    return person.GetID() in self.friends      
        


def FriendOfFriend(user_a, user_b):
  friends_of_a = user_a.GetFriends()
  for friend in friends_of_a.values():
    if friend.IsFriend(user_b):
      return True    
  return False      


def GetNetwork(user_a, D=False):
  network = user_a.GetFriends().keys()
  #print "initial network: ", network
  if D==1 and network:
    return network
  if D==2 and network:	
    friends_of_a = user_a.GetFriends()
    for friend in friends_of_a.values():
      their_friends = friend.GetFriends()
    for afriend in their_friends.values():
      if afriend.unique_id != user_a.unique_id:
        if FriendOfFriend(user_a, afriend):
          network.append(afriend.unique_id)
    return network					
  if D==3:
    friends_of_a = user_a.GetFriends()
    for friend in friends_of_a.values():
      their_friends = friend.GetFriends()
      for afriend in their_friends.values():
        if afriend.unique_id != user_a.unique_id:
          if FriendOfFriend(user_a, afriend):
            network.append(afriend.unique_id)
            fofof = afriend.GetFriends()
            for afof in fofof.values():
              if afof.unique_id not in network:
                network.append(afof.unique_id)            
    return  network
  		  		
  if D > 3:
    raise ValueError("Degrees of connection greater than 3, really? Those aren't friends, those are strangers.")
     

