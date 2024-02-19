import numpy as np
from PIL import Image
import os

from struct_builder import * 
class MosaicMaker:
    def __init__(self, file_dir_name):
        self.bucket_dict = color_to_bucket(os.listdir(file_dir_name))
        self.colorspace_map = label_colorspace(list(self.bucket_dict.keys()))

    # blocksize is side length of the square patches we'll be pulling from the big picture
    # also called the "kernel" in typical convolution models
    def make_image(self, big_picture_file, blocksize):
        with Image.open(big_picture_file) as img:
            #get the x and y dims of the picture in terms of patches
            xdim = np.floor(img.width/blocksize).astype('int')
            ydim = np.floor(img.height/blocksize).astype('int')
            # the new (initially empty) picture we'll be pasting small pics onto.
            # gonna scale the small pics to 100x100 - should still by clear, but more managable for
            # final picture size
            new_mosaic = Image.new("RGB", (xdim*100, ydim*100))
            for dx in range(xdim):
                for dy in range(ydim):
                    # coordinates of patch from original big picture
                    cropbox = (dx*blocksize, dy*blocksize, (dx+1)*blocksize, (dy+1)*blocksize)
                    # new image destingation coordinates
                    blankpatch = (dx*100, dy*100, (dx+1)*100, (dy+1)*100)

                    tile = img.crop(cropbox)
                    tile_arr = np.asarray(tile)
                    tile_avg = np.mean(tile_arr, axis=(0,1))
                    tile_reduced = np.floor(tile_avg/25.6).astype('int')
                    tile_colorspace_key = ColorPoint(tile_reduced[0], tile_reduced[1], tile_reduced[2])
                    closebucket_key = self.colorspace_map[tile_colorspace_key]
                    closecolor_file = self.bucket_dict[closebucket_key][0]
                    self.bucket_dict[closebucket_key].rotate()
                    with Image.open(closecolor_file) as blit_img:
                        scaled_blit = blit_img.resize((100, 100))
                        new_mosaic.paste(scaled_blit, blankpatch)


            new_mosaic.show()

def mos_test():
    test_maker = MosaicMaker("./assets")
    test_maker.make_image("monalisa.jpeg", 20)

mos_test()