"""

New Utility: Automated Noise Filter & Image Cleaner (src/data_cleaner.py)This script uses a low-pass Butterworth filter to smooth out random signal spikes in your sensor telemetry, and applies a Gaussian blur to your thermal images to remove scanner artifacts before annotation occurs.
"""

import numpy as np
import cv2
from scipy.signal import butter, filtfilt

class DataCleaner:
    @staticmethod
    def filter_sensor_noise(signal_data, cutoff=0.2, order=2):
        """
        Applies a digital low-pass Butterworth filter to smooth out high-frequency 
        electrical noise from physical sensor telemetry.
        """
        if len(signal_data) < 10:
            return signal_data
        try:
            b, a = butter(order, cutoff, btype='low', analog=False)
            return filtfilt(b, a, signal_data)
        except Exception:
            return signal_data

    @staticmethod
    def clean_thermal_image(image_path):
        """
        Loads a thermal image matrix and applies a localized Gaussian filter 
        to eliminate speckle noise and pixel artifacts before hotspot mapping.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None
        # 5x5 Kernel size with automated standard deviation calculation
        return cv2.GaussianBlur(img, (5, 5), 0)
