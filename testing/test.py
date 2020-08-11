import cv2 as cv
import numpy as np

img = cv.imread("screen.jpg", cv.IMREAD_COLOR)
templ = cv.imread("bobbery.png", cv.IMREAD_COLOR)
templ_incl_alpha_ch = cv.imread("bobbery.png", cv.IMREAD_UNCHANGED)

channels = cv.split(templ_incl_alpha_ch)
#extract "transparency" channel from image
alpha_channel = np.array(channels[3]) 
#generate mask image, all black dots will be ignored during matching
mask = cv.merge([alpha_channel,alpha_channel,alpha_channel])
cv.imshow("Mask", mask)

result = cv.matchTemplate(img, templ, cv.TM_CCOEFF_NORMED, None, mask)
cv.imshow("Matching with mask", result)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
print('Highest correlation WITH mask', max_val)

result = cv.matchTemplate(img, templ, cv.TM_CCOEFF_NORMED)
cv.imshow("Matching without mask", result)
min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
print('Highest correlation without mask', max_val)

while True:
    if cv.waitKey(10) == 27:
        break

cv.destroyAllWindows()