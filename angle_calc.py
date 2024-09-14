import math


def calculate_angle(point1, point2, point3):
    """Calculates the angle between three points (in degrees)."""
    angle = math.degrees(math.atan2(point3[1] - point2[1], point3[0] - point2[0]) -
                         math.atan2(point1[1] - point2[1], point1[0] - point2[0]))
    angle = abs(angle)

    if angle > 180.0:
        angle = 360 - angle

    return angle
