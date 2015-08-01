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
				if 'UTM' not in el:
					m_dict.append(el)
		else:
			m_data.append(row)


n = len(m_dict)

m_dict.append('Location')

def getGPS(x_a, x_b):
	k = 1
	k0 = 0.9996
	drad = math.pi / 180.0
	a = 6378137.0
	f = 1.0 / 298.2572236
	b = a * (1 - f)
	e = math.sqrt(1 - (b/a)*(b/a))
	e0 = e / math.sqrt(1 - e*e)
    
	def utmToLatLng (x, y, utmz=16):
		esq = (1 - (b/a)*(b/a))
		e0sq = e * e / (1 - e * e)
		zcm = 3 + 6 * (utmz - 1) - 180
		e1 = (1 - math.sqrt(1 - e * e)) / (1 + math.sqrt(1 - e * e))
		M = y / k0 
		mu = M / (a * (1 - esq * (1 / 4 + esq * (3 / 64 + 5 * esq / 256))))
		phi1 = mu + e1 * (3 / 2 - 27 * e1 * e1 / 32) * math.sin(2 * mu) + e1 * e1 * (21 / 16 - 55 * e1 * e1 / 32) * math.sin(4 * mu)
		phi1 = phi1 + e1 * e1 * e1 * (math.sin(6 * mu) * 151 / 96 + e1 * math.sin(8 * mu) * 1097 / 512)
		C1 = e0sq * math.cos(phi1)*math.cos(phi1)
		T1 = math.tan(phi1)*math.tan(phi1)
		N1 = a / math.sqrt(1 - (e * math.sin(phi1))*(e * math.sin(phi1)))
		R1 = N1 * (1 - e*e) / (1 - (e * math.sin(phi1))*(e * math.sin(phi1)))
		D = (x - 500000) / (N1 * k0)
		phi = (D * D) * (1 / 2 - D * D * (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * e0sq) / 24)
		phi = phi + (D*D*D*D*D*D) * (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 252 * e0sq - 3 * C1 * C1) / 720
		phi = phi1 - (N1 * math.tan(phi1) / R1) * phi

		lat = math.floor(100000000 * phi / drad) / 100000000
		lng = D * (1 + D * D * ((-1 - 2 * T1 - C1) / 6 + D * D * (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * e0sq + 24 * T1 * T1) / 120)) / math.cos(phi1)
		lng = zcm + lng / drad

		return { 'lat': lat, 'lng': lng }

	# print x_a, x_b
	res = utmToLatLng(int(x_a), int(x_b)) 
	return res['lat'], res['lng']

def get(data):
	res = [s[:7] for s in data.split() if len(s) >= 5]
	return res

def getUTM(data):
	res = [s[:7] for s in data.split() if len(s) >= 5]
	lon, lat = res[0], res[1]
	return getGPS(lon, lat)

t=open('vis.js','w')

res_json = '{"type": "FeatureCollection", "features": ['

cnt = 0
for j in range(len(m_data)):
	lon, lat = (None, None)
	pos = 0
	for i in range(len(m_data[j])):
		if m_data[j][i] and ',' in m_data[j][i]:
			res = get(m_data[j][i])
			if "None" not in res:
				t.write('{location: new google.maps.LatLng(utmconv.utmToLat(%s, %s, 16, false),utmconv.utmToLng(%s, %s, 16, false)), weight: 1.0},\n'%(res[0],res[1],res[0],res[1]))
					
				lat, lon = getUTM(m_data[j][i])
	  			res_json += '''
					  		{
					            "geometry": {
					                "type": "Point", 
					                "coordinates": [
					                    %s, 
					                    %s
					                ]
					            }, 
					            "type": "Feature", 
					            "properties": {
					                "utm_zone": "16N", 
					                "utm_easting": %s, 
					                "manually_marked_outlier": "false", 
					                "ground_speed": null, 
					                "timestamp": "%s", 
					                "created_at": "%s", 
					                "height_above_ellipsoid": null, 
					                "study_local_timestamp": "%s", 
					                "visible": true, 
					                "sensor_type": "gps", 
					                "utm_northing": %s, 
					            }
							},
				''' % (str(lat+0.09),str(lon+0.009),str(lat+0.09), m_data[j][1], m_data[j][1], m_data[j][1], str(lon+0.009))

			pos = i
			break

	m_data[j] = m_data[j][:pos] + m_data[j][pos+1:]
	m_data[j].append(','.join([str(lat), str(lon)]))

t.close()

with open('result.csv', 'wb') as f:
    writer = csv.writer(f)
    f.write(','.join(p for p in m_dict))
    f.write('\n')
    writer.writerows(m_data)

ppp=open('ppp.geojson','w')
ppp.write(res_json)
ppp.write(']}')
ppp.close()