from http.server import HTTPServer, BaseHTTPRequestHandler
import re
from urllib.request import urlopen
import cv2
import numpy as np
from mozaika import Mozaika


class Serv(BaseHTTPRequestHandler):
	def do_GET(self):
		w = 2048 # default width
		h = 2048 # default height
		losowo = 1 # random image placement = true
		urls = [] # images URLs
		if self.path.startswith("/mozaika?"): # keyword for getting mosaic, URL should be put in format:
			parameters = self.path.split("&") # http://localhost:8080/mozaika?losowo=Z&rozdzielczosc=XxY&zdjecia=URL1,URL2,URL3..
			for par in parameters:
				if par.find("losowo") == -1:
					pass
				else:
					losowo_index = par.find("losowo")
					try:
						losowo = int(par[losowo_index + 7])
					except:
						pass

				if par.find("rozdzielczosc") == -1:
					pass
				else:
					try:
						w, h = re.findall('\d+', par)
					except:
						pass

				if par.find("zdjecia=") == -1:
					pass
				else:
					urls = self.path[self.path.find("zdjecia=") + 8 :]
					urls = urls.split(",")
					
			try:
				image_list = create_images_list(urls)	
				# call mosaic creator
				# 1 required attribute: list of images in cv2 format,
				# 3 optional attributes: random image positioning, width of output image, height of output image
				mozaika = Mozaika(image_list, losowo, w, h)
				img = mozaika.output_image # store output image

				f = cv2.imencode('.jpg', img)[1].tostring() # encode to binary format
				self.send_response(200)
				self.send_header('Content-type', 'image/jpg')
			except:
				self.send_response(404)
			self.end_headers()
			self.wfile.write(f) # send output image
				#return


def url_to_image(url):
	# gets image from URL and converts it to cv2 color image format
	resp = urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype="uint8")
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	return image


def create_images_list(urls):
	# takes URLs list and creates list of images
	image_list = []
	for url in urls:
		image = url_to_image(url)
		if image is not None:
			image_list.append(image)
	return image_list
		


httpd = HTTPServer(("localhost", 8080), Serv)
httpd.serve_forever()



