import requests,json
from flask import Flask,render_template,request,jsonify, url_for
from flask_mail import Mail, Message
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
app=Flask(__name__, static_url_path='/static')
mail=Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pypragmatics@gmail.com'
app.config['MAIL_PASSWORD'] = 'ssmm@py3.8'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail=Mail(app)
engine=create_engine("postgres://postgres:Dsjo;#ooy619@localhost:5432/postgres")
db=scoped_session(sessionmaker(bind=engine))
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/bookindex")
def bookindex():
    flights=db.execute("SELECT * FROM flights").fetchall()
    return render_template("bookindex.html",flights=flights)
@app.route("/prebook",methods=["POST"])
def prebook():
    global departure_date
    departure_date=request.form.get("departure")
    global return_date
    return_date=request.form.get("return")
    global trip
    trip=request.form.get("trip")
    global flight_id
    try:
        flight_id=int(request.form.get("flight_id"))
    except ValueError:
        return render_template("bookerror.html",message="Invalid Flight Number.")
    fly=db.execute("SELECT * FROM flights WHERE id=:id",{"id":flight_id}).fetchone()
    api_key = "ecb7ac7804856a74c00fa686ae28e868"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = fly.destination
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name 
    response = requests.get(complete_url) 
    x = response.json() 
    y = x["main"] 
    current_temperature = int(y["temp"] - 273.15)
    current_pressure = y["pressure"] 
    current_humidiy = y["humidity"] 
    z = x["weather"] 
    weather_description = z[0]["description"]
    return render_template("passenger.html",dest=fly.destination,curtemp=current_temperature,curpres=current_pressure,curhum=current_humidiy,des=weather_description)
@app.route("/book",methods=["POST"])
def book():
    name=request.form.get("name")
    age=request.form.get("age")
    gender=request.form.get("gender")
    seat_no=request.form.get("seat_no")
    email=request.form.get("email")
    phone=request.form.get("phone")
    meal=request.form.get("meal")
    addinfo=request.form.get("addinfo")
    if db.execute("SELECT * FROM flights WHERE id=:id", {"id":flight_id}).rowcount==0:
        return render_template("bookerror.html",message="No such Flight with that ID")
    db.execute("INSERT INTO passengers (name,flight_id,age,gender,departure_date,return_date,trip,seat_no,email,phone,meal,addinfo) VALUES (:name,:flight_id,:age,:gender,:departure_date,:return_date,:trip,:seat_no,:email,:phone,:meal,:addinfo)",
               {"name":name,"flight_id":flight_id,"age":age,"gender":gender,"departure_date":departure_date,"return_date":return_date,"trip":trip,"seat_no":seat_no,"email":email,"phone":phone,"meal":meal,"addinfo":addinfo})
    db.commit()
    fly=db.execute("SELECT * FROM flights WHERE id=:id",{"id":flight_id}).fetchone()
    msg=Message('Thank You for booking flight with us',
                sender='pypragmatics@gmail.com',
                recipients=[email]
                )
    msg.body=f'Hello {name} ,\n Your booking for flight {fly.origin} to {fly.destination} on {departure_date} is confirmed'
    mail.send(msg)
    return render_template("bookerror.html",message="Your Booking is Confirmed")
@app.route("/contact")
def contact():
    return render_template("contact.html")
@app.route("/flights")
def flightdetails():
    flights=db.execute("SELECT * FROM flights").fetchall()
    return render_template("flightdetails.html",flights=flights)
@app.route("/flights/<int:flight_id>")
def flight(flight_id):
    fly=db.execute("SELECT * FROM flights WHERE id=:id",{"id":flight_id}).fetchone()
    if fly is None:
        return render_template("bookerror.html",message="No such Flight with that ID")
    passengers=db.execute("SELECT name FROM passengers WHERE flight_id=:flight_id",{"flight_id":flight_id}).fetchall()
    return render_template("flight.html",flight=fly,passengers=passengers)
@app.route("/api/flights/<int:flight_id>")
def flight_api(flight_id):
    fly=db.execute("SELECT * FROM flights WHERE id=:id",{"id":flight_id}).fetchone()
    if fly is None:
        return jsonify({"error":"Invalid Flight id"}),422
    passengers=db.execute("SELECT * FROM passengers WHERE flight_id=:flight_id",{"flight_id":flight_id}).fetchall()
    names=[]
    for passenger in passengers:
        names.append(passenger.name)
    return jsonify({
            "origin":fly.origin,
            "destination":fly.destination,
            "duration":fly.duration,
            "passengers":names
            })
@app.route("/feedback",methods=["POST"])
def feedback():
    firstname=request.form.get("firstname")
    lastname=request.form.get("lastname")
    email=request.form.get("emailid")
    con=request.form.get("approve")
    kaha=request.form.get("how")
    msg=request.form.get("feedback")
    try:
        phone=request.form.get("telnum")
        areacode=request.form.get("areacode")
    except TypeError:
        return render_template("bookerror.html",message="Invalid Area code or Phone Number.")
    except ValueError:
        return render_template("bookerror.html",message="Invalid Area code or Phone Number.")
    db.execute("INSERT INTO contacts (firstname,lastname,areacode,phone,email,con,msg,kaha) VALUES (:firstname,:lastname,:areacode,:phone,:email,:con,:msg,:kaha)",
               {"firstname":firstname,"lastname":lastname,"areacode":areacode,"phone":phone,"email":email,"con":con,"msg":msg,"kaha":kaha})
    db.commit()
    return render_template("bookerror.html",message="Thank You for your Valuable Feedback")
if __name__=="__main__":
    app.run(debug=True)
    