"""
Created on Aug 1, 2022

@author: kairom13
"""

from Medieval_Europe.Code.CustomObjects import Reign, Person, Place
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class ObjectButton(QPushButton):
    def __init__(self, parameters):
        super(ObjectButton, self).__init__(parameters['Page Type'])

        self.window = parameters['Window']
        self.classKey = 'Object Button'
        self.logger = self.window.logger

        self.subject = parameters['Subject']
        self.objectType = parameters['Object Type']
        self.pageType = parameters['Page Type']

        self.checkedPlace = True

        if 'Spouse' in parameters:
            self.spouseChoice = parameters['Spouse']
        else:
            self.spouseChoice = None

        if self.pageType == 'Choose':
            self.target = parameters['Target']
            self.connection = parameters['Connection']

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            if self.pageType == 'View':
                self.logger.log('Code', 'Clicked to view ' + str(self.subject.getName()))
                if self.objectType == 'Person':
                    self.window.page_factory('display_person_page', {'Person': self.subject})
                elif self.objectType == 'Title':
                    self.window.page_factory('display_title_page', {'Title': self.subject, 'Page Type': 'View'})
                elif self.objectType == 'Place':
                    self.window.page_factory('display_place_page', {'Place': self.subject})
                else:
                    self.logger.log('Error', str(self.objectType) + ' is not a valid object type to view')

            elif self.pageType == 'Choose':
                self.logger.log('Code', 'Clicked to choose {' + str(self.target.getID()) + '} as ' + str(self.connection) + ' for {' + str(self.subject.getID()) + '}')

                spouse = None
                if self.spouseChoice is not None:
                    spouse = self.spouseChoice.getSelectedSpouse()
                    print('Choosing: ' + str(spouse))

                self.window.add_connection(self.subject, self.connection, self.target, spouse)

                # When setting predecessor or successor, transfer any places, if desired
                if self.checkedPlace and self.connection in ('Predecessor', 'Successor'):
                    self.logger.log('Code', 'Transferring places to {' + str(self.target.getID()) + '}')
                    # Transfer all the places in the subject reign to the target reign
                    count = 0

                    for p, place in self.subject.placeList.items():
                        if p not in self.target.placeList:
                            self.target.addPlace(place)
                            place.addReign(self.target)

                            count += 1

                    # Transfer all the places in the subject's junior reigns to the equivalent in the target reign
                    for prev_j in self.subject.mergedReigns['Junior']:
                        sub_j = self.window.get_object(prev_j)  # Get the object of the junior reign
                        tar_j = self.window.get_object(sub_j.getConnectedReign(self.connection))  # Get the target object
                        for p, place in sub_j.placeList.items():
                            if p not in tar_j.placeList:
                                tar_j.addPlace(place)
                                place.addReign(tar_j)

                                count += 1

                    # Do the same transfers from target to subject
                    for p, place in self.target.placeList.items():
                        if p not in self.subject.placeList:
                            self.subject.addPlace(place)
                            place.addReign(self.subject)

                            count += 1

                    if self.connection == 'Predecessor':
                        new_con = 'Successor'
                    else:
                        new_con = 'Predecessor'

                    # Transfer all the places in the target's junior reigns to the equivalent in the subject reign
                    for prev_j in self.target.mergedReigns['Junior']:
                        sub_j = self.window.get_object(prev_j)  # Get the object of the junior reign
                        tar_j = self.window.get_object(sub_j.getConnectedReign(new_con))  # Get the target object
                        for p, place in sub_j.placeList.items():
                            if p not in tar_j.placeList:
                                tar_j.addPlace(place)
                                place.addReign(tar_j)

                                count += 1

                    self.logger.log('Code', 'Transferred ' + str(count) + ' places')

                person = None
                place = None

                if isinstance(self.subject, Reign):
                    person = self.subject.getConnectedReign('Ruler')
                elif isinstance(self.subject, Person):
                    person = self.subject
                elif isinstance(self.subject, Place):
                    place = self.subject
                else:
                    self.logger.log('Error', str(self.subject) + ' is not a valid object to get person or place from')

                if person is not None:
                    self.window.page_factory('edit_person_page', {'Person': person})

                if self.connection == 'Reign' and isinstance(self.target, Reign):
                    self.window.page_factory('edit_place_page', {'Place': place})

            else:
                self.logger.log('Error', str(self.pageType) + ' is not a valid page type')

            return True
        return False


