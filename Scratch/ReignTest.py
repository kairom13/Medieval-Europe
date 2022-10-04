
from Medieval_Europe.Code.CustomObjects import Reign, Person, Title, Logger
import pandas as pd

# 6 reigns:
# pre one: X
# pre two: Y
# suc one: A
# suc two: B
# junior: J
# senior: S

objectLists = {'Person': {},
               'Title': {},
               'Reign': {},
               'Place': {}}

logger = Logger(objectLists, True)

objectLists['Title'].update({'SeniorTitle': Title(logger, None, 'SeniorTitle')})
objectLists['Title'].update({'JuniorTitle': Title(logger, None, 'JuniorTitle')})
objectLists['Title'].update({'2ndJunTitle': Title(logger, None, '2ndJunTitle')})
objectLists['Title'].update({'2ndSenTitle': Title(logger, None, '2ndSenTitle')})


def createPerson(index, personType):
    if personType != 'None':
        key = personType + f'{index:03d}'
        if key not in objectLists['Person']:
            objectLists['Person'].update({key: Person(logger, 1, None, key)})
        return key
    return None


people_types = {'Predecessor': [None, 'X', 'Y'],
                'Successor': [None, 'A', 'B']}

connections = ['Predecessor', 'Successor', 'Main']
levels = ['Senior', 'Junior']

oppConnect = {'Predecessor': 'Successor',
              'Successor': 'Predecessor'}

delim = '_'

output = []
cats = []

for lev in levels:
    for c in connections[:-1]:
            cats.append(lev + delim + c)

def getTestCaseDict():
    testCaseDict = {}
    for lev in levels:
        testCaseDict.update({lev: {}})
        for c in connections:
            testCaseDict[lev].update({c: ''})

    return testCaseDict


index = 0
testCaseList = []

def createTestCase(cases, index, xtraJun, xtraSen):
    cases = cases.split(',')

    testCasePeople = getTestCaseDict()

    for case in cases:
        vals = case.split(delim)
        testCasePeople[vals[0]].update({vals[1]: createPerson(index, vals[2])})

    mainKey = createPerson(index, 'M')
    testCasePeople['Junior'].update({'Main': mainKey})
    testCasePeople['Senior'].update({'Main': mainKey})

    testCases = {'Senior': None,
                 'Junior': None,
                 '2ndJunior': None,
                 '2ndSenior': None}

    for lev in testCasePeople:
        testCaseDict = testCasePeople[lev]
        mainReign = Reign(logger, objectLists['Person'][testCaseDict['Main']], objectLists['Title'][lev + 'Title'], None, None)
        objectLists['Reign'].update({mainReign.getID(): mainReign})

        if lev == 'Junior' and xtraJun:
            secJuniorReign = Reign(logger, objectLists['Person'][testCaseDict['Main']], objectLists['Title']['2ndJunTitle'], None, None)
            objectLists['Reign'].update({secJuniorReign.getID(): secJuniorReign})

            testCases.update({'2ndJunior': secJuniorReign})

        if lev == 'Senior' and xtraSen:
            secSeniorReign = Reign(logger, objectLists['Person'][testCaseDict['Main']], objectLists['Title']['2ndSenTitle'], None, None)
            objectLists['Reign'].update({secSeniorReign.getID(): secSeniorReign})

            testCases.update({'2ndSenior': secSeniorReign})

        for connect in testCaseDict:
            if connect != 'Main' and testCaseDict[connect] is not None:
                reign = Reign(logger, objectLists['Person'][testCaseDict[connect]], objectLists['Title'][lev + 'Title'], None, None)
                objectLists['Reign'].update({reign.getID(): reign})

                mainReign.setConnection(reign.getID(), connect)
                reign.setConnection(mainReign.getID(), oppConnect[connect])

                if lev == 'Junior' and xtraJun:
                    secReign = Reign(logger, objectLists['Person'][testCaseDict[connect]], objectLists['Title']['2ndJunTitle'], None, None)
                    objectLists['Reign'].update({secReign.getID(): secReign})

                    secJuniorReign.setConnection(secReign.getID(), connect)
                    secReign.setConnection(secJuniorReign.getID(), oppConnect[connect])

                if lev == 'Senior' and xtraSen:
                    secReign = Reign(logger, objectLists['Person'][testCaseDict[connect]], objectLists['Title']['2ndSenTitle'], None, None)
                    objectLists['Reign'].update({secReign.getID(): secReign})

                    secSeniorReign.setConnection(secReign.getID(), connect)
                    secReign.setConnection(secSeniorReign.getID(), oppConnect[connect])

        testCases.update({lev: mainReign})

    if xtraJun:
        testCases['Junior'].mergeReign(testCases['2ndJunior'], 'Junior')
        testCases['2ndJunior'].mergeReign(testCases['Junior'], 'Senior')

    if xtraSen:
        testCases['Senior'].mergeReign(testCases['2ndSenior'], 'Junior')
        testCases['2ndSenior'].mergeReign(testCases['Senior'], 'Senior')

    return testCases


