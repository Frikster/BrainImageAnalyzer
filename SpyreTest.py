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
import numpy as np
import scipy.stats as ss
import pandas as pd

import pickle

width = 128
height = 128
#frame_ref= 400
frame_rate = 30.
#f_low=[.1,.3]
#f_high=[1.,3.]

class SpyreTest(server.App):

    title = "Brain Image Analyzer"
    inputs = [# Bring constants under user-control
		      {"type": "text",
			   "key": "frame_ref",
			   "label": "Enter frame reference for alignment",
			   "value": "400"
			  },
			  {"type": "text",
			   "key": "f_low",
			   "label": "Enter f_low for cheby filter",
			   "value": ".3"
			  },
			  {"type": "text",
			   "key": "f_high",
			   "label": "Enter f_high for cheby filter",
			   "value": "3."
			  },
			  # Define output folder
			  {"type": "text",
			   "key": "output_dir",
			   "label": "Enter output directory",
			   "value": "/home/cornelis/Downloads/"
			  },
    		  # Raw file inputs (20 max)
			  {"type": "text",
					"key": "raw_file_folder",
					"label": "Enter path to folder containing all raw files to be analyzed",
					"value": "/media/cornelis/DataCDH/Data/Raw-data/Test Data/Sexy_Tif"
			  },
			  # Pick raw file that will be aligned to. Other alignments will be saved to file
			  {"type": "text",
			   "key": "raw_file_to_align",
			   "label": "Enter name of raw file that other raw files will be aligned to",
			   "value": "BA2_Oct31am_15Hz_8x8.tif"
			  },
			  # uncheck if you want to only see the result aligned to user selcected raw
			  {	"type": "checkboxgroup",
					"key": "all_alignments_check",
				   	"options" : [
						{"label": "Save all possible alignments", "value":"all_aligns", "checked":False}
					]},

			  # GSR Checkbox
			  {	"type": "checkboxgroup",
					"key": "gsr_check",
				   	"options" : [
						{"label": "Perform Global Signal Regression", "value":"gsr", "checked":True}
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

			  # GSR Checkbox
			  {	"type": "checkboxgroup",
					"key": "regions_check",
				   	"options" : [
						{"label": "Hindlimb", "value":"HL", "checked":True},
						{"label": "Barrel", "value":"BC", "checked":True},
						{"label": "V1", "value":"V1", "checked":True},
					]},


			   # Choose seed pixel location if using it
			   # HL = HindLimb, BC = Barrel Cortex, V1 = Primary Visual Cortex
		      { "type": "text",
				"key": "x_HL",
				"label": "Hindlimb x",
				"value": ""},
			  { "type": "text",
				"key": "y_HL",
				"label": "Hindlimb y",
				"value": ""},
			  { "type": "text",
				"key": "x_BC",
				"label": "Barrel x",
				"value": ""},
			  { "type": "text",
				"key": "y_BC",
				"label": "Barrel y",
				"value": ""},
			  { "type": "text",
				"key": "x_V1",
				"label": "V1 x",
				"value": ""},
			  { "type": "text",
				"key": "y_V1",
				"label": "V1 y",
				"value": ""}]

    controls = [{"type":"button",
				 "id":"render_button",
				 "label":"Pray it works"}]

    tabs = ["Images","Table"]

    outputs = [{"type":"image",
				"id":"image",
				"control_id":"render_button",
				"tab":"Images"},
               {"type":"table",
				"id":"table_id",
				"control_id":"render_button",
				"tab":"Table"}]

    # controls = [{"type":"hidden",
    #  			"id":"render",
    #  			"label":"render"}]

    def getImage(self,params):
        import pandas as pd
        print("getImage entered")
        choose_map = params['choose_map']
        preprocessed_frames_dict = {}

        if choose_map == 'spc_map':
            # Retrieve list of all x,y values for what was ticked
            tups=[(k,v) for (k,v) in params.items() if k[2:] in params['regions_check']]
            coords={}
            for x_tup in tups:
                for y_tup in tups:
                    # print(str(x_tup) + " and " + str(y_tup) + "?")
                    if x_tup[0][0] == 'x' and y_tup[0][0] == 'y' and x_tup[0][2:] == y_tup[0][2:]:
                        # print(str(x_tup) + " and " + str(y_tup))
                        coords[x_tup[0][2:]] = (x_tup[1],y_tup[1])


		# 5,6,3,2,1,4

        images = {}
        for coord in coords.items():
            if coord[1][0]!='' and coord[1][1]!='':

                print("Entered the loop")
                region = coord[0]
                x = float(coord[1][0])
                y = float(coord[1][1])
                f_low = float(params['f_low'])
                f_high = float(params['f_high'])
                frame_ref = float(params['frame_ref'])
                raw_file_folder = params['raw_file_folder']
                raw_filename_to_align = params['raw_file_to_align']


                if 'preprocessed_frames' not in globals():
                    # The first file added to lof is raw_file_to_align
                    lof=[]
                    for root, dirs, files in os.walk(raw_file_folder):
                        for file in files:
                            if(raw_filename_to_align.lower() in file.title().lower()):
                                lof.append((os.path.join(root, file)))
                    for root, dirs, files in os.walk(raw_file_folder):
                        for file in files:
                            if ((file.endswith(".raw") or file.endswith(".g")) and (os.path.join(root, file)) not in lof):
                                lof.append((os.path.join(root, file)))

                    # Uncomment to check result immdediately after import
                    # frames=dj.get_green_frames(str(lof[1]),width,height)
                    # return(frames[0])

                    # CorrelationMapDisplayer = fj.CorrelationMapDisplayer(frames)
                    # image = CorrelationMapDisplayer.get_correlation_map(x, y, frames)
                    #return(frames[0])
                    #print("Well Fuck")

                    # First element in aligned_frames_list is all frames aligned to user selected raw
                    if len(lof) > 1:
                        print("Doing alignments...")
                        aligned_frames_list = []
                        lp=dj.get_distance_var(lof,width,height,frame_ref)
                        if 'all_aligns' in params['all_alignments_check']:
                            for i in range(len(lp)):
                                print('Working on this file: ')+str(lof[i])
                                frames=fj.get_frames(str(lof[i]),width,height)
                                frames_aligned=dj.shift_frames(frames,lp[i])
                                aligned_frames_list.append(frames_aligned)
                        else:
                            print('Working on this file: ')+str(lof[0])
                            frames=dj.get_frames(str(lof[0]),width,height)
                            frames_aligned=dj.shift_frames(frames,lp[0])
                            aligned_frames_list.append(frames_aligned)
                    else:
                        aligned_frames_list=[dj.get_frames(str(lof[0]),width,height)]
                        frames = aligned_frames_list[0]

                    # Uncomment to check result immdediately after alignment
                    #print('MADE IT')
                    #return(aligned_frames_list[0][0])

                    # CorrelationMapDisplayer = fj.CorrelationMapDisplayer(aligned_frames_list[0])
                    # image = CorrelationMapDisplayer.get_correlation_map(x, y, aligned_frames_list[0])
                    # return(image)
                    #print("Well Fuck")

                    # Do temporal filters, apply and calculate dff
                    # each filter band
                    # Again, the first element in preprocessed_frames_list is cheby filter applied to all frames aligned to user selected
                    # raw and then df/f0 computed and then gsr applied if option was selected
                    preprocessed_frames_list = []
                    for f in aligned_frames_list:
                        avg_frames=fj.calculate_avg(frames)
                        frames=fj.cheby_filter(frames, f_low, f_high, frame_rate)
                        #return(np.gradient(frames[0]))[0]
                        frames+=avg_frames

                        frames=fj.calculate_df_f0(frames)
                        preprocessed_frames_list.append(frames)
                        #do gsr
                        # if 'gsr' in params['gsr_check']:
                        # 	frames=fj.gsr(frames,width,height)
                        # 	preprocessed_frames_list.append(frames)
                        # else:
                        # 	preprocessed_frames_list.append(frames)

                    preprocessed_frames = preprocessed_frames_list[0]
                    global preprocessed_frames

                 #do gsr
                if 'gsr' in params['gsr_check']:
                    #gsr_memory = True
                    #global gsr_memory
                    print('gsr commence')
                    preprocessed_frames=fj.gsr(preprocessed_frames,width,height)


                #pickle.dump( favorite_color, open( "save.p", "wb" ) )

                seed_indicator = 0.5
                # output selected map
                if choose_map == 'spc_map':
                    print('x = '+str(x))
                    print('y = '+ str(y))
                    CorrelationMapDisplayer = fj.CorrelationMapDisplayer(preprocessed_frames)
                    image = CorrelationMapDisplayer.get_correlation_map(y, x, preprocessed_frames)
                    preprocessed_frames_dict[region] = preprocessed_frames
                    # Make pixels around the seed equal to the maximum value 1 for the red dot to show
                    image[y,x]=seed_indicator
                    image[y+1,x]=seed_indicator
                    image[y,x+1]=seed_indicator
                    image[y+1,x+1]=seed_indicator
                    image[y-1,x]=seed_indicator
                    image[y,x-1]=seed_indicator
                    image[y-1,x-1]=seed_indicator
                    image[y-1,x+1]=seed_indicator
                    image[y+1,x-1]=seed_indicator
                    images[region] = image

                else:
                    image = fj.standard_deviation(preprocessed_frames)
                    # Make pixels around the seed equal to the maximum value 1 for the red dot to show
                    image[y,x]=seed_indicator
                    image[y+1,x]=seed_indicator
                    image[y,x+1]=seed_indicator
                    image[y+1,x+1]=seed_indicator
                    image[y-1,x]=seed_indicator
                    image[y,x-1]=seed_indicator
                    image[y-1,x-1]=seed_indicator
                    image[y-1,x+1]=seed_indicator
                    image[y+1,x-1]=seed_indicator
                    images[region] = image

        # You have a dictionary of all the images. Concatenate them vertically in a logical order
        global preprocessed_frames_dict
        images_list = []

        for region in params['regions_check']:
            for image_and_key in images.items():
                if image_and_key[0] == region:
                    print(image_and_key[0])
                    images_list = images_list + [image_and_key[1]]

        combined_image = np.vstack(images_list)
        return combined_image
		# else:
		# 	# output selected map
		# 	if choose_map == 'spc_map':
		# 		print('x = '+str(x))
		# 		print('y = '+ str(y))
		# 		CorrelationMapDisplayer = fj.CorrelationMapDisplayer(preprocessed_frames)
		# 		image = CorrelationMapDisplayer.get_correlation_map(x, y, preprocessed_frames)
		# 	else:
		# 		image = fj.standard_deviation(preprocessed_frames)
		# 	return image

    # Plot connectivity matrix
    def getData(self, params):
        if len(params['regions_check'])>1:
            print("getData entered")
            # retrieve pixels across all frames at the seed along with nearby pixels
            # average each to colapse into a one dimensional array - place in a dictionary
            single_arrays = {}
            for frames_and_key in preprocessed_frames_dict.items():
                key = frames_and_key[0]
                frames = frames_and_key[1]
                coords = [param for param in params.items() if key in param[0]]
                assert(len(coords) == 2)
                if 'x' in coords[0][0]:
                    x = int(coords[0][1])
                    y = int(coords[1][1])
                else:
                    x = int(coords[1][1])
                    y = int(coords[0][1])

                # Retrieve all frames at a region around the seed pixel and add to dictionary
                # TODO: Ensure this doesn't throw index out of range
                region_frames = frames[:,y-1:y+2,x-1:x+2]
                avg_region_frames = map(np.average,region_frames)
                single_arrays[key] = avg_region_frames

            # Build the correlation index matrix
            header = zip(*single_arrays.items())[0]
            rows = zip(*single_arrays.items())[1]
            mat = np.corrcoef(rows)
            return pd.DataFrame(mat,columns=header)




if __name__ == '__main__':
	app = SpyreTest()
	app.launch(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))



