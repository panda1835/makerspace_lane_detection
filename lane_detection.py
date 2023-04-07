import numpy as np
import yaml

# Import custom modules
import utils

# Read config
with open('./config.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.loader.SafeLoader)

# Define constant
FRAME_WIDTH = data['frame_width'][0]
FRAME_HEIGHT = data['frame_height'][0]

def separate_left_right_up_down_lines(lines):
    """Separate left and right lines depending on the slope."""

    left_lines = []
    right_lines = []

    top_left_lines = []
    top_right_lines = []
    bottom_left_lines = []
    bottom_right_lines = []

    slopes = []
    left_slopes = []
    right_slopes = []
    
    top_left_slopes = []
    top_right_slopes = []
    bottom_left_slopes = []
    bottom_right_slopes = []
    

    centers_x = []
    
    # Store indices of lines with abs(slope) > 1000 or < 0.1 to remove later
    remove_idx = []

    # Calculate the center of each line
    for i in range(len(lines)):
      line = lines[i]
      x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]
      centers_x.append((x1 + x2)/2)
      slope = (y1-y2) / (x1-x2+1e-6)
      slopes.append(slope)
      if abs(slope) > 1000:
        remove_idx.append(i)
      if abs(slope) < 0.1:
        remove_idx.append(i)
      
    slopes = np.delete(slopes, remove_idx, axis=0)
    lines = np.delete(lines, remove_idx, axis=0)
    centers_x = np.delete(centers_x, remove_idx, axis=0)

    center_x = FRAME_WIDTH // 2

    # Separate left and right lines by relative position with center_x
    for i in range(len(centers_x)):
      if centers_x[i] < center_x:
        left_lines.append(lines[i][0])
        left_slopes.append([slopes[i]])
      else:
        right_lines.append(lines[i][0])
        right_slopes.append([slopes[i]])

    # Vectorization
    left_lines = np.array(left_lines)
    right_lines = np.array(right_lines)
    left_slopes = np.array(left_slopes)
    right_slopes = np.array(right_slopes)

    if len(left_slopes) != 0:
      num_clusters = min(2, len(left_slopes))

      _, clusters = utils.kmeans(left_slopes, num_clusters)

      line_group_0 = left_lines[clusters == 0]
      line_group_1 = left_lines[clusters == 1]
      slope_group_0 = left_slopes[clusters == 0]
      slope_group_1 = left_slopes[clusters == 1]

      y_group_0 = []
      y_group_1 = []

      for line in line_group_0:
        y_group_0.append((line[1] + line[3])/2)

      for line in line_group_1:
        y_group_1.append((line[1] + line[3])/2)

      if np.array(y_group_0).mean() > np.array(y_group_1).mean():
        top_left_lines = line_group_1
        bottom_left_lines = line_group_0 
        top_left_slopes = slope_group_1
        bottom_left_slopes = slope_group_0 
      else:
        top_left_lines = line_group_0
        bottom_left_lines = line_group_1
        top_left_slopes = slope_group_0
        bottom_left_slopes = slope_group_1

    if len(right_slopes) != 0:

      num_clusters = min(2, len(right_slopes))

      _, clusters = utils.kmeans(right_slopes, num_clusters)

      line_group_0 = right_lines[clusters == 0]
      line_group_1 = right_lines[clusters == 1]
      slope_group_0 = right_slopes[clusters == 0]
      slope_group_1 = right_slopes[clusters == 1]

      y_group_0 = []
      y_group_1 = []

      for line in line_group_0:
        y_group_0.append((line[1] + line[3])/2)

      for line in line_group_1:
        y_group_1.append((line[1] + line[3])/2)

      if np.array(y_group_0).mean() > np.array(y_group_1).mean():
        top_right_lines = line_group_1
        bottom_right_lines = line_group_0 
        top_right_slopes = slope_group_1
        bottom_right_slopes = slope_group_0 
      else:
        top_right_lines = line_group_0
        bottom_right_lines = line_group_1
        top_right_slopes = slope_group_0
        bottom_right_slopes = slope_group_1

    # Merge top and bottom if their average slopes are close (<1)
    # Left first
    if (len(top_left_slopes) != 0) and (len(bottom_left_slopes) != 0):
      if abs(np.array(top_left_slopes).mean() - np.array(bottom_left_slopes).mean()) < 1.2:
        bottom_left_lines = np.concatenate((bottom_left_lines, top_left_lines), axis=0) 
        top_left_lines = []
        bottom_left_slopes = np.concatenate((bottom_left_slopes, top_left_slopes), axis=0) 
        top_left_slopes = []
    # Then right
    if (len(top_right_slopes) != 0) and (len(bottom_right_slopes) != 0):
      if abs(np.array(top_right_slopes).mean() - np.array(bottom_right_slopes).mean()) < 1.2:
        bottom_right_lines = np.concatenate((bottom_right_lines, top_right_lines), axis=0)
        top_right_lines = []
        bottom_right_slopes = np.concatenate((bottom_right_slopes, top_right_slopes), axis=0)
        top_right_slopes = []

    # Merge top and bottom if their average slopes are both large (>5)
    # Left first
    if (len(top_left_slopes) != 0) and (len(bottom_left_slopes) != 0):
      if (abs(np.array(top_left_slopes).mean()) > 4.5) and (abs(np.array(bottom_left_slopes).mean()) > 4.5):
        bottom_left_lines = np.concatenate((bottom_left_lines, top_left_lines), axis=0)
        top_left_lines = []
        bottom_left_slopes = np.concatenate((bottom_left_slopes, top_left_slopes), axis=0)
        top_left_slopes = []
    # Then right
    if (len(top_right_slopes) != 0) and (len(bottom_right_slopes) != 0):
      if (abs(np.array(top_right_slopes).mean()) > 4.5) and (abs(np.array(bottom_right_slopes).mean()) > 4.5):
        bottom_right_lines = np.concatenate((bottom_right_lines, top_right_lines), axis=0)
        top_right_lines = []
        bottom_right_slopes = np.concatenate((bottom_right_slopes, top_right_slopes), axis=0)
        top_right_slopes = []

    return top_left_lines, top_right_lines, bottom_left_lines, bottom_right_lines