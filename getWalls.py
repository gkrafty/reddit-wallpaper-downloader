#!/usr/bin/env python3

# ---------------------
# SCRIPT INFO ---------
# ---------------------
# This script downloads X amount of images from a
# selected subreddit. The subreddit can be specified
# in the user config section of this srcipt or as 
# a parameter in the script.
#
# Run example: python getWalls.py earthporn




# ---------------------
# USER CONFIG ---------
# ---------------------


# ---------------------
# IMPORTS -------------
# ---------------------
import os
import sys
import argparse
from os.path import expanduser
from sanitize_filename import sanitize
import requests
import urllib
from PIL import ImageFile


# ---------------------
# FUNCTIONS -----------
# ---------------------

# Returns false on status code error
def validURL(URL):
    statusCode = requests.get(URL, headers = {'User-agent':'getWallpapers'}).status_code
    if statusCode == 404:
        return False
    else: return True

# Creates download directory if needed
def prepareDirectory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print('Created directory {}'.format(directory))

# Returns false if subreddit doesn't exist
def verifySubreddit(subreddit):
    URL = 'https://reddit.com/r/{}.json'.format(subreddit)
    result= requests.get(URL, headers = {'User-agent':'getWallpapers'}).json()
    try:
        result['error']
        return False
    except:
        return True

# Returns list of posts from subreddit as json
def getPosts(subreddit, sort, loops, jsonLimit, after):
    allPosts = []
    
    i = 0
    while i < loops:
        URL = 'https://reddit.com/r/{}/{}/.json?t=all&limit={}&after={}'.format(subreddit, sort, jsonLimit, after)
        posts = requests.get(URL, headers = {'User-agent':'getWallpapers'}).json()
        # allPosts.append(posts['data']['children'])
        for post in posts['data']['children']:
            allPosts.append(post)
        after = posts['data']['after']
        i += 1
    
    return allPosts

# Returns false if URL is not an image
def isImg(URL):
    if URL.endswith(('.png', '.jpeg', '.jpg')):
        return True
    else: return False

# Returns false if image from URL is not HD (Specified by min-/max_width)
def isHD(URL, min_width, min_height):
    file = urllib.request.urlopen(URL)
    size = file.headers.get("content-length")
    if size: size = int(size)
    p = ImageFile.Parser()
    while 1:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            # return p.image.size
            if p.image.size[0] >= min_width and p.image.size[1] >= min_height:
                return True
                break
            else:
                return False
                break
    file.close()
    return False

# Returns false if image from URL is not landscape
def isLandscape(URL):
    file = urllib.request.urlopen(URL)
    size = file.headers.get("content-length")
    if size: size = int(size)
    p = ImageFile.Parser()
    while 1:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            # return p.image.size
            if p.image.size[0] >= p.image.size[1]:
                return True
                break
            else:
                return False
                break
    file.close()
    return False

# Returns true if image from URL is already downloaded
def alreadyDownloaded(URL,title,directory):
    imgName = os.path.basename(URL)
    imgName = title
    localFilePath = os.path.join(directory, imgName)
    if(os.path.isfile(localFilePath)):
        return True
    else: return False

# Returns false if image from post/URL is not from reddit or imgur domain
def knownURL(post):
    if post.lower().startswith('https://i.redd.it/') or post.lower().startswith('http://i.redd.it/') or post.lower().startswith('https://i.imgur.com/') or post.lower().startswith('http://i.imgur.com/'):
        return True
    else: return False

# Returns true if image from post/URL is stored locally
def storeImg(post,title,directory):
#### uncomment to print for debug
#    print(directory + title)
#    if urllib.request.urlretrieve(post, os.path.join(directory, os.path.basename(post))):
    if urllib.request.urlretrieve(post, os.path.join(directory, title)):
        return True
    else: return False

def right(s, amount):
    return s[-amount:]

def left(s, amount):
    return s[:amount]

def stylizeFileName(title):
    title = sanitize(title)
    title = title.lower()
    title = title.replace(" ","_")
    title = title.replace("-","_")
    title = title.replace("/","")
    title = title.replace("!","")
    title = title.replace("#","")
    title = title.replace("%","")
    title = title.replace("&","")
    title = title.replace("'","")
    title = title.replace(",","")
    title = title.replace(">","")
    title = title.replace("<","")
    title = title.replace(".","")
    title = title.replace("[","(")
    title = title.replace("]",")")
    title = title.replace("_×_","x")
    title = title.replace("_x_","x")
    title = title.replace("_X_","x")
    title = title.replace("__","_")
    return title


# ---------------------
# COLORS --------------
# ---------------------
DARK = '\033[1;30m'
RED = '\033[1;31m'
GREEN = '\033[1;32m'
ORANGE = '\033[1;33m'
PURPLE = '\033[1;35m'
NC = '\033[0m'


