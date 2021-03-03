import pandas
import time
from numpy import max, sum, zeros

# List: commonly used constant
period_strs = ('08:30 - 09:50', '10:00 - 11:20', '11:30 - 12:50', '13:00 - 14:20', '14:30 - 15:50', '16:00 - 17:20', '17:30 - 18:50')

# Object: represent the fundanmental semester time schedule information for add/drop/swap
class TheSemesterTimeSchedule:
    def __init__(self, progCode: str, clList: list, timeTable):
        self.progCode = progCode
        self.clList = clList
        self.rank = rank_timeTable(timeTable)
        self.earlyMorningLesson = countEarlyMorningLesson(timeTable)
        self.lateEveningLesson = countLateEveningLesson(timeTable)
        self.skyGroundLessons = countSkyGroundLesson(timeTable)
        self.dayoff = countDayoff(timeTable)
        self.timeTable = timeTable
        
    # functionality: display information
    def displayInfo(self):
        clCodeList = [cl.clCode + cl.clNo for cl in self.clList]
        
        display_str = f"{'Period':^13}|Mon|Tue|Wed|Thu|Fri|Sat|\n"
        for i in len(self.timeTable):
            display_str += f"{period_strs[i]:^13}|"
            for j in len(self.timeTable[i]):
                display_str += f"{'x' if self.timeTable[i][j] == 1 else ' ':^3}|"
            display_str += "\n"
        return display_str + '+'.join(clCodeList) + f"\nEML: {self.earlyMorningLesson:1d} LEL: {self.lateEveningLesson:1d} SGL: {self.skyGroundLessons:1d} Day off(s): {self.dayoff:1d}"



# Object: represent the fundanmental class schedule information for add/drop/swap
class TheClassSchedule:
    def __init__(self, clCode: str, clNo: str, clName: str, sem: int, clRoom: str, weekday: int, timeSlot: int):
        self.clCode = clCode
        self.clNo = clNo
        self.clName = clName
        self.clSemester = sem
        self.clRoom = clRoom
        self.timeTable = zeros((7, 6), dtype=int)
        # print(f"{self.clCode}-{self.clNo} before:\n", self.timeTable)
        self.timeTable[timeSlot, weekday] = 1
        # print(f"{self.clCode}-{self.clNo} after:\n", self.timeTable)


    def addTimetable(self, weekday, timeSlot):
        # print(f"{self.clCode}-{self.clNo} before addition:\n", self.timeTable)
        self.timeTable[timeSlot, weekday] = 1
        # print(f"{self.clCode}-{self.clNo} after addition:\n", self.timeTable)


# functionality: check whether the input courses are feasible without location and time conflict, return None if it is not feasible, return combined time table in 7 x 6 matrix format
def combinationCheck(*args):
    timeTable = zeros((7, 6), dtype=int)
    for i in range(len(args)):
        for j in range(i + 1, len(args[(i + 1):])):
            if args[i].clCode == args[j].clCode:
                return None
            # Assuming the classes should be in the same campus or some exceptions, such as "TBC" or "HKU"    
            elif args[i].clRoom[:3] != args[j].clRoom[:3] and ((args[i].clRoom[:3] != "TBC" and args[i].clRoom[:3] != "HKU") and (args[j].clRoom[:3] != "TBC" and args[j].clRoom[:3] != "HKU")):
                return None
        timeTable += args[i].timeTable

    # Check the timetable would not be overlapped
    if max(timeTable) > 1:
        return None
    else:
        # Check there doesn't exist consecutive 4 lessons
        for i in range(6):
            for k in range(4):
                if sum(timeTable[k:k + 4,i]) >= 4:
                    return None
        return timeTable


# functionality: combined the time table of TheClassSchedule Object in 7 x 6 matrix format without checking
def combinedTable(*args):
    timeTable = zeros((7, 6), dtype=int)
    for i in range(len(args)):
        timeTable += args[i].timeTable
    return timeTable


