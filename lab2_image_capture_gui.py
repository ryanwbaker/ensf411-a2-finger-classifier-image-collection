# Adapted from code found in this thread:
# https://stackoverflow.com/questions/32342935/using-opencv-with-tkinter
# Author: Ryan Baker

from msilib.schema import RadioButton
from PIL import Image, ImageTk, ImageOps
import tkinter as tk
from tkinter import ttk
import argparse
import cv2
import os
import time
import threading

class ImageCaptureFrame(ttk.Frame):
    def __init__(self, parent=None, output_path = "./"):
        """ Initialize frame which uses OpenCV + Tkinter. 
            The frame:
            - Uses OpenCV video capture and periodically captures an image
              and show it in Tkinter
            - A save button allows saving the current image to output_path.
            - Consecutive numbering is used, starting at 00000000.jpg.
            - Checks if output_path exists, creates folder if not.
            - Checks if images are already present and continues numbergin.
            
            attributes:
                vs (cv2 VideoSource): webcam to capture images from
                output_path (str): folder to save images to.
                count (int): number used to create the next filename.
                current_image (PIL Image): current image displayed
                btn (ttk Button): press to save image
                panel (ttk Label): to display image in frame
        """
        super().__init__(parent)
        self.pack()
        
        # 0 is your default video camera
        # Used external webcam, changed API for faster loading
        self.vs = cv2.VideoCapture(2, cv2.CAP_DSHOW) 
        
        self.valid_sets=['train', 'valid']
        self.valid_counts = ['one', 'two', 'three', 'four', 'five']

        self.selected_set = tk.StringVar()      # from self.valid_sets   
        self.selected_count = tk.StringVar()    # from self.valid_counts
        self.countdown_time = tk.IntVar()         # Seconds of delay before first photo is taken once 'Burst' or 'Save' is clicked
        self.burst_num = tk.IntVar()            # Number of photos to take in the burst
        self.burst_delay = tk.IntVar()          # Seconds of delay between bursts
        self.save_type = tk.IntVar()            # 0 if single image, 1 if burst

        set, digit = args.output.split('/')[1:3]

        if (set in self.valid_sets) and (digit in self.valid_counts):
            self.selected_set.set(set)
            self.selected_count.set(digit)
        else:
            raise Exception("Invalid directory. See README.md for directory structure.")

        self.countdown_time.set(0)
        self.burst_num.set(10)
        self.burst_delay.set(0.5)

        # TODO: create directory if it does not exist. Create a method?
        self.set_output_path()
        self.check_dir()

        # Get current largest file number already in folder
        # This is done from self.set_output_path()    
        
        # Prepare an attribute for the image
        self.current_image = None 
        
        # Custom method to execute when window is closed.
        parent.protocol('WM_DELETE_WINDOW', self.destructor)

        # Countdown timer
        fr0 = ttk.Frame(self)
        fr0.pack(fill="both", expand=True, padx=5, pady=5)
        cntdwn_label = ttk.Label(fr0, text='Countdown (seconds):')
        cntdwn_label.pack(anchor='w', side=tk.LEFT, expand=True, padx=5, pady=5)
        cntdwn_spbox = ttk.Spinbox(fr0, textvariable=self.countdown_time, from_=0, to=10)
        cntdwn_spbox.pack(anchor='w', side=tk.LEFT, expand=True, padx=5, pady=5)

         # Button to save current image to file
        save_btn = ttk.Button(self, text="Save", command=self.save_single_image)
        save_btn.pack(fill="both", expand=True, padx=5, pady=5)

         # Burst Button
        burst_btn = ttk.Button(self, text="Burst", command=self.save_burst_images)
        burst_btn.pack(fill="both", expand=True, padx=5, pady=5)

        burst_settings_label = ttk.Label(self, text="Burst Settings:")
        burst_settings_label.pack(fill="both", expand=True, padx=5, pady=5)

        fr1 = ttk.Frame(self)
        fr1.pack(fill="both", expand=True, padx=5, pady=5)
        burst_num_label = ttk.Label(fr1, text='# Photos:')
        burst_num_label.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        burst_num_spbox = ttk.Spinbox(fr1, textvariable=self.burst_num, from_=0, to=10)
        burst_num_spbox.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        burst_delay_label = ttk.Label(fr1, text='Delay Between Bursts (seconds):')
        burst_delay_label.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        burst_num_spbox = ttk.Spinbox(fr1, textvariable=self.burst_delay, increment=0.1, from_=0, to=5)
        burst_num_spbox.pack(side=tk.LEFT, expand=True, padx=5, pady=5)

        fr2=ttk.Frame(self)
        fr2.pack(fill="both", expand=True, padx=5, pady=5)
        digit_label = ttk.Label(fr2, text='Digit:')
        digit_label.pack(anchor='w', side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        for i in self.valid_counts:
            ttk.Radiobutton(fr2,
                            text=i,
                            variable=self.selected_count,
                            value=i,
                            command=self.set_output_path).pack(anchor='w', side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        fr3=ttk.Frame(self)
        fr3.pack(fill="both", expand=True, padx=5, pady=5)
        set_label = ttk.Label(fr3, text='Set:')
        set_label.pack(anchor='w', side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        for i in self.valid_sets:
            ttk.Radiobutton(fr3,
                            text=i,
                            variable=self.selected_set,
                            value=i,
                            command=self.set_output_path).pack(anchor='w', side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

        # Label to display image
        self.panel = ttk.Label(self)  
        self.panel.pack(padx=5, pady=10)

        # start the display image loop
        self.video_loop()
    
    def check_dir(self):
        """Checks if self.output_path exists, and creates self.output_path if it doesn't exist.

        return: (bool) if path exists
        """
        return os.path.isdir(self.output_path)

    def make_dir(self):
        "creates directory at self.output_path"
        os.makedirs(self.output_path)
        print(f'[INFO] Created directory {self.output_path}')

    def get_output_path(self):
        """Gets latest data from radio buttons
            return: (str) path of desired output
        """
        return './digits/'+self.selected_set.get()+'/'+self.selected_count.get()+'/'
    
    def set_output_path(self):
        """Updates self.output_path and necessarily calls self.update_count()
        """
        self.output_path = self.get_output_path()
        self.update_count()

    def get_current_count(self):
        """Checks for existing images and returns current file number.
        
            folder(str): directory to search for existing images
            
            return: (int) the current highest number in jpg filename
                          or -1 if no jpg files present.
        """
        #TODO: implement this method
        self.check_dir()
        jpg_filenums = [int(os.path.splitext(filename)[0]) for filename in os.listdir(self.get_output_path()) if filename.endswith('.jpg')]
        return max(jpg_filenums, default=-1)
    
    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter 
            
            The image is processed using PIL: 
            - crop left and right to make image smaller
            - mirror 
            - convert to Tkinter image
            
            Uses after() to call itself again after 30 msec.
        
        """
        # read frame from video stream
        ok, frame = self.vs.read()  
        # frame captured without any errors
        if ok:  
            # convert colors from BGR (opencv) to RGB (PIL)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
            # convert image for PIL
            self.current_image = Image.fromarray(cv2image)  
            # camera is wide: crop 200 from left and right
            self.current_image = ImageOps.crop(self.current_image, (200,0,200,0)) 
            # mirror, easier to locate objects
            self.current_image = ImageOps.mirror(self.current_image) 
            # convert image for tkinterfor display
            imgtk = ImageTk.PhotoImage(image=self.current_image) 
            # anchor imgtk so it does not get deleted by garbage-collector
            self.panel.imgtk = imgtk  
             # show the image
            self.panel.config(image=imgtk)
        # do this again after 30 msec
        self.after(30, self.video_loop) 

    def update_count(self):
        """Accounts for first file of '00000000.jpg', sets self.count to the number of .jpg files in a directory, and prints this number to the console.
        """
        if self.check_dir():
            self.count = self.get_current_count() + 1
        else:
            self.count = 0
        print(f"[INFO] current count for {self.output_path} is {self.count}")

    def countdown(self, time_remaining):
        while time_remaining >= 0:
            print(time_remaining)
            time.sleep(1)
            time_remaining -= 1
        self.save_image()
    
    def take_bursts(self, countdown, num_bursts, time_delay):
        thread = threading.Thread(target=self.countdown, args=(countdown, ))
        thread.start()
        thread.join()
        num_bursts -= 1
        while num_bursts > 0:
            time.sleep(time_delay)
            self.save_image()
            num_bursts -= 1

    def save_single_image(self):
        threading.Thread(target=self.countdown, args=(self.countdown_time.get(), )).start()

    def save_burst_images(self):
        threading.Thread(target=self.take_bursts, args=(self.countdown_time.get(), self.burst_num.get(), self.burst_delay.get(), )).start()
        

    def save_image(self):
        """ Save current image to the file 
        
        Current image is saved to output_path using
        consecutive numbering in 
        zero-filled, eight-number format, e.g. 00000000.jpg.
        
        """
        #TODO: implement this method
        if self.check_dir() != True:
            self.make_dir()
        filename = f'{self.count:08}.jpg'
        self.current_image.save(self.output_path+filename)
        print(f"[INFO] saved file {filename}")
        self.update_count()

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # close OpenCV windows
        self.master.destroy() # close the Tk window

# construct the argument parse and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", default="digits/train/one/",
    help="path to output directory to store images (default: current folder")
args = parser.parse_args()

# start the app
print("[INFO] starting...")
gui = tk.Tk() 
gui.title("Image Capture")  
ImageCaptureFrame(gui, args.output)
gui.mainloop()