def recursiveFunction(key, catList, axes):
    if len(axes) == 0:
        for j in range(2):
            for s in range(2):
                testCaseList.append(createTestCase(key[:-1], len(testCaseList), j, s))

    else:
        axis = axes[0]
        for cat in catList[axis[axis.index(delim) + 1:]]:
            recursiveFunction(key + str(axis) + '_' + str(cat) + ',', catList, axes[1:])


recursiveFunction('', people_types, cats)

testingDict = {'Junior Pre': [],
               'Senior Pre': [],
               'Junior Suc': [],
               'Senior Suc': [],
               '2nd Junior': [],
               '2nd Senior': [],
               'Merge Flag': [],
               'Pre Equal': [],
               'Suc Equal': [],
               'Senior Check': [],
               'Junior Check': [],
               '2nd Junior Check': [],
               '2nd Senior Check': [],
               'Consistent Person': [],
               'Good Connections': [],
               'Overall Check': []}


def isEqual(reignOne, reignTwo):
    if reignOne is None or reignTwo is None:
        return reignOne == reignTwo
    else:
        if isinstance(reignOne, str):
            reignOne = objectLists['Reign'][reignOne]
        if isinstance(reignTwo, str):
            reignTwo = objectLists['Reign'][reignTwo]

        personOne = reignOne.getConnection('Person')
        personTwo = reignTwo.getConnection('Person')
        return personOne == personTwo


def getReignName(reignID):
    if isinstance(reignID, str):
        reign = objectLists['Reign'][reignID]
        ruler = reign.getConnection('Person')
        title = reign.getConnection('Title')
        return ruler.getID() + '_' + title.getID()

    return 'None'


print('|\t\t\t\t\t\t\tPredecessor Reign\t\t\t\t\t\t\t|\t\t\t\t\t\t\t\tMain Reign\t\t\t\t\t\t\t\t|\t\t\t\t\t\t\tSuccessor Reign\t\t\t\t\t\t\t\t|')
print('')

