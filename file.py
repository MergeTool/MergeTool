import subprocess


def compilate():
    fout = open('code.cpp', 'w')
    for bit in bits_of_file:
        for line in bit:
            fout.write(line)

    fout.close()
    subprocess.check_output(["g++", "code.cpp"])


def conflictServe(list, first):
    obj = list[first]
    print("\n left = ")

    for i in range(len(obj[0])):
        print(obj[0][i][0:len(obj[0][i]) - 1])

    print("\n right = ")

    flag1 = False
    stop = False

    for i in range(len(obj[1])):
        print(obj[1][i][0:len(obj[1][i]) - 1])

    response = input(
        "Choose what to leave ('R' = right, 'L' = left, 'B' = both, 'N' = next conflict, 'P' = previous conflict"
        + " 'C' = compile): \n")

    if (response[0] == 'R') | (response[0] == 'r'):
        bits_of_file[first * 2 + 1] = obj[1]
        flag1 = True
    elif (response[0] == 'L') | (response[0] == 'l'):
        bits_of_file[first * 2 + 1] = obj[0]
        flag1 = True
    elif (response[0] == 'B') | (response[0] == 'b'):
        new = obj[0]
        new.expand(obj[1])
        bits_of_file[first * 2 + 1] = new
        flag1 = True

    if (response[0] == 'P') | (response[0] == 'p'):
        flag1 = True
    elif (response[0] == 'N') | (response[0] == 'n'):
        flag1 = False
    elif (response[0] == 'C') | (response[0] == 'c'):
        compilate()
        stop = True

    if stop == False:
        if flag1 == True:
            if first + 1 != len(list):
                conflictServe(list, first + 1)
            else:
                conflictServe(list, 0)
        else:
            if first != 0:
                conflictServe(list, first - 1)
            else:
                conflictServe(list, len(list) - 1)


conflicts_list = []
fileobj = open('prog.cpp', 'r', encoding="latin-1")
fileobj_lines = fileobj.readlines()
fr = fileobj.read()
list = [0, 0, 0]
tuples_list = []

for index in range(len(fileobj_lines)):
    if fileobj_lines[index][0:3] == "<<<":
        list[0] = index
    elif fileobj_lines[index][0:3] == "===":
        list[1] = index
    elif fileobj_lines[index][0:3] == ">>>":
        list[2] = index
        tuples_list.append(list)
        list = [0, 0, 0]

for tuply in tuples_list:
    conflict_left = fileobj_lines[tuply[0] + 1:tuply[1]]
    conflict_right = fileobj_lines[tuply[1] + 1:tuply[2]]
    conflict = (conflict_left, conflict_right)
    conflicts_list.append(conflict)

fileobj.close()
bits_of_file = []
iter = 0

for tuply in tuples_list:
    bits_of_file.append(fileobj_lines[iter:tuply[0]])
    iter = tuply[2] + 1
    bits_of_file.append([])

bits_of_file.append(fileobj_lines[tuples_list[len(tuples_list) - 1][2] + 1:len(fileobj_lines)])
conflictServe(conflicts_list, 0)
