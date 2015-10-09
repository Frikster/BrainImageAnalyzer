# import filter_jeff as fj
# from skimage import data, filter, io
#
# image = fj.get_frames('/media/cornelis/DataCDH/Raw-data/Test Data/0910/EL_noled/Videos/M1302000245_1441918072.809071.raw',256,256)
#
# image2 = data.coffee()

# tested with python2.7 and 3.4
from spyre import server

from scipy import signal
import skimage
from skimage import data, filter, io
from scipy.stats.stats import pearsonr
from scipy import ndimage

import filter_jeff as fj
import jeffs_functions as jf
import shutil
import os
import glob
import numpy as np
import displacement_jeff as dj

starting_frame = 100

class SpyreTest(server.App):

    title = "Brain Image Analyzer"
    inputs = [{	"type": "text",
					"key": "rawFile",
					"label": "Raw File Location",
					"value": "/media/cornelis/DataCDH/Raw-data/Test Data/0910/EL_noled/Videos/M1302000245_1441918072.809071.raw",
					"action_id":"image"},
				{"type": "text",
					"key": "x",
					"label": "x",
					"value": "100",
					"action_id":"image"},
				{"type": "text",
					"key": "y",
					"label": "y",
					"value": "100",
					"action_id":"image"}]

    controls = [{"type":"hidden",
					"id":"render",
					"label":"render"}]

    outputs = [{"type":"image",
					"id":"image",
					"control_id":"render"}]

    def getImage(self,params):
		rawFile = (params['rawFile'])
		x = float(params['x'])
		y = float(params['y'])

		print('x = '+str(x))
		print('y = '+ str(y))

		frames = fj.get_frames(rawFile,256,256)
		#image = fj.standard_deviation(frames)
		CorrelationMapDisplayer = fj.CorrelationMapDisplayer(frames)
		image = CorrelationMapDisplayer.get_correlation_map(x, y, frames)

		return image

if __name__ == '__main__':
	app = SpyreTest()
	app.launch(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))



