import cv2 as cv
import numpy as np
import yaml

# Import custom modules
import utils
import midline
import annotation
import lane_detection

# Read config
with open('./config.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.loader.SafeLoader)

# Define constant
FRAME_WIDTH = data['frame_width'][0]
FRAME_HEIGHT = data['frame_height'][0]
PERSPECTIVE_MATRIX = np.array(data['perspective_matrix']) 
CM_PER_PIXEL = data['cm_per_pixel'][0]

LOW_BORDER_PERSPECTIVE_TRANSFORMATION = data['low_border_perspective_transformation'][0]

def process_image(image, fill_region=True):  
    # Convert to grayscale.
    gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)

    # Apply Histogram Equalization
    gray_histeq = cv.equalizeHist(gray)

    # Apply morphological operations
    kernel = np.ones((7,7), np.uint8)
    gray_histeq = cv.dilate(gray_histeq, kernel, iterations=1)
    gray_histeq = cv.erode(gray_histeq, kernel, iterations=1)

    # Intensity selection.
    threshold = cv.inRange(gray_histeq, 230, 255)
  
    roi_vertices = np.array([[[FRAME_WIDTH // 2, 0],
                          [FRAME_WIDTH // 3, FRAME_HEIGHT],
                          [0,FRAME_HEIGHT],
                          [0, 0],
                          [FRAME_WIDTH, 0],
                          [FRAME_WIDTH, FRAME_HEIGHT],
                          [2 * FRAME_WIDTH // 3, FRAME_HEIGHT],
                          [FRAME_WIDTH // 2, 0]]])
    # Defining a blank mask.
    mask = np.zeros_like(threshold)   

    # Defining a 3 channel or 1 channel color to fill the mask.
    if len(threshold.shape) > 2:
      channel_count = threshold.shape[2]  # 3 or 4 depending on the image.
      ignore_mask_color = (255,) * channel_count
    else:
      ignore_mask_color = 255
    # Filling pixels inside the polygon.
    cv.fillPoly(mask, roi_vertices, ignore_mask_color)

    # Constructing the region of interest based on where mask pixels are nonzero.
    roi = cv.bitwise_and(threshold, mask)

    # Smooth with a Gaussian blur.
    kernel_size = 3
    roi_blur = cv.GaussianBlur(roi, (kernel_size, kernel_size), 0)

    # Perform Edge Detection.
    low_threshold = 50
    high_threshold = 100
    canny_blur = cv.Canny(roi_blur, low_threshold, high_threshold)

    # Hough transform parameters set according to the input image.
    rho = 1
    theta = np.pi / 180
    threshold = 80
    min_line_len = 20
    max_line_gap = 50

    lines = cv.HoughLinesP(
      canny_blur, rho, theta, threshold, minLineLength = min_line_len, maxLineGap = max_line_gap)

    roi_upper_border = 0
    roi_lower_border = image.shape[0]

    # Create a blank array to contain the (colorized) results.
    lanes_img = np.zeros((image.shape[0], image.shape[1], 3), dtype = np.uint8)

    top_left_lines, top_right_lines, bottom_left_lines, bottom_right_lines = lane_detection.separate_left_right_up_down_lines(lines)

    top_left_lane = utils.extrapolate_lines_without_borders(top_left_lines)
    top_right_lane = utils.extrapolate_lines_without_borders(top_right_lines)
    bottom_left_lane = utils.extrapolate_lines_without_borders(bottom_left_lines)
    bottom_right_lane = utils.extrapolate_lines_without_borders(bottom_right_lines)

    # top_left_lane, top_right_lane, bottom_left_lane, bottom_right_lane = separate_left_right_up_down_lanes(lanes)

    # if (top_left_lane != []) and (bottom_left_lane == []):
    #   top_left_lane, bottom_left_lane = bottom_left_lane, top_left_lane

    # if (top_right_lane != []) and (bottom_right_lane == []):
    #   top_right_lane, bottom_right_lane = bottom_right_lane, top_right_lane

    # Elongated the whole line to both ends if there is no turn
    if (len(top_left_lane) == 0) and (len(bottom_left_lane) != 0):
      bottom_left_lane = utils.extrapolate_lines_with_borders([bottom_left_lane], roi_upper_border, roi_lower_border)

    if (len(top_right_lane) == 0) and (len(bottom_right_lane) != 0):
      bottom_right_lane = utils.extrapolate_lines_with_borders([bottom_right_lane], roi_upper_border, roi_lower_border)

    if (len(bottom_left_lane) == 0) and (len(top_left_lane) != 0):
      top_left_lane = utils.extrapolate_lines_with_borders([top_left_lane], roi_upper_border, roi_lower_border)

    if (len(bottom_right_lane) == 0) and (len(top_right_lane) != 0):
      top_right_lane = utils.extrapolate_lines_with_borders([top_right_lane], roi_upper_border, roi_lower_border)

    # Elongated top lines to top and bottom lines to bottom
    if len(top_left_lane) != 0:
      top_left_lane = utils.extrapolate_lines_with_borders([top_left_lane], roi_upper_border, max(top_left_lane[1], top_left_lane[3]))
    if len(top_right_lane) != 0:
      top_right_lane = utils.extrapolate_lines_with_borders([top_right_lane], roi_upper_border, max(top_right_lane[1], top_right_lane[3]))
    if len(bottom_left_lane) != 0:
      bottom_left_lane = utils.extrapolate_lines_with_borders([bottom_left_lane], min(bottom_left_lane[1], bottom_left_lane[3]), roi_lower_border)
    if len(bottom_right_lane) != 0:
      bottom_right_lane = utils.extrapolate_lines_with_borders([bottom_right_lane], min(bottom_right_lane[1], bottom_right_lane[3]), roi_lower_border)

    lanes = [top_left_lane, top_right_lane, bottom_left_lane, bottom_right_lane]

    for i in range(len(lanes)):
      if len(lanes[i]) != 0:
        annotation.draw_lines(lanes_img, [[lanes[i]]], thickness = 10)

    if fill_region == True:
      annotation.draw_con(lanes_img, top_left_lane, top_right_lane, bottom_left_lane, bottom_right_lane)
    
    alpha = 0.7
    beta = 0.4
    gamma = 0.0
    image_result = cv.addWeighted(image, alpha, lanes_img, beta, gamma)

    try: 
      upper_midpoint, middle_midpoint, lower_midpoint = midline.find_midpoints(lanes)
      image_result = annotation.draw_midline(image_result, upper_midpoint, middle_midpoint, lower_midpoint)

      image_center = [FRAME_WIDTH // 2, LOW_BORDER_PERSPECTIVE_TRANSFORMATION]

      middle_lower_line = lower_midpoint
      if middle_midpoint != []:
        middle_lower_line += middle_midpoint
      else:
        middle_lower_line += upper_midpoint

      center_line_point = utils.find_point_on_line_from_y(middle_lower_line, LOW_BORDER_PERSPECTIVE_TRANSFORMATION)
      cv.circle(image_result, image_center[:2], 10, [0,255,0], thickness=3)
      cv.circle(image_result, center_line_point[:2], 10, [0,0,255], thickness=3)

      left_intersect = utils.find_point_on_line_from_y(bottom_left_lane, LOW_BORDER_PERSPECTIVE_TRANSFORMATION) 
      right_intersect = utils.find_point_on_line_from_y(bottom_right_lane, LOW_BORDER_PERSPECTIVE_TRANSFORMATION)
      
      
      cv.line(image_result, left_intersect, right_intersect, [255,0,0], thickness=2)

      # Convert to homogeneous, add another dimension of value 1
      left_intersect = left_intersect + [1]
      right_intersect = right_intersect + [1]
      lane_width = utils.compute_distance(left_intersect, right_intersect)

      # Convert to homogeneous, add another dimension of value 1
      center_line_point = center_line_point + [1]
      image_center = image_center + [1]

      distance_from_center = utils.compute_distance(image_center, center_line_point)

      font = cv.FONT_HERSHEY_SIMPLEX
      fontScale = 1
      color = (255, 0, 0)
      thickness = 2

      # Display distance
      cv.putText(image_result, f'distance from midline: {distance_from_center} cm', (50, 50), font, 
                    fontScale, color, thickness, cv.LINE_AA)
      cv.putText(image_result, f'lane width: {lane_width} cm', (50, 100), font, 
                    fontScale, color, thickness, cv.LINE_AA)
    except Exception as e: 
      pass
    return image_result