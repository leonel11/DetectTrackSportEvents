import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

import constants


class Heatmapper:
    '''
    Implement class of building a heatmap on image according to set of points
    '''

    def __init__(self, point_diameter=30, point_strength=0.2, opacity=0.5):
        '''
        Constructor
        :param point_diameter: diameter of each spot to model a heatmap
        :param point_strength: blur of each spot to model a heatmap
        :param opacity: transparence of heatmap on background image
        '''
        self.point_diameter = point_diameter
        self.point_strength = point_strength
        self.opacity = opacity
        self.cmap = self.__setColorMapFromImage(constants.COLORMAP_IMAGE)


    def __imageToOpacity(self, img, opacity):
        img = img.copy()
        alpha = img.split()[3]
        img.putalpha(alpha.point(lambda p: int(p * opacity)))
        return img


    def buildHeatmapOnImage(self, points, background_img):
        '''
        Build a heatmap on background image according to set of points
        :param points: set of points
        :param background_img: background image
        :return: heatmap on background image
        '''
        width, height = background_img.size
        heatmap = self.__makeHeatmap(width, height, points)
        heatmap = self.__imageToOpacity(heatmap, self.opacity)
        if background_img is not None:
            return Image.alpha_composite(background_img.convert('RGBA'), heatmap)
        else:
            return None


    def __setColorMapFromImage(self, colormap_img):
        # Load colomap image
        img = Image.open(colormap_img)
        img = img.resize((256, img.height))
        # Extract colors from colormap image
        colours = [img.getpixel((x, 0)) for x in range(256)]
        colours = [(r/255, g/255, b/255, a/255) for r, g, b, a in colours]
        return LinearSegmentedColormap.from_list('from_image', colours)


    def __makeHeatmap(self, width, height, points):
        '''
        Form a heatmap of fixed width and height for set of points
        :param width: width of heatmap
        :param height: height of heatmap
        :param points: set of points
        :return: heatmap image
        '''
        heatmap = Image.new('L', (width, height), color=255) # empty heatmap
        spot = Image.open(constants.SPOT_IMAGE).copy().resize((self.point_diameter, self.point_diameter),
                                                              resample=Image.ANTIALIAS) # spot image to model a heatmap
        spot = self.__imageToOpacity(spot, self.point_strength)
        # Locate spots on a heatmap according to coordinates of points
        for x, y in points:
            x, y = int(x - self.point_diameter/2), int(y - self.point_diameter/2)
            heatmap.paste(spot, (x, y), spot)
        # Paint over using heatmap
        res = self.cmap(np.array(heatmap), bytes=True)
        return Image.fromarray(res)