# ---------------------
# FUNCTIONS - Main
# ---------------------
def main():

    # Where to store downloaded images
    directory = '~/Pictures/Wallpapers/Reddit/'
    # Which subreddit to download from
    subreddit = 'wallpapers'
    # Sort Type
    sort_type = 'top' # options are 'top', 'hot', 'new'
    # Minimum width of image
    min_width = 3440
    # Minimum height of image
    min_height = 1440
    # How many posts to get for each request (Max 100)
    jsonLimit = 100
    # Increase this number if the number above (jsonLimit) isn't enough posts
    loops = 5

    # create parser object
    parser = argparse.ArgumentParser(description = "An background image processor!")
  
    # defining arguments for parser object
    parser.add_argument("-d", "--directory", type=str, nargs = '?',
                        metavar='output-directory', const = 'none', default = directory,
                        help = "Specify directory location to store wallpapers \
                        default = '~/Pictures/Wallpapers/Reddit/")

    parser.add_argument("-s", "--subreddit", metavar='subreddit', type=str, nargs=1,
                        default = subreddit,
                        help = "Subreddit to troll through")

    parser.add_argument("-mw", "--minimal-width", type = int, nargs = '?',
                        default = min_width,
                        metavar = ('minimal-width'),
                        help = "Minium width in pixels.")

    parser.add_argument("-mh", "--minimal-height", type = int, nargs = '?',
                        default = min_height,
                        metavar = ('minimal-height'),
                        help = "Minium height in pixels.")

    parser.add_argument("-st", "--sort", type = str, nargs = '?',
                        default = sort_type,
                        metavar = ('sort'),
                        help = "Minium height in pixels.")

    parser.add_argument("-l", "--jsonLimit", type = int, nargs = '?',
                        default = jsonLimit,
                        metavar = ('post limit'),
                        help = "number of posts to scan through. \
                        default = 100")
  
    # parse the arguments from standard input
    args = parser.parse_args()


    # Check if subreddit name is specified as parameter
    try:
        subreddit = args.subreddit[0]
    except:
        pass

    # Creates directory
    print("args.directory[0] = " + args.directory)
    directory = expanduser(args.directory)
    print("fist directory = " + directory)
    directory = os.path.join(args.directory, subreddit)
    print("second directory = " + directory)
    prepareDirectory(directory)
    print("prepared directory = " + directory)

    # Exits if invalid subreddit name
    if not verifySubreddit(subreddit):
        print('r/{} is not a valid subreddit'.format(subreddit))
        sys.exit()

    # For reddit pagination (Leave empty)
    after = ''

    # Stores posts from function
    posts = getPosts(subreddit, args.sort, loops, str(args.jsonLimit), after)

    # For adding index numbers to loop
    index = 1

    # Counting amount of images downloaded
    downloadCount = 0

    # Print starting message
    print()
    print(DARK + '--------------------------------------------' + NC)
    print(PURPLE + 'Downloading to      : ' + ORANGE + directory + NC)
    print(PURPLE + 'From r/             : ' + ORANGE + subreddit + NC)
    print(PURPLE + 'Minimum resolution  : ' + ORANGE + str(min_width) + 'x' + str(min_height) + NC)
    print(PURPLE + 'Maximum downloads   : ' + ORANGE + str(jsonLimit*loops) + NC)
    print(DARK + '--------------------------------------------' + NC)
    print()


    # Loops through all posts
    for post in posts:

        # Define and cleanup title for use as file name    
        title = post['data']['title'] + "_" + post['data']['name'] 
        title = stylizeFileName(title)
        title = title + right(post['data']['url'],4)

    #### uncomment to print during debug
    #    print(title)
        # Shortening variable name
        post = post['data']['url']

        # Skip post on 404 error
        if not validURL(post):
            print(RED + '{}) 404 error'.format(index) + NC)
            index += 1
            continue

        # Skip unknown URLs
        elif not knownURL(post):
            print(RED + '{}) Skipping unknown URL'.format(index) + NC)
            index += 1
            continue

        # Skip post if not image
        elif not isImg(post):
            print(RED + '{}) No image in this post'.format(index) + NC + NC + NC + NC)
            index += 1
            continue

        # Skip post if not landscape
        elif not isLandscape(post):
            print(RED + '{}) Skipping portrait image'.format(index) + NC)
            index += 1
            continue
        
        # Skip post if not HD
        elif not isHD(post, args.minimal_width, args.minimal_
        height):
            print(RED + '{}) Skipping low resolution image'.format(index) + NC)
            index += 1
            continue

        # Skip already downloaded images
        elif alreadyDownloaded(post,title,directory):
            print(RED + '{}) Skipping already downloaded image'.format(index) + NC)
            index += 1
            continue

        # All checks cleared, download image
        else:
            # Store image from post locally
            if storeImg(post,title,directory):
                print(GREEN + '{}) Downloaded {}'.format(index, title) + NC)
                downloadCount += 1
                index += 1
            # For unexpected errors
            else:
                print(RED + 'Unexcepted error' + NC)
                index += 1


    # Print info when loop is finished
    print()
    print(ORANGE + '{}'.format(downloadCount) + PURPLE + ' images was downloaded to ' + ORANGE + '{}'.format(directory) + NC)

# ---------------------
# START SCRIPT --------
# ---------------------
if __name__ == "__main__":
    # calling the main function
    main()
