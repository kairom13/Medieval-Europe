"""
Created on Nov 10, 2021

@author: kairom13
"""

import json
import os
import uuid
from abc import ABC, abstractmethod
from Medieval_Europe import get_parent_path


######################################
###                                ###
###      Custom Object Class       ###
###                                ###
######################################

class CustomObject(ABC):
    def __init__(self, logger, objectType, objectID, attribute_list):
        if objectID is None:
            self.objectID = uuid.uuid4().hex[:8]
        else:
            self.objectID = objectID
        self.name = 'No Name'
        self.objectType = objectType

        self.logger = logger

        self.attributes = {}
        self.connectionDict = {}
        self.eventList = {}

        for a in attribute_list:
            self.attributes.update({a: ''})

    #### Common Methods:
    ## Set the name of the object (unique to the object)
    @abstractmethod
    def setName(self):
        pass

    ## Get the name of the object
    def getName(self):
        return self.name

    ## Get new ID if this one is a duplicate (Should be redundant)
    def getNewID(self):
        self.logger.log('Code', 'Creating new id')
        self.objectID = uuid.uuid4().hex[:8]

    ## Return this object's id
    def getID(self):
        return self.objectID

    def removeEvent(self, id):
        self.eventList.pop(id)

    def updateEvent(self, id, eventDetails):
        self.eventList.update({id: eventDetails})

    def getEvent(self, id):
        return self.eventList[id]

    def getEventList(self):
        return self.eventList

    def getObjectType(self):
        return self.objectType

    ## Generic function to update specific attribute data
    def updateAttribute(self, attribute, info):
        if attribute in self.attributes:
            self.attributes.update({attribute: info})
        else:
            self.logger.log('Error', str(attribute) + ' is not a valid attribute of a ' + str(self.__class__.__name__))

    ## Get attribute value
    def getAttribute(self, attribute):
        #print('Getting attribute ' + str(attribute))
        if attribute in self.attributes:
            return self.attributes[attribute]
        else:
            self.logger.log('Error', str(attribute) + ' is not a valid attribute of a ' + str(self.__class__.__name__))
            return None

    def check_argument(self, arg, connection=None):
        if isinstance(arg, str):
            return arg
        elif arg.__class__.__name__ in ('Person', 'Title', 'Reign', 'Place'):
            return arg.getID()
        else:
            self.logger.log('Error', str(arg) + ' is an invalid data type. Should be String ID or CustomObject.')
            return None

    ## Function to handle modification to the connection dict:
    # Add: subject with the given connection name
    # Get: the connection name with the given subject
    # Remove: the connection with the given subject
    def connection(self, update, subject, name=None):
        subjectID = self.check_argument(subject)

        if subjectID is None:
            self.logger.log('Error', 'Cannot modify connection, no subject given')
        else:
            if update == 'Add':
                if subjectID in self.connectionDict:
                    self.logger.log('Warning', 'No need to add {' + str(subjectID) + '} as ' + str(name) + ' of {' + self.getID() + '}. Already connected')
                elif name is None:
                    self.logger.log('Warning', 'No connection name given')
                else:
                    self.connectionDict.update({subjectID: name})

            elif update == 'Get':
                if subjectID in self.connectionDict:
                    return self.connectionDict[subjectID]
                else:
                    self.logger.log('Error', 'Cannot get connection. {' + str(subjectID) + '} is not a connection of ' + self.getName())
                    return None

            elif update == 'Remove':
                if subjectID in self.connectionDict:
                    self.connectionDict.pop(subjectID)
                else:
                    self.logger.log('Warning', 'Cannot remove connection. {' + str(subjectID) + '} is not a connection of ' + self.getName())

            else:
                self.logger.log('Error', str(update) + ' is an invalid update value')

    ## Get Dictionary of values
    @abstractmethod
    def getDict(self):
        pass

    ## Get Info to display in object list
    @abstractmethod
    def getDisplayInfo(self):
        pass

######################################
###                                ###
###          Person Class          ###
###                                ###
######################################

## Required common fields and methods:
# id: unique 8 character string that defines a given person
# getName(): method that returns the name of the title
#    is the simple name of the person
# updateFreeInfo(): method that updates certain fields that use text boxes
#    applicable fields for Person:
#    - Name
#    - Nickname
#    - Primary Title
#    - Birth Date
#    - Death Date
# getDict(): method that returns a dictionary that defines this person, used when writing to output file

