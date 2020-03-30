from traceplace import Traceplace


def time_string(ms):
    '''
    Milliseconds -> string, MM:SS (minutes:seconds)
    :param ms: milliseconds
    :return: format string
    '''
    seconds = int((ms/1000) % 60)
    minutes = int((ms/(1000*60)) % 60)
    return '{:d}:{:02d}'.format(minutes, seconds)


def get_color(human_number):
    '''
    Get color in tuple (R, G, B), where R - red, G -green B - blue
    :param human_number: id of human to generate unique color
    :return: color  (R, G, B) as tuple
    '''
    color = ((111*int(human_number))%255, (51*int(human_number))%255, (87*int(human_number))%255)
    return color


def get_point(row_dataframe, marker_pos):
    '''
    Get point of bbox according to marker (strategy of point choice on bbox)
    :param row_dataframe: row of dataframe which stores vertices of bbox
    :param marker_pos: marker (strategy of point choice on bbox)
    :return: point of bbox
    '''
    if marker_pos == Traceplace.LOWER_LEFT:
        return (int(row_dataframe['bb_y']),
                int(row_dataframe['bb_x'] + row_dataframe['bb_w']))
    if marker_pos == Traceplace.LOWER_CENTER:
        return (int(row_dataframe['bb_y'] + row_dataframe['bb_h'] / 2.0),
                int(row_dataframe['bb_x'] + row_dataframe['bb_w']))
    if marker_pos == Traceplace.LOWER_RIGHT:
        return (int(row_dataframe['bb_y'] + row_dataframe['bb_h']),
                int(row_dataframe['bb_x'] + row_dataframe['bb_w']))
    if marker_pos == Traceplace.UPPER_LEFT:
        return (int(row_dataframe['bb_y']),
                int(row_dataframe['bb_x']))
    if marker_pos == Traceplace.UPPER_CENTER:
        return (int(row_dataframe['bb_y'] + row_dataframe['bb_h'] / 2.0),
                int(row_dataframe['bb_x']))
    if marker_pos == Traceplace.UPPER_RIGHT:
        return (int(row_dataframe['bb_y'] + row_dataframe['bb_h']),
                int(row_dataframe['bb_x']))
    if marker_pos == Traceplace.CENTER:
        return (int((row_dataframe['bb_y'] + row_dataframe['bb_h']) / 2.0),
                int((row_dataframe['bb_x'] + row_dataframe['bb_w']) / 2.0))


def is_bbox_intersected(cur_bbox, other_bbox):
    '''
    Check if bboxes are intersect
    :return: True, if bboxes are intersect
    '''
    bbox_y1 = cur_bbox['bb_y']
    bbox_y2 = cur_bbox['bb_y'] + cur_bbox['bb_h']
    bbox_x1 = cur_bbox['bb_x']
    bbox_x2 = cur_bbox['bb_x'] + cur_bbox['bb_w']
    y1 = other_bbox['bb_y']
    y2 = other_bbox['bb_y'] + other_bbox['bb_h']
    x1 = other_bbox['bb_x']
    x2 = other_bbox['bb_x'] + other_bbox['bb_w']
    if (x1 > bbox_x1 and x1 < bbox_x2 and y1 > bbox_y1 and y1 < bbox_y2) or \
        (x2 > bbox_x1 and x2 < bbox_x2 and y2 > bbox_y1 and y2 < bbox_y2) or \
        (x1 > bbox_x1 and x1 < bbox_x2 and y2 > bbox_y1 and y2 < bbox_y2) or \
        (x2 > bbox_x1 and x2 < bbox_x2 and y1 > bbox_y1 and y1 < bbox_y2):
        return True
    return False