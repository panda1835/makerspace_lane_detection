import cv2 as cv
import numpy as np

def draw_lines(img, lines, color = [255, 0, 0], thickness = 2):
    """Utility for drawing lines."""
    if lines is not None:
        for line in lines:
            for x1,y1,x2,y2 in line:
                cv.line(img, (x1, y1), (x2, y2), color, thickness)

    
def draw_con(img, up_left_lane, up_right_lane, bottom_left_lane, bottom_right_lane):
    """Fill in lane area."""
    points = []
    if up_left_lane != []:
      x1, y1, x2, y2 = up_left_lane
      if y1 > y2:
        x1, y1, x2, y2 = x2, y2, x1, y1
      points.append((x1, y1))
      points.append((x2, y2))
    if bottom_left_lane != []:
      x1, y1, x2, y2 = bottom_left_lane
      if y1 > y2:
        x1, y1, x2, y2 = x2, y2, x1, y1
      points.append((x1, y1))
      points.append((x2, y2))
    if bottom_right_lane != []:
      x1, y1, x2, y2 = bottom_right_lane
      if y1 > y2:
        x1, y1, x2, y2 = x2, y2, x1, y1
      points.append((x2, y2))
      points.append((x1, y1))
    if up_right_lane != []:
      x1, y1, x2, y2 = up_right_lane
      if y1 > y2:
        x1, y1, x2, y2 = x2, y2, x1, y1
      points.append((x2, y2))
      points.append((x1, y1))

    # Sort the points by x-coordinate
    # print (points)
    points = np.array([points], dtype = 'int32')        
    cv.fillPoly(img, points, (0,255,0))

def draw_midline(image_result, upper_midpoint, middle_midpoint, lower_midpoint):
  x_upper = int(round(upper_midpoint[0]))
  y_upper = int(round(upper_midpoint[1]))
  x_lower = int(round(lower_midpoint[0])) 
  y_lower = int(round(lower_midpoint[1])) 
  if (len(middle_midpoint)) == 0:
    cv.line(image_result, (x_upper, y_upper), (x_lower, y_lower), (255, 0, 0), thickness=5)
  else:
    x_middle = int(round(middle_midpoint[0]))
    y_middle = int(round(middle_midpoint[1]))
    cv.line(image_result, (x_upper, y_upper), (x_middle, y_middle), (255, 0, 0), thickness=5)
    cv.line(image_result, (x_middle, y_middle), (x_lower, y_lower), (255, 0, 0), thickness=5)
  return image_result