class Person(CustomObject):
    def __init__(self, logger, gender, init_dict, personID):
        super().__init__(logger, 'Person', personID, ['Name', 'Nickname', 'Birth Date', 'Death Date'])

        self.classKey = 'Person Class'
        self.classInstance = self.objectID

        self.gender = gender
        self.primaryTitle = None
        
        self.spouses = {'unknown_spouse': []}  # Dictionary, each key is a spouse id, each value is the list of children id's for the spouse
        self.parents = {'Father': None, 'Mother': None}
        
        if init_dict is not None:
            for a in self.attributes:
                self.updateAttribute(a, init_dict['Attributes'][a])

            for c in init_dict['Connections']:
                if c == 'Spouses':
                    self.addSpouses(init_dict['Connections'][c])
                else:
                    self.addParent(init_dict['Connections'][c], c)

            for e in init_dict['Events']:
                self.updateEvent(e, init_dict['Events'][e])

        self.setName()
        
        self.reignList = {}  # {reign.id: reignObject}
        self.placeList = {}  # {place.id: placeObject

    ## Set this person's name as the full name
    def setName(self):
        if self.getAttribute('Nickname') == '':
            nickname = ''
        else:
            nickname = ' ' + self.getAttribute('Nickname')
            
        if self.primary_title('Has'):
            primaryTitle = ', ' + self.primary_title('Get')
        else:
            primaryTitle = ''
            
        self.name = self.getAttribute('Name') + nickname + primaryTitle

    ## Return a string of info to display for this person
    def getDisplayInfo(self):
        name_split = self.getName().split(', ')
        if len(name_split) == 2:
            return name_split[0] + ' (' + self.getAttribute('Birth Date') + ' - ' + self.getAttribute('Death Date') + ')\n' + name_split[1]
        else:
            return name_split[0] + ' (' + self.getAttribute('Birth Date') + ' - ' + self.getAttribute('Death Date') + ')'

    ## Add Relationship with Child
    ## If there is no spouse, add child with unknown spouse
    def addChild(self, child, spouse):
        childID = self.check_argument(child, 'Child')

        if spouse is None:  ## Person had child with an unknown spouse
            if childID in self.spouses['unknown_spouse']:
                self.logger.log('Error', '{' + childID + '} is already a child of {' + self.getID() + '} with unknown spouse')
            else:
                self.logger.log('Code', 'Add {' + childID + '} as new child with unknown spouse')
                self.spouses['unknown_spouse'].append(childID)  # Add the child to the unknown spouse list
                self.connection('Add', childID, 'Child')

        else:
            spouseID = self.check_argument(spouse, 'Spouse')
            
            if spouseID in self.spouses:
                ## Person had child with known spouse of person
                ## Add child to the person with given spouse

                self.logger.log('Code', 'Add {' + childID + '} as new child with spouse {' + spouseID + '}')
                self.spouses[spouseID].append(childID)  # Add the child to the given spouse's list

            else:
                self.logger.log('Error', 'Cannot add child, {' + spouseID + '} is not a valid spouse')
        
    ## Remove Relationship with Child 
    def removeChild(self, child):
        childID = self.check_argument(child, 'Child')

        for s in self.spouses:
            for c in self.spouses[s]:
                if childID == c:
                    self.logger.log('Code', 'Removed {' + childID + '} as a child with spouse {' + s + '}')
            
                    self.spouses[s].remove(childID)
                    self.connection('Remove', childID)
                    return s  # Return the spouse with whom the child is being removed
                
        self.logger.log('Warning', '{' + childID + '} is not a child of {' + self.getID() + '}, so cannot be removed')
        return None  # No spouse is returned
        
    ## Add full list of spouses
    def addSpouses(self, spouses):
        for s, children in spouses.items():
            self.spouses.update({s: children})
            if s != 'unknown_spouse':
                self.connection('Add', s, 'Spouse')

            for c in children:
                self.connection('Add', c, 'Child')
        
    ## Add Relationship with Spouse
    def addSpouse(self, spouse):
        spouseID = self.check_argument(spouse, 'Spouse')

        self.spouses.update({spouseID: []})
        self.connection('Add', spouseID, 'Spouse')
        self.logger.log('Code', 'Added {' + spouseID + '} as a spouse')
        
    ## Remove Relationship with Spouse
    def removeSpouse(self, target):
        targetID = self.check_argument(target, 'Spouse')

        if targetID in self.spouses:
            self.logger.log('Code', 'Removing {' + targetID + '} as spouse')
            childrenList = self.spouses[targetID] ## Get the list of children with that spouse

            for c in childrenList:  ## Add those children to the unknown spouse list
                self.logger.log('Code', 'Moving {' + c + '} to unknown spouse')
                self.spouses['unknown_spouse'].append(c)

            self.spouses.pop(targetID)  # Remove the target spouse from the spouse dictionary
            self.connection('Remove', targetID)

        else:
            self.logger.log('Error', '{' + targetID + '} not a valid spouse to remove')

    # Add parent as the relation to self
    def addParent(self, parent, relation):
        if parent is not None:
            parentID = self.check_argument(parent, 'Person')  # Get the parentID

            if relation in ('Father', 'Mother'):
                self.parents.update({relation: parentID})
                if parentID is not None:  # Only add parent relationship if the parent exists (should not have a None key)
                    self.connection('Add', parentID, name=relation)
            else:
                self.logger.log('Error', str(relation) + ' is not a valid parent type to add')
    
    ## Remove Relationship with Parent (can be either name or subject)
    def removeParent(self, parent):
        if parent in ('Father', 'Mother'):
            parentID = self.getParents(parent)[0]  # Get the subjectID of the parent to remove
            self.parents.update({parent: None})  # Update the parents dict to specify the parent name as None
        else:
            parentID = self.check_argument(parent, 'Person')  # Get the parentID
            relation = self.connection('Get', parentID)  # Get the name of the relationship
            if relation is not None:
                self.parents.update({relation: None})  # Set the relationship as None

        self.logger.log('Code', 'Removing ' + self.connection('Get', parentID) + ' from {' + self.getID() + '}')
        self.connection('Remove', parentID)

    ## Get the parent IDs as a tuple with an order based on what relation name was given
    def getParents(self, relation=None):
        if relation == 'Father':
            return self.parents['Father'], self.parents['Mother']
        elif relation == 'Mother':
            return self.parents['Mother'], self.parents['Father']
        elif relation is None:
            return self.parents['Father'], self.parents['Mother']
        else:
            self.logger.log('Error', str(relation) + ' is not a valid parent type to get')
            return None
            
    def addReign(self, reign):
        if isinstance(reign, Reign):
            self.reignList.update({reign.getID(): reign})
            self.connection('Add', reign.getID(), 'Reign')
        else:
            self.logger.log('Error', 'Cannot add ' + str(reign) + ' as Reign. Invalid type')
        
    def removeReign(self, reign):
        reignID = self.check_argument(reign, 'Reign')

        self.logger.log('Code', 'Removing reign {' + str(reignID) + '}')
        placeList = self.reignList[reignID].placeList
        for p, place in placeList.items():
            place.removeReign(reignID)

        self.reignList.pop(reignID)
        
    ## Merges the junior reign with the senior reign 
    def mergeReigns(self, juniorReign, seniorReign, window):
        seniorReign.mergeReign(juniorReign, 'Junior')
        
        self.logger.log('Code', 'Senior Reign: ' + str(seniorReign.titleName))
        self.logger.log('Code', 'Junior Reign: ' + str(juniorReign.titleName))
        
        # Transfer any junior reigns in the reign object to the target senior reign
        for j in juniorReign.mergedReigns['Junior']:
            reignObject = window.reignList[j]
            seniorReign.mergeReign(reignObject, 'Junior')
            reignObject.mergeReign(seniorReign, 'Senior')
            
        juniorReign.mergeReign(seniorReign, 'Senior')
        
        ## If the senior reign has a predecessor, make sure the junior reign has a similar predecessor
        ##    1) Get the predecessor person
        ##    2) Iterate through the reign list to find the equivalent title
        ##        a) The title is found, look for the successor
        ##            i) A successor is found, note it in the log and replace it with this reign
        ##            ii) A successor is not found, so set this reign as the new successor
        ##            iii) No other action needed
        ##        b) The title is not found, create new reign
        ##            i) Set the successor as this reign
        ##            ii) Add it to the person, title, and global reignlist
        ##            iii) Merge the reign with the senior (restart the process with the new person)
        if seniorReign.hasConnectedReign('Predecessor'):
            self.logger.log('Code', 'Add Predecessor')
            
            seniorPredecessor = window.get_object(seniorReign.predecessor)  # The predecessor to the senior reign
            predecessorPerson = window.get_object(seniorPredecessor.rulerID)  # The person who has the predecessor senior reign
            
            allJuniorReigns = [juniorReign.getID()]
            for j in juniorReign.mergedReigns['Junior']:
                allJuniorReigns.append(j)
            
            for j in allJuniorReigns:
                juniorReignObject = window.get_object(j)
                juniorTitle = window.get_object(juniorReignObject.titleID)  # The title of the junior reign being merged
                
                self.logger.log('Code', 'Adding Predecessor to ' + str(juniorReignObject.titleName))
                
                noTitle = True
                for r, predecessorReign in predecessorPerson.reignList.items():  # Iterate through the reigns of the predecessor
                    if predecessorReign.titleID == juniorReignObject.titleID:  # Look for the junior reign-title in the list
                        noTitle = False  # If found, then no need for new reign
                        # Set the junior reign as this reign's successor
                        if not predecessorReign.hasConnectedReign('Successor'):
                            predecessorReign.setSuccessor(juniorReignObject.getID())
                            juniorReignObject.setPredecessor(predecessorReign.getID())
                        else:
                            print(str(predecessorPerson.getAttribute('Name')) + ', ' + juniorTitle.getFullRulerTitle(predecessorPerson.gender) +
                                  ' already has a successor in ' + str(juniorReignObject.getConnectedReign('Ruler').getName()))
                            predecessorReign.setSuccessor(juniorReignObject.getID())
                            juniorReignObject.setPredecessor(predecessorReign.getID())
                
                if noTitle: ## Case when the title is not in the person's list
                    juniorPredecessor = Reign(self.logger, predecessorPerson.getID(), predecessorPerson.getAttribute('Name'))
                    juniorPredecessor.setSuccessor(juniorReignObject.getID())
                    juniorReignObject.setPredecessor(juniorPredecessor.getID())
                    juniorPredecessor.setTitle(juniorTitle)
                    juniorPredecessor.setDate(seniorPredecessor.stDate, 'Start Date')
                    juniorPredecessor.setDate(seniorPredecessor.endDate, 'End Date')
                    
                    predecessorPerson.addReign(juniorPredecessor)
                    juniorTitle.addReign(juniorPredecessor)
                    window.add_object(juniorPredecessor)
                    
                    # Merge the new junior reign with the existing senior predecessor
                    predecessorPerson.mergeReigns(juniorPredecessor, seniorPredecessor, window)
        
        ## If the senior reign has a successor, make sure the junior reign has a similar successor
        ##    1) Get the predecessor person
        ##    2) Iterate through the reign list to find the equivalent title
        ##        a) The title is found, look for the predecessor
        ##            i) A predecessor is found, note it in the log and replace it with this reign
        ##            ii) A predecessor is not found, so set this reign as the new predecessor
        ##            iii) No other action needed
        ##        b) The title is not found, create new reign
        ##            i) Set the predecessor as this reign
        ##            ii) Add it to the person, title, and global reignlist
        ##            iii) No other action needed
        ##    3) Merge the selected reign with the senior (restart the process with the new person)
        if seniorReign.hasConnectedReign('Successor'):
            self.logger.log('Code', 'Add Successor')
            
            seniorSuccessor = window.get_object(seniorReign.successor)
            successorPerson = window.get_object(seniorSuccessor.rulerID)
            
            allJuniorReigns = [juniorReign.getID()]
            for j in juniorReign.mergedReigns['Junior']:
                allJuniorReigns.append(j)
            
            for j in allJuniorReigns:
                juniorReignObject = window.get_object(j)
                juniorTitle = juniorReign.getConnectedReign('Title')
                
                self.logger.log('Code', 'Adding Successor to ' + str(juniorReignObject.titleName))
                
                noTitle = True
                for r, successorReign in successorPerson.reignList.items():
                    if successorReign.titleID == juniorReignObject.titleID:
                        noTitle = False
                        if not successorReign.hasConnectedReign('Successor'):
                            successorReign.setPredecessor(juniorReignObject.getID())
                            juniorReignObject.setSuccessor(successorReign.getID())
                        else:
                            print(str(successorPerson.getAttribute('Name')) + ', ' + juniorTitle.getFullRulerTitle(successorPerson.gender) +
                                  ' already has a successor in ' + str(juniorReignObject.getConnectedReign('Ruler').getName()))
                            successorReign.setPredecessor(juniorReignObject.getID())
                            juniorReignObject.setSuccessor(successorReign.getID())
                
                if noTitle:
                    juniorSuccessor = Reign(self.logger, successorPerson.getID(), successorPerson.getAttribute('Name'))
                    juniorSuccessor.setPredecessor(juniorReignObject.getID())
                    juniorReignObject.setSuccessor(juniorSuccessor.getID())
                    juniorSuccessor.setTitle(juniorTitle)
                    juniorSuccessor.setDate(seniorSuccessor.stDate, 'Start Date')
                    juniorSuccessor.setDate(seniorSuccessor.endDate, 'End Date')
                    
                    successorPerson.addReign(juniorSuccessor)
                    juniorTitle.addReign(juniorSuccessor)
                    window.add_object(juniorSuccessor)
                    
                    # Merge the new junior reign with the existing senior successor
                    successorPerson.mergeReigns(juniorSuccessor, seniorSuccessor, window)

    #
    def primary_title(self, action, title=None):
        if action == 'Set':
            self.primaryTitle = title.getFullRulerTitle(self.gender)
            self.setName()

        elif action == 'Get':
            return self.primaryTitle

        elif action == 'Remove':
            self.primaryTitle = None
            self.setName()

        elif action == 'Has':
            if self.primaryTitle is None:
                return False
            else:
                return True

    ## Add a title (with a new reign) to the list
    def addTitle(self, title):
        newReign = Reign(self.logger, self, title, None, None)

        self.reignList.update({newReign.getID(): newReign})
        
        return newReign

    ## Add place to place list
    def addPlace(self, placeObject):
        placeID = placeObject.getID()

        if placeID in self.placeList:
            self.logger.log('Warning', str(placeObject.getAttribute('Name')) + ' is already associated with ' + str(self.getAttribute('Name')))
        else:
            self.placeList.update({placeID: placeObject})

    def removePlace(self, placeObject):
        placeID = placeObject.getID()

        if placeID in self.placeList:
            self.placeList.pop(placeID)
        else:
            self.logger.log('Warning', str(placeObject.getAttribute('Name')) + ' is already associated with ' + str(self.getAttribute('Name')))
        
    ## Get Dictionary of values
    def getDict(self):
        returnDict = {self.getID(): {'Attributes': self.attributes,
                                     'Gender': self.gender,
                                     'Connections': {'Spouses': self.spouses,
                                                     'Father': self.parents['Father'],
                                                     'Mother': self.parents['Mother']},
                                     'Events': self.eventList,
                                     'Reign List': {}}}
        
        for r in self.reignList:
            returnDict[self.getID()]['Reign List'].update(self.reignList[r].getDict())
            
        return returnDict

    ## Get Dictionary of immutable characteristics
    def getStaticLabels(self):
        genderDict = {0: 'Man', 1: 'Woman'}
        return {'Gender': genderDict[self.gender],
                'Birth Date': self.getAttribute('Birth Date'),
                'Death Date': self.getAttribute('Death Date')}

