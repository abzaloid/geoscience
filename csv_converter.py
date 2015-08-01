import csv

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

def getUTM(data):
	res = [s[:7] for s in data.split() if len(s) >= 5]
	lon, lat = res[0], res[1]
	return lon, lat


cnt = 0
for j in range(len(m_data)):
	lon, lat = (None, None)
	for i in range(len(m_data[j])):
		if m_data[j][i] and ',' in m_data[j][i]:
			lon, lat = getUTM(m_data[j][i])
			break
	m_data[j].append(lon)
	m_data[j].append(lat)


print m_data