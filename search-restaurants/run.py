from flask import Flask,render_template,redirect,request
import requests
import json
app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def home():
	if request.method=='POST':
		User_key=request.form['Api']
		address = request.form['address']
		Cuisines=request.form['Cuisines']
		Sort_By=request.form['SortBy']
		Sort_Order=request.form['SortOrder']
		count=request.form['Count']
		q=request.form['Query']
		headers={'Accept': "application/json","user-key": str(User_key)}
		headers2 = {'Authorization': 'prj_live_pk_feddf0d04ae764d8157faf0d35e0926e711d8c8d',}
		params2 = (('query', address),)
		response2 = requests.get('https://api.radar.io/v1/geocode/forward', headers=headers2, params=params2)
		data2 = response2.json()
		Lat = data2['addresses'][0]['latitude']
		Long = data2['addresses'][0]['longitude']
		params={'lat':Lat,'lon':Long,'cuisines':Cuisines,'sort':Sort_By,'order':Sort_Order,'count':count,'q':q}
		r=requests.get('https://developers.zomato.com/api/v2.1/search',headers=headers,params=params)

		data=r.json()
		data=data['restaurants']

		result=[]
		for i in data:
			result.append((i['restaurant']['name'],i['restaurant']['location']['address'],i['restaurant']['average_cost_for_two'],i['restaurant']['user_rating']['aggregate_rating']))

		return render_template('response.html',data=result,length=len(result))






	return render_template('home.html',title='Find restaurants')



if __name__=='__main__':
	app.run(debug=True)
