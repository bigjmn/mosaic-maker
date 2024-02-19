import numpy as np
from PIL import Image
from collections import deque, defaultdict, namedtuple 
import os 
def average_color(filename):
    pic_array = np.asarray(Image.open(filename))
    # for each of R, G, and B, get the average value across all pixels
    avcolor = np.mean(pic_array, axis=(0,1))
    return avcolor

def deque_factory():
    return lambda: deque([])

def color_to_bucket(dir_name):
    
    color_buckets = defaultdict(deque_factory())
    for filename in os.listdir(dir_name):
        filepath = os.path.join(dir_name, filename)
        im_color = average_color(filepath)
        reduced_arr = np.floor(im_color/25.6).astype('int')
        string_arr = reduced_arr.astype('str')
        #this is really unforgivable, but the numpy join is weird
        string_key = string_arr[0]+string_arr[1]+string_arr[2]
        color_buckets[string_key].append(filepath)

    return color_buckets

ColorPoint = namedtuple("ColorPoint", ["red", "green", "blue"])

def adjacent_colorpoints(color_arr):
    a, b, c = color_arr[0], color_arr[1], color_arr[2]
    return [
        ColorPoint(a+1, b, c),
        ColorPoint(a-1, b, c),
        ColorPoint(a, b+1, c),
        ColorPoint(a, b-1, c),
        ColorPoint(a, b, c+1),
        ColorPoint(a, b, c-1)
    ]

# factory for creating unlabeled color space
def fresh_pool():
    startpool = set({})
    for i in range(10):
        for j in range(10):
            for k in range(10):
                startpool.add(ColorPoint(i, j, k))
    return startpool

# the set-labelers that will expand boundaries.
# Here, "name" refers to the label
 #(corresponding to the color bucket dictionary key) they will give each point
class Crawler:
    def __init__(self, name, startpt):
        self.name = name
        self.startpt = startpt
        self.innerpoints = set([])
        self.currentboundary = set([startpt])

    def push_boundary(self, pool):
        newboundary = []
        for i in self.currentboundary:
            node_boundary = adjacent_colorpoints(i)
            # for boundary points still in the set, add to the new boundary
            for k in node_boundary:
                if k in pool:
                    newboundary.append(k)
                    pool.remove(k)
        self.innerpoints.update(self.currentboundary)
        self.currentboundary = set(newboundary)


#create crawlers from a list of bucket keys
def bucket_keys_to_crawlers(bucket_keys):
    all_crawlers = []
    for i in bucket_keys:
        #turn number string into integer list
        int_arr = [int(a) for a in list(i)]
        newcrawler = Crawler(i, ColorPoint(int_arr[0], int_arr[1], int_arr[2]))
        all_crawlers.append(newcrawler)
    return all_crawlers

#finally, func to get fully labeled color space from bucket keys
def label_colorspace(bucket_keys):
    full_dict = {} # the fully labeled space
    startpool = fresh_pool()
    crawler_list = bucket_keys_to_crawlers(bucket_keys)

    is_running = True
    #gotta manually remove crawler start points before expansion
    for c in crawler_list:
        startpool.remove(c.startpt)

    while is_running:
        for c in crawler_list:
            c.push_boundary(startpool)

        if len(startpool) <= 0:
            is_running = False

    #label the points collected by the crawlers (both interior and boundary)
    for c in crawler_list:
        for closecolor in c.innerpoints:
            full_dict[closecolor] = c.name
        for closecolor in c.currentboundary:
            full_dict[closecolor] = c.name

    return full_dict