######################################
###                                ###
###          Title Class           ###
###                                ###
######################################

## Required common fields and methods:
# id: unique 8 character string that defines a given person
# getName(): method that returns the name of the title
#    is the full realm title
# updateFreeInfo(): method that updates certain fields that use text boxes
#    applicable fields for Title:
#    - Realm Name
#    - Realm Title
#    - Male Ruler Title
#    - Female Ruler Title
# getDict(): method that returns a dictionary that defines this title, used when writing to output file

class Title(CustomObject):
    def __init__(self, logger, init_dict, titleID):
        attributes = ['Realm Name',  # The name of the realm the title refers to (e.g. Bavaria, Tirol, France, etc)
                      'Realm Title',  # The type of title (e.g. Duchy, County, Kingdom, etc)
                      'Male Ruler Title',  # How the male ruler is referred to, vis-à-vis their title (e.g. Duke, Count, King, etc)
                      'Female Ruler Title']  # How the female ruler is referred to, vis-à-vis their title (e.g. Duchess, Countess, Queen, etc)

        super().__init__(logger, 'Title', titleID, attributes)

        self.availableOrder = 1000
        
        if init_dict is None:
            self.isTitular = False
        else:
            for a in self.attributes:
                self.updateAttribute(a, init_dict['Attributes'][a])
            self.isTitular = init_dict['Titular']

            for e in init_dict['Events']:
                self.updateEvent(e, init_dict['Events'][e])

        self.setName()
        
        self.reignDict = {}  ## structure: {<reignID>: <reignObject>}
        
        ## For when the type of title changes (county to duchy, de jure to titular, etc.)
        self.predecessor = None
        self.successor = None
        
        self.orderReignList = []
        
        #self.logger.log('Code', 'Init: Created ' + self.getName() + ' title')

    def setName(self):
        self.name = self.getFullRealmTitle()

    ## Return a string of info to display for this person
    def getDisplayInfo(self):
        return self.getFullRealmTitle()

    def getFullRealmTitle(self):
        if self.isTitular:
            return 'Titular ' + self.getAttribute('Realm Title') + ' of ' + self.getAttribute('Realm Name')
        else:
            return self.getAttribute('Realm Title') + ' of ' + self.getAttribute('Realm Name')
    
    def getFullRulerTitle(self, gender):
        rulerTitle = ''
        if self.isTitular:
            rulerTitle = 'Titular '

        if gender == 0:
            return rulerTitle + self.getAttribute('Male Ruler Title') + ' of ' + self.getAttribute('Realm Name')
        elif gender == 1:
            return rulerTitle + self.getAttribute('Female Ruler Title') + ' of ' + self.getAttribute('Realm Name')
        else:
            self.logger.log('Error', str(gender) + ' is not a valid gender')
            return None
        
    def orderReigns(self):
        self.orderReignList = list(self.reignDict.keys())
        
        # Python program for implementation of Quicksort Sort
 
        # This function takes last element as pivot, places
        # the pivot element at its correct position in sorted
        # array, and places all smaller (smaller than pivot)
        # to left of pivot and all greater elements to right
        # of pivot
         
         
        def partition(arr, low, high):
            i = (low-1)         # index of smaller element
            pivot = self.reignDict[arr[high]].order    # pivot
         
            for j in range(low, high):
                # If current element is less than or equal to pivot
                if self.reignDict[arr[j]].order <= pivot:
                    # increment index of smaller element
                    i = i+1
                    arr[i], arr[j] = arr[j], arr[i]
         
            arr[i+1], arr[high] = arr[high], arr[i+1]
            
            return i + 1
         
        # The main function that implements QuickSort
        # arr[] --> Array to be sorted,
        # low  --> Starting index,
        # high  --> Ending index
         
        # Function to do Quick sort
         
        def quickSort(arr, low, high):
            if len(arr) == 1:
                return arr
            
            if low < high:
         
                # pi is partitioning index, arr[p] is now
                # at right place
                pi = partition(arr, low, high)
         
                # Separately sort elements before
                # partition and after partition
                quickSort(arr, low, pi-1)
                quickSort(arr, pi+1, high)
        
        quickSort(self.orderReignList, 0, len(self.orderReignList)-1)
        
    def addReign(self, reign):
        if isinstance(reign, Reign):
            self.reignDict.update({reign.getID(): reign})
            self.connection('Add', reign.getID(), 'Reign')

            reign.order = self.availableOrder
            self.availableOrder += 200
        else:
            self.logger.log('Error', 'Cannot add ' + str(reign) + ' to title ' + str(self.getName()) + '. Invalid type')
    
    def removeReign(self, reignID):
        if reignID in self.reignDict:
            self.reignDict.pop(reignID)
            self.connection('Remove', reignID)
        else:
            self.logger.log('Warning', 'Cannot remove {' + str(reignID) + '}; Not in dictionary of reigns')
            
    def getDict(self):
        return {self.getID(): {'Attributes': self.attributes,
                               'Titular': self.isTitular,
                               'Connections': {'Predecessor': self.predecessor,
                                               'Successor': self.successor},
                               'Events': self.eventList,
                               'Reign List': list(self.reignDict.keys())}}

