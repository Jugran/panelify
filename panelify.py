#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import cv2
import sys

# TODO: black colored panels not detecting
# since detecting from smaller res, the detecion should be less forgiving (add erosion/dialation)

# FEATURE: add extra margin in image for inline panels
#           where there is less or no padding at edges

# Findings -
# scaling is a factor 
# 		lower image redude noise but can 
#		merge panels with low gutter
#
# cv2.THRESH_OTSU helps in pale/dark panels
# threadhold values affect accuracy (should depend on total intensity)
# scale is dependent on intensity of image color 
#	(light ones need higher res and dark lower res)
#
#


# see-> https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html

# FIXED-> by resizing to lower res : 
#	remove concentric rectangles 
#	(Watchmen comic -> cover pages with watches)

def show(img):
	cv2.namedWindow('image', cv2.WINDOW_KEEPRATIO)
	cv2.resizeWindow('image', width, height)
	cv2.imshow('image', img)
	k = 0
	while ( k != 27):
		k = cv2.waitKey(0) & 0xFF
		if k == 27:
			cv2.destroyAllWindows()


def showRects(rects, image): 
	img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

	for r in rects: 
		x,y,w,h = r 
		cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 10) 
	show(img)

def showComics(comics):
	cv2.namedWindow('image', cv2.WINDOW_NORMAL)
	cv2.resizeWindow('image', width, height)

	k=0
	for file, rects in comics:
		img = cv2.imread(file, 0)
		img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

		for r in rects: 
			x,y,w,h = r 
			cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 10)

		cv2.imshow('image', img)

		k = cv2.waitKey(0) & 0xFF
		if k == 27:
			cv2.destroyAllWindows()
			return

def panels(image):
	img = np.copy(image)
	imgr = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	#ret, imgr = cv2.threshold(imgr, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
	ret, imgr = cv2.threshold(imgr, 240, 255, cv2.THRESH_BINARY_INV)

	# morphological tranformation
	kernel = np.ones([3,3], dtype=np.int8)
	imgr = cv2.morphologyEx(imgr, cv2.MORPH_CLOSE, kernel)
	
	contours, heir = cv2.findContours(imgr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	rects = []

	for cntr in contours:
		# perimeter = cv2.arcLength(cntr, True)
		# epsilon = 0.1 * perimeter
		# approx_cntr = cv2.approxPolyDP(cntr, epsilon, True)
		rect = cv2.boundingRect(cntr)

		x,y,w,h = rect

		if w < img.shape[1] * 0.1 or h < img.shape[0] * 0.1:
			continue

		rects.append(rect)
		# show(cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 10))

	return rects

def readImage(filename, scale=1):
	image = cv2.imread(filename, 1)
	if scale == 1:
		return image

	s_img = cv2.resize(image, None, fx = scale, fy = scale, interpolation=cv2.INTER_AREA)
	return s_img

def saveComics(filename, comics):

	annotation = []
	for comic, rects in comics:
		boxes = []
		# rect x, y, w, h
		for rect in rects:
			x, y, w, h = rect
			box = [x, y, x + w, y + h, 1] # 1 for panel
			boxes.append(box)

		line = f"{comic} {' '.join(','.join(str(x) for x in b) for b in boxes)}"
		annotation.append(line + '\n')		
	
	with open(filename, 'w') as file:
		file.writelines(annotation)



if __name__ == '__main__':

	width, height = 800, 1000
	scale = 0.25
	upscale = 1/scale

	if len(sys.argv) >= 3:
		print('batch mode')
		filepath = sys.argv[1].strip()
		start = int(sys.argv[2])
		num = start + int(sys.argv[3]) -1
		
		showrects = bool(sys.argv[4])

		comics = []

		for i in range(start, num):
			filename = filepath.replace('+', f'{i:03}')

			img = readImage(filename, scale)

			rects = panels(img)

			rects = [[round(i*upscale) for i in t] for t in rects]
			print(rects)
			comics.append((filename, rects))
			
			#if showrects :
			#	showRects(rects, image)
			
			print(f'{filename} rect count: {len(rects)}')

	elif len(sys.argv) >= 2 :
		filename = sys.argv[1].strip()
		img = readImage(filename, scale)
		rects = panels(img)
		rects = [[round(i*upscale) for i in t] for t in rects]
		print(f'{filename} rect count: {len(rects)}')
		comics = [(filename, rects)]
	else:
		sys.exit(0)
	
	if showrects :
		showComics(comics)

	saveComics('panels.txt', comics)

