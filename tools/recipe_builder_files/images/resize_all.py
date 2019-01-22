import os
import PIL
import re

new_size = (35, 50)

image_dir = 'raw_images/'

file_names = os.listdir(image_dir)
file_names = list(filter(lambda s: re.search('.png$', s), file_names))

for file_name in file_names:
	image = PIL.Image.open(image_dir + file_name)
	image = image.resize(new_size, PIL.Image.ANTIALIAS)
	image.save(file_name)
