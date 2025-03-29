from django.test import TestCase
from .models import garden,User,message
from rest_framework.test import APIClient
from rest_framework.test import APIRequestFactory
from django.utils import timezone




# Create your tests here.

#First Step is to test model implementation without using APIs
class ModelTests(TestCase) :
    #Create a test user.
    def setUp(self):
        self.user = User.objects.create_user(username="dog", password="pass1",email="dog@dog.com")
        self.garden = garden.objects.create(ownerID = self.user, name = "garden1", longitude = 10, latitude = 10, bio = "big garden bio")
        self.message = message.objects.create(senderID = self.user, gardenID = self.garden, body = "message one")
    def testuserCreate(self):
        self.assertEqual(self.user.username , "dog")
        self.assertEqual(self.user.email , "dog@dog.com")


    def testGardenCreate(self):
        self.assertEqual(self.garden.name , "garden1")
        self.assertEqual(self.garden.longitude , 10)
        self.assertEqual(self.garden.latitude , 10)
        self.assertEqual(self.garden.bio , "big garden bio")
    
    def testMessageCreate(self):
        self.assertEqual(self.message.senderID , self.user)
        self.assertEqual(self.message.gardenID , self.garden)
        self.assertEqual(self.message.body , "message one")
        #self.assertEqual(self.message.date_sent , timezone.now())



class llmAPItest(TestCase):
    def setup(self):
        self.client = APIClient()
    
    def testLLMResponse(self):
        #Define Basic Query to return a simple response if connection is made 
        queryJson = {
            "query" : "Please respond only with the word Affirmative if you receive this query"
        }
        #Post query
        apiResponse = self.client.post("/api/chat/", queryJson, format = 'json' )
        #Convert response to json.
        apiResponseData = apiResponse.json()
        #Confirm LLM has responded with "Affirmative"
        self.assertEqual(apiResponseData["response"], "Affirmative") 


class gardenAPItests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="dog", password="pass1",email="dog@dog.com")
        self.garden =garden.objects.create(ownerID = self.user, name = "garden1", longitude = 10, latitude = 10, bio = "big garden bio")
        #Create a second garden to test garden list
        garden.objects.create(ownerID = self.user,name = "garden2", longitude = 11, latitude = 11, bio = "small garden bio")

    def testGardenList(self):
        #Dummy request to list all gardens
        apiResponse = self.client.get(path='/api/garden/')
        #Isolate first two gardens in list
        firstGarden = apiResponse.data[0]
        secondGarden = apiResponse.data[1]
        #Confirm first two gardens returned as per definition
        self.assertEqual(firstGarden['name'], "garden1")
        self.assertEqual(secondGarden['name'], "garden2")
    
    def testCreate_Garden(self):
        #Define a garden in JSON as required by the api
        gardenDefinitionJson = {
            "ownerID" : self.user.username,
            "latitude" : "-11.0",
            "longitude" :  "11.0",
            "bio" : "Test Garden",
            "name" : "TestGarden1",
        }
        #Dummy post request for our test garden
        apiResponse = self.client.post('/api/postGarden/', gardenDefinitionJson, format='json')
    #    #Assert positive response from server
        self.assertEqual(apiResponse.status_code, 201)
#
        #Assert that Garden exists in db with info as defined above
        newGarden = garden.objects.get(name = gardenDefinitionJson["name"])
        self.assertEqual(newGarden.name, gardenDefinitionJson["name"])
        self.assertEqual(newGarden.longitude, float(gardenDefinitionJson["longitude"]))
        self.assertEqual(newGarden.latitude, float(gardenDefinitionJson["latitude"]))
        self.assertEqual(newGarden.bio, gardenDefinitionJson["bio"])
        


class userAPItests(TestCase):
    def setUp(self):
        self.client = APIClient()
        #Create a user to test that API can get info
        self.user = User.objects.create_user(username="dog1", password="pass1",email="dog@dog.com")
        #Data here to test the API posting
        self.test_data = {
            "username": "dog1",
            "email": "dog@dog.com",
            "password": "pass1"
        }


    def testGetUser(self):
        #Make a dummy get request for the user dog1
        userID = self.user.id
        testURL = '/api/user/' + str(userID) + '/'
        apiResponse = self.client.get(testURL)
        #Assert response is positive
        self.assertEqual(apiResponse.status_code, 200)
        #Assert APi returns user as requested
        self.assertEqual(apiResponse.data['username'] , self.test_data['username'])
        self.assertEqual(apiResponse.data['email'] , self.test_data['email'])
    
    def testCreate_User(self):
        #Define a user in JSON as required by the api
        userDefinitionJson = {
            "username" : "dog2",
            "email" :  "dog2@dog.com",
            "password" : "dogpass"
        }
        #Dummy post request for our test user
        apiResponse = self.client.post('/api/post/', userDefinitionJson, format='json')
        #Assert positive response from server
        self.assertEqual(apiResponse.status_code, 201)

        #Assert that User exists in db with info as defined above
        newUser = User.objects.get(username = userDefinitionJson["username"])
        self.assertEqual(newUser.username, userDefinitionJson["username"])
        self.assertEqual(newUser.email, userDefinitionJson["email"])
        

'''

for garden in garden.objects.all():
    print(garden.ownerID, garden.name)


    #def testCreateUser(self):
    #    apiResponse = self.client.post('/api/post/',self.test_data)
    #    print(apiResponse.data)
    #    self.assertEqual(apiResponse.data['username'], self.test_data['username'])
    #    print("done1")
    #

'''