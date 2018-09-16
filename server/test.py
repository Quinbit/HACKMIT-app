from bottle import route, run, error, request, post, static_file, get

import numpy as np
import math
import pandas as pd
from pyntcloud import PyntCloud
import os

def processData(dataTemp):
	try:
		os.remove("cur_mesh.ply")
		os.remove("cur_mesh.obj")
	except:
		print("Fresh")
	f = open("data.txt", "w")
	print(dataTemp)
	data = dataTemp.decode("utf-8").replace(" ","").split("\n")
	data = data[:max(0,len(data)-2)]
	for d in range(len(data)):
		data[d] = data[d].split(",")
		data[d] = [float(e) for e in data[d]]

	data = np.array(data)
	average = np.array([np.average(data[:,i]) for i in range(3)])
	average[2] = min(data[:,2])
	print(average)

	data = np.array([np.array(point) - average for point in data])

	frame = pd.DataFrame(data=data, columns=['x', 'y', 'z'])
	pc = PyntCloud(frame)
	kd_id = pc.add_structure("kdtree")
	pc.get_filter("SOR", and_apply=True, kdtree_id = kd_id, k = 20, z_max = 0.4)
	convex_hull_id = pc.add_structure("convex_hull")
	convex_hull = pc.structures[convex_hull_id]
	pc.mesh = convex_hull.get_mesh()
	pc.to_file("cur_mesh.ply", also_save=["mesh"])
	pc.to_file("cur_mesh.obj", also_save=["mesh", "points"])

	for i in range(3):
		data[:,i] /= max(np.abs(data[:,i]))
	polarData = []
	for r in range(len(data)):
		rho = np.sqrt(data[r][0]**2 + data[r][1]**2)
		if data[r][0] < 0:  # if x < 0
			phi = np.arctan2(data[r][1], data[r][0]) + math.pi
		else:
			phi = np.arctan2(data[r][1], data[r][0])
		if phi < 0:
			phi += math.pi * 2  # phi from [0, 360)
		# round to nearest 20deg for now
		prop = 1.0 / 20.0
		if phi < 0:
			phi += math.pi * 2
		phi /= math.pi * 2.0
		phi = min(phi // prop, 19)

		z = data[r][2]

		# round to 1/4 radius
		prop2 = 1.0 / 4.0
		rho = min(rho // prop2, 3.0)

		# round to 1/6 height
		prop3 = 1.0 / 6.0
		z = min(z // prop3, 5.0)
		polarData.append([int(rho), int(phi), int(z)])
	#print(polarData)
	m_data = np.zeros((20,4,6))

	for p in polarData:
		m_data[p[1], p[0], p[2]] += 1

	string = "0b"
	for rows in range(m_data.shape[0]):
		for cols in range(m_data.shape[1]):
			for theta in range(m_data.shape[2]):
				if (m_data[rows, cols, theta] < 1):
					string += "0"
					m_data[rows, cols, theta] = 0
				else:
					string += "1"
					m_data[rows, cols, theta] = 1

	print(m_data)
	f.write(string)
	f.close()

@post('/hello')
def hello():
	processData(request.body.read())
	return "HELLO WORLD!"

@error(404)
def error404(error):
	return error

@get('/mesh.obj')
def get_object():
	f = open("cur_mesh.obj",'rb')
	s = f.read()
	f.close()
	return s

run(host='206.189.238.224', port=8078, debug=True)
