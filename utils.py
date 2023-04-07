import numpy as np
import cv2 as cv
import yaml

# Read config
with open('./config.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.loader.SafeLoader)

# Define constant
FRAME_WIDTH = data['frame_width'][0]
FRAME_HEIGHT = data['frame_height'][0]
PERSPECTIVE_MATRIX = np.array(data['perspective_matrix']) 
CM_PER_PIXEL = data['cm_per_pixel'][0]

def kmeans(data, k, max_iterations=100):
    # Initialize centroids randomly
    centroids = data[np.random.choice(data.shape[0], size=k, replace=False)]
    
    for i in range(max_iterations):
        # Assign data points to closest centroid
        distances = np.linalg.norm(data[:, np.newaxis] - centroids, axis=2)
        clusters = np.argmin(distances, axis=1)
        
        # Update centroids to be the mean of assigned data points
        new_centroids = np.array([data[clusters == j].mean(axis=0) for j in range(k)])
        
        # Check for convergence
        if np.all(centroids == new_centroids):
            break
        
        centroids = new_centroids
    
    return centroids, clusters

def cal_avg(values):
    """Calculate average value."""
    if not (type(values) == 'NoneType'):
        if len(values) > 0:
            n = len(values)
        else:
            n = 1
        return sum(values) / n
    
def compute_distance(pt1, pt2):
  # Transform both image_center and center_line_point to a new perspective
  new_pt1, new_pt2 = (PERSPECTIVE_MATRIX @ np.array([pt1, pt2]).T).T
  return round(CM_PER_PIXEL * np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2), 1)

def warp_perspective(img):
  object_width, object_height = 25.1, 33

  new_width, new_height = int(FRAME_WIDTH), int(object_height / object_width * FRAME_WIDTH)

  
  result = cv.warpPerspective(img, PERSPECTIVE_MATRIX, (new_width, new_height))
  return result

def find_point_on_line_from_y(line, y):
  x1, y1, x2, y2 = line
  slope = (y1-y2) / (x1-x2+1e-6)
  c = y1 - slope * x1
    
  # Calculate average intersection at lower_border.
  x = int((y - c) / (slope + 1e-6))
  return [x, y]

def extrapolate_lines_with_borders(lines, upper_border, lower_border):
    """Extrapolate lines keeping in mind the lower and upper border intersections."""
    slopes = []
    consts = []
    
    if len(lines) == 0:
      return None

    for x1, y1, x2, y2 in lines:
        slope = (y1-y2) / (x1-x2+1e-6)
        slopes.append(slope)
        c = y1 - slope * x1
        consts.append(c)
    avg_slope = cal_avg(slopes)
    avg_consts = cal_avg(consts)
      
    # Calculate average intersection at lower_border.
    x_lane_lower_point = int((lower_border - avg_consts) / (avg_slope + 1e-6))
    
    # Calculate average intersection at upper_border.
    x_lane_upper_point = int((upper_border - avg_consts) / (avg_slope + 1e-6))
    
    return [x_lane_lower_point, lower_border, x_lane_upper_point, upper_border]

def extrapolate_lines_without_borders(lines):
    """Extrapolate lines keeping in mind the lower and upper border intersections."""
    slopes = []
    consts = []
    
    upper_border, lower_border = 1000, 0

    if len(lines) == 0:
      return []

    for x1, y1, x2, y2 in lines:
        slope = (y1-y2) / (x1-x2 +1e-6)
        slopes.append(slope)
        c = y1 - slope * x1
        consts.append(c)

        if max(y1, y2) > lower_border:
          lower_border = max(y1, y2)
        if min(y1, y2) < upper_border:
          upper_border = min(y1, y2)

    avg_slope = cal_avg(slopes)
    avg_consts = cal_avg(consts)
    
    # Calculate average intersection at lower_border.
    x_lane_lower_point = int((lower_border - avg_consts) / (avg_slope + 1e-6))
    
    # Calculate average intersection at upper_border.
    x_lane_upper_point = int((upper_border - avg_consts) / (avg_slope + 1e-6))
    
    return [x_lane_lower_point, lower_border, x_lane_upper_point, upper_border]