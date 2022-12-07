from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, CarModel, CarMake, DealerReview, ReviewPost
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, get_request, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
from django.db import models
from django.core import serializers
from django.utils.timezone import now
import uuid
import logging
import json


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            #message.success(request, "Login successfully!")
            return redirect('/djangoapp/')
        else:
            # If not, return to login page again
            message.warning(request, "Invaild username or password.")
            return render(request, 'djangoapp/user_login.html', context)
#    else:
 #       return render(request, 'djangoapp/user_login.html', context)


# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('/djangoapp')


# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['pword']
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context["message"]="Account could not be created try again."
            return render(request, 'djangoapp/registration.html', context))

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    #get global dealership
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/f2068c64-a7e4-4264-ae32-3ae6ae786879/appdevcapstoneproject/get_dealerships"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/f2068c64-a7e4-4264-ae32-3ae6ae786879/appdevcapstoneproject/get_dealerships"
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)
        context["dealer"] = dealer
        
        review_url = "https://us-south.functions.appdomain.cloud/api/v1/web/f2068c64-a7e4-4264-ae32-3ae6ae786879/appdevcapstoneproject/get_reviews"
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id=dealer_id)
        print(reviews)
        context["reviews"] = reviews

        return render(request, 'djangoapp/dealer_details.html', context)
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    context = {}
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/f2068c64-a7e4-4264-ae32-3ae6ae786879/appdevcapstoneproject/get_dealerships"
    dealer_url = "https://us-south.functions.appdomain.cloud/api/v1/web/f2068c64-a7e4-4264-ae32-3ae6ae786879/appdevcapstoneproject/get_dealerships"
    dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)
    context["dealer"] = dealer
    # If it is a GET request, just render the add_review page
    if request.method == 'GET':    
        # Get dealers from the URL
        cars = CarModel.object.all()
        print(cars)
        context["cars"] = cars

        #print(context)
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = dealer_id
            payload["dealer_id"] = dealer_id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.make.name
            payload["car_model"] = car.name
            payload["car_year"] = int(car.year.strftime("%Y"))

            new_payload = {}
            new_payload["review"] = payload
            review_post_url = "https://us-south.functions.appdomain.cloud/api/v1/web/f2068c64-a7e4-4264-ae32-3ae6ae786879/appdevcapstoneproject/post_review"
            post_request(review_post_url, new_payload, dealer_id=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
            
            
            
            #review = dict()
            #review["id"]=0#placeholder
            #review["name"]=request.POST["name"]
            #review["dealership"]=dealer_id
            #review["review"]=request.POST["content"]
            #if ("purchasecheck" in request.POST):
            #    review["purchase"]=True
            #else:
            #    review["purchase"]=False
            #print(request.POST["car"])
            #if review["purchase"] == True:
            #    car_parts=request.POST["car"].split("|")
            #    review["purchase_date"]=request.POST["purchase_date"] 
             #   review["car_make"]=car_parts[0]
              #  review["car_model"]=car_parts[1]
               # review["car_year"]=car_parts[2]
#
 #           else:
  #              review["purchase_date"]=None
   #             review["car_make"]=None
    #            review["car_model"]=None
     #           review["car_year"]=None
      #      json_result = post_request("https://us-south.functions.appdomain.cloud/api/v1/web/f2068c64-a7e4-4264-ae32-3ae6ae786879/appdevcapstoneproject/post_review", review, dealerId=dealer_id)
       #     print(json_result)
        #    if "error" in json_result:
         #       context["message"] = "ERROR: Review was not submitted."
          #  else:
           #     context["message"] = "Review was submited"
       # return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

