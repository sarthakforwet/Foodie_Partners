from flask import Flask,render_template,redirect,request
import requests
import json
app = Flask(__name__)

@app.route('/',methods=['POST','GET'])
def home():
	if request.method=='POST':
		address = request.form['address']

		count=request.form['Count']
		headers={'Accept': "application/json","user-key": "6f1a6514744476d55591d9dd25198c4c"}
		headers2 = {'Authorization': 'prj_live_pk_feddf0d04ae764d8157faf0d35e0926e711d8c8d',}
		params2 = (('query', address),)
		response2 = requests.get('https://api.radar.io/v1/geocode/forward', headers=headers2, params=params2)
		data2 = response2.json()
		Lat = data2['addresses'][0]['latitude']
		Long = data2['addresses'][0]['longitude']
		params={'lat':Lat,'lon':Long,'count':count}
		r=requests.get('https://developers.zomato.com/api/v2.1/search',headers=headers,params=params)

		data=r.json()
		data=data['restaurants']

		result=[]
		name = []
		address = []
		rating = []
		images = ['static/food1.jpg','static/food2.jpg','static/food3.jpg','static/food4.jpg','static/food5.jpg','static/food6.jpg',
		'static/food7.jpg','static/food8.jpg','static/food9.jpg','static/food10.jpg','static/food11.jpg','static/food12.jpg','static/food13.jpg','static/food14.jpg','static/food15.jpg']
		for i in data:
			name.append((i['restaurant']['name']))
			address.append((i['restaurant']['location']['address']))
			rating.append((i['restaurant']['user_rating']['aggregate_rating']))
			result.append((i['restaurant']['name'],i['restaurant']['location']['address'],i['restaurant']['average_cost_for_two'],i['restaurant']['user_rating']['aggregate_rating']))

		return render_template('cards.html',address=address,name=name,rating=rating,count=int(count),image_url=images)






	return render_template('index.html',title='Find restaurants')



if __name__=='__main__':
	app.run(debug=True)
