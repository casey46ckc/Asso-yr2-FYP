import pandas
import numpy
from time import process_time 

# Object: represent the fundanmental class schedule information for add/drop/swap
class TheClassSchedule:
    def __init__(self, clCode, clNo, clName, sem, clRoom, weekday, timeSlot):
        self.clCode = clCode
        self.clNo = clNo
        self.clName = clName
        self.clSemester = sem
        self.clRoom = clRoom
        self.timeTable = numpy.zeros((7, 6), dtype=int)
        # print(f"{self.clCode}-{self.clNo} before:\n", self.timeTable)
        self.timeTable[timeSlot, weekday] = 1
        # print(f"{self.clCode}-{self.clNo} after:\n", self.timeTable)


    def addTimetable(self, weekday, timeSlot):
        # print(f"{self.clCode}-{self.clNo} before addition:\n", self.timeTable)
        self.timeTable[timeSlot, weekday] = 1
        # print(f"{self.clCode}-{self.clNo} after addition:\n", self.timeTable)


# functionality: check whether the input courses are feasible without location and time conflict, return None if it is not feasible, return combined time table in 7 x 6 matrix format
def combinationCheck(*args):
    timeTable = numpy.zeros((7, 6), dtype=int)
    for i in range(len(args)):
        for j in range(i + 1, len(args[(i + 1):])):
            if args[i].clCode == args[j].clCode:
                return None
            # Assuming the classes should be in the same campus or some exceptions, such as "TBC" or "HKU"    
            elif args[i].clRoom[:3] != args[j].clRoom[:3] and ((args[i].clRoom[:3] != "TBC" and args[i].clRoom[:3] != "HKU") and (args[j].clRoom[:3] != "TBC" and args[j].clRoom[:3] != "HKU")):
                return None
        timeTable += args[i].timeTable

    # Check the timetable would not be overlapped
    if numpy.max(timeTable) > 1:
        return None
    else:
        # Check there doesn't exist consecutive 4 lessons
        for i in range(6):
            for k in range(4):
                if numpy.sum(timeTable[k:k + 4,i]) >= 4:
                    return None
        return timeTable


# functionality: combined the time table of TheClassSchedule Object in 7 x 6 matrix format without checking
def combinedTable(*args):
    timeTable = numpy.zeros((7, 6), dtype=int)
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
def countDayoff(timeTable):
    dayOffCounter = 0
    for i in range(6):
        if numpy.max(timeTable[:,i]) == 0:
            dayOffCounter += 1
    return dayOffCounter


# functionality: check the existence of early lesson (start at 8:30 a.m.) for the time table in 7 x 6 matrix format, return True when exists
def earlyLesson(timeTable):
    if numpy.max(timeTable[0,:]) == 0:
        return True
    else:
        return False


# functionality: recursive function for product of N class in object approach
# args[0]:start depth, args[1]:current depth, arg[0]...arg[n]:clsList, replaced by clsList[0][i], clsList[1][j], ... one by one recursively
# original version for debugging, version 1 for performance
def collect_result(*args):
    if args[1] < args[0]:
        for i in range(len(args[args[1] + 2])):
            paras_next = []
            paras_next.append(args[0])
            paras_next.append(args[1] + 1)
            for k in range(args[0]):
                print(f"i: {i}\tk: {k}")
                if k != args[1]:
                    if isinstance(args[k + 2], TheClassSchedule):
                        print(f"i: {i}\tk: {k}\tCl Code:{args[k + 2].clCode}{args[k + 2].clNo}")
                    paras_next.append(args[k + 2])
                else:
                    paras_next.append(args[k + 2][i])
                    print(f"i: {i}\tk: {k}\tCl Code:{args[k + 2][i].clCode}{args[k + 2][i].clNo}")
    
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
        tmpTable = combinationCheck(*args[2:])
        if(tmpTable is not None):
            clCodeList = [cl.clCode + cl.clNo for cl in args[2:]]
            print(f"{'+'.join(clCodeList)}|Early Lesson: {earlyLesson(tmpTable)} No. of day-off: {countDayoff(tmpTable)}\n{tmpTable}")



def collect_result_V1(depth, curr_depth, *args):
    if curr_depth < depth:
        for i in range(len(args[curr_depth])):
            paras_next = []
            for k in range(depth):
                if k != curr_depth:
                    paras_next.append(args[k])
                else:
                    paras_next.append(args[k][i])
            collect_result_V1(depth, curr_depth + 1, *paras_next)
    else:
        tmpTable = combinationCheck(*args)
        if(tmpTable is not None):
            clCodeList = [cl.clCode + cl.clNo for cl in args]
            print(f"{'+'.join(clCodeList)}|Early Lesson: {earlyLesson(tmpTable)} No. of day-off: {countDayoff(tmpTable)}\n{tmpTable}")
    

def collect_result_V2(depth, curr_depth, *args):
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
                    collect_result_V2(depth, curr_depth + 1, *paras_next)
            else:
                collect_result_V2(depth, curr_depth + 1, *paras_next)
    else:
        tmpTable = combinationCheck(*args)
        if(tmpTable is not None):
            clCodeList = [cl.clCode + cl.clNo for cl in args]
            print(f"{'+'.join(clCodeList)}|Early Lesson: {earlyLesson(tmpTable)} No. of day-off: {countDayoff(tmpTable)}\n{tmpTable}")






if __name__ == "__main__":
        
    clList = readClSchedule('MTT_2021S2_Custom.xls')
    tmpTable = None

    clS = ['CCCH4003CL54', 'CCCU4041', 'CCEN4005', 'CCIT4033CL03', 'CCIT4059CL03', 'CCIT4080']
    clK = ['CCIT4033', 'CCIT4080']
    clSList = []
    clKList = []
    loopDepth = len(clS)
    for i in range(loopDepth):
        if len(clS[i]) > 8:
            clSList.append([cl for cl in clList if cl.clCode == clS[i][:8] and cl.clNo == clS[i][8:]])
        else:
            clSList.append([cl for cl in clList if cl.clCode == clS[i]])

    loopDepthK = len(clK)
    for i in range(loopDepthK):
        if len(clK[i]) > 8:
            clKList.append([cl for cl in clList if cl.clCode == clK[i][:8] and cl.clNo == clK[i][8:]])
        else:
            clKList.append([cl for cl in clList if cl.clCode == clK[i]])

    t1_start = process_time()
    collect_result_V1(loopDepth, 0, *clSList)
    t1_stop = process_time()
    print("Elapsed time during the V1 in seconds:", t1_stop - t1_start)  

    t1_start = process_time()
    collect_result_V2(loopDepth, 0, *clSList)
    t1_stop = process_time()
    print("Elapsed time during the V2 in seconds:", t1_stop - t1_start)  
    

