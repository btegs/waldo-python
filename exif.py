#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# This is an application created by Brian Tegtmeier based on the requirements at
# https://gist.github.com/alwaysunday/db0b32f5ce0538afbb75ccf143adf116
#
# This application will use built-in libraries to download XML data from S3
# and then parse the XML data to get the image information (links, date)

# Import native libraries
from json import dump
from os import remove
from os.path import isdir, isfile
from shutil import copyfileobj
from sys import exit
from urllib2 import HTTPError, URLError, urlopen
from xml.dom.minidom import parseString

# Using local exifread library
import exifread

# Create new class
class OrganizeExif(object):

    # Initialize
    def __init__(self):

        # Reusable information
        self.doc = 'http://s3.amazonaws.com/waldo-recruiting' # Document URL
        self.jsonResults = 'photos-results.json' # Where final data is in JSON
        self.photoDict = {} # Dictionary to store photo data
        self.tempJPG = '/tmp/temp.jpg' # Temporary file for extracting EXIF

    # Read the remote document
    def read_doc(self):

        # Inform user of progress
        print('Reading remote document')

        # Get XML data (remote)
        photos = urlopen(self.doc)

        # Store data in variable and once stored, close the connection
        data = photos.read(); photos.close()

        # Get elements in Contents tags
        c = parseString(str(data)).getElementsByTagName('Contents')

        # Inform user of progress
        print('Now reading EXIF data for the images')

        # Now loop through Content tags
        # Also get an index starting at 1 for JSON or SQL storage
        for i, e in enumerate(c, 1):

            # Get the JPG name from the Key tag
            jpg = e.getElementsByTagName('Key')[0].childNodes[0].nodeValue

            # Create direct URL to JPG for the dictionary
            img =  '{0}/{1}'.format(self.doc, jpg)

            # Create secondary dictionary to store more values and add to main
            self.photoDict[i] = {'url':img, 'exif':{}}

            # Now run function to read EXIF data (send index and direct URL)
            if isdir('/tmp'):
                self.read_exif(i, img)
            else:
                exit('Temporary directory does not exist')

        # Once the loop has ended (this and read_exif), save results
        self.save_data()

    # Read EXIF data according to direct image URL
    def read_exif(self, index, img):

        # Remove temporary photo if it exists
        if isfile(self.tempJPG):
            remove(self.tempJPG)

        # Download image
        try:
            photo = urlopen(img)

        # If there was HTTP error, send response to console
        except HTTPError as e:

            # If forbidden or not found error
            if e.code == 403 or e.code == 404:
                print('File could not be reached, not adding EXIF')

        # If there was a URL error, send response to console
        except URLError as e:
            print('File could not be reached, not adding EXIF')

        # No errors, so continue
        else:

            # Open a temporary file
            with open(self.tempJPG, 'wb') as fp:

                # Write file data
                copyfileobj(photo, fp, 16*1024)

            # If file exists, continue
            if isfile(self.tempJPG):

                # Open the temporary file again
                with open(self.tempJPG, 'rb') as f:

                    # Get the EXIF tags
                    tags = exifread.process_file(f)

                    # Now loop them
                    for tag in tags.keys():

                        # Update photoDict dictionary with EXIF tags
                        self.photoDict[index]['exif'][tag] = tags[tag]

            # If not, exit
            else:
                exit('File was not copied to temporary directory')


    # Take photoDict with the saved EXIF data and output to a file
    # This runs after the read_doc and read_exif loops
    def save_data(self):

        # Inform user of progress
        print('Now saving results in JSON format')

        # Remove any previous results
        if isfile(self.jsonResults):
            remove(self.jsonResults)

        # Save to local JSON file
        with open(self.jsonResults, 'w') as j:
            dumps(self.photoDict, j)


if __name__ == '__main__':
    OrganizeExif().read_doc()