## Button to remove relative in edit screen
class RemoveConnectionButton(QPushButton):
    def __init__(self, window, subject, target):
        super(RemoveConnectionButton, self).__init__('Remove')

        self.window = window
        self.subject = subject  # The subject who is losing a connection
        self.target = target  # The target who is also losing a connection

        self.connection = self.subject.connection('Get', self.target)

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            if self.connection == 'Spouse':
                self.subject.removeSpouse(self.target)
                self.target.removeSpouse(self.subject)
                self.window.page_factory('edit_person_page', {'Person': self.subject})

            elif self.connection in ('Mother', 'Father'):
                self.subject.removeParent(self.connection)
                s = self.target.removeChild(self.subject)

                if s != 'unknown_spouse':
                    spouse = self.window.get_object(s)
                    spouse.removeChild(self.target)
                    spouse.addChild(self.target, None)

                self.window.page_factory('edit_person_page', {'Person': self.subject})

            elif self.connection == 'Child':
                childObject = self.window.get_object(self.target.getID())

                if self.subject.gender == 0:
                    childObject.removeParent('Father')
                    if childObject.mother is not None:
                        motherObject = self.window.get_object(childObject.mother)
                        motherObject.removeChild(childObject)
                        motherObject.addChild(childObject, None)
                else:
                    childObject.removeParent('Mother')
                    if childObject.father is not None:
                        fatherObject = self.window.get_object(childObject.father)
                        fatherObject.removeChild(childObject)
                        fatherObject.addChild(childObject, None)

                self.subject.removeChild(self.target.getID())

                self.window.page_factory('edit_person_page', {'Person': self.subject})

            elif self.connection in ('Predecessor', 'Successor'):
                if self.connection == 'Predecessor':
                    opp_connection = 'Successor'
                else:
                    opp_connection = 'Predecessor'

                # Self.subject is the reign
                # Self.target is the connected reign to be removed
                self.subject.removeConnectedReign(self.connection)  # Remove the target reign as connection to the subject reign
                self.target.removeConnectedReign(opp_connection)  # Remove the subject reign as the opposite connection to the target reign

                # Get the person of the subject reign to return to
                person = self.subject.getConnectedReign('Ruler')
                self.window.page_factory('edit_person_page', {'Person': person})

            else:
                print(str(self.connection) + ' is not a valid relation for removal')

            return True
        return False


class UnmergeButton(QPushButton):
    def __init__(self, window, juniorReign):
        super(UnmergeButton, self).__init__('Unmerge')

        self.window = window
        self.juniorReign = juniorReign
        self.seniorReign = juniorReign.mergedReigns['Senior']
        self.person = juniorReign.getConnectedReign('Ruler')

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.juniorReign.mergedReigns['Senior'] = -1
            self.juniorReign.isJunior = False

            self.seniorReign.mergedReigns['Junior'].remove(self.juniorReign.getID())

            self.window.page_factory('edit_person_page', {'Person': self.person})

            return True
        return False


class SwitchGenderButton(QPushButton):
    def __init__(self, window, logger, person):
        super(SwitchGenderButton, self).__init__('Switch')

        self.window = window
        self.logger = logger
        self.classKey = 'Activated Widget'

        self.person = person

        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonRelease:
            self.logger.log('Code', self.person.getName() + ' is switching gender')
            self.person.gender = 1 - self.person.gender

            self.window.write_data()
            self.window.page_factory('edit_person_page', {'Person': self.person})
            return True
        return False