# functionality: combined the time table in 7 x 6 matrix format without checking
def readClSchedule(fileName):
    clList = []
    data = pandas.read_excel(fileName, dtype={'Course Code': str, 'Class No': str, 'Course Name': str, 'Semester': int, 'Weekday': int, 'Time': str, 'Room': str})
    data['Time Slot'] = 0
    data.loc[data.Time == '10:00 - 11:20', 'Time Slot'] = 1
    data.loc[data.Time == '11:30 - 12:50', 'Time Slot'] = 2
    data.loc[data.Time == '13:00 - 14:20', 'Time Slot'] = 3
    data.loc[data.Time == '14:30 - 15:50', 'Time Slot'] = 4
    data.loc[data.Time == '16:00 - 17:20', 'Time Slot'] = 5
    data.loc[data.Time == '17:30 - 18:50', 'Time Slot'] = 6

    for i in range(len(data)):
        targetClass = [listIndex for listIndex, cl in enumerate(clList) if cl.clCode == data['Course Code'][i] and cl.clNo == data['Class No'][i]]
        if len(targetClass) != 0:
            clList[targetClass[0]].addTimetable(data['Weekday'][i] - 1, data['Time Slot'][i])
        else:
            clList.append(TheClassSchedule(data['Course Code'][i], data['Class No'][i], data['Course Name'][i], data['Semester'][i], data['Room'][i], data['Weekday'][i] - 1, data['Time Slot'][i]))

    return clList


# functionality: check the number of dayoff for the time table in 7 x 6 matrix format, return in integer primitive type
def countDayoff(timeTable) -> int:
    dayOffCounter = 0
    for i in range(6):
        if max(timeTable[:,i]) == 0:
            dayOffCounter += 1
    return dayOffCounter


# functionality: check the existency of early morning lesson (start at 8:30 a.m.) for the time table in 7 x 6 matrix format, return in integer primitive type
def countEarlyMorningLesson(timeTable) -> int:
    return sum(timeTable[0,:])


# functionality: check the existency of early morning lesson (start at 8:30 a.m.) for the time table in 7 x 6 matrix format, return in integer primitive type
def countLateEveningLesson(timeTable) -> int:
    return sum(timeTable[6,:])

# functionality: check the existency of sky-ground time gap between lessons (> 3 hours) for the time table in 7 x 6 matrix format, return in integer primitive type
def countSkyGroundLesson(timeTable) -> int:
    skyGroundCounter = 0
    for i in range(6):
        # for the day is not day-off
        if max(timeTable[:,i]) != 0:
            for k in range(3):
                start = sum(timeTable[k + 1: k + 4, i])
                end = sum(timeTable[k + 4:, i])
                # print(f"curr: {timeTable[k, i]}\t start: {start}\t end: {end}")
                if timeTable[k, i] > 0 and start == 0 and end == 0:
                    skyGroundCounter += 1
    return skyGroundCounter


# functionality: recursive function for product of N class in object approach
# args[0]:start depth, args[1]:current depth, arg[0]...arg[n]:clsList, replaced by clsList[0][i], clsList[1][j], ... one by one recursively
# original version for debugging, version 1 for performance and readibility
def collect_result(*args):
    if args[1] < args[0]:
        for i in range(len(args[args[1] + 3])):
            paras_next = []
            paras_next.append(args[0])
            paras_next.append(args[1] + 1)
            paras_next.append(args[2])
            for k in range(args[0]):
                print(f"i: {i}\tk: {k}")
                if k != args[1]:
                    if isinstance(args[k + 3], TheClassSchedule):
                        print(f"i: {i}\tk: {k}\tCl Code:{args[k + 3].clCode}{args[k + 3].clNo}")
                    paras_next.append(args[k + 3])
                else:
                    paras_next.append(args[k + 3][i])
                    print(f"i: {i}\tk: {k}\tCl Code:{args[k + 3][i].clCode}{args[k + 3][i].clNo}")
    
            for l in range(len(paras_next)):
                if isinstance(paras_next[l], list):
                    for m in range(len(paras_next[l])):
                        if isinstance(paras_next[l][m], TheClassSchedule):
                            print(f"paras_next[{l}][{m}]: {paras_next[l][m].clCode}{paras_next[l][m].clNo}")
                elif isinstance(paras_next[l], TheClassSchedule):
                    print(f"paras_next[{l}]: {paras_next[l].clCode}{paras_next[l].clNo}")
                else:
                    print(f"paras_next[{l}]: {paras_next[l]}")
            collect_result(*paras_next)

    else:
        tmpTable = combinationCheck(*args[3:])
        if(tmpTable is not None):
            args[2].append(TheSemesterTimeSchedule(progCode="xx xxx", clList=args, timeTable=tmpTable))