######################################
###                                ###
###          Place Class           ###
###                                ###
######################################

## Required common fields and methods:
# id: unique 8 character string that defines a given person
# getName(): method that returns the name of the reign
#    is the associated person + the full ruler title of the associated title
# updateFreeInfo(): method that updates certain fields that use text boxes
#    applicable fields for Reign:
#    - Start Date
#    - End Date
# getDict(): method that returns a dictionary that defines this reign, used when writing to output file

class Place(CustomObject):
    def __init__(self, logger, init_dict, place_id):
        super().__init__(logger, 'Place', place_id, ['Name', 'Latitude', 'Longitude'])

        if init_dict is None:
            self.reignList = []

        else:
            for a in self.attributes:
                self.updateAttribute(a, init_dict['Attributes'][a])

            for e in init_dict['Events']:
                self.updateEvent(e, init_dict['Events'][e])

            self.reignList = init_dict['Reign List']
            for r in self.reignList:
                self.connection('Add', r, 'Reign')

        self.setName()

    def setName(self):
        self.name = self.getAttribute('Name') + ' Place'

    ## Return a string of info to display for this person
    def getDisplayInfo(self):
        return self.getAttribute('Name') + ' (' + self.getAttribute('Latitude') + ', ' + self.getAttribute('Longitude') + ')'

    def addReign(self, reign):
        reignID = self.check_argument(reign, 'Reign')

        if reignID is not None:
            if reignID in self.reignList:
                self.logger.log('Warning', '{' + reignID + '} already in list for {' + self.getID() + '}')
            else:
                self.reignList.append(reignID)
                self.connection('Add', reignID, 'Reign')

    def removeReign(self, reign):
        reignID = self.check_argument(reign, 'Reign')

        if reignID is not None:
            if reignID in self.reignList:
                self.reignList.remove(reignID)
                self.connection('Remove', reignID)
            else:
                self.logger.log('Warning', '{' + reignID + '} already in list for {' + self.getID() + '}')

    def hasReign(self, reign):
        reignID = self.check_argument(reign, 'Reign')

        if reignID in self.reignList:
            return True
        else:
            return False

    def addCoords(self, lat=None, long=None):
        if lat is not None:
            self.updateAttribute('Latitude', lat)

        if long is not None:
            self.updateAttribute('Longitude', long)

    def getCoords(self):
        return {self.getAttribute('Latitude'), self.getAttribute('Longitude')}

    def isEmpty(self):
        if self.name != '':
            return False
        elif self.lat != '':
            return False
        elif self.long != '':
            return False
        else:
            return True

    def getDict(self):
        return {self.getID(): {'Attributes': self.attributes,
                               'Events': self.eventList,
                               'Reign List': self.reignList}}

