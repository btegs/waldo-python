# EXIF reading application for Waldo Photos
This Python based application will remotely contact the Amazon S3 instance, create a Python dictionary to store the photo indices, URLs, and EXIF data. This is accomplished by looping through the provided XML document, grabbing each image to a temporary directory, parsing the EXIF data, and storing it back into the Python dictionary. The indicies for the Python dictionary start at 1 for easy reference and it will be handy if they had to be imported into a SQL database since the indicies start at 1 in SQL.

I have heavily commented the code to explain my methodology and also provided print messages to the console to alert the user when the next stage is happening. I used system libraries for the majority of the code and only one 3rd party library (exifread) was used and is referenced locally.

There are some checks to make sure the image isn't giving a 403 or 404 error and if there is an error of that type, the EXIF fields for that associated image are left blank. This test is currently saving data to a local JSON document, but storage in a SQL (MySQL, SQLite) or NoSQL (MongoDB) can be added if requested.

NOTE: When running the script to contact the S3 instance, I was getting 403 errors meaning the file was forbidden. When running your tests, you may run across an issue where the request times out from the server and sometimes it will not. Either way, if you comb through the code, you will see the methodology of getting the images, storing the data, and exporting them into a format like JSON that can be read and stored through any programming language and inserted into a database.


# Running
Open up a Mac or Linux terminal and run "python2.7 exif.py" or "./exif.py" to use the locally installed Python 2.7 runtime on the machine.
