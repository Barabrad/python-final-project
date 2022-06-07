# Brad Barakat
# ITP 499, Spring 2021
# This program will make an updated inventory file using an old inventory file and a changes file

import datetime
import numpy
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox

def numFormat(x, popupText, zeroOrOne = 0, line = ""):
    if isinstance(x, str):
        x = x.strip()
    try:
        if int(x) == float(x):
            return int(x)
        else:
            return float(x)
    except:
        if zeroOrOne == 1:
            warning = "The following line lacks a number: " + str(line)
            messagebox.showwarning("Input File Error", warning)
            popupText.append("Input File Error: " + warning)
        return 0

def noMults(x, popupText, LI, LN):
    warning = "Adding the multiple entries of " + str(x)
    messagebox.warning("Duplicates", warning)
    popupText.append("Duplicates: " + warning)
    total = 0
    while x in LI:
        y = LI.index(x)
        total += numFormat(LN[y], popupText)
        LI.pop(y)
        LN.pop(y)
    LI.append(x)
    LN.append(total)

def verFile(name, popupText):
    x = name.strip()
    try:
        f = open(x, "r")
        f.close()
        y = 1
    except:
        messagebox.showerror("File Input Error", "That file does not exist!")
        popupText.append("File Input Error: That file does not exist!")
        y = 0
    return y

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

def isolateChangeLog(invFileContents, popupText):
    x = invFileContents.count("Change Log")
    if x > 1:
        messagebox.showerror("Multiple Change Logs", "There cannot be more than one Change Log.")
        popupText.append("Multiple Change Logs: There cannot be more than one Change Log.")
    try:
        y = invFileContents.index("Change Log")
        return [invFileContents[:y], invFileContents[y:]]
    except:
        return [invFileContents, []]

def separateLists(contents, popupText):
    item = []
    number = []
    for i in contents:
        pair = i.strip().split(",")
        while len(pair) > 2:
            pair = [",".join(pair[:2])] + pair[2:]
        if len(pair) == 1:
            warning = "The following line lacks a number: " + str(i.strip())
            messagebox.showwarning("Missing Quantity", warning)
            popupText.append("Missing Quantity: " + warning)
            pair.append("(Error: No number)")
        elif pair[1].replace(" ","").lower() == "removed":
            pair[1] = "Removed"
        else:
            pair[1] = numFormat(pair[1].replace(" ",""), popupText, 1, i.strip())
        pair[0] = pair[0].strip().title()
        item.append(pair[0])
        number.append(pair[1])
    for entry in item:
        i = item.index(entry)
        x = item.count(entry)
        if x > 1:
            noMults(entry, popupText, item, number)
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

def updateFile(invItem, invNum, chaItem, chaNum, chaFileContents, logContents, popupText):
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
                if numFormat(newInvNum[-1], popupText) < 0: # Because it is appended, the index will be -1
                    warning = "Amount for " + str(newInvItem[-1]) + " will become negative."
                    messagebox.showwarning("Negative Value", warning)
                    popupText.append("Negative Value: " + warning)
        else:
            if x > 1:
                # This somehow bypassed the separateLists function
                noMults(item, popupText, newInvItem, newInvNum)
            y = newInvItem.index(item)
            if chaNum[i] == "Removed":
                newInvItem.pop(y)
                newInvNum.pop(y)
            else:
                newInvNum[y] += numFormat(chaNum[i], popupText)
                if newInvNum[y] < 0:
                    warning = "Amount for " + str(newInvItem[y]) + " will become negative."
                    messagebox.showwarning("Negative Value", warning)
                    popupText.append("Negative Value: " + warning)
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

def genPoints(logContents, chaItem, chaNum, invItem, invNum, popupText):
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
            formLog[key] = separateLists(formLog[key], popupText)
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

class InventoryGUI:
    def __init__(self):
        root = Tk()
        root.title("Taking Inventory GUI")
        root.geometry("500x500")
        self.myFrame = Frame(root)
        self.myFrame.grid(row=0, column=0, sticky="NESW")
        self.myFrame.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        self.label0 = Label(self.myFrame, text="Inventory Manager\n", font="Arial 20 bold")
        self.label0.grid(pady=10)
        self.filetypeList = ["inventory", "changes", "output"]
        self.index = 0
        self.fileText = "Enter the name of the " + self.filetypeList[self.index] + " file."
        self.label1 = Label(self.myFrame, text=self.fileText)
        self.label1.grid()
        self.textfield = Entry(self.myFrame)
        self.textfield.grid()
        self.enterButton = Button(self.myFrame, text="Enter File", command=self.buttonClicked)
        self.enterButton.grid()
        self.label2 = Label(self.myFrame, text="")
        self.label2.grid()
        exit_button = Button(root, text="Exit Program", command=root.destroy)
        exit_button.grid(pady=30)
        self.fileNames = []
        self.popupText = ["\n"]

    def buttonClicked(self):
        textValue = self.textfield.get()
        if self.filetypeList[self.index] == "output":
            self.fileNames.append(textValue)
            self.textfield.delete(0, END)
            self.textfield.destroy()
            self.label1.destroy()
            self.label2.destroy()
            self.enterButton.destroy()
            self.originalMain()
            self.newLayout()
        else:
            x = verFile(textValue, self.popupText)
            if x:
                self.fileNames.append(textValue)
                self.textfield.delete(0, END)
                self.label2["text"] += "\n" + self.filetypeList[self.index].title() + " File : " + textValue
                self.changeText()

    def changeText(self):
        self.index += 1
        self.fileText = "Enter the name of the " + self.filetypeList[self.index] + " file."
        self.label1.config(text=self.fileText)

    def newLayout(self):
        self.textButton = Button(self.myFrame, text="See All Pop-up Text", command=self.textButtonClicked)
        self.textButton.grid()
        self.graphButton = Button(self.myFrame, text="See Graphs of Changed Items", command=self.graphButtonClicked)
        self.graphButton.grid()

    def textButtonClicked(self):
        self.textButton["text"] = "Hide All Pop-up Text"
        self.textButton["command"] = self.hideButtonClicked
        self.allText = "\n".join(self.popupText)
        self.label1 = Label(self.myFrame, text=self.allText)
        self.label1.grid()

    def hideButtonClicked(self):
        self.textButton["text"] = "Show All Pop-up Text"
        self.textButton["command"] = self.textButtonClicked
        self.label1.destroy()
    
    def graphButtonClicked(self):
        genGraphs(self.series)

    def originalMain(self):
        self.invFileName = self.fileNames[0]
        self.chaFileName = self.fileNames[1]
        self.outputFileName = self.fileNames[2]
        self.invFileContents = readFile(self.invFileName)
        [self.invFileContents, self.logContents] = isolateChangeLog(self.invFileContents, self.popupText)
        self.chaFileContents = readFile(self.chaFileName)
        [self.invItem, self.invNum] = separateLists(self.invFileContents, self.popupText)
        [self.chaItem, self.chaNum] = separateLists(self.chaFileContents, self.popupText)
        self.fileContents = updateFile(self.invItem, self.invNum, self.chaItem, self.chaNum, self.chaFileContents, self.logContents, self.popupText)
        writeFile(self.fileContents, self.outputFileName)
        messagebox.showinfo("Process Completed", "Inventory has been updated.")
        self.popupText.append("Process Completed: Inventory has been updated.")
        self.series = genPoints(self.logContents, self.chaItem, self.chaNum, self.invItem, self.invNum, self.popupText)

def main():
    ti = InventoryGUI()
    ti.myFrame.mainloop()

main()