######################################
###                                ###
###          Reign Class           ###
###                                ###
######################################

## Required common fields and methods:
# id: unique 8 character string that defines a given person
# getName(): method that returns the name of the reign
#    is the associated person + the full ruler title of the associated title
# updateFreeInfo(): method that updates certain fields that use text boxes
#    applicable fields for Reign:
#    - Start Date
#    - End Date
# getDict(): method that returns a dictionary that defines this reign, used when writing to output file

class Reign(CustomObject):
    def __init__(self, logger, ruler, title, init_dict, reignID):
        attributes = ['Start Date',  # The start date of this reign
                      'End Date']  # The end date of this reign

        super().__init__(logger, 'Reign', reignID, attributes)

        self.connection('Add', ruler, 'Ruler')
        self.connection('Add', title, 'Title')

        ruler.addReign(self)
        title.addReign(self)

        self.isJunior = False  # Is this reign a junior to another reign
        self.isPrimary = False  # Is this reign the primary for the person

        self.order = -1  # The order of this reign in the title

        if init_dict is None:
            self.connections = {'Ruler': ruler,
                                'Title': title,
                                'Predecessor': None,
                                'Successor': None}

            self.mergedReigns = {'Senior': None,
                                 'Junior': []}

        else:
            for a in self.attributes:
                self.updateAttribute(a, init_dict['Attributes'][a])

            self.connections = {'Ruler': ruler,
                                'Title': title,
                                'Predecessor': init_dict['Connections']['Predecessor'],
                                'Successor': init_dict['Connections']['Successor']}

            for connectedReign in ('Predecessor', 'Successor'):
                if self.connections[connectedReign] is not None:
                    self.connection('Add', self.connections[connectedReign], connectedReign)

            self.mergedReigns = init_dict['Merged Reigns']

            if self.mergedReigns['Senior'] != -1 and self.mergedReigns['Senior'] is not None:
                self.isJunior = True

            self.isPrimary = init_dict['Is Primary']
            if self.isPrimary:
                self.connections['Ruler'].primary_title('Set', self.getConnectedReign('Title'))

        self.setName()

        self.placeList = {}  # List of places associated with this reign

    def setName(self):
        self.name = self.getConnectedReign('Ruler').getAttribute('Name') + ', ' + self.getConnectedReign('Title').getFullRulerTitle(self.getConnectedReign('Ruler').gender)

    ## Return a string of info to display for this person
    def getDisplayInfo(self):
        return self.getConnectedReign('Ruler').getAttribute('Name') + ' ' + self.getDateString()

    def setConnectedReign(self, target, connection):
        targetID = self.check_argument(target, connection)

        if connection in self.connections:
            self.connections.update({connection: targetID})
            self.connection('Add', targetID, connection)
        else:
            self.logger.log('Error', str(connection) + ' is not a valid connection to add for a reign')

    def getConnectedReign(self, connection):
        if connection in self.connections:
            return self.connections[connection]
        else:
            self.logger.log('Error', str(connection) + ' is not a valid connection for a reign')
            return None

    def removeConnectedReign(self, connection):
        if connection not in ('Predecessor', 'Successor'):
            self.logger.log('Error', str(connection) + ' is not a valid connection to remove from a reign')
        elif connection in self.connections:
            self.connections.update({connection: None})
            self.connection('Remove', self.getConnectedReign(connection))
        else:
            self.logger.log('Error', str(connection) + ' is not a valid connection for a reign')

    def hasConnectedReign(self, connection):
        if connection in self.connections:
            if self.connections[connection] is not None:
                return True
            else:
                return False
        else:
            self.logger.log('Error', str(connection) + ' is not a valid connection for a reign')
            return False

    def setPrimary(self, checked):
        self.isPrimary = checked
        ruler = self.getConnectedReign('Ruler')

        if checked:
            ruler.primary_title('Set', self.getConnectedReign('Title'))
        else:
            ruler.primary_title('Remove', self.getConnectedReign('Title'))
        
    def setDate(self, date, side):
        if side == 'Start Date':
            self.stDate = date
        else:
            self.endDate = date
    
    def setTitle(self, title):
        self.titleID = title.getID()
        self.titleName = title.getFullRealmTitle()

        self.updateAttribute('Name', self.rulerName + ', ' + self.titleName)
        
    ## The order of this reign for the associated title
    def setOrder(self, order):
        self.order = order
    
    ## Merge with <reign> by setting it as the <relation> in the relationship
    ## Expected relation values:
    # Senior
    # Junior
    
    ## Handling scenarios
    # Will not override senior reign appointment. Once the relationship is established, can only unmerge first
    # Will not have reigns as both senior/junior, cannot pick a junior reign as senior reign also
    
    def mergeReign(self, reign, relation):
        if relation == 'Senior':
            ## Set <reign> as this reign's senior
            self.mergedReigns[relation] = reign.getID()
            self.isJunior = True
            self.connection('Add', reign.getID(), 'Senior')
            
            self.mergedReigns['Junior'] = []  # Remove all junior reigns from the list
        elif relation == 'Junior':
            ## Add <reign> as a junior to this reign
            self.mergedReigns[relation].append(reign.getID())
            self.connection('Add', reign.getID(), 'Junior')
        else:
            self.logger.log('Error', str(relation) + ' is not a valid relation for merging reigns')

    def addPlace(self, placeObject):
        placeID = placeObject.getID()

        if placeID in self.placeList:
            self.logger.log('Warning', str(placeObject.getAttribute('Name')) + ' is already associated with ' + str(self.getAttribute('Name')))
        else:
            self.getConnectedReign('Ruler').addPlace(placeObject)
            self.placeList.update({placeID: placeObject})
            self.connection('Add', placeID, 'Place')

    def removePlace(self, placeObject):
        placeID = placeObject.getID()

        if placeID in self.placeList:
            self.getConnectedReign('Ruler').removePlace(placeObject)
            self.placeList.pop(placeID)
            self.connection('Remove', placeID)
        else:
            self.logger.log('Warning', str(placeObject.getAttribute('Name')) + ' is already associated with ' + str(self.getAttribute('Name')))

    def isEmpty(self):
        if self.titleID != '':
            return False
        elif self.titleName != '':
            return False
        elif self.predecessor != -1:
            return False
        elif self.successor != -1:
            return False
        elif self.stDate != '':
            return False
        elif self.endDate != '':
            return False
        else:
            return True
        
    def getDateString(self):
        return '(' + str(self.getAttribute('Start Date')) + ' - ' + str(self.getAttribute('End Date')) + ')'
        
    def getDict(self):    
        return {self.getID(): {'Attributes': self.attributes,
                               'Connections': {'Title': self.getConnectedReign('Title').getID(),
                                               'Predecessor': self.getConnectedReign('Predecessor'),
                                               'Successor': self.getConnectedReign('Successor')},
                               'Is Primary': self.isPrimary,
                               'Merged Reigns': self.mergedReigns}}

        
