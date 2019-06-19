import cv2
import numpy as np
import random
from math import ceil


class Image:
    def __init__(self, image):
        self._image = image
        self.height, self.width = image.shape[:2]

    @property
    def ratio(self):
        return max(self.height, self.width) / min(self.height, self.width)

    def square(self):
        if self.height > self.width:
            cut = int((self.height - self.width) / 2)
            return Image(self._image[cut : -cut, :self.width])
        else:
            cut = int((self.width - self.height) / 2)
            return Image(self._image[:self.height, cut : -cut])

    def make_horizontal_rectangle(self):
        ratio = self.ratio
        if ratio < 2:
            cut = int((self.height - ratio * self.height / 2) / 2)
            return Image(self._image[cut : -cut, : self.width])
        elif ratio > 2:
            if self.width > self.height:
                cut = int((self.height - 2 * self.height / ratio) / 2)
                return Image(self._image[: self.height, cut : -cut])
        return self

    def make_vertical_rectangle(self):
        ratio = self.ratio
        if ratio < 2:
            cut = int((self.width - ratio * self.width / 2) / 2)
            return Image(self._image[: self.height, cut : -cut])
        elif ratio > 2:
            cut = int((self.width - 2 * self.width / ratio) / 2)
            return Image(self._image[cut : -cut, : self.width])
        return self

    def resize(self, width, height):
        return cv2.resize(self._image, (width, height))

    def merge(self, other, horizontally=True):
        axis = 0 if horizontally else 1
        return Image((self._image, other._image), axis=axis)


class Mozaika:
    def __init__(self, image_list, losowo=1, w=512, h=512):
        self.losowo = losowo # defines whether image position is random
        self.w = int(w) # width of output image
        self.h = int(h) # height of output image
        self.output_image = 0

        self.images = [Image(i) for i in image_list]
        if self.losowo == 1:
            random.shuffle(self.images)
        self.how_many_images()

    def how_many_images(self):
        number_of_images = len(self.images) # checks how many images is given
        if number_of_images == 1:
            self.output_image = self.images[0].square().resize(self.w, self.h)
        elif 2 <= number_of_images <= 4:
            self.grid2x2()
        elif number_of_images > 4:
            self.grid3x3()

    def rectangle_image(self):
        largest = max(self.images, key=lambda i: i.ratio)
        maxratio = largest.ratio

        if images == 1:
            if largest.width > largest.height:
                return largest.make_horizontal_rectangle(), 0
            elif self.width < self.height:
                return largest.make_vertical_rectangle(), 1

    def resize_big_image(self, index):
        # returns one image of 2/3 width/height of the output image
        self.images[index].resize(int(self.w/(3/2)), int(self.h/(3/2)))

    def resize_medium_image(self, index):
        # returns one image of 1/2 width/height of the output image
        return cv2.resize(self.image_list[index], (int(self.w/2), int(self.h/2)))
        
    def resize_small_image(self, index):
        # returns one image of 1/3 width/height of the output image
        return cv2.resize(self.image_list[index], (int(self.w/3), int(self.h/3)))


if __name__ == "__main__":
    image_names = ["img1.jpg", "img2.jpg"]
    image_list = [cv2.imread(e) for e in image_names]
    mozaika = Mozaika(image_list)
    cv2.imshow("i", mozaika.output_image)
    cv2.waitKey(0)