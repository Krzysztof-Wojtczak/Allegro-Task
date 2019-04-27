import cv2
import numpy as np
import random
from math import ceil

class Mozaika:
	"""Class Mozaika takes 1 required attribute: list of images in cv2 format,
	3 optional attributes: random image positioning, width of output image, height of output image.
	Output image is stored in variable 'output_image'.
	Class is looking for the least proportional image and returns it in (0,0) - top left corner if no random positioning"""
	def __init__(self, image_list, losowo, w=2048, h=2048):
		self.losowo = losowo # defines whether image position is random
		self.w = int(w) # width of output image
		self.h = int(h) # height of output image
		self.output_image = 0

		# variables are stored in 3 lists: image_names for sorted name strings, image_list for image in cv2 format,
		# image_dict for height and width for every image
		self.image_names = [] # Names of images

		self.image_list = image_list # list of files (images)
		if self.losowo == 1:
			random.shuffle(self.image_list)

		for i in range(len(self.image_list)):
			self.image_names.append(f"img{i}")

		self.image_dict = {}
		for image in range(len(self.image_list)):
			key = self.image_names[image]
			h, w = self.image_list[image].shape[:2] # height, width of each image
			self.image_dict[key] = [h, w]

		self.how_many_images()

	def how_many_images(self):
		number_of_images = len(self.image_dict) # checks how many images is given
		if number_of_images == 1:
			self.make_square()
			self.resize_huge_image()
		elif number_of_images == 2:
			self.rectangle_image(2)
		elif number_of_images == 3 or number_of_images == 4:
			self.grid2x2()
		elif number_of_images > 4:
			self.grid3x3()

	def rectangle_image(self, images=1): # the least proportional image will become a rectangle
		ratios = []
		self.check_ratio() 
		ratios = [e[2] for e in list(self.image_dict.values())] # getting image ratio(s)
		max_ratio = max(ratios)

		for name, value in self.image_dict.items(): # finding highest/longest image
			if value[2] == max_ratio:
				name_max = name
				list_index_max = self.image_names.index(name)
		
		if images == 1: # method is called for 1 image
			if self.image_dict[name_max][1] > self.image_dict[name_max][0]: # checks if width or height of the image is greater
				return self.make_horizontal_rectangle(name_max, list_index_max, max_ratio), 0, name_max # return image, horizontal/vertical, name of image 
				
			elif self.image_dict[name_max][1] < self.image_dict[name_max][0]:
				return self.make_vertical_rectangle(name_max, list_index_max, max_ratio), 1, name_max
				

		elif images == 2: #it will only work if there are 2 images, creates mosaic of 2 images
			i = 0
			if self.image_dict[name_max][1] > self.image_dict[name_max][0]:
				for name, value in self.image_dict.items(): # checks ratio the least proportional image and decides
					self.make_horizontal_rectangle(name, i, value[2]) # whether images should be vertical or horizontal
					i += 1
				self.merge_two_images_horizontally() # merge 2 images with minimum quality loss
			elif self.image_dict[name_max][1] < self.image_dict[name_max][0]:
				for name, value in self.image_dict.items():
					self.make_vertical_rectangle(name, i, value[2])
					i += 1
				self.merge_two_images_vertically()

	def check_ratio(self):
		# appends to dictionary height to width (or width to height) ratio
		i = 0
		for image in self.image_dict:
			if self.image_dict[image][0] > self.image_dict[image][1]:
				ratio = self.image_dict[image][0]/self.image_dict[image][1]
			else:
				ratio = self.image_dict[image][1]/self.image_dict[image][0]
			self.image_dict[image].append(ratio)
		

	def make_square(self):
		# centralizes picture and cuts it so it becomes a square
		i = 0
		for image in self.image_dict.values(): # check in dictionary for width/height
			if image[0] > image[1]:
				cut = int((image[0] - image[1])/2)
				self.image_list[i] = self.image_list[i][cut : -cut, :image[1]] # numpy operation on image
			elif image[0] < image[1]:
				cut = int((image[1] - image[0])/2)
				self.image_list[i] = self.image_list[i][:image[0], cut : -cut]
			i += 1

	def make_horizontal_rectangle(self, name, list_index, ratio):
		# if ratio == 2, it's perfect rectangle. Otherwise it is cut to this ratio
		if ratio < 2:
			cut = int(  (self.image_dict[name][0] - (self.image_dict[name][0] / (2/ratio)))/2  )
			return self.image_list[list_index][cut : -cut, : self.image_dict[name][1]]	
		elif ratio > 2:
			if self.image_dict[name][1] > self.image_dict[name][0]:
				cut = int(  (self.image_dict[name][0] - (self.image_dict[name][0] / (ratio/2)))/2  )
				return self.image_list[list_index][: self.image_dict[name][0], cut : -cut]
							
	def make_vertical_rectangle(self, name, list_index, ratio):
		if ratio < 2:
			cut = int(  (self.image_dict[name][1] - (self.image_dict[name][1] / (2/ratio)))/2  )
			return self.image_list[list_index][: self.image_dict[name][0], cut : -cut]
		elif ratio > 2:
			cut = int(  (self.image_dict[name][1] - (self.image_dict[name][1] / (ratio/2)))/2  )
			return self.image_list[list_index][cut : -cut, : self.image_dict[name][1]]

	def merge_two_images_horizontally(self):
		# method takes 2 horizontal images and merges them
		self.image_list[0] = cv2.resize(self.image_list[0], (self.w, int(self.h/2)))
		self.image_list[1] = cv2.resize(self.image_list[1], (self.w, int(self.h/2)))
		self.output_image = np.concatenate((self.image_list[0], self.image_list[1]), axis=0)		

	def merge_two_images_vertically(self):
		# method takes 2 vertical images and merges them
		self.image_list[0] = cv2.resize(self.image_list[0], (int(self.w/2), self.h))
		self.image_list[1] = cv2.resize(self.image_list[1], (int(self.w/2), self.h))
		self.output_image = np.concatenate((self.image_list[0], self.image_list[1]), axis=1)

	def resize_huge_image(self):
		# returns one image of the size of the output image
		self.output_image = cv2.resize(self.image_list[0], (self.w, self.h))

	def resize_big_image(self, index):
		# returns one image of 2/3 width/height of the output image
		name = self.image_names[index]
		return cv2.resize(self.image_list[index], (int(self.w/(3/2)), int(self.h/(3/2)))), name

	def resize_medium_image(self, index):
		# returns one image of 1/2 width/height of the output image
		return cv2.resize(self.image_list[index], (int(self.w/2), int(self.h/2)))
		
	def resize_small_image(self, index):
		# returns one image of 1/3 width/height of the output image
		return cv2.resize(self.image_list[index], (int(self.w/3), int(self.h/3)))

	def grid2x2(self):
		placement = self.put_image2x2() # defines where to put images
		decrease_h = ceil(2*(self.h/2 - int(self.h/2))) # decrease size of output image due to roundings, so there are no black spaces
		decrease_w = ceil(2*(self.w/2 - int(self.w/2)))
		vis = np.zeros((self.h - decrease_h, self.w - decrease_w, 3), np.uint8) # smaller image due to roundings
		num = 0
		for i in range(0,2): # grid 2x2, so 4 squares to fill
			for k in range(0,2):
				vis[i*int(self.h/2) : (i+1)*int(self.h/2), k*int(self.w/2) : (k+1)*int(self.w/2)] = placement[num]
				num += 1
		self.output_image = cv2.resize(vis, (self.w, self.h)) # optional, scales image to match requirements accurately

	def grid3x3(self):
		placement = self.put_image3x3() # defines where to put images
		decrease_h = ceil(3*(self.h/3 - int(self.h/3))) # decrease size of output image due to roundings, so there are no black spaces
		decrease_w = ceil(3*(self.w/3 - int(self.w/3)))
		vis = np.zeros((self.h - decrease_h, self.w - decrease_w, 3), np.uint8) # smaller image due to roundings
		num = 0
		for i in range(0,3): # grid 3x3, so nine squares to fill
			for k in range(0,3):
				vis[i*int(self.h/3) : (i+1)*int(self.h/3), k*int(self.w/3) : (k+1)*int(self.w/3)] = placement[num]
				num += 1
		self.output_image = cv2.resize(vis, (self.w, self.h)) # optional, scales image to match requirements accurately

	def put_image2x2(self):
		placement = [0]*4 # it'll store images
		if len(self.image_names) == 3: # to do if there are 3 images
			rect_image, vertical, name = self.rectangle_image()
			index = self.image_names.index(name)
			self.image_list.pop(index) # deleting rectangle image from image_list, so there will be no duplicates
			other_position = [e for e in range(4)] # 4 possibilities to put 1 image
			if vertical: # 1 vertical image
				rect_image = cv2.resize(rect_image, (int(self.w/2), self.h))
				if self.losowo == 1:
					position = random.randrange(0,2) # choose random position for image
				else:
					position = 0 					# or fixed position
				other_position.remove(position) # rectangle image takes 2 places
				other_position.remove(position + 2)
				placement[position] = rect_image[:int(self.h/2), :int(self.w/2)]
				placement[position + 2] = rect_image[int(self.h/2):self.h, :int(self.w/2)]
			else: # 1 horizontal image
				rect_image = cv2.resize(rect_image, (self.w, int(self.h/2)))
				if self.losowo == 1:
					position = random.randrange(0,3,2) # possible positions are top left and bottom left
				else:
					position = 0
				other_position.remove(position)
				other_position.remove(position + 1)
				placement[position] = rect_image[:int(self.h/2), :int(self.w/2)]
				placement[position + 1] = rect_image[:int(self.h/2), int(self.w/2):self.w]

			num = 0
			for i in other_position: # after puting bigger image fill other places with smalles images
				placement[i] = self.resize_medium_image(num)
				num += 1
		else: # 4 images
			for i in range(len(self.image_list)): 
				placement[i] = self.resize_medium_image(i) # fill 4 places with medium images

		return placement

	def put_image3x3(self):
		placement = [0]*9
		img2x = [] # list of rectangle images
		img4x = [] # list of big square images
		num_img = len(self.image_names)
		var = 0
		var1 = 0
		while num_img < 9:
			if 9 - num_img < 3: # big image can't fit, increase number of takes space by making rectangles
				img2x.append(self.rectangle_image())
				remove_image = img2x[var][2] # get image name
				self.image_dict.pop(remove_image) # delete image to avoid duplicates (there are 3 places where it is)
				index = self.image_names.index(remove_image)
				self.image_names.remove(remove_image)
				self.image_list.pop(index)
				num_img += 1
				var += 1
			else:
				img4x.append(self.resize_big_image(0))
				remove_image = img4x[var1][1] # get image name
				self.image_dict.pop(remove_image) # delete image to avoid duplicates
				index = self.image_names.index(remove_image)
				self.image_names.remove(remove_image)
				self.image_list.pop(index)
				var1 += 1
				num_img += 3
		
		biash = ceil(self.h*(2/3) - int(self.h*(2/3))) # image can be to big to fit in square, need to decrease it
		biasw = ceil(self.w*(2/3) - int(self.w*(2/3)))
		other_position = set([e for e in range(9)]) # 9 possible places for one image
		
		for img in img4x: # takes big image and tries to fit it
			square_img = img[0]
			other_position, position = self.find_big_position(other_position) # find possible position
			placement[position] = square_img[:int(self.h/3), :int(self.w/3)] # top left corner of the image
			placement[position + 1] = square_img[:int(self.h/3), int(self.w/3):int(self.w*(2/3)) - biasw] # top right corner
			placement[position + 3] = square_img[int(self.h/3):int(self.h*(2/3)) - biash, :int(self.w/3)] # bottom left corner
			placement[position + 4] = square_img[int(self.h/3):int(self.h*(2/3)) - biash, int(self.w/3):int(self.w*(2/3)) - biasw] # bottom right corner

		for img in img2x: # takes rectangles and tries to fit them
			rect_image, vertical = img[:2] # check if rectangle is vertical
			if vertical:
				rect_image = cv2.resize(rect_image, (int(self.w/3), int(self.h*(2/3))))
				other_position, position = self.find_vertical_position(other_position) # checks for vertical possibilities
				placement[position] = rect_image[:int(self.h/3), :int(self.w/3)]
				placement[position + 3] = rect_image[int(self.h/3):int(self.h*(2/3)) - biash, :int(self.w/3)]
			else:
				rect_image = cv2.resize(rect_image, (int(self.w*(2/3)), int(self.h/3)))
				other_position, position = self.find_horizontal_position(other_position) # checks for horizontal possibilities
				placement[position] = rect_image[:int(self.h/3), :int(self.w/3)]
				placement[position + 1] = rect_image[:int(self.h/3), int(self.w/3):int(self.w*(2/3)) - biasw]

		num = 0
		for i in other_position: # after puting bigger image fill other places with smaller images
			placement[i] = self.resize_small_image(num)
			num += 1

		return placement

	def find_big_position(self, avaiable_pos):
		# find position for 2/3 width/height image
		myList = avaiable_pos
		mylistshifted=[x-1 for x in myList]
		possible_position = [0,1,3,4] # only possible possisions for big image
		intersection_set = list(set(myList) & set(mylistshifted) & set(possible_position))
		if self.losowo == 1:
			position = random.choice(intersection_set)
		else:
			position = intersection_set[0]
		myList.remove(position) # removes places from other_position, so no other image can take these places
		myList.remove(position + 1)
		myList.remove(position + 3)
		myList.remove(position + 4)
		return myList, position

	def find_horizontal_position(self, avaiable_pos):
		# find position for horizontal rectangle image
		myList = avaiable_pos
		mylistshifted=[x-1 for x in myList]
		possible_position = [0,1,3,4,6,7] # positions where image is not cut in half
		intersection_set = list(set(myList) & set(mylistshifted) & set(possible_position))
		if self.losowo == 1:
			position = random.choice(intersection_set)
		else:
			position = intersection_set[0]
		myList.remove(position) # removes places from other_position, so no other image can take these places
		myList.remove(position + 1)
		return myList, position

	def find_vertical_position(self, avaiable_pos):
		# find position vertical rectangle image
		myList = avaiable_pos
		mylistshifted=[x-3 for x in myList]
		possible_position = [e for e in range(6)] # positions where image is not cut in half
		intersection_set = list(set(myList) & set(mylistshifted) & set(possible_position))
		if self.losowo == 1:
			position = random.choice(intersection_set)
		else:
			position = intersection_set[0]
		myList.remove(position) # removes places from other_position, so no other image can take these places
		myList.remove(position + 3)
		return myList, position



	


