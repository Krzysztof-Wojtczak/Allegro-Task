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

    def make_rectangle1x2(self, vertical=True):
        ratio = self.ratio
        if vertical:
            if ratio < 2:
                cut = int((self.width - ratio * self.width / 2) / 2)
                return Image(self._image[: self.height, cut : -cut])
            elif ratio > 2:
                cut = int((self.width - 2 * self.width / ratio) / 2)
                return Image(self._image[cut : -cut, : self.width])
            return self
        else:
            if ratio < 2:
                cut = int((self.height - ratio * self.height / 2) / 2)
                return Image(self._image[cut : -cut, : self.width])
            elif ratio > 2:
                if self.width > self.height:
                    cut = int((self.height - 2 * self.height / ratio) / 2)
                    return Image(self._image[: self.height, cut : -cut])
            return self        

    def resize(self, dimensions):
        return Image(cv2.resize(self._image, dimensions))

    def final_resize(self, dimensions):
        return cv2.resize(self._image, dimensions)

    def merge(self, other, horizontally=True):
        axis = 0 if horizontally else 1
        # print(self._image.shape)
        # print(other._image.shape)
        return Image(np.concatenate([self._image, other._image], axis=axis))


class Mozaika:
    def __init__(self, image_list, losowo=1, w=512, h=512):
        self.losowo = losowo # defines whether image position is random
        self.w = int(w) # width of output image
        self.h = int(h) # height of output image
        self.output_image = 0

        self.images = [Image(i) for i in image_list]
        if self.losowo == 1:
            random.shuffle(self.images)
        # for i in range(2):
        #     self.images[i] =  self.images[i].resize(self.medium_image)
        self.how_many_images()

    # @property
    # def huge_image(self):
    #     return self.w, self.h

    @property
    def big_image(self):
        return int(self.w*2/3), int(self.h*2/3)

    @property
    def medium_image(self):
        return int(self.w/2), int(self.h/2)
        
    @property
    def small_image(self):
        return int(self.w/3), int(self.h/3)

    @property
    def big_rectangle_image(self, vertical=True):
        if vertical:
            return int(self.w/2), self.h
        else:
            return self.w, int(self.h/2)

    @property
    def small_rectangle_image(self, vertical=True):
        if vertical:
            return int(self.w/3), int(self.h*2/3)
        else:
            return int(self.w*2/3), int(self.h/3)

    def how_many_images(self):
        number_of_images = len(self.images) # checks how many images is given
        if number_of_images == 1:
            self.output_image = self.images[0].square().final_resize(dimensions=(self.w, self.h))
        elif 2 <= number_of_images <= 4:
            pass
            # self.output_image = self.images[0].merge(self.images[1]).final_resize(dimensions=(self.w, self.h))
        elif number_of_images > 4:
            self.output_image = self.images.grid3x3().resize(dimensions=(self.w, self.h))

    def find_rectangle_image(self):
        enum_largest = max(enumerate(self.images), key=lambda i: i[1].ratio)
        largest = enum_largest[1]
        maxratio = largest.ratio

        if largest.width > largest.height:
            return largest.make_rectangle1x2(vertical=False), 0, enum_largest[0]
        else: #self.width < self.height:
            return largest.make_rectangle1x2(vertical=True), 1, enum_largest[0]

    def put_image2x2(self):
        placement = [0]*4
        if len(self.images) == 2:
            image1, vertical, num = self.find_rectangle_image()
            image2 = [e for e in self.images if self.images.index(e) != num][0]
            return image2



if __name__ == "__main__":
    image_names = ["img1.jpg", 'img2.jpg']
    image_list = [cv2.imread(e) for e in image_names]
    mozaika = Mozaika(image_list)
    # print(mozaika.find_rectangle_image()[0]._image)
    cv2.imshow("i", mozaika.put_image2x2()._image)
    cv2.waitKey(0)