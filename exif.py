#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# This is an application created by Brian Tegtmeier based on the requirements at
# https://gist.github.com/alwaysunday/db0b32f5ce0538afbb75ccf143adf116
#
# This application will use built-in libraries to download XML data from S3
# and then parse the XML data to get the image information (links, date)

# Import native libraries
from json import dump, load
from os import remove
from os.path import isdir, isfile
from pprint import pprint, isreadable
from shutil import copyfileobj
from sys import exit
from urllib2 import HTTPError, URLError, urlopen
from xml.dom.minidom import parseString

# Import local 3rd party EXIF library
import exifread

# Create new class
class OrganizeExif(object):

    # Initialize
    def __init__(self):

        # Reusable information
        self.doc = 'http://s3.amazonaws.com/waldo-recruiting'  # Document URL
        self.jsonResults = 'photos-results.json'  # Where final data is in JSON
        self.photoDict = {}  # Dictionary to store photo data
        self.tempJPG = '/tmp/temp.jpg'  # Temporary file for extracting EXIF

    # Read the remote document
    def read_doc(self):

        # Inform user of progress
        print('Reading remote document.')

        # Get XML data from remote source. Sometimes the server times out and
        # gives a "socket.error: [Errno 104] Connection reset by peer" error
        photos = urlopen(self.doc)

        # Store data in variable and once stored, close the connection
        data = photos.read()
        photos.close()

        # Get elements in Contents tags
        c = parseString(str(data)).getElementsByTagName('Contents')

        # Inform user of progress
        print('Now reading EXIF data for the images. Please wait.')

        # Now loop through Content tags
        # Also get an index starting at 1 for JSON or SQL storage
        for i, e in enumerate(c, 1):

            # Get the JPG name from the Key tag
            jpg = e.getElementsByTagName('Key')[0].childNodes[0].nodeValue

            # Create direct URL to JPG for the dictionary
            img = '{0}/{1}'.format(self.doc, jpg)

            # Create secondary dictionary to store more values and add to main
            self.photoDict[i] = {'url': img, 'exif': {}}

            # Now run function to read EXIF data (send index and direct URL)
            if isdir('/tmp'):
                self.read_exif(i, img)
            else:
                exit('Temporary directory does not exist.')

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
                print('{0} could not be reached ({1}) and will have no EXIF data.'.format(
                    img, e.code))

        # If there was a URL error, send response to console
        except URLError as e:
            print('{0} could not be reached and will have no EXIF data.'.format(img))

        # No errors, so continue
        else:

            # Open a temporary file
            with open(self.tempJPG, 'wb') as t:

                # Write file data
                copyfileobj(photo, t, (16 * 1024))

            # If file exists, continue
            if isfile(self.tempJPG):

                # Open the temporary file again
                with open(self.tempJPG, 'rb') as j:

                    # Get the EXIF tags
                    tags = exifread.process_file(j)

                    # Now loop them
                    for tag in tags.keys():

                        # Update photoDict dictionary with EXIF tags
                        self.photoDict[index]['exif'][tag] = tags[tag]

            # If not, exit
            else:
                exit('File was not copied to temporary directory.')

    # Take photoDict with the saved EXIF data and output to a file
    # This runs after the read_doc and read_exif loops
    def save_data(self):

        '''
        Currently saving as JSON causes issues if there are certain characters
        inside the value. For the future, data may be better stored in a SQL or
        NoSQL database or closer inspection of escaping or replacing certain
        characters if it has to be stored in JSON.

        In the future, a script like this may take the EXIF data and continue
        to work with the Python object without the need to export to a local
        file and will simply go the extra step of digging deeper into the EXIF
        data and utilizing each tag individually.

        # Inform user of progress
        print('Now saving results in JSON format.')

        # Remove any previous results
        if isfile(self.jsonResults):
            remove(self.jsonResults)

        # Save to local JSON file and also handle unicode data
        # Also make it readable for testing with indentation
        # NOTE: This currently has issues with characters like [ and ]
        with open(self.jsonResults, 'w') as j:
            dump(self.photoDict, j, ensure_ascii=False,
                 sort_keys=True, indent=4).encode('utf-8', 'ignore')

        # If JSON file now exists, check
        if isfile(self.jsonResults):

            # If JSON file validates
            try:
                with open(self.jsonResults, 'r') as jd:
                    jsonData = load(jd)
                    print('JSON results available at {0}.'.format(self.jsonResults))

            # Invalid JSON file
            except ValueError as e:
                exit('JSON not saved correctly.')
        '''

        # Instead of a local JSON file, data will be simply displayed in the
        # console via pretty print to show the results of the data structure
        if isreadable(self.photoDict):
            pprint(self.photoDict)
        else:
            exit('Photo dictionary is not readable.')


if __name__ == '__main__':
    OrganizeExif().read_doc()
