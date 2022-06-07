# Brad Barakat
# ITP 499, Spring 2021
# This program will make an updated inventory file using an old inventory file and a changes file, but without a GUI

import datetime
import numpy
import matplotlib.pyplot as plt

def numFormat(x, zeroOrOne = 0, line = ""):
    if isinstance(x, str):
        x = x.strip()
    try:
        if int(x) == float(x):
            return int(x)
        else:
            return float(x)
    except:
        if zeroOrOne == 1:
            print("Error: The following line lacks a number:", line)
        return 0

def noMults(x,LI,LN):
    print("Adding the multiple entries of", x)
    total = 0
    while x in LI:
        y = LI.index(x)
        total += numFormat(LN[y])
        LI.pop(y)
        LN.pop(y)
    LI.append(x)
    LN.append(total)

def verFile(x):
    try:
        f = open(x, "r")
        f.close()
        y = 1
    except:
        print("That file does not exist!")
        y = 0
    return y

def getFileName(typeOfFile):
    x = input("Enter the name of the " + typeOfFile + " file: ")
    # Output file won't exist, so don't run verification loop for it
    if (typeOfFile.lower() == "inventory" or typeOfFile.lower() == "changes"):
        y = 0
    else: # typeOfFile.lower() == "output"
        y = 1
    while not y:
        y = verFile(x) # Verifies existence of input file
        if not y:
            x = input("Enter the name of the " + typeOfFile + " file: ")
    return x

def readFile(inputFileName):
    contents = []
    inputFile = open(inputFileName, "r")
    for line in inputFile:
        line = line.strip()
        if line.title() == "Change Log":
            contents.append(line.title())
        elif not (line[0:2] == "//" or line == ""):
            contents.append(line.title())
    inputFile.close()
    return contents

def writeFile(lines, outputFileName):
    outputFile = open(outputFileName, "w")
    print("//Item, Quantity", file=outputFile, end="\n")
    for line in lines:
        print(line, file=outputFile, end="\n")
    outputFile.close()

def isolateChangeLog(invFileContents):
    x = invFileContents.count("Change Log")
    if x > 1:
        print("Error: There cannot be more than one Change Log.")
    try:
        y = invFileContents.index("Change Log")
        return [invFileContents[:y], invFileContents[y:]]
    except:
        return [invFileContents, []]

def separateLists(contents):
    item = []
    number = []
    for i in contents:
        pair = i.strip().split(",")
        while len(pair) > 2:
            pair = [",".join(pair[:2])] + pair[2:]
        if len(pair) == 1:
            print("Error: The following line lacks a number:", i.strip())
            pair.append("(Error: No number)")
        elif pair[1].replace(" ","").lower() == "removed":
            pair[1] = "Removed"
        else:
            pair[1] = numFormat(pair[1].replace(" ",""), 1, i.strip())
        pair[0] = pair[0].strip().title()
        item.append(pair[0])
        number.append(pair[1])
    for entry in item:
        i = item.index(entry)
        x = item.count(entry)
        if x > 1:
            noMults(entry, item, number)
    contents.clear() # Cleaning up the original
    for i in range(0,len(item)):
        try:
            if number[i] >= 0:
                numC = "+ " + str(number[i])
            else:
                numC = "- " + str(number[i])[1:]
        except:
            numC = number[i]
        contents.append(item[i] + ", " + numC)
    return [item, number]

def updateFile(invItem, invNum, chaItem, chaNum, chaFileContents, logContents):
    newInvItem = invItem
    newInvNum = invNum
    newContents = []
    for item in chaItem:
        i = chaItem.index(item)
        x = newInvItem.count(item)
        if x == 0:
            if not chaNum[i] == "Removed":
                newInvItem.append(item)
                newInvNum.append(chaNum[i])
                if numFormat(newInvNum[-1]) < 0: # Because it is appended, the index will be -1
                    print("Warning: Amount for", newInvItem[-1], "will become negative.")
        else:
            if x > 1:
                # This somehow bypassed the separateLists function
                noMults(item, newInvItem, newInvNum)
            y = newInvItem.index(item)
            if chaNum[i] == "Removed":
                newInvItem.pop(y)
                newInvNum.pop(y)
            else:
                newInvNum[y] += numFormat(chaNum[i])
                if newInvNum[y] < 0:
                    print("Warning: Amount for", newInvItem[y], "will become negative.")
    # Replaces the old invItem and invNumber lists for a future function (they aren't needed anymore)
    invItem = newInvItem
    invNum = newInvNum
    # Combines the items and numbers
    for i in range(0,len(invItem)):
        newContents.append(", ".join([invItem[i], str(invNum[i])]))
    if len(logContents) == 0:
        newContents.append("\nChange Log")
    else:
        newContents.append("")
        newContents += logContents
    d = datetime.datetime.now()
    dForm = str(d.strftime("%m")) + "/" + str(d.strftime("%d")) + "/" + str(d.strftime("%Y"))
    newContents.append(dForm)
    newContents.append("; ".join(chaFileContents))
    return newContents

