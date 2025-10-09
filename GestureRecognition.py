import math

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def is_ok_sign(lmList):
    thumb = next((x,y) for i,x,y in lmList if i==4)
    index = next((x,y) for i,x,y in lmList if i==8)
    return distance(thumb, index) < 40

def is_peace_sign(fingers):
    return fingers == [0,1,1,0,0]

def is_l_sign(fingers, lmList):
    thumb = next((x,y) for i,x,y in lmList if i==4)
    index = next((x,y) for i,x,y in lmList if i==8)
    return fingers == [1,1,0,0,0] and distance(thumb, index) > 40

def is_three_fingers(fingers):
    return fingers == [0,1,1,1,0]

def is_index_only(fingers):
    return fingers == [0,1,0,0,0]

def is_rock_sign(fingers):
    return fingers == [1,1,0,0,1]
