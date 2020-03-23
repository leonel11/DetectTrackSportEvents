SENT_FROM_USER = 'sportaisystemyar@gmail.com'
SENT_FROM_PASSWORD = 'matveevdv_ivanovskyli'

# Background extraction settings
BACKGROUND_STRATEGIES = ['median', 'mean', 'cumulated']
BACKGROUND_READY_IMAGE = 'system/background.jpg'

# Heatmap building settings
COLORMAP_IMAGE = 'system/colormap.png'
SPOT_IMAGE = 'system/spot.png'

# Folders for saving
RESULTS_FOLDER = '../results'
STATISTICS_FOLDER = '../statistics'

# JDE tracker settings
OUTPUT_FRAME_SIZE = (1088, 608)
GPU_NUMBER = 5
TRACKER_CONFIG = 'cfg/yolov3.cfg'
TRACKER_WEIGHTS = 'models/jde.1088x608.uncertainty.pt'
IOU_THRESHOLD = 0.5
CONFIDENCE_THRESHOLD = 0.5
SUPPRESSION_THRESHOLD = 0.4
MIN_BOX_AREA = 200
TRACKING_BUFFER = 30