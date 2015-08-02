import csv
import utm
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

def get(data):
	res = [s[:7] for s in data.split() if len(s) >= 5]
	return res

t=open('vis.js','w')

res_json = '{"type": "FeatureCollection", "features": ['
res_csv = "latitude,longitude\n"
res_fusiontables = "location\n"
cnt = 0
for j in range(len(m_data)):
	lon, lat = (None, None)
	pos = 0
	for i in range(len(m_data[j])):
		if m_data[j][i] and ',' in m_data[j][i]:
			res = get(m_data[j][i])
			if "None" not in res:
				t.write('{location: new google.maps.LatLng(utmconv.utmToLat(%s, %s, 16, false),utmconv.utmToLng(%s, %s, 16, false)), weight: 1.0},\n'%(res[0],res[1],res[0],res[1]))
			
				lat, lon = utm.to_latlon(int(res[0]), int(res[1]), 16, 'N')
	  			res_csv += str(lat) + "," + str(lon) + "\n";
	  			res_fusiontables += str(lat) + ";" + str(lon) + "\n"
	  			res_json += """
			  		{
			            "geometry": {
			                "type": "Point", 
			                "coordinates": [
			                    %s, 
			                    %s
			                ]
			            },
			            "properties": {
			            """ % (str(lon),str(lat))

			o = 0
			for l in range(len(m_dict)):
				if 'Fog' in m_dict[l] and 'N' not in m_data[j][l]:
					res_json += '"%s": "%s",\n' % (m_dict[l + 1], m_data[j][l])
					continue
				if '477' in m_data[j][l]:
					o = 1
				if 'UTM' not in m_dict[l] and 'Fog' not in m_dict[l] and 'Wind' not in m_dict[l]:
					res_json += '"%s": "%s",\n' % (m_dict[l], m_data[j][l + o])
			res_json += '}},' 

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

m_csv = open('m_csv.csv', 'w')
m_csv.write(res_csv)
m_csv.close()

ftables = open('ftables.csv', 'w')
ftables.write(res_fusiontables)
ftables.close()