######################################
###                                ###
###      Custom Logger Class       ###
###                                ###
######################################

## A custom logger class for logging code, warnings, and errors
## Includes functionality to convert object IDs into their names

class Logger:
    def __init__(self, objectList):
        self.objectList = objectList

        self.logDict = {'Code': {'Pages': {}, 'Log': {}},
                        'Error': {'Pages': {}, 'Log': {}},
                        'Warning': {'Pages': {}, 'Log': {}}}

        self.page_key = '000_Init'

        self.writeLogs()
        
    ## Main method that stores information sent in <value>
    #        in the appropriate log, determined by <kind>
    #        and the appropriate location, determined by <key>
    
    ## Considering classes as three types: class, object, widget
    #    class: the logic and display of the application, facilitates the process. Method's super important
    #    object: custom way to store and manipulate data. Will have many instances, but similar processes'
    #    widget: custom way to display on the GUI. Always created as part of class method, only notable when activated
    #
    # Keys for each type of class
    #    :
    #    - classKey: describes the class object in which methods are called, no index used
    #    - methodKey: records when method is called and run, global index used
    #    object:
    #    - classKey: describes the generic object class, no index used
    #    - classInstance: describes the specific instance of the object, including method calls, no index used
    #    widget:
    #    - classKey: describes the underlying class for which 
    
    # <value> expected as String
    # <kind> expected as String with allowed values:
    #    - 'Code'
    #    - 'Warning'
    #    - 'Error'
    # <key> expected as String
    
    ## Key expectations (future enhancement for more generic expectations)
    #    key[0] is the class (class instance for objects)
    #    key[1] is the specific method called, or object instance
    
    ## Use curly brace wrappers to identify object IDs
    def log(self, kind, value):
        value = self.enhanceStringLinks(value)
                
        # Get the appropriate log dict
        if kind in self.logDict:
            codeLog = self.logDict['Code']['Log']
            sublog = self.logDict[kind]['Log']
            pages = self.logDict['Code']['Pages']
        else:
            sublog = {}
            pages = {}
            print(str(kind) + ' is not a valid log type')
            
        if self.page_key in pages:
            pages[self.page_key] += 1
            index = pages[self.page_key]

            if self.page_key in sublog:
                sublog[self.page_key].append(f'{index:03d}_' + value)
            else:
                sublog.update({self.page_key: [f'{index:03d}_' + value]})
        else:
            index = 0
            pages.update({self.page_key: index})

            sublog.update({self.page_key: [f'{index:03d}_' + value]})

        # Call writeLogs to write to external file  
        self.writeLogs()
        
    def enhanceStringLinks(self, value):
        if '{' in value: # Only replace IDs if there are actually IDs to replace
            idSplit = value.split('{')  # Split the value along curly braces
            value = idSplit[0]
            for objectID in idSplit[1:]:  # Iterate through list starting from 2nd value (first is before curly brace is found)
                after = objectID[objectID.find('}')+1:]  # Get string after curly braces for new value string
                objectID = objectID[:objectID.find('}')]  # Get objectID from characters up to closed curly brace
                                                          # need handling of no closed curly brace, too long/short id

                obj = None

                for o_key, o_list in self.objectList.items():
                    if objectID in o_list:
                        obj = o_list[objectID]  # Get object based on which list it's in

                if obj is not None:
                    value += obj.getName() + after  # Replace object ID with associated object name
                else:
                    print('Could not enhance ' + str(objectID) + '. ID not found in object lists')
                    value += str(objectID) + after
                
        return value
    
    def writeLogs(self):
        for k in self.logDict:
            with open(os.path.join(get_parent_path(), 'Logs/' + k.lower() + '_log.json'), 'w') as outfile:
                json.dump(self.logDict[k]['Log'], outfile, indent=4)
