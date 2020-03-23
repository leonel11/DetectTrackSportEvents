from enum import Enum


class Traceplace(Enum):
    '''
    Enum which collects types of strategies for point choice on bounding box
    '''

    LOWER_LEFT = 0,
    LOWER_CENTER = 1,
    LOWER_RIGHT = 2,
    UPPER_LEFT = 3,
    UPPER_CENTER = 4,
    UPPER_RIGHT = 5,
    CENTER = 6

    def __repr__(self):
        if self.value == Traceplace.LOWER_LEFT:
            return 'lower_left'
        if self.value == Traceplace.LOWER_CENTER:
            return 'lower_center'
        if self.value == Traceplace.LOWER_RIGHT:
            return 'lower_right'
        if self.value == Traceplace.UPPER_LEFT:
            return 'upper_left'
        if self.value == Traceplace.UPPER_CENTER:
            return 'upper_center'
        if self.value == Traceplace.UPPER_RIGHT:
            return 'upper_right'
        if self.value == Traceplace.CENTER:
            return 'center'