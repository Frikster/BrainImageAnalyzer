import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
from scipy import ndimage
#from joblib import Parallel, delayed  
#import multiprocessing
import parmap
#import image_registration
from PIL import Image

from libtiff import TIFF

#M1312000377_1438367187.563086.raw
#processed_data/Concatenated Stacks.raw
#file_to_filter = "/media/user/DataFB/AutoHeadFix_Data/0731/EL_LRL/Videos/M2015050115_1438365772.086721.raw"
#file_to_filter2 = "/media/user/DataFB/AutoHeadFix_Data/0731/EL_LRL/Videos/M2015050115_1438366080.539013.raw"
#file_to_save = "/media/user/DataFB/AutoHeadFix_Data/0731/EL_LRL/global_signal.rawf"
#corrfile_to_save = "/media/ch0l1n3/DataFB/AutoHeadFix_Data/0802/EL_LRL/corr.rawf"
#sd_file = "/media/user/DataFB/AutoHeadFix_Data/0731/EL_LRL/mean_filter.rawf"

#save_dir = "/media/user/DataFB/AutoHeadFix_Data/0731/EL_LRL/"

#todo: These are evil globals
width = 128
height = 128
#frame_rate = 30.0
#frame_size = width * height * 3

starting_frame = 100

def get_frames(rgb_file,width,height):

    if(rgb_file.endswith(".tif")):
        ########
        # Cat method
        img = Image.open(rgb_file)

        counter=0
        # if True:
        #     while True:
        #         try:
        #             img.seek(counter)
        #         except EOFError:
        #             break
        #         counter+=1
        #         print counter

        #Default pic sizes
        n_pixels = 128

        # Initialize 3D image array
        n_frames = counter
        n_frames = 20000

        images_raw = np.zeros((n_frames, n_pixels, n_pixels), dtype = np.float64)

        print "n_frames: ", n_frames
        for i in range(0, n_frames,1):
            img.seek(i)
            #print "Loading frame: ", i
            #images_raw [i] = np.flipud(np.fliplr(np.float16(img))) #FLIP IMAGES FOR Experiments Nov and Dec 2015
            images_raw [i] = np.float64(img) #2016-1-11 2016-1-14 experiment no flipping needed
        imarray = images_raw

        ######
        # # plt method
        # I = plt.imread(rgb_file)
        #
        # #tifflib method
        # # to open a tiff file for reading:
        # tif = TIFF.open(rgb_file, mode='r')
        # # to read an image in the currect TIFF directory and return it as numpy array:
        # image = tif.read_image()
        # # to read all images in a TIFF file:
        # for image in tif.iter_images(): # do stuff with image
        #     image = tif.read_image()
        #
        # # to open a tiff file for writing:
        # tif = TIFF.open('filename.tif', mode='w')
        # #to write a image to tiff file
        # tif.write_image(image)
        #
        # #PIL method
        # im = Image.open(rgb_file)
        # imarray = np.array(im)
        return imarray

    frame_size = width * height * 3
    with open(rgb_file, "rb") as file:
        frames = np.fromfile(file, dtype=np.uint8)
        total_number_of_frames = int(np.size(frames)/frame_size)
        print total_number_of_frames
        frames = np.reshape(frames, (total_number_of_frames, width, height, 3))

        frames = frames[starting_frame:, :, :, 1]
        frames = np.asarray(frames, dtype=np.float32)
        total_number_of_frames = frames.shape[0]

    return frames
    
def get_green_frames(g_file,width,height):
    with open(g_file, "rb") as file:
        frames = np.fromfile(file, dtype=np.uint8)
        total_number_of_frames = int(np.size(frames)/(width*height))
        print total_number_of_frames
        frames = np.reshape(frames, (total_number_of_frames, width, height))
        frames = np.asarray(frames, dtype=np.uint8)
        total_number_of_frames = frames.shape[0]
    return frames

def get_processed_frames(rgb_file,width,height):
    with open(rgb_file, "rb") as file:
        frames = np.fromfile(file, dtype=np.float32)
        total_number_of_frames = int(np.size(frames)/(width*height))
        print total_number_of_frames
        frames = np.reshape(frames, (total_number_of_frames, width, height))
        frames = np.asarray(frames, dtype=np.float32)
        total_number_of_frames = frames.shape[0]
    return frames

def filt(pixel, b, a):
    return signal.filtfilt(b, a, pixel)

def cheby_filter(frames, low_limit, high_limit,frame_rate):
    nyq = frame_rate/2.0
    low_limit = low_limit/nyq
    high_limit = high_limit/nyq
    order = 4
    rp = 0.1
    Wn = [low_limit, high_limit]
    
    b, a = signal.cheby1(order, rp, Wn, 'bandpass', analog=False)
    print "Filtering..."
    frames = signal.filtfilt(b, a, frames, axis=0)
    #frames = parmap.map(filt, frames.T, b, a)
    #for i in range(frames.shape[-1]):
    #    frames[:, i] = signal.filtfilt(b, a, frames[:, i])
    print "Done!"
    return frames

def calculate_avg(frames):
    return np.mean(frames, axis=0)

def calculate_df_f0(frames):
    print frames.shape
    baseline = np.mean(frames, axis=0)
    frames = np.divide(np.subtract(frames, baseline), baseline)
    return frames

def save_to_file(dir, filename, frames, dtype):
    with open(dir+filename, "wb") as file:
        frames.astype(dtype).tofile(file)


def gsr(frames,width,height):
    # Reshape into time and space
    frames = np.reshape(frames, (frames.shape[0], width*height))
    mean_g = np.mean(frames, axis=1)
    g_plus = np.squeeze(np.linalg.pinv([mean_g]))

    beta_g = np.dot(g_plus, frames)
    
    print np.shape(mean_g)

    print np.shape(beta_g)

    global_signal = np.dot(np.asarray([mean_g]).T, [beta_g])

    #save_to_file(file_to_save, global_signal, np.float32)

    frames = frames - global_signal
    
    frames = np.reshape(frames, (frames.shape[0], width, height))
    return frames

def masked_gsr(frames, mask_filename):
    mask = 0
    with open(mask_filename, "rb") as file:
        mask = np.fromfile(file, dtype=np.uint8)
    
    mask = np.asarray(mask, dtype=np.float32)

    print mask.shape
    indices = np.squeeze((mask > 0).nonzero())
    print np.shape(indices)
    brain_frames = np.zeros((frames.shape[0], len(indices)))
    frames = np.reshape(frames, (frames.shape[0], width*height))

    for i in range(frames.shape[0]):
        brain_frames[i, :] = frames[i, indices]



    mean_g = np.mean(brain_frames, axis=1)
    g_plus = np.squeeze(np.linalg.pinv([mean_g]))

    beta_g = np.dot(g_plus, frames)
    
    print np.shape(mean_g)
    print np.shape(beta_g)
    global_signal = np.dot(np.asarray([mean_g]).T, [beta_g])
    frames = frames - global_signal
    frames = np.reshape(frames, (frames.shape[0], width, height))
    return frames

def standard_deviation(frames):
    return np.std(frames, axis=0)

def generate_mean_filter_kernel(size):
    kernel = 1.0/(size * size) * np.array([[1]*size]*size)
    return kernel

def filter2_test(frames, frame_no):
    kernel = generate_mean_filter_kernel(8)
    frame = ndimage.convolve(frames[frame_no], kernel, mode='constant', cval=0.0)
    return frames[frame_no] - frame

def filter2_test_j(frame):
    kernel = generate_mean_filter_kernel(8)
    framek = ndimage.convolve(frame, kernel, mode='constant', cval=0.0)
    return frame - framek

def apply_shift(shift_corr, frames2):
    row, col = np.unravel_index(np.argmax(shift_corr), shift_corr.shape)

    for frame2 in frames2:
        ndimage.interpolation.shift(frame2, [0, col-128], frame2, mode='constant')
    print row, " ", col
    return frames2
    
def corr(pixel, seed_pixel):
    return pearsonr(pixel, seed_pixel)[0]
                    

