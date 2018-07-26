"""
Entity Annotation Migrator (EAM)
v1.0

Usage:
  * Run manually for each entity you want to switch the annotations for.
  * Then execute e.g.
      `python3 EntityAnnotationMigrator.py [filename (optional)] > output.txt`
  * Fix any import statement issues in the output, and you're done!
"""
import re
import traceback
import sys

DEBUG = False
NEWLINE_BETWEEN_DEFINITIONS = True
COMMENT_PREFIX = "//"
FILENAME = "input.txt"


def getEntireFunction(data, start):
    """ Gets the entire function (precisely, the indices of the first and last line) including preceding annotations! """
    parens = 0  # '{' '}' specifically
    end = start
    # Find the first line of the function
    while start >= 0:
        start -= 1
        # Ignore comments
        if data[start].strip().startswith(COMMENT_PREFIX):
            continue
        elif data[start].strip().startswith("@"):
            continue
        else:
            break
    start += 1
    # Find the last line of the function
    while end < len(data):
        line = data[end].replace('\{', '').replace('\}', '')
        parens += line.count('{') - line.count('}')
        if parens <= 0:
            break
        end += 1

    if parens != 0:
        raise Exception(
            "getEntireFunction error: Syntax Problem around line %d" % start)

    return (start, end) if parens == 0 else (None, None)


def readFile(filename, variableInfo, variableNames):
    try:
        with open(filename, "r") as f:
            """
            {"id": {"JAnn": [], "Declaration": "", "HAnn": [], "Getter": [], "Setter": []}}
            """
            doneWithDeclarationsFlag = False
            data = f.readlines()
            i = 0
            # Parse lines preceding the class body
            while i < len(data):
                variableInfo["fileHead"].append(data[i])
                if data[i].strip().startswith("public class"):
                    break
                i += 1
            # Parse lines in the class body
            while i < len(data)-1:
                i += 1
                if DEBUG:
                    print("Parsing input line {}...".format(i+1))
                line = data[i].strip()
                # Ignore irrelevant lines
                if line == "" or not (line.startswith("public") or line.startswith("private") or line.startswith("@")):
                    continue
                elif line.startswith("@Id"):
                    doneWithDeclarationsFlag = True
                # Check whether dealing with declarations or definitions
                if not doneWithDeclarationsFlag:
                    # Organize the JsonAnnotations and Declarations
                    if line[0] != "@":
                        varName = line.split()[-1][:-1]
                        variableNames.append(varName)
                        variableInfo.setdefault(
                            varName, {"JAnn": [], "Declaration": "", "HAnn": [], "Getter": [], "Setter": []})
                        variableInfo[varName]["Declaration"] = data[i]
                        # Obtain the Annotations
                        j = i - 1
                        while data[j].strip() != [] and data[j].strip().startswith("@"):
                            variableInfo[varName]["JAnn"].insert(0, data[j])
                            j -= 1
                else:
                    # Getters start with "public", Setters start with "public void"
                    if line[0] != "@":
                        # Obtain variable name
                        varName = line.split()[2]
                        if not (varName.startswith("get") or varName.startswith("set")):
                            start, i = getEntireFunction(data, i)
                            otherFunc = data[start:i+1]
                            variableInfo["otherFunctions"].append(otherFunc)
                            continue
                        varName = re.search('(.*)\(', varName[3:])[0][:-1]
                        varName = varName[0].lower() + varName[1:]
                        # Check if function is getter or setter
                        if not line.startswith("public void"):
                            # It's a getter
                            start, i = getEntireFunction(data, i)
                            variableInfo[varName]["Getter"] = data[start:i+1]
                            k = 0
                            while variableInfo[varName]["Getter"][k].strip().startswith("@"):
                                k += 1
                            # Split into Annotations and Getter Function Body
                            variableInfo[varName]["HAnn"] = variableInfo[varName]["Getter"][:k]
                            del variableInfo[varName]["Getter"][:k]
                        else:
                            # It's a setter
                            start, i = getEntireFunction(data, i)
                            variableInfo[varName]["Setter"] = data[start:i+1]
                            # It shouldn't have annotations preceding it, but just in case...
                            k = 0
                            while variableInfo[varName]["Setter"][k].strip().startswith("@"):
                                k += 1
                            # Split into Annotations and Setter Function Body
                            variableInfo[varName]["HAnn"] += variableInfo[varName]["Setter"][:k]
                            del variableInfo[varName]["Setter"][:k]
    # Nicely prints traceback on Terminal for faster debugging
    except IndexError as e:
        traceback.print_exc()
    except Exception as e:
        traceback.print_exc()


def printMigrated(variableInfo, variableNames):
    """
    Prints the class declarations and methods out!
    """
    for line in variableInfo["fileHead"]:
        print(line, end="")

    for v in variableNames:
        for line in variableInfo[v]["HAnn"]:
            print(line, end="")
        for line in variableInfo[v]["Declaration"]:
            print(line, end="")
        if NEWLINE_BETWEEN_DEFINITIONS:
            print()
    print()

    for v in variableNames:
        for line in variableInfo[v]["JAnn"]:
            if line.strip() == "@JsonIgnore":
                variableInfo[v]["Setter"].insert(
                    0, line.replace("Ignore", "Deserialize"))
            print(line, end="")
        for line in variableInfo[v]["Getter"]:
            print(line, end="")
        for line in variableInfo[v]["Setter"]:
            print(line, end="")
        print()

    for f in variableInfo["otherFunctions"]:
        for line in f:
            print(line, end="")
        print()

    print('}')


def migrate():
    variableInfo = {}
    variableNames = []  # Maintain the ordering of variables
    variableInfo["fileHead"] = []
    variableInfo["otherFunctions"] = []
    readFile(FILENAME, variableInfo, variableNames)
    if DEBUG:
        print(variableInfo["toolId"])
    else:
        printMigrated(variableInfo, variableNames)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        FILENAME = sys.argv[1]
    migrate()