# function calls for sorting Objects with specific fields
def getRank(sTM: TheSemesterTimeSchedule) -> int:
    return sTM.rank

def getDayOff(sTM: TheSemesterTimeSchedule) -> int:
    return sTM.dayoff

def getEarlyMorningLesson(sTM: TheSemesterTimeSchedule) -> int:
    return sTM.earlyMorningLesson

def getLateEveningLesson(sTM: TheSemesterTimeSchedule) -> int:
    return sTM.lateEveningLesson

def getSkyGroundLessons(sTM: TheSemesterTimeSchedule) -> int:
    return sTM.skyGroundLessons


def collect_result_V1(outList: list, depth: int, curr_depth: int, *args):
    if curr_depth < depth:
        for i in range(len(args[curr_depth])):
            paras_next = []
            for k in range(depth):
                if k != curr_depth:
                    paras_next.append(args[k])
                else:
                    paras_next.append(args[k][i])
            collect_result_V1(outList, depth, curr_depth + 1, *paras_next)
    else:
        tmpTable = combinationCheck(*args)
        if(tmpTable is not None):
            outList.append(TheSemesterTimeSchedule(progCode="xx xxx", clList=args, timeTable=tmpTable))
    

# once thought it should be faster, but it isn't
def collect_result_V2(outList: list, depth: int, curr_depth: int, *args):
    if curr_depth < depth:
        for i in range(len(args[curr_depth])):
            paras_next = []
            for k in range(depth):
                if k != curr_depth:
                    paras_next.append(args[k])
                else:
                    paras_next.append(args[k][i])

            if curr_depth + 1 > 1:
                tmpTable = combinationCheck(*paras_next[:curr_depth + 1])
                if tmpTable is not None:
                    collect_result_V2(outList, depth, curr_depth + 1, *paras_next)
            else:
                collect_result_V2(outList, depth, curr_depth + 1, *paras_next)
    else:
        tmpTable = combinationCheck(*args)
        if(tmpTable is not None):
            outList.append(TheSemesterTimeSchedule(progCode="xx xxx", clList=args, timeTable=tmpTable))


# functionality: check the existency of Class by the input Code with specific class Schedule list, will turn an empty list if incorrect code input
def codeValidity(clList: list, inCode: str) -> list:
    if len(inCode) > 8:
        return [cl for cl in clList if cl.clCode == inCode[:8] and cl.clNo == inCode[8:]]
    else:
        return [cl for cl in clList if cl.clCode == inCode]

# functionality: rank the time table with certain constraints:
# + 10 marks for each day of day-off, including saturday
# -  3 marks for each day of early morning lessons or late evening lessons
# -  2 marks for the time gap between two lessons within one day is greater than 3 hours
def rank_timeTable(tmpTable):
    return 10 * countDayoff(tmpTable) - 3 * (countEarlyMorningLesson(tmpTable) + countLateEveningLesson(tmpTable) - 2 * countSkyGroundLesson(tmpTable))

if __name__ == "__main__":

    # sample code        
    clList = readClSchedule('MTT_2021S2_Custom.xls')
    tmpTable = None

    clS = ['CCCH4003CL54', 'CCCU4041', 'CCEN4005', 'CCIT4033CL03', 'CCIT4059CL03', 'CCIT4080']
    clSList = []
    resultList1 = []
    resultList2 = []
    loopDepth = len(clS)
    for i in range(loopDepth):
        tmpList = codeValidity(clList, clS[i])
        if(len(tmpList) != 0):
            clSList.append(tmpList)
        else:
            print("Error: incorrect course code input. Please try again")
            break
    t1_start = time.time()
    collect_result_V1(resultList1, loopDepth, 0, *clSList)
    result_sorted = sorted(resultList1, key=getRank, reverse=True)
    for i in range(len(result_sorted)):
        if(i < 10):
            print(result_sorted[i].displayInfo())
    t1_stop = time.time()
    print("Elapsed time during the V1 in seconds:", t1_stop - t1_start)  

    t2_start = time.time()
    collect_result_V2(resultList2, loopDepth, 0, *clSList)
    result_sorted = sorted(resultList2, key=getRank, reverse=True)
    for i in range(len(result_sorted)):
        if(i < 10):
            print(result_sorted[i].displayInfo())
    t2_stop = time.time()
    print("Elapsed time during the V2 in seconds:", t2_stop - t2_start)  
    

