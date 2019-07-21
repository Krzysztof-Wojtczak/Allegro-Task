import cv2
import numpy as np
import random
from functools import reduce


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
            return Image(self._image[cut: -cut, :self.width])
        else:
            cut = int((self.width - self.height) / 2)
            return Image(self._image[:self.height, cut: -cut])

    # check later if it works for images with high ratio ver/hor
    def make_rectangle1x2(self, vertical=True):
        ratio = self.ratio
        if vertical:
            if ratio < 2:
                cut = int((self.width - ratio * self.width / 2) / 2)
                return Image(self._image[: self.height, cut: -cut])
            elif ratio > 2:
                cut = int((self.width - 2 * self.width / ratio) / 2)
                return Image(self._image[cut: -cut, : self.width])
            return self
        else:
            if ratio < 2:
                cut = int((self.height - ratio * self.height / 2) / 2)
                return Image(self._image[cut: -cut, : self.width])
            elif ratio > 2:
                if self.width > self.height:
                    cut = int((self.height - 2 * self.height / ratio) / 2)
                    return Image(self._image[: self.height, cut: -cut])
            return self

    def resize(self, dimensions, final=False):
        if final:  # returns numpy array
            return cv2.resize(self._image, dimensions)
        else:  # returns Image class object
            return Image(cv2.resize(self._image, dimensions))

    def split(self, vertical=True):
        if vertical:
            return Image(self._image[: int(self.height/2), :]), Image(self._image[int(self.height/2): self.height, :])
        else:
            return Image(self._image[:, : int(self.width/2)]), Image(self._image[:, int(self.width/2): self.width])

    def merge(self, other, horizontally=True):
        axis = 0 if horizontally else 1
        return Image(np.concatenate([self._image, other._image], axis=axis))


