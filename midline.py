import utils

def find_midpoints(lanes):
  if (lanes[0] == []) and (lanes[1]==[]):
      upper_midpoint = [(lanes[2][2]+lanes[3][2])/2, (lanes[2][3]+lanes[3][3])/2]
      lower_midpoint = [(lanes[2][0]+lanes[3][0])/2, (lanes[2][1]+lanes[3][1])/2]
      middle_midpoint = []
  elif (lanes[2] == []) and (lanes[3]==[]):
      upper_midpoint = [(lanes[0][2]+lanes[1][2])/2, (lanes[0][3]+lanes[1][3])/2]
      lower_midpoint = [(lanes[0][0]+lanes[1][0])/2, (lanes[0][1]+lanes[1][1])/2]
      middle_midpoint = []
  elif (lanes[0] == []):
      shorten_line = utils.extrapolate_lines_with_borders([lanes[2]], lanes[2][3], lanes[1][1])
      x_middle = (shorten_line[0]+ lanes[1][0])/2
      upper_midpoint = [(lanes[1][2]+lanes[3][2])/2, (lanes[1][3]+lanes[3][3])/2]
      middle_midpoint = [x_middle,lanes[1][1]]
      lower_midpoint = [(lanes[3][0]+lanes[4][0])/2, (lanes[3][1]+lanes[4][1])/2]
  elif (lanes[1] == []):
      #Done
      shorten_line = utils.extrapolate_lines_with_borders([lanes[3]], lanes[3][3], lanes[0][1])
      x_middle = (shorten_line[0] + lanes[0][0])/2
      upper_midpoint = [(lanes[0][2]+lanes[3][2])/2, (lanes[0][3]+lanes[3][3])/2]
      middle_midpoint = [x_middle,lanes[0][1]]
      lower_midpoint = [(lanes[2][0]+lanes[3][0])/2, (lanes[2][1]+lanes[3][1])/2]
  elif (lanes[2] == []):
      shorten_line = utils.extrapolate_lines_with_borders([lanes[0]], lanes[1][1], lanes[0][3])
      x_middle = (shorten_line[2] + lanes[3][2])/2
      upper_midpoint = [(lanes[0][2]+lanes[1][2])/2, (lanes[0][3]+lanes[1][3])/2]
      middle_midpoint = [x_middle,lanes[1][1]]
      lower_midpoint = [(lanes[0][0]+lanes[3][0])/2, (lanes[0][1]+lanes[3][1])/2]
  elif (lanes[3] == []):
      shorten_line = utils.extrapolate_lines_with_borders([lanes[1]], lanes[0][1], lanes[1][1])
      x_middle = (shorten_line[2] + lanes[0][0])/2
      upper_midpoint = [(lanes[2][2]+lanes[1][2])/2, (lanes[2][3]+lanes[1][3])/2]
      middle_midpoint = [x_middle,lanes[0][1]]
      lower_midpoint = [(lanes[0][0]+lanes[1][0])/2, (lanes[0][1]+lanes[1][1])/2]
  else: 
      upper_midpoint = [(lanes[0][2]+lanes[1][2])/2, (lanes[0][3]+lanes[1][3])/2]
      middle_midpoint = [(lanes[0][0]+lanes[1][0])/2, (lanes[0][1]+lanes[1][1])/2]
      lower_midpoint = [(lanes[2][0]+lanes[3][0])/2, (lanes[2][1]+lanes[3][1])/2]
  return upper_midpoint, middle_midpoint, lower_midpoint