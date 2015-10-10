# import filter_jeff as fj
# from skimage import data, filter, io
#
# image = fj.get_frames('/media/cornelis/DataCDH/Raw-data/Test Data/0910/EL_noled/Videos/M1302000245_1441918072.809071.raw',256,256)
#
# image2 = data.coffee()

# tested with python2.7 and 3.4
from spyre import server

#from scipy import signal
#import skimage
#from skimage import data, filter, io
#from scipy.stats.stats import pearsonr
#from scipy import ndimage

import filter_jeff as fj
import displacement_jeff as dj
#import jeffs_functions as jf
#import shutil
import os
#import glob
#import numpy as np

starting_frame = 100
width = 256
height = 256

class SpyreTest(server.App):

    title = "Brain Image Analyzer"
    inputs = [ # Raw file inputs (20 max)
			  {"type": "text",
					"key": "raw_file1",
					"label": "Raw File Locations (max 20) Leave blank the ones you dont use",
					"value": "/media/cornelis/DataCDH/Raw-data/Test Data/0910/EL_noled/Videos/M1302000245_1441918072.809071.raw"
			  },
			  {	"type": "text",
					"key": "raw_file2",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file3",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file4",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file5",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file6",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file7",
					"value": ""
		 	  },
			  {	"type": "text",
					"key": "raw_file8",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file9",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file10",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file11",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file12",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file13",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file14",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file15",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file16",
					"value": ""
			  },
			  {	"type": "text",
					"key": "raw_file17",
					"value": "",
			  },
			  {	"type": "text",
					"key": "raw_file18",
					"value": "",
			  },
			  {	"type": "text",
					"key": "raw_file19",
					"value": "",
			  },
			  {	"type": "text",
					"key": "raw_file20",
					"value": "",
			  },
			  # GSR Checkbox
			  {	"type": "checkboxgroup",
					"key": "gsr_check",
				   	"options" : [
						{"label": "Perform GLobal Signal Regression", "value":"gsr", "checked":True}
					]},
			   # Choose SD map vs Correlation map dropdown list
			  {	"type":'dropdown',
				"key": 'choose_map',
				"label": 'Choose Map',
				"options" : [
					{"label": "Seed Pixel Correlation Map", "value":"spc_map"},
					{"label": "Standard Deviation Map", "value":"sd_map"}
				],
				"value":'spc_map'},
			   # Choose seed pixel location if using it
		      { "type": "text",
				"key": "x",
				"label": "x",
				"value": ""},
			  { "type": "text",
				"key": "y",
				"label": "y",
				"value": ""}]


    controls = [{"type":"button",
				 "id":"render_button",
				 "label":"Pray it works"}]

    outputs = [{"type":"image",
				"id":"image",
				"control_id":"render_button"}]


    # controls = [{"type":"hidden",
    #  			"id":"render",
    #  			"label":"render"}]

    def getImage(self,params):
		print(params.keys())

		raw_file_keys=filter(lambda x:'raw_file' in x,params.keys())
		raw_files=[params[i] for i in raw_file_keys if params[i]!='']

		if len(raw_files > 1):
			print "Doing alignments..."
			for m in the_mice:
				lof, lofilenames=dj.get_file_list(green_dir, m)
				print(lof)
				lp=dj.get_distance_var(lof,width,height,frame_ref)
				for i in range(len(lp)):
					print('Working on this file: ')+str(lof[i])
					#tmp_lof=[]
					#tmp_lof.append(lof[i])
					#print('creating 1 element list')
					#print(type(tmp_lof))
					frames=dj.get_green_frames(str(lof[i]),width,height)
					frames=dj.shift_frames(frames,lp[i])


		raw_file = (params['raw_file1'])
		x = float(params['x'])
		y = float(params['y'])

		print('x = '+str(x))
		print('y = '+ str(y))

		frames = fj.get_frames(raw_file,256,256)
		#image = fj.standard_deviation(frames)
		CorrelationMapDisplayer = fj.CorrelationMapDisplayer(frames)
		image = CorrelationMapDisplayer.get_correlation_map(x, y, frames)

		return image

if __name__ == '__main__':
	app = SpyreTest()
	app.launch(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))