count = 0
for case in testCaseList:
    # for i in case:
    #     caseObject = case[i]
    #     if caseObject is not None:
    #         print(i + ': ' + getReignName(caseObject.getID()))
    #     else:
    #         print(i + ': None')

    juniorReign = case['Junior']
    seniorReign = case['Senior']

    juniorPre = juniorReign.getConnection('Predecessor')
    juniorSuc = juniorReign.getConnection('Successor')

    seniorPre = seniorReign.getConnection('Predecessor')
    seniorSuc = seniorReign.getConnection('Successor')

    preBad = juniorPre is not None and seniorPre is not None and not isEqual(juniorPre, seniorPre)
    sucBad = juniorSuc is not None and seniorSuc is not None and not isEqual(juniorSuc, seniorSuc)
    mergeFlag = not (preBad or sucBad)

    openPre = mergeFlag and (juniorPre is not None or seniorPre is not None)
    openSuc = mergeFlag and (juniorSuc is not None or seniorSuc is not None)

    if juniorPre is None:
        testingDict['Junior Pre'].append(None)
    else:
        reign = objectLists['Reign'][juniorPre]
        testingDict['Junior Pre'].append(reign.getConnection('Person').getID())

    if juniorSuc is None:
        testingDict['Junior Suc'].append(None)
    else:
        reign = objectLists['Reign'][juniorSuc]
        testingDict['Junior Suc'].append(reign.getConnection('Person').getID())

    if seniorPre is None:
        testingDict['Senior Pre'].append(None)
    else:
        reign = objectLists['Reign'][seniorPre]
        testingDict['Senior Pre'].append(reign.getConnection('Person').getID())

    if seniorSuc is None:
        testingDict['Senior Suc'].append(None)
    else:
        reign = objectLists['Reign'][seniorSuc]
        testingDict['Senior Suc'].append(reign.getConnection('Person').getID())

    testingDict['2nd Junior'].append(bool(len(juniorReign.mergedReigns['Junior'])))
    testingDict['2nd Senior'].append(bool(len(seniorReign.mergedReigns['Junior'])))

    testingDict['Merge Flag'].append(mergeFlag)
    testingDict['Pre Equal'].append(openPre)
    testingDict['Suc Equal'].append(openSuc)

    actions = []

    if mergeFlag:
        actions.append('Merge')

        prevJuniors = []
        for j in seniorReign.mergedReigns['Junior']:
            prevJuniors.append(j)

        seniorReign.mergeReign(juniorReign, 'Junior')
        juniorReign.transferJuniorReigns(objectLists['Reign'], seniorReign)
        juniorReign.mergeReign(seniorReign, 'Senior')

        if openPre:
            if juniorPre is None:
                actions.append('Set junior predecessor as ' + getReignName(seniorPre))

                SPObject = objectLists['Reign'][seniorPre]
                for j in seniorReign.mergedReigns['Junior']:
                    if j not in prevJuniors:
                        junReign = objectLists['Reign'][j]
                        newJuniorPre = Reign(logger, SPObject.getConnection('Person'), junReign.getConnection('Title'), None, None)
                        objectLists['Reign'].update({newJuniorPre.getID(): newJuniorPre})

                        junReign.setConnection(newJuniorPre, 'Predecessor')
                        newJuniorPre.setConnection(junReign, 'Successor')

                actions.append("Propagate")

            if seniorPre is None:
                actions.append('Set senior predecessor as ' + getReignName(juniorPre))

                JPObject = objectLists['Reign'][juniorPre]
                newSeniorPre = Reign(logger, JPObject.getConnection('Person'), seniorReign.getConnection('Title'), None, None)
                objectLists['Reign'].update({newSeniorPre.getID(): newSeniorPre})

                seniorReign.setConnection(newSeniorPre, 'Predecessor')
                newSeniorPre.setConnection(seniorReign, 'Successor')

                for j in seniorReign.mergedReigns['Junior']:
                    if j in prevJuniors:
                        junReign = objectLists['Reign'][j]
                        newSeniorPre = Reign(logger, JPObject.getConnection('Person'), junReign.getConnection('Title'), None, None)
                        objectLists['Reign'].update({newSeniorPre.getID(): newSeniorPre})

                        junReign.setConnection(newSeniorPre, 'Predecessor')
                        newSeniorPre.setConnection(junReign, 'Successor')

        if openSuc:
            if juniorSuc is None:
                actions.append('Set junior successor as ' + getReignName(seniorSuc))

                SSObject = objectLists['Reign'][seniorSuc]
                for j in seniorReign.mergedReigns['Junior']:
                    if j not in prevJuniors:
                        junReign = objectLists['Reign'][j]
                        newJuniorSuc = Reign(logger, SSObject.getConnection('Person'), junReign.getConnection('Title'), None, None)
                        objectLists['Reign'].update({newJuniorSuc.getID(): newJuniorSuc})

                        junReign.setConnection(newJuniorSuc, 'Successor')
                        newJuniorSuc.setConnection(junReign, 'Predecessor')

                actions.append("Propagate")

            if seniorSuc is None:
                actions.append('Set senior successor as ' + getReignName(juniorSuc))

                JSObject = objectLists['Reign'][juniorSuc]
                newSeniorSuc = Reign(logger, JSObject.getConnection('Person'), seniorReign.getConnection('Title'), None, None)
                objectLists['Reign'].update({newSeniorSuc.getID(): newSeniorSuc})

                seniorReign.setConnection(newSeniorSuc, 'Successor')
                newSeniorSuc.setConnection(seniorReign, 'Predecessor')

                for j in seniorReign.mergedReigns['Junior']:
                    if j in prevJuniors:
                        junReign = objectLists['Reign'][j]
                        newSeniorSuc = Reign(logger, JSObject.getConnection('Person'), junReign.getConnection('Title'), None, None)
                        objectLists['Reign'].update({newSeniorSuc.getID(): newSeniorSuc})

                        junReign.setConnection(newSeniorSuc, 'Successor')
                        newSeniorSuc.setConnection(junReign, 'Predecessor')


    def getReignTitle(reignID):
        if isinstance(reignID, str):
            reign = objectLists['Reign'][reignID]
            title = reign.getConnection('Title')
            return title.getID()

        return 'None'


    ## Check that all senior reigns have the same title
    # Senior reign
    # Senior predecessor
    # SP successor
    # Senior successor
    # SS predecessor


    def checkTitleConsistency(reignID):
        reign = objectLists['Reign'][reignID]
        reign_check = [getReignTitle(reignID)]

        if reign.hasConnection('Predecessor'):
            PreObject = objectLists['Reign'][reign.getConnection('Predecessor')]
            reign_check.append(getReignTitle(PreObject.getID()))
            reign_check.append(getReignTitle(PreObject.getConnection('Successor')))

        if reign.hasConnection('Successor'):
            SucObject = objectLists['Reign'][reign.getConnection('Successor')]
            reign_check.append(getReignTitle(SucObject.getID()))
            reign_check.append(getReignTitle(SucObject.getConnection('Predecessor')))

        return len(set(reign_check)) == 1


    testingDict['Senior Check'].append(checkTitleConsistency(seniorReign.getID()))

    jrDict = {'JuniorTitle': ['Junior Check', ''],
              '2ndJunTitle': ['2nd Junior Check', ''],
              '2ndSenTitle': ['2nd Senior Check', '']}

    for j in seniorReign.mergedReigns['Junior']:
        givenDict = jrDict[getReignTitle(j)]
        givenDict[1] = checkTitleConsistency(j)

    for j in jrDict:
        givenDict = jrDict[j]
        testingDict[givenDict[0]].append(givenDict[1])

    checkDict = {'Predecessor': {'Pre': [], 'Main': [], 'Suc': []},
                 'Main': {'Pre': [], 'Main': [], 'Suc': []},
                 'Successor': {'Pre': [], 'Main': [], 'Suc': []}}

    def displayReign(reignID, section):
        if reignID is not None:
            reignObject = objectLists['Reign'][reignID]

            if reignObject.hasConnection('Predecessor'):
                pre_id = getReignName(reignObject.getConnection('Predecessor'))
                checkDict[section]['Pre'].append(pre_id[:pre_id.index('_')])
            else:
                pre_id = '\t\t\t\t'
                checkDict[section]['Pre'].append('')

            main_id = getReignName(reignID)
            checkDict[section]['Main'].append(main_id[:main_id.index('_')])

            if reignObject.hasConnection('Successor'):
                suc_id = getReignName(reignObject.getConnection('Successor'))
                checkDict[section]['Suc'].append(suc_id[:suc_id.index('_')])
            else:
                suc_id = '\t\t\t\t'
                checkDict[section]['Suc'].append('')

            return pre_id + '\t<\t' + main_id + '\t>\t' + suc_id
        else:
            checkDict[section]['Pre'].append('')
            checkDict[section]['Main'].append('')
            checkDict[section]['Suc'].append('')
            return '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t'


    print(str(count) + ': ' + str(actions))
    print('|\t' + displayReign(seniorReign.getConnection('Predecessor'), 'Predecessor') + '\t|\t' + displayReign(seniorReign.getID(), 'Main') + '\t|\t' + displayReign(seniorReign.getConnection('Successor'), 'Successor') + '\t|')

    for j in seniorReign.mergedReigns['Junior']:
        juniorObject = objectLists['Reign'][j]
        print('|\t' + displayReign(juniorObject.getConnection('Predecessor'), 'Predecessor') + '\t|\t' + displayReign(juniorObject.getID(), 'Main') + '\t|\t' + displayReign(juniorObject.getConnection('Successor'), 'Successor') + '\t|')

    consistentPersonList = []
    for cd in checkDict:
        for sub in checkDict[cd]:
            consistentPersonList.append(len(set(checkDict[cd][sub])) == 1)

    testingDict['Consistent Person'].append(len(set(consistentPersonList)) == 1)

    checkList = [True]
    if checkDict['Predecessor']['Main'][0] != '':
        checkList.append(checkDict['Predecessor']['Main'][0] == checkDict['Main']['Pre'][0])
        checkList.append(checkDict['Predecessor']['Suc'][0] == checkDict['Main']['Main'][0])
    if checkDict['Successor']['Main'][0] != '':
        checkList.append(checkDict['Successor']['Main'][0] == checkDict['Main']['Suc'][0])
        checkList.append(checkDict['Successor']['Pre'][0] == checkDict['Main']['Main'][0])

    testingDict['Good Connections'].append(len(set(checkList)) == 1)

    overall_check = []
    overall_check.append(testingDict['Senior Check'][-1])
    if testingDict['Junior Check'][-1] != '':
        overall_check.append(testingDict['Junior Check'][-1])
    if testingDict['2nd Junior Check'][-1] != '':
        overall_check.append(testingDict['2nd Junior Check'][-1])
    if testingDict['2nd Senior Check'][-1] != '':
        overall_check.append(testingDict['2nd Senior Check'][-1])
    overall_check.append(testingDict['Consistent Person'][-1])
    overall_check.append(testingDict['Good Connections'][-1])

    testingDict['Overall Check'].append(len(set(overall_check)) == 1)

    print('')
    count += 1

print('OVERALL CHECK FOR ALL TEST CASES: ' + str(len(set(testingDict['Overall Check'])) == 1))

df = pd.DataFrame(testingDict)
df.to_csv('test_cases.csv', index_label='case')