def compareNames(D):
    toRemove = []
    itemSet = set()
    k = list(D.keys())
    for key in k[:-1]:
        for i in range(0,len(D[key][0])):
            if D[key][0][i] in toRemove:
                toRemove.remove(D[key][0][i])
            if D[key][1][i] == "Removed":
                toRemove.append(D[key][0][i])
    for key in D:
        i = 0
        m = len(D[key][0])
        while i < m:
            if D[key][0][i] in toRemove:
                D[key][0].pop(i)
                D[key][1].pop(i)
                m = len(D[key][0])
            else:
                i += 1
    for key in k[:-1]:
        for i in range(0,len(D[key][0])):
            itemSet.add(D[key][0][i])
    D2 = {}
    for key in D:
        D2Vals = []
        for item in itemSet:
            if item in D[key][0]:
                i = D[key][0].index(item)
                D2Vals.append(D[key][1][i])
            else:
                D2Vals.append(0)
            D2[key] = [list(itemSet), D2Vals]
    return D2

def genPoints(logContents, chaItem, chaNum, invItem, invNum):
    formLog = {}
    series = {}
    logItem = []
    logNum = []
    i = 0
    if len(logContents) > 0:
        for item in logContents:
            if item.count(",") > 0:
                formLog[i] = item.strip()
                i += 1
    if len(formLog) > 0:
        for key in formLog:
            formLog[key] = formLog[key].split(";")
            formLog[key] = separateLists(formLog[key])
    while "(Error: No number)" in chaNum:
        x = chaNum.index("(Error: No number)")
        chaNum.pop(x)
        chaItem.pop(x)
    formLog[i] = [chaItem, chaNum]
    while "(Error: No number)" in invNum:
        x = invNum.index("(Error: No number)")
        invNum[x] = 0
    formLog[i+1] = [invItem, invNum]
    pList = compareNames(formLog)
    for j in range(len(pList)-2, -1, -1):
        if "Removed" in pList[j][1]:
            x = pList[j][1].index("Removed")
            for k in range(0, j+1):
                pList[k][1][x] = 0
        v1 = numpy.array(pList[j][1])
        v2 = numpy.array(pList[j+1][1])
        v = v2-v1
        pList[j][1] = list(v)
    for j in range(0,len(pList[0][0])):
        allVals = []
        allLabels = []
        for k in range(0,len(pList)):
            allVals.append(pList[k][1][j])
            allLabels.append(str(k))
        series[j] = [pList[0][0][j], allLabels, allVals]
    return series

def genGraphs(series):
    for i in range(0,len(series)):
        plt.figure(i+1)
        plt.title(series[i][0])
        plt.plot(series[i][1], series[i][2], "b")
    plt.show()

def main():
    invFileName = getFileName("inventory")
    chaFileName = getFileName("changes")
    outputFileName = getFileName("output")
    invFileContents = readFile(invFileName)
    [invFileContents,logContents] = isolateChangeLog(invFileContents)
    chaFileContents = readFile(chaFileName)
    [invItem, invNum] = separateLists(invFileContents)
    [chaItem, chaNum] = separateLists(chaFileContents)
    fileContents = updateFile(invItem, invNum, chaItem, chaNum, chaFileContents, logContents)
    writeFile(fileContents, outputFileName)
    series = genPoints(logContents, chaItem, chaNum, invItem, invNum)
    genGraphs(series)
    print("Inventory has been updated, and graphs have been made.")

main()
