import csv
import math

cnt = 0

m_dict = []
m_data = []

with open('Mastersheet.csv', 'rb') as csvfile:
	scanner = csv.reader(csvfile, delimiter=',', quotechar='"', dialect=csv.excel_tab)
	
	for row in scanner:
		cnt += 1
		if (cnt == 1):
			for el in row:
				m_dict.append(el)
		else:
			m_data.append(row)


n = len(m_dict)

m_dict.append('Long')
m_dict.append('Lat')

def getGPS(x_a, x_b):
	k = 1
	k0 = 0.9996
	drad = math.pi / 180.0
	a = 6378137.0
	f = 1 / 298.2572236
	b = a * (1 - f)
	e = math.sqrt(1 - (b**2) / (a**2))
	e0 = e / math.sqrt(1 - e)
    
	def utmToLatLng (x, y, utmz=16):
		esq = (1 - (b / a) * (b / a))
		e0sq = e * e / (1 - e**2)
		zcm = 3 + 6 * (utmz - 1) - 180
		e1 = (1 - math.sqrt(1 - e**2.)) / (1 + math.sqrt(1 - e**2))
		M = y / k0 
		mu = M / (a * (1 - esq * (1 / 4 + esq * (3 / 64 + 5 * esq / 256))))
		phi1 = mu + e1 * (3 / 2 - 27 * e1 * e1 / 32) * math.sin(2 * mu) + e1 * e1 * (21 / 16 - 55 * e1 * e1 / 32) * math.sin(4 * mu)
		phi1 = phi1 + e1 * e1 * e1 * (math.sin(6 * mu) * 151 / 96 + e1 * math.sin(8 * mu) * 1097 / 512)
		C1 = e0sq * math.cos(phi1)**2.
		T1 = math.tan(phi1)**2.
		N1 = a / math.sqrt(1 - (e * math.sin(phi1))**2.)
		R1 = N1 * (1 - e**2.) / (1 - (e * math.sin(phi1))**2.)
		D = (x - 500000) / (N1 * k0)
		phi = (D * D) * (1 / 2 - D * D * (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * e0sq) / 24)
		phi = phi + (D**6) * (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 252 * e0sq - 3 * C1 * C1) / 720
		phi = phi1 - (N1 * math.tan(phi1) / R1) * phi

		lat = math.floor(1000000 * phi / drad) / 1000000
		lng = D * (1 + D * D * ((-1 - 2 * T1 - C1) / 6 + D * D * (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * e0sq + 24 * T1 * T1) / 120)) / math.cos(phi1)
		lng = zcm + lng / drad

		return { 'lat': lat, 'lng': lng }

	# print x_a, x_b
	res = utmToLatLng(int(x_a), int(x_b)) 
	return res['lat'], res['lng']

def getUTM(data):
	res = [s[:7] for s in data.split() if len(s) >= 5]
	lon, lat = res[0], res[1]
	return getGPS(lon, lat)


cnt = 0
for j in range(len(m_data)):
	lon, lat = (None, None)
	pos = 0
	for i in range(len(m_data[j])):
		if m_data[j][i] and ',' in m_data[j][i]:
			lon, lat = getUTM(m_data[j][i])
			pos = i
			# print m_data[j][i], lon, lat
			break

	m_data[j] = m_data[j][:pos] + m_data[j][pos+1:]
	m_data[j].append(lon)
	m_data[j].append(lat)


with open('result.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(m_data)

