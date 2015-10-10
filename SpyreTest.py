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

width = 256
height = 256
frame_ref= 400
frame_rate = 30.
f_low=[.1,.3]
f_high=[1.,3.]

class SpyreTest(server.App):

    title = "Brain Image Analyzer"
    inputs = [ # Raw file inputs (20 max)
			  {"type": "text",
					"key": "raw_file_folder",
					"label": "Enter path to folder containing all raw files to be analyzed",
					"value": "/media/cornelis/DataCDH/Raw-data/Test Data/0910/EL_noled/Videos/"
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
		raw_file_folder = params['raw_file_folder']
		lof=[]
		for root, dirs, files in os.walk(raw_file_folder):
			for file in files:
				if (file.endswith(".raw") or file.endswith(".g") ):
					lof.append((os.path.join(root, file)))

		if len(lof > 1):
			print "Doing alignments..."
			aligned_frames = []
			lp=dj.get_distance_var(lof,width,height,frame_ref)
			for i in range(len(lp)):
				print('Working on this file: ')+str(lof[i])
				frames=dj.get_green_frames(str(lof[i]),width,height)
				frames_aligned=dj.shift_frames(frames,lp[i])
				aligned_frames.append(frames_aligned)
		else:
			frames=dj.get_green_frames(str(lof[0]),width,height)

		#Do temporal filters, apply and calculate dff
		#each filter band



		chebyfied_frames = []
		for i in range(len(f_low)):
			for frames in aligned_frames:
				avg_frames=fj.calculate_avg(frames)
				frames=fj.cheby_filter(frames, f_low[i], f_high[i], frame_rate)
				frames+=avg_frames
				frames=fj.calculate_df_f0(frames)
				#do gsr
				if params['gsr_check']:
					frames=fj.gsr(frames,width,height)









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



