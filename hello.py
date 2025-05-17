import math

def getAngle(cameranum: int) -> tuple[float, float]:
    # get the angles from the camera
    # cameranum = 1 or 2
    # return the angles in degrees
    # XZangle = horizontal angle between the x and z axis
    # YZangle = vertical angle between the y and z axis

    if cameranum == 0:
        XZangle = 10.8
        YZangle = 10
    elif cameranum == 1:
        XZangle = -11.1
        YZangle = 10

    return XZangle, YZangle 

class BallDetector:
    # this class is used to detect the ball in the camera
    # it will take the angles from the camera and return the 3D coordinates of the ball
    # it will also check if the ball is on the screen or not
    HORIZONTAL_FOV = 55.28168977
    VERTICAL_FOV = 32.82769798

    HORIZONTAL_RESOLUTION = 640
    VERTICAL_RESOLUTION = 480

    SEPERATION_DISTANCE = 10

    SCREEN_RANGE = 30


    def __init__(self):
        # output [x, y, z, length, height]
        # x,y = bottom left corner of the camera
        bottomleft = findPosition(placeholders)
        bottomright = findPosition()
        topleft = findPosition()
        topright = findPosition()

        self.cornerx = (bottomleft[0] + topleft[0]) / 2
        self.cornery = (bottomleft[1] + bottomright[1]) / 2
        self.cornerz = (bottomleft[2] + bottomright[2] + topleft[2] + topright[2]) / 4

        l1 = bottomright[0] - bottomleft[0]
        l2 = topright[0] - topleft[0]
        self.screenlength = (l1 + l2) / 2

        h1 = bottomright[1] - bottomleft[1] 
        h2 = topright[1] - topleft[1]
        self.screenheight = (h1 + h2) / 2

        # return [x, y, z, length, height]


    def findPosition(self, XZangle1, YZangle1, XZangle2, YZangle2) -> list[float]:
        # take angles from two cameras and return the 3D coordinates of the object
        # XZangle1 = horizontal angle between the x and z axis of camera 1
        # YZangle1 = vertical angle between the y and z axis of camera 1
        # XZangle2 = horizontal angle between the x and z axis of camera 2
        # YZangle2 = vertical angle between the y and z axis of camera 2

        a = 90 - XZangle1
        b = 90 + XZangle2
        c = 180 - (a + b)
        d = (YZangle1 + YZangle2) / 2

        r1 = SEPERATION_DISTANCE * math.sin(math.radians(b)) / math.sin(math.radians(c))
        r2 = SEPERATION_DISTANCE * math.sin(math.radians(a)) / math.sin(math.radians(c))

        z = r1 * math.sin(math.radians(a))

        x = -(SEPERATION_DISTANCE / 2) + r1 * math.cos(math.radians(a))

        y = z * math.tan(math.radians(d))

        return x, y, z


    def checkBallonScreen(self, x, y, z) -> bool:
        # check if the ball is on the screen
        # x,y,z = 3D coordinates of the ball

        if x > self.cornerx and x < self.cornerx + self.screenlength:
            if y > self.cornery and y < self.cornery + self.screenheight:
                if z > self.cornerz - SCREEN_RANGE and z < self.cornerz + SCREEN_RANGE:
                    return True

        return False

# def calibrateCamera() -> list[float]:
#     # output [x, y, z, length, height]
#     # x,y = bottom left corner of the camera
#     bottomleft = findPosition()
#     bottomright = findPosition()
#     topleft = findPosition()
#     topright = findPosition()

#     x = (bottomleft[0] + topleft[0]) / 2
#     y = (bottomleft[1] + bottomright[1]) / 2
#     z = (bottomleft[2] + bottomright[2] + topleft[2] + topright[2]) / 4

#     l1 = bottomright[0] - bottomleft[0]
#     l2 = topright[0] - topleft[0]
#     length = (l1 + l2) / 2

#     h1 = bottomright[1] - bottomleft[1]
#     h2 = topright[1] - topleft[1]
#     height = (h1 + h2) / 2

#     return [x, y, z, length, height]


if __name__ == "__main__":
    print(findPosition(10.8, 10, -11.1, 10))