class AutoPrinting:
    def __init__(self, filePath):
        self.setNewName(filePath)
        
    def setNewName(self, fileName):
        self.printStatement = list()
        self.fileName = fileName
        self.index = 0
        self.totalClass = 0
        self.totalMethod = 0
        self.classOpenBracket = list()
        self.classCloseBracket = list()
        self.methodOpenBracket = list()
        self.methodCloseBracket = list()
        if(fileName.endswith(".java")):
            self.systemPrint = "System.out."
            self.javaFile = True
        else:
            self.systemPrint = ""
            self.javaFile = False
        
    def main(self):

        # Read .Java file
        readFile = open(self.fileName,'r')
        lineList = readFile.readlines()
        haveClass = False

        # Whole loop through all the lines of the Java file
        while(self.index < len(lineList)):
            # Get first class name 
            if not haveClass:
                if self.index >= len(lineList):
                    break
                self.findFirstClass(lineList)
                if self.index >= len(lineList): break
                self.findClassName(lineList)
                haveClass = True

            # Get sub-class name
            elif self.findClass(lineList):
                self.findClassName(lineList)
            
            # Enter to a method
            elif self.findMethod(lineList):
                # Line manipulation
                extraSpace = "    "
                space = " "
                space *= lineList[self.index].index('p')

                # Special case: when the method only one liner
                if("{" in lineList[self.index] and "}" in lineList[self.index]):
                    self.handleSpecialMethod(lineList)
                    self.index += 1
                    continue

                # Get method name        
                self.findMethodName(lineList)

                # Skipp all white space in method
                while lineList[self.index] == '\n':
                    self.index += 1

                # Enter body    
                if len(self.methodOpenBracket) > 0:
                    # Printing line should be after super initialization/call
                    if self.haveSuper(lineList) == True:
                        self.index += 1
                        if self.containCloseBracket(lineList):
                            lineList[self.index-1] += extraSpace + space + self.systemPrint + "println(\"xxx " + '.'.join(self.printStatement) + "\");" + "\n"
                    # Printing line should be after this() call
                    if self.haveThisForConstructor(lineList) == True:
                        self.index += 1
                        if self.containCloseBracket(lineList):
                            lineList[self.index-1] += extraSpace + space + self.systemPrint + "println(\"xxx " + '.'.join(self.printStatement) + "\");" + "\n"
                    # Special case: if there is a open bracket at the first line of the body
                    if self.containOpenBracket(lineList):
                        self.methodOpenBracket.append("{") 
                    # Print 
                    if "}" not in lineList[self.index]:
                        lineList[self.index] = extraSpace + space + self.systemPrint + "println(\"xxx " + '.'.join(self.printStatement) + "\");" + "\n" + lineList[self.index]
                    # Special case: body only has one line
                    else:
                        self.methodOpenBracket.pop()
                        self.totalMethod -= 1
                        #self.classOpenBracket.pop()
                        self.index += 1
                        self.printStatement.pop()
                        continue
                
                # Loop method, and repeat above behavior
                # TODO: REDUNDANCY, need to shorten
                while len(self.methodOpenBracket) > 0:
                    self.index += 1

                    if self.endMethod(lineList):
                        self.methodOpenBracket.pop()
                        continue

                    # repeat above behavior    
                    elif self.findMethod(lineList):
                        extraSpace = "    "
                        space = " "
                        space *= lineList[self.index].index('p') 
                        
                        if("{" in lineList[self.index] and "}" in lineList[self.index]):
                            self.handleSpecialMethod(lineList)
                            self.index += 1
                            continue
                        self.findMethodName(lineList)
                        while lineList[self.index] == '\n':
                            self.index += 1
                        if self.containOpenBracket(lineList):
                            self.methodOpenBracket.append("{") 
                        if len(self.methodOpenBracket) > 0:
                            if self.haveSuper(lineList) == True:
                                self.index += 1
                                if self.containCloseBracket(lineList):
                                    lineList[self.index-1] += extraSpace + space + self.systemPrint + "println(\"xxx " + '.'.join(self.printStatement) + "\");" + "\n"
                            if self.haveThisForConstructor(lineList) == True:
                                self.index += 1
                                if self.containCloseBracket(lineList):
                                    lineList[self.index-1] += extraSpace + space + self.systemPrint + "println(\"xxx " + '.'.join(self.printStatement) + "\");" + "\n"
                            if "}" not in lineList[self.index]:
                                lineList[self.index] = extraSpace + space + self.systemPrint + "println(\"xxx "  + '.'.join(self.printStatement) + "\");" + "\n" + lineList[self.index]
                            else:
                                self.methodOpenBracket.pop()
                                self.totalMethod -= 1
                                self.index += 1
                                self.printStatement.pop()
                                continue
                        # Remove method name from the printstatement
                        self.printStatement.pop()

                    elif self.containBothBracket(lineList):
                        self.index += 1
                        continue    

                    elif self.containOpenBracket(lineList):
                        self.methodOpenBracket.append("{") 

                    elif self.containCloseBracket(lineList):
                        self.methodOpenBracket.pop()  

                # Remove method name from the printstatement 
                self.printStatement.pop()     

            # When end the only one class existed, find the next one, or end
            elif self.endFirstClass(lineList):
                self.classOpenBracket.pop() 
                haveClass = False 
                self.totalClass = 0
                self.index += 1 
                continue

            elif self.endClass(lineList):
                self.classOpenBracket.pop() 
                self.index += 1 
                continue

            elif self.containBothBracket(lineList):
                self.index += 1
                continue

            elif self.containOpenBracket(lineList):
                self.classOpenBracket.append("{") 

            elif self.containCloseBracket(lineList):
                self.classOpenBracket.pop()   

            self.index += 1 
        
        readFile.close()

        # Write all the line back to the file using overwriting
        readFile = open(self.fileName,'w')
        for line in lineList:
            readFile.write(line)
        readFile.close()


    def handleSpecialMethod(self, lineList):
        methodHeaderLine = lineList[self.index].split("(")
        methodName = methodHeaderLine[0].split(" ")[-1]
        self.printStatement.append(methodName)

        oneLineMethodSplit = lineList[self.index].split("{")
        length = len(oneLineMethodSplit)
        oneLineMethodSplit[length-1] = "{ " + "System.out.println(\"xxx "  + '.'.join(self.printStatement) + "\");" + oneLineMethodSplit[length-1] 
        lineList[self.index] = oneLineMethodSplit[0] + oneLineMethodSplit[length-1]
        self.printStatement.pop()

    def containBothBracket(self, lineList):
        return "{" in lineList[self.index] and "}" in lineList[self.index]
   
    def containOpenBracket(self, lineList):
        return "{" in lineList[self.index]
    
    def containCloseBracket(self, lineList):
        return "}" in lineList[self.index]

    def endMethod(self, lineList):
        if len(self.methodOpenBracket) == self.totalMethod and "}" in lineList[self.index] and "{" not in lineList[self.index]:
            self.totalMethod -= 1
            return True
        return False
    
    def haveSuper(self, lineList):
        return 'super' in lineList[self.index]

    def haveThisForConstructor(self, lineList):
        return 'this' in lineList[self.index] and '(' in lineList[self.index]

    def findMethodName(self, lineList):
        self.totalMethod += 1
        methodHeaderLine = lineList[self.index].split("(")
        methodName = methodHeaderLine[0].split(" ")[-1] #if "static" not in methodHeaderLine else methodHeaderLine[3]
        while self.index < len(lineList) and "{" not in lineList[self.index]:
            self.index += 1
        self.printStatement.append(methodName)
        self.methodOpenBracket.append("{") 
        self.index += 1
        
    def findMethod(self, lineList):
        if self.javaFile:
            return ("public" in lineList[self.index] or "private" in lineList[self.index] or "protected" in lineList[self.index]) and "(" in lineList[self.index] and "}" not in lineList[self.index] and "new" not in lineList[self.index]
        else:
            return "fun" in lineList[self.index]

    def findClass(self, lineList):
        return "class" in lineList[self.index].split(" ")
    
    def findFirstClass(self, lineList):
        while self.index < len(lineList) and "class" not in lineList[self.index].split(" "):
            self.index += 1
            
    def findClassName(self, lineList):
        # Find class name if it is java find
        if self.javaFile:
            self.totalClass += 1
            classHeaderLine = lineList[self.index].split(" ")
            while '' in classHeaderLine:
                classHeaderLine.remove('')
            className = ""

            # Condition to get class name 
            if "static" not in classHeaderLine and \
                ("public" not in classHeaderLine and \
                "private" not in classHeaderLine and\
                "protected" not in classHeaderLine):
                if "final" in classHeaderLine or "abstract" in classHeaderLine: 
                    className = classHeaderLine[2] 
                else:
                    className = classHeaderLine[1]
            elif "public" not in classHeaderLine and \
                "private" not in classHeaderLine and\
                "protected" not in classHeaderLine:
                className = classHeaderLine[2]
            elif "static" not in classHeaderLine:
                if "final" in classHeaderLine or "abstract" in classHeaderLine: 
                    className = classHeaderLine[3]
                else:
                    className = classHeaderLine[2]
            elif "static" in classHeaderLine and \
                ("public" in classHeaderLine or \
                "private" in classHeaderLine or\
                "protected" in classHeaderLine):
                className = classHeaderLine[3]
            
            while self.index < len(lineList) and "{" not in lineList[self.index]:
                self.index += 1
            self.index += 1
            self.printStatement.append(className)
            self.classOpenBracket.append("{")

        # Find class name if it is kotlin file:
        else:
            self.totalClass += 1
            classHeaderLine = lineList[self.index].split(" ")
            while '' in classHeaderLine:
                classHeaderLine.remove('')
            className = ""
        
            while self.index < len(lineList) and "{" not in lineList[self.index]:
                self.index += 1
            self.index += 1
            self.printStatement.append(className)
            self.classOpenBracket.append("{")
        
    def endFirstClass(self,lineList):
        if len(self.classOpenBracket) == 1 and self.totalClass == 1 and "}" in lineList[self.index] and "{" not in lineList[self.index]:
            self.printStatement = list()
            self.totalClass -= 1
            return True
        return False

    def endClass(self, lineList):
        if len(self.classOpenBracket) == self.totalClass and "}" in lineList[self.index] and "{" not in lineList[self.index]:
            self.printStatement.pop()
            self.totalClass -= 1
            return True
        return False

# autoPrinting = AutoPrinting("Java Error/anotherTemp.java")
# autoPrinting.main()