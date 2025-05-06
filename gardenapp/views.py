from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import garden,User, message
from .serializers import UserSerializer,GardenSerializer,messageSerializer
from rest_framework import status
from django.urls import reverse
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.http import JsonResponse
import ollama


#Contact Trefle API to request list of plants
def proxy_plants(request):
    # Trefle API URL - should be in venv - refactor.
    #Not security issue due to free API
    api_url = 'https://trefle.io/api/v1/plants'
    api_token = 'K7a2PF5WFsGN4YTfRHNW-v-CRjXgkx-9nt_jZVWt2EA'

    if request.method == 'GET':
        try:
            response = requests.get(api_url, params={'token': api_token})
            response.raise_for_status() 
            data = response.json()  
            plants = data.get('data', [])  
            
            return JsonResponse(plants, safe=False) 
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)



def index(request):
    return HttpResponse("Hello, welcome to GardenGram!")


@api_view(['POST'])
def loginUser(request):
    emailIn = request.data.get("email")
    passwordIn = request.data.get("password")
    #Missing values
    if not emailIn or not passwordIn:
        return(JsonResponse({"error" : "Missing Credentials"},status=400))
    #Get first user
    userInstance = User.objects.filter(email=emailIn).first()
    if not userInstance:
        return(JsonResponse({"error" : "Email not found"},status = 401))
    #Authenticate
    user = authenticate(username = userInstance.username, password = passwordIn)
    #If auth fails, then user is NONE
    if user is None:
        return(JsonResponse({"error" : "Invalid Credentials","name" : userInstance.username}, status = 401))
    django_login(request,user)
    
    return JsonResponse({"message": "Successfully logged in as ", "user":  user.username, "userID" : user.id})

@api_view(['POST'])
def logoutUser(request):
    django_logout(request)
    print(request)
    return(JsonResponse({'message' : 'Successfully logged out.'}))



@api_view(['POST'])
def garden_search(request):
    #Get garden by lat long
    Lat = request.data.get('latitude')
    Long = request.data.get('longitude')
    foundGarden = garden.objects.get(latitude = Lat , longitude = Long )
    return JsonResponse({"name" : foundGarden.name, "bio" : foundGarden.bio, "ownerID": foundGarden.ownerID.id})


@api_view(['POST'])
def resetPasswordEmail(request):
    #Builds reset pass email with the email of user
    email = request.data.get('email')
    #get user to get name
    user = User.objects.get(email = email)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link  = f'http://127.0.0.1:8000/api/reset/{uid}/{token}/'    
    send_mail(
        'Password Reset Request',

        f'Hi {user.username},\n\nUse the link below to reset your password:\n{reset_link}',

        'gardenapplicationdev@gmail.com' ,
        [user.email],
        fail_silently=False,
        )
    





@api_view(['POST'])
def checkUserStatus(request):
    #Checks auth
    if request.user.is_authenticated:
        return(JsonResponse({'Auth' : True, 'username' : request.user.username},status = 200))
    else:
        return(JsonResponse({'Auth' : False},status = 401))




@api_view(['POST'])
def getUserInfo(request):
    #Gets user ID then gets the user.  If user is serializeable then return all user info from serializer
    ID_in = request.data.get("ID")
    try:
        user_ = User.objects.get(id = ID_in)
    except Exception as e:
        print(e)
    try:
        serializer = UserSerializer(user_, many=False)
    except Exception as e:
        print(e)
    try:
        print(serializer)#.data)
    except Exception as e:
        print(e)
    return(Response(serializer.data))


@api_view(['get'])
def user_list(request):
    #Lists all users
    users_ = User.objects.all()
    serializer = UserSerializer(users_, many=True)
    return Response(serializer.data)



@api_view(['get'])
def user_garden_list(request,username):
    #Get current user
    currentUser =  User.objects.get(username = username)
    #Get relevant gardens
    gardenList = garden.objects.filter(ownerID = currentUser)
    #If any gardens exist then return list
    if gardenList.exists():
        serializer = GardenSerializer(gardenList,many=True)
        return Response(serializer.data,status=200)
    else:
        return(Response(serializer.errors, status = 400))



@api_view(['get'])
def user_get(request, id):
    user = User.objects.get(id=id)
    serializer = UserSerializer(user)
    return Response(serializer.data, status = 200)






@api_view(['POST'])
def create_user(request):
    #Confirm that request method is correct.
    if request.method == 'POST':
        #If correct, feed the user data submitted into the serialiser
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            #if serialiser accepts the new user data then commit and return positive response.
            serializer.save()  
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)








@api_view(['POST'])
def create_garden_follower(request, gardenName):
    if request.method == 'POST':
        activeGarden = garden.objects.get(name = gardenName)
        currentUserID = request.data["userID"]
        currentUser  = User.objects.get(id = currentUserID)
        if currentUser.username == activeGarden.ownerID:
            return(JsonResponse({'Success' : False},status = 400))
        activeGarden.members.add(currentUser)
        return(JsonResponse({'Success' : True},status = 201))

@api_view(['POST'])
def remove_garden_follower(request, gardenName):
    print("activate")
    if request.method == 'POST':
        print("unf")
        activeGarden = garden.objects.get(name = gardenName)
        currentUserID = request.data["userID"]
        currentUser  = User.objects.get(id = currentUserID)
        activeGarden.members.remove(currentUser)
        return(JsonResponse({'Success' : True},status = 201))
    

@api_view(['GET'])
def get_followed_gardens(request, userID):
    if request.method == 'GET':
        currentUser  = User.objects.get(id = userID)
        gardenList = currentUser.followed_gardens.all()
    if gardenList.exists():
        serializer = GardenSerializer(gardenList,many=True)
        return Response(serializer.data,status=200)
    else:
        return(Response(serializer.errors, status = 400))

@api_view(['get'])
def get_follower_list(request, gardenID):
    activeGarden = garden.objects.get(id = gardenID)
    follower_list = activeGarden.members.all()
    serializer = UserSerializer(follower_list, many=True)
    return Response(serializer.data)





@api_view(['POST'])
def create_message(request):
    if request.method == 'POST':
        alteredRequest = request.data.copy()
        currentUser =  User.objects.get(pk = request.data['senderID'])
        currentGarden = garden.objects.get(name = request.data['gardenID'])
        alteredRequest['gardenID'] = currentGarden.id
        alteredRequest['senderID'] = currentUser.id
        serializer = messageSerializer(data=alteredRequest)

        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=201)
        print(serializer.errors)
        return Response(serializer.errors, status=400)
    
@api_view(['GET'])
def message_get(request, gardenID):
    currentGarden = garden.objects.get(name = gardenID)
    message_list = message.objects.filter(gardenID=currentGarden.id)
    serializer = messageSerializer(message_list,many=True)
    return Response(serializer.data, status = 200)

 



@api_view(['POST'])
def create_garden(request):
    if request.method == 'POST': 
        currentUser = User.objects.get(username = request.data['ownerID'])
        request.data['ownerID'] = currentUser.pk
        print(request.data)
        #print(1)
        serializer = GardenSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=201)
        print(serializer.errors)
        return Response(serializer.errors, status=400)
    
@api_view(['GET'])
def garden_list(request):
    print("yes")
    gardens_ = garden.objects.all()
    print(gardens_[0].name)
    serializer = GardenSerializer(gardens_, many=True)
    print(serializer.data[0])
    print(serializer.data[1])
    return Response(serializer.data)

@api_view(['GET'])
def message_list(request, gardenName):
    messages = message.objects.get(gardenName)
    serializer = messageSerializer(messages, many = True)
    return Response(serializer.data)






@api_view(['POST']) 
def chat_view(request):
    #Access the query from the JSON object
    user_input = request.data.get("query")
    #Submit the query to the model and save the response object
    response = ollama.chat(model="gemma", messages=[{"role": "user", "content": user_input}])
    #Return a JSON response with the reply from the LLM
    return JsonResponse({"response": response["message"]["content"]})
    