class Mozaika:
    def __init__(self, image_list, losowo=1, w=512, h=512):
        self.losowo = losowo  # defines whether image position is random
        self.w = int(w)  # width of output image
        self.h = int(h)  # height of output image
        self.output_image = 0

        self.images = [Image(i) for i in image_list]
        if self.losowo == 1:
            random.shuffle(self.images)

        self.how_many_images()

    @property
    def big_image(self):
        return int(self.w*2/3), int(self.h*2/3)

    @property
    def medium_image(self):
        return int(self.w/2), int(self.h/2)

    @property
    def small_image(self):
        return int(self.w/3), int(self.h/3)

    def big_rectangle_image(self, vertical=True):
        if vertical:
            return int(self.w/2), self.h
        else:
            return self.w, int(self.h/2)

    def small_rectangle_image(self, vertical=True):
        if vertical:
            return int(self.w/3), int(self.h*2/3)
        else:
            return int(self.w*2/3), int(self.h/3)

    def how_many_images(self):
        number_of_images = len(self.images)  # checks how many images is given
        if number_of_images == 1:
            self.output_image = self.images[0].square().resize(dimensions=(self.w, self.h), final=True)
        elif 2 <= number_of_images <= 4:
            self.output_image = self.merge2x2().resize(dimensions=(self.w, self.h), final=True)
        elif number_of_images > 4:
            self.output_image = self.merge3x3().resize(dimensions=(self.w, self.h), final=True)

    def merge2x2(self):
        placement = self.put_image2x2()
        row1 = placement[0].merge(placement[1], horizontally=False)
        row2 = placement[2].merge(placement[3], horizontally=False)
        return row1.merge(row2, horizontally=True)

    def merge3x3(self):
        placement = self.put_image3x3()
        row1 = reduce(lambda x, y: x.merge(y, horizontally=False), placement[:3])
        row2 = reduce(lambda x, y: x.merge(y, horizontally=False), placement[3:6])
        row3 = reduce(lambda x, y: x.merge(y, horizontally=False), placement[6:9])
        rows = row1.merge(row2, horizontally=True)
        rows = rows.merge(row3, horizontally=True)
        return rows

    def put_image2x2(self):
        placement = [0]*4 # four possible image positions
        # 2 images
        if len(self.images) == 2:
            image1, vertical, num = self.find_rectangle_image()  # finds image with greatest ratio and shapes it 1x2
            # vertical is boolean value, num is an index of image with highest ratio
            image2 = [e for e in self.images if self.images.index(e) != num][0]
            image2 = image2.make_rectangle1x2(vertical=vertical) # shaping second image
            image1 = image1.resize(self.big_rectangle_image(vertical=vertical))
            image2 = image2.resize(self.big_rectangle_image(vertical=vertical))

            if self.losowo == 1:  # find_rectangle fixes image position, it shuffles them again
                shuffle = random.randrange(0, 2)
                if shuffle:
                    image1, image2 = image2, image1

            if vertical:
                placement[0], placement[2] = image1.split(vertical=True)
                placement[1], placement[3] = image2.split(vertical=True)
            else:
                placement[0], placement[1] = image1.split(vertical=False)
                placement[2], placement[3] = image2.split(vertical=False)

        # 3 images
        elif len(self.images) == 3:
            rect_image, vertical, num = self.find_rectangle_image()  # finds image with greatest ratio and shapes it 1x2
            other_images = [e for e in self.images if self.images.index(e) != num]
            rect_image = rect_image.resize(self.big_rectangle_image(vertical=vertical))
            all_positions = [e for e in range(4)]

            if vertical:
                if self.losowo == 1:
                    position = random.randrange(0, 2)  # choose random position for image
                else:
                    position = 0
                all_positions.remove(position)  # rectangle image takes 2 places
                all_positions.remove(position + 2)
                placement[position], placement[position + 2] = rect_image.split(vertical=True)
            else:
                if self.losowo == 1:
                    position = random.randrange(0, 3, 2)
                else:
                    position = 0
                all_positions.remove(position)
                all_positions.remove(position + 1)
                placement[position], placement[position + 1] = rect_image.split(vertical=False)

            var = 0
            for i in all_positions:
                placement[i] = other_images[var].square().resize(self.medium_image)
                var += 1
                
        # 4 images
        elif len(self.images) == 4:
            placement = [e.square().resize(self.medium_image) for e in self.images]

        return placement

    def put_image3x3(self):
        placement = [0]*9
        img2x = []  # list of rectangle images
        img4x = []  # list of big square images 2x2
        num_img = len(self.images)
        while num_img < 9:
            if 9 - num_img < 3:  # big image can't fit, increase number of images by making rectangles
                rect_image, vertical, num = self.find_rectangle_image()  # finds most rectangle image and shapes it
                img2x.append([rect_image, vertical])
                del self.images[num]
                num_img += 1
            else:
                img4x.append(self.images[0].square())
                del self.images[0]
                num_img += 3

        all_positions = [e for e in range(9)]
        for img in img4x:
            img = img.resize(self.big_image)
            hor_img1, hor_img2 = img.split(vertical=False)  # making 2 rectanles and then 4 small squares
            img1, img2 = hor_img1.split(vertical=True)
            img3, img4 = hor_img2.split(vertical=True)
            all_positions, position = self.find_big_position(avaiable_pos=all_positions)
            placement[position] = img1.resize(self.small_image)
            placement[position + 1] = img3.resize(self.small_image)
            placement[position + 3] = img2.resize(self.small_image)
            placement[position + 4] = img4.resize(self.small_image)

        for img in img2x:  # takes rectangles and tries to fit them
            rect_image, vertical = img
            if vertical:
                rect_image = rect_image.resize(self.small_rectangle_image(vertical=True))
                img1, img2 = rect_image.split(vertical=True)
                all_positions, position = self.find_vertical_position(avaiable_pos=all_positions)  # checks for vertical possibilities
                placement[position] = img1.resize(self.small_image)
                placement[position + 3] = img2.resize(self.small_image)
            else:
                rect_image = rect_image.resize(self.small_rectangle_image(vertical=False))
                img1, img2 = rect_image.split(vertical=False)
                all_positions, position = self.find_horizontal_position(avaiable_pos=all_positions)  # checks for horizontal possibilities
                placement[position] = img1.resize(self.small_image)
                placement[position + 1] = img2.resize(self.small_image)

        num = 0
        for i in all_positions:  # after puting bigger image fill other places with smaller images
            placement[i] = self.images[num].square().resize(self.small_image)
            num += 1

        return placement

    def find_rectangle_image(self):
        enum_largest = max(enumerate(self.images), key=lambda i: i[1].ratio)
        largest = enum_largest[1]
        maxratio = largest.ratio

        if largest.width > largest.height:
            return largest.make_rectangle1x2(vertical=False), False, enum_largest[0]
        else:
            return largest.make_rectangle1x2(vertical=True), True, enum_largest[0]

    def find_big_position(self, avaiable_pos):
        # find position for 2/3 width/height image
        myList = avaiable_pos
        mylistshifted = [x-1 for x in myList]
        possible_position = [0, 1, 3, 4]  # only possible possisions for big image
        intersection_set = list(set(myList) & set(mylistshifted) & set(possible_position))
        if self.losowo == 1:
            position = random.choice(intersection_set)
        else:
            position = intersection_set[0]
        myList = [e for e in myList if e not in (position, position + 1, position + 3, position + 4)]
        return myList, position

    def find_vertical_position(self, avaiable_pos):
        # find position vertical rectangle image
        myList = avaiable_pos
        mylistshifted = [x-3 for x in myList]
        possible_position = [e for e in range(6)]  # positions where image is not cut in half
        intersection_set = list(set(myList) & set(mylistshifted) & set(possible_position))
        if self.losowo == 1:
            position = random.choice(intersection_set)
        else:
            position = intersection_set[0]
        myList.remove(position)  # removes places from other_position, so no other image can take these places
        myList.remove(position + 3)
        return myList, position

    def find_horizontal_position(self, avaiable_pos):
        # find position for horizontal rectangle image
        myList = avaiable_pos
        mylistshifted = [x-1 for x in myList]
        possible_position = [0, 1, 3, 4, 6, 7]  # positions where image is not cut in half
        intersection_set = list(set(myList) & set(mylistshifted) & set(possible_position))
        if self.losowo == 1:
            position = random.choice(intersection_set)
        else:
            position = intersection_set[0]
        myList.remove(position)  # removes places from other_position, so no other image can take these places
        myList.remove(position + 1)
        return myList, position


if __name__ == "__main__":  # check if it's working with local files
    image_names = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg", "img7.jpg"]  # enter image names here
    image_list = [cv2.imread(e) for e in image_names]
    mozaika = Mozaika(image_list)
    cv2.imshow("i", mozaika.output_image)
    cv2.waitKey(0)
