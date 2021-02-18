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
        #print(f"{self.clCode}-{self.clNo} before:\n", self.timeTable)
        self.timeTable[timeSlot][weekday] = 1
        #print(f"{self.clCode}-{self.clNo} after:\n", self.timeTable)


    def addTimetable(self, weekday, timeSlot):
        #print(f"{self.clCode}-{self.clNo} before addition:\n", self.timeTable)
        self.timeTable[timeSlot][weekday] = 1
        #print(f"{self.clCode}-{self.clNo} after addition:\n", self.timeTable)


class TheTimeSchedule:
    def __init__(timeTable):
        self.timeTable = timeTable
        self.dayOff = calDayOff()
        self.

    def calDayOff(self):


def validityCheck(clA, clB):
    if clA.clCode != clB.clCode:
        # Assuming the classes should be in the same campus or some exceptions, such as "TBC" or "HKU"
        if clA.clRoom[:3] == "TBC" or clA.clRoom[:3] == "HKU" or clB.clRoom[:3] == "TBC" or clB.clRoom[:3] == "HKU" or (clA.clRoom[:3] == clB.clRoom[:3]):
            if numpy.max(clA.timeTable + clB.timeTable):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def __main__():
    data = pandas.read_excel('MTT_2021S2_Custom.xls', dtype={'Course Code': str, 'Class No': str, 'Course Name': str, 'Semester': int, 'Weekday': int, 'Time': str, 'Room': str})
    data['Time Slot'] = 0
    data.loc[data.Time == '10:00 - 11:20', 'Time Slot'] = 1
    data.loc[data.Time == '11:30 - 12:50', 'Time Slot'] = 2
    data.loc[data.Time == '13:00 - 14:20', 'Time Slot'] = 3
    data.loc[data.Time == '14:30 - 15:50', 'Time Slot'] = 4
    data.loc[data.Time == '16:00 - 17:20', 'Time Slot'] = 5
    data.loc[data.Time == '17:30 - 18:50', 'Time Slot'] = 6

    print(data)


    clList = []

    for i in range(len(data)):
        targetClass = [listIndex for listIndex, cl in enumerate(clList) if cl.clCode == data['Course Code'][i] and cl.clNo == data['Class No'][i]]
        if len(targetClass) != 0:
            clList[targetClass[0]].addTimetable(data['Weekday'][i] - 1, data['Time Slot'][i])
        else:
            clList.append(TheClassSchedule(data['Course Code'][i], data['Class No'][i], data['Course Name'][i], data['Semester'][i], data['Room'][i], data['Weekday'][i] - 1, data['Time Slot'][i]))

    #for i in range(len(clList)):
    #    print(f"{clList[i].clCode}-{clList[i].clNo} {clList[i].clRoom[:3]}:\n", clList[i].timeTable)
    print(validityCheck(clList[0], clList[4]))