class CorrelationMapDisplayer:
    def __init__(self, frames):
        print "Calling the constructor."
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        # calculate initial map at center pixel
        print (frames.shape[0]/2)
        print(frames.shape[1]/2)
        print (frames.shape[2]/2)
        # TODO: Is it correct for the indices to be [0] and [1] Jeff (answer is no I think)
        self.image = self.get_correlation_map(frames.shape[1]/2, frames.shape[2]/2, frames)
        self.imgplot = self.ax.imshow(self.image) 
        self.canvas = self.fig.canvas
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.frames = frames
        self.count = 0

    def display(self, c_map, low, high):
        self.c_map = c_map
        self.low = low
        self.high = high
        #self.imgplot.set_cmap(c_map)
        self.imgplot.set_clim(low, high)
        self.fig.colorbar(self.imgplot)
        plt.show()

    def onclick(self, event):
        print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        event.button, event.x, event.y, event.xdata, event.ydata)
        # X and Y must be flipped to have correct dimmensions!
        self.image = self.get_correlation_map(int(event.ydata), int(event.xdata), self.frames)

        self.imgplot = self.ax.imshow(self.image)
        #self.imgplot.set_cmap(self.c_map)
        self.imgplot.set_clim(self.low, self.high)
	
        self.canvas.draw()
        save_to_file("Maps/map_" + str(self.count) + ".raw", self.image, np.float32)
        self.count += 1

    def get_correlation_map(self, seed_x, seed_y, frames):
        print(seed_x,seed_y)
        seed_pixel = np.asarray(frames[:, seed_x, seed_y], dtype=np.float32)
        
        print np.shape(seed_pixel)
        width=frames.shape[1]
        height=frames.shape[2]
        # Reshape into time and space
        frames = np.reshape(frames, (frames.shape[0], width*height))

        print np.shape(frames)
        #correlation_map = []
        print 'Getting correlation...'
        #correlation_map = Parallel(n_jobs=4, backend="threading")(delayed(corr)(pixel, seed_pixel) for pixel in frames.T)
        #correlation_map = []
        #for i in range(frames.shape[-1]):
        #    correlation_map.append(pearsonr(frames[:, i], seed_pixel)[0])
        correlation_map = parmap.map(corr, frames.T, seed_pixel)
        correlation_map = np.asarray(correlation_map, dtype=np.float32)
        correlation_map = np.reshape(correlation_map, (width, height))
        print np.shape(correlation_map)

        return correlation_map

def display_image(image, c_map, low_end_limit, high_end_limit, frames):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    imgplot = ax.imshow(image)
    
    imgplot.set_cmap(c_map)
    imgplot.set_clim(low_end_limit, high_end_limit)
    fig.colorbar(imgplot)

    displayer = CorrelationMapDisplayer(fig, image, frames)

    plt.show()



frame_oi = 500

#frames = get_frames(file_to_filter)
#frames = frames[100:, :, :]
#for i in range(728):
#    frames[i] = filter2_test(frames, i)

all_dx = []
all_dy = []


#frames = get_frames("/media/user/DataFB/AutoHeadFix_Data/0731/EL_LRL/Videos/M2015050115_1438365772.086721.raw")
#frames = masked_gsr(frames, save_dir+"377_mask.raw")
#print np.shape(frames)

#res_trials = parmap.map(image_registration.chi2_shift, frames, frames[0]) 
#for res in res_trials:
#    all_dx.append(-res[0])
#    all_dy.append(-res[1])

#for frame in frames:
#dx, dy, edx, edy = image_registration.chi2_shift(frames[0], frame, upsample_factor='auto', boundary='constant', nthreads=1)
    
#print np.mean(all_dx)
#print np.mean(all_dy)
#print max(all_dx) - min(all_dx)
#print max(all_dy) - min(all_dy)

#save_to_file("test.raw", frames, np.float32)

#filtered_frame = filter2_test(frames, frame_oi)



#save_to_file(sd_file, filtered_frame, np.float32)

#frames2 = get_frames(file_to_filter2)
#for frame2 in frames2:
#    ndimage.interpolation.shift(frame2, [0, -4], frame2, mode='constant')
                                
#filtered_frame2 = filter2_test(frames2, frame_oi)
#shift_corr = get_shift_correlation(filtered_frame, filtered_frame2)
#frames2 = apply_shift(shift_corr, frames2)

#dx, dy, edx, edy = image_registration.chi2_shift(filtered_frame, filtered_frame2, upsample_factor='auto', boundary='constant', nthreads=12)
#print dx
#print dy
#print edx
#print edy

#frames2[frame_oi] = image_registration.fft_tools.shift2d(frames2[frame_oi],-dx,-dy)


#combination = np.asarray([frames[frame_oi], frames2[frame_oi]])
#print np.shape(shift_corr)

#save_to_file('images_with_shift.raw', combination, np.float32)

#avg_pre_filt = calculate_avg(frames)
#frames = np.reshape(frames, (total_number_of_frames, width*height))
#frames = cheby_filter(frames)
#frames = np.reshape(frames, (total_number_of_frames, width, height))
#frames += avg_pre_filt

#frames = calculate_df_f0(frames)

#frames = gsr(frames)
#frames = np.reshape(frames, (total_number_of_frames, width, height))

#sd = standard_deviation(frames)
#save_to_file(sd_file, sd, np.float32)


#mapper = CorrelationMapDisplayer(frames)
#mapper.display('spectral', -1.0, 1.0)

#save_to_file(corrfile_to_save, mapper.image, np.float32)
#save_to_file(file_to_save, frames, np.float32)


