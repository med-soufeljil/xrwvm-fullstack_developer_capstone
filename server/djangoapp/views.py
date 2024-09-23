# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import get_request, analyze_review_sentiments, post_review
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            # Get username and password from request body (JSON format)
            data = json.loads(request.body)
            username = data['userName']
            password = data['password']
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Log the user in
                login(request, user)
                response_data = {
                    "userName": username,
                    "status": "Authenticated"
                }
            else:
                # Authentication failed
                response_data = {
                    "userName": username,
                    "status": "Failed to authenticate"
                }
            return JsonResponse(response_data)
        except Exception as e:
            # Log any errors that occur
            logger.error(f"Error in login_user: {str(e)}")
            return JsonResponse({"error": "Invalid request format or missing data"}, status=400)
    else:
        return JsonResponse({"error": "POST request required"}, status=405)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
# Add the logout view to handle the logout request
@csrf_exempt
def logout_user(request):
    if request.method in ['POST', 'GET']:
        try:
            # Log the user out
            logout(request)
            # Return a response indicating the user is logged out
            data = {"userName": ""}
            return JsonResponse(data)
        except Exception as e:
            # Log any errors and return a failure response
            logger.error(f"Error in logout_user: {str(e)}")
            return JsonResponse({"error": "Failed to logout"}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...
@csrf_exempt
def register_user(request):
    if request.method == 'GET':
        # Handle GET request - return a simple message or form information
        return JsonResponse({"message": "This is the registration page. Please send a POST request with 'userName' and 'password' to register."})

    elif request.method == 'POST':
        try:
            # Parse the incoming request data (username and password)
            data = json.loads(request.body)
            username = data['userName']
            password = data['password']

            # Check if a user with the same username already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)

            # Create a new user
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # Authenticate and log in the newly registered user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"userName": username, "status": "Registered and Logged in"})

            # If user authentication fails after registration
            return JsonResponse({"error": "Registration successful, but failed to log in"}, status=500)

        except Exception as e:
            # Log any errors and return a failure response
            logger.error(f"Error in register_user: {str(e)}")
            return JsonResponse({"error": "Failed to register"}, status=500)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
# ...
#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})
# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request, dealer_id):
# ...

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})
# Create a `add_review` view to submit a review
# def add_review(request):
# ...
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})