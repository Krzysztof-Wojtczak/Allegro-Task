Mozaika.py takes list of images in cv2 format and returns mosaic. Server.py takes URLs,
downloads images, decodes them to cv2 format and creates a list of images. Files must be in the same directory.

Required libraries:
- http.server
- numpy
- opencv-python

Start cmd where server.py is located. Mozaika.py should be in the same location.
Run server.py with python.
In your browser type:
http://localhost:8080/mozaika?losowo=Z&rozdzielczosc=XxY&zdjecia=URL1,URL2,URL3...

where:
losowo - optional parameter, if Z = 1 images places are random. Otherwise bigger images are placed in (0,0) - top left corner, smaller images fill empty space. 
rozdielczosc - optional parameter, defines width and height. Default is 2048x2048
URL1,URL2,URL3... image adresses separated by commas (no empty space), that will be in mosaic.
