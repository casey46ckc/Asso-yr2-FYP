import pandas
import numpy

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


def countDayoff(timeTable):
    dayOffCounter = 0
    for i in range(6):
        if numpy.max(timeTable[:,i]) == 0:
            dayOffCounter += 1
    return dayOffCounter


def earlyLesson(timeTable):
    if numpy.max(timeTable[0,:]) == 0:
        return True
    else:
        return False


if __name__ == "__main__":
        
    clList = readClSchedule('MTT_2021S2_Custom.xls')
    tmpTable = None

    clS = ['CCCH4003CL54', 'CCCU4041', 'CCEN4005', 'CCIT4033CL03', 'CCIT4059CL03', 'CCIT4080']
    clSList = []
    for i in range(len(clS)):
        if len(clS[i]) > 8:
            clSList.append([cl for cl in clList if cl.clCode == clS[i][:8] and cl.clNo == clS[i][8:]])
        else:
            clSList.append([cl for cl in clList if cl.clCode == clS[i]])

    for i in range(len(clSList[0])):
        for j in range(len(clSList[1])):
            for k in range(len(clSList[2])):
                for l in range(len(clSList[3])):
                    for m in range(len(clSList[4])):
                        for n in range(len(clSList[5])):
                            tmpTable = combinationCheck(clSList[0][i], clSList[1][j], clSList[2][k], clSList[3][l], clSList[4][m], clSList[5][n])
                            if(tmpTable is not None):
                                print(f'{clSList[0][i].clCode}{clSList[0][i].clNo}+{clSList[1][j].clCode}{clSList[1][j].clNo}+{clSList[2][k].clCode}{clSList[2][k].clNo}+{clSList[3][l].clCode}{clSList[3][l].clNo}+{clSList[4][m].clCode}{clSList[4][m].clNo}+{clSList[5][n].clCode}{clSList[5][n].clNo}|Early Lesson: {earlyLesson(tmpTable)} No. of day-off: {countDayoff(tmpTable)}\n{tmpTable}')

