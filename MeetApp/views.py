#working till now 

import threading
from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.contrib import messages
import random
from django.core.cache import cache
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import logout
from django.contrib.auth import login,  authenticate
from django.contrib.auth.models import User 
import re
from datetime import datetime
from django.views.decorators.cache import never_cache
import pymongo
myclient = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
db = myclient["PROJECT"]
collection = db["UserData"]
# Create your views here.

from .bot import send_mail

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        Name = request.POST.get('Name')
        Number = request.POST.get('Number')
        Email = request.POST.get('Email')
        Password = request.POST.get('Password')
        City = request.POST.get('City')
        State = request.POST.get('State')
        Zip = request.POST.get('Zip')
        request.session['from_register'] = True
        
        if User.objects.filter(username=Name).exists():
            messages.info(request, "Username already taken!")
            return redirect('register')
        
        if User.objects.filter(email=Email).exists():
            messages.info(request, "In this Email account already exists")
            return redirect('register')
        
        if len(Number) == 10:
            pass
        else:
            messages.error(request, "check your number")
            return redirect('register')
        
        if len(Name) >= 3:
            pass
        else:
            messages.error(request, "lenght of name shoud be grater than 3")
            return redirect('register')
        
        if len(Password) >= 3:
            pass
        else:
            messages.error(request, "lenght of Password shoud be grater than 3")
            return redirect('register')
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if Email and re.match(email_regex, Email):
            pass
        else:
            messages.error(request, "this Email account is invalid")
            return redirect('register')
            
        
        
        random_number = random.randint(10000, 99999)
        print('=====================> your otp is ' f'{random_number}')
        
        request.session['from_register'] = True
        request.session['Name'] = Name
        request.session['Number'] = Number
        request.session['Email'] = Email
        request.session['Password'] = Password  
        request.session['City'] = City
        request.session['State'] = State
        request.session['Zip'] = Zip
        request.session['Otp'] = random_number
        
        #to_email, subject, message,
        send_mail([Email],"Registeration", f"your otp is {random_number} dont share with others")

        messages.info(request, f"Otp sent to {Email}")
        return redirect('registercon')
    
    return render(request,"register.html")


def registercon(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if not request.session.get('from_register'):
        messages.error(request, "You must register first.")
        return redirect('register')
    
    
    if request.method == 'POST':
        entered_otp = int(request.POST.get('Number'))
        session_otp = int(request.session.get('Otp'))
        
        if 'File' not in request.FILES:
            del request.session['Name']
            del request.session['Number']
            del request.session['Email']
            del request.session['Password']
            del request.session['City']
            del request.session['State']
            del request.session['Zip']
            del request.session['from_register']
            del request.session['Otp']
            messages.info(request, "File not found")
            return redirect('register')
        
        uploaded_file = request.FILES['File']
        File_content = uploaded_file.read()
        
        
        if entered_otp == session_otp :
            Name = request.session.get('Name')
            Number = request.session.get('Number')
            Email = request.session.get('Email')
            Password = request.session.get('Password')
            City = request.session.get('City')
            State = request.session.get('State')
            Zip = request.session.get('Zip')
            Superuser = False
            
            upload_folder = "D:\DOCLINK\MEETBOT FOLDER\MeetBotStorage\DOCS"
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, uploaded_file.name)
            with open(file_path, 'wb') as destination:
                destination.write(File_content) 
            
            myclient = pymongo.MongoClient('mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true')
            db = myclient["PROJECT"]
            collection = db["Registerauthentication"]
            
            # user = User.objects.create_user(
            # username=Name , email=Email )
            # user.set_password(Password)
            # user.save()
            
            dict = {'Name':Name,'Number':Number,'Email':Email,'Password':Password,'City':City,'State':State,'Zip':Zip,'Superuser':Superuser ,'File_path' : file_path , 'File' : File_content}
            collection.insert_one(dict)
            
            send_mail([Email]," Registration ", f"your Registration request is being Processed , will confirm within 24 hrs")
            
            del request.session['Name']
            del request.session['Number']
            del request.session['Email']
            del request.session['Password']
            del request.session['City']
            del request.session['State']
            del request.session['Zip']
            del request.session['from_register']
            del request.session['Otp']
            
            messages.info(request, "Request Sent Successfully!")
            return redirect('loginone')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            del request.session['Name']
            del request.session['Number']
            del request.session['Email']
            del request.session['Password']
            del request.session['City']
            del request.session['State']
            del request.session['Zip']
            del request.session['from_register']
            del request.session['Otp']
            return redirect('register')
    
    return render(request,"registercon.html")

@login_required(login_url='loginone')
def registerauthentication(request):
    user = request.user 
    username = user.username
    email = user.email
    db = myclient["PROJECT"]
    collection = db["UserData"]
    pipeline = [{"$match": {"Name":username,"Email":email}}]
    x = collection.aggregate(pipeline)
    for i in x:
        Superuser = i.get('Superuser')
        
    if Superuser == True:
        db = myclient["PROJECT"]
        collection = db["Registerauthentication"]
        all_data = list(collection.find())
        
        for item in all_data:
            item['id_str'] = str(item['_id'])
        
        return render(request, 'registerauthentication.html' ,{'all_data': all_data})
    
    else:
        return redirect('mainhome')

from bson.objectid import ObjectId
@login_required(login_url='loginone')
def operate_item(request, item_id):
    user = request.user 
    username = user.username
    email = user.email
    db = myclient["PROJECT"]
    collection = db["UserData"]
    pipeline = [{"$match": {"Name":username,"Email":email}}]
    x = collection.aggregate(pipeline)
    for i in x:
        Superuser = i.get('Superuser')
        
    if Superuser == True:
        db = myclient["PROJECT"]
        collection = db["Registerauthentication"]
        item = collection.find_one({"_id": ObjectId(item_id)})
        Name = item.get('Name')
        Number = item.get('Number')
        Email = item.get('Email')
        Password = item.get('Password')
        City = item.get('City')
        State = item.get('State')
        Zip = item.get('Zip')
        Superuser = item.get('Superuser')
        File_path = item.get('File_path')
        Doctor = True
        Patient = False
        
        user = User.objects.create_user(username=Name , email=Email )
        user.set_password(Password)
        user.save()
        
        db = myclient["PROJECT"]
        collection = db["UserData"]
        dict = {'Name':Name,'Number':Number,'Email':Email,'Password':Password,'City':City,'State':State,'Zip':Zip,'Superuser':Superuser ,'File_path' : File_path ,'Doctor' :Doctor , 'Patient' :Patient }
        collection.insert_one(dict)
        
        db = myclient["PROJECT"]
        collection = db["Registerauthentication"]
        qurey = {"_id": ObjectId(item_id)}
        collection.delete_one(qurey)  
        
        db = myclient["PROJECT"]
        collection = db["Profile"]
        dict = {'Name':Name,'Number':Number,'Email':Email,'City':City,'Doctor' :True , 'Patient' :False ,'FilePath': "profilepic/DDD.jpg" , 'BloodGroup': 'Not Mentioned' , 'Age' : 'Not Mentioned' ,'Gender' : 'Not Mentioned' , 'Emergency Contact' : 'None' , 'Specilazitation' : 'None' }
        collection.insert_one(dict) 
        
        
        send_mail([Email]," Account Created Sucessfully ", f"login Name : {Name} , Password : {Password} , dont share with others ")
    else:
        return redirect('mainhome')
    
    return redirect ('registerauthentication')
    

@never_cache
def loginone(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        Name = request.POST.get('Name')
        if not User.objects.filter(username=Name).exists():
            print()
            messages.error(request, 'Invalid Name')
            return redirect('loginone')
        db = myclient["PROJECT"]
        collection = db["UserData"]
        pipeline = [{"$match": {"Name":Name}}]
        x = collection.aggregate(pipeline)
        for i in x:
            Superuser = i.get('Superuser')
            Password = i.get('Password')
        
        if Superuser == True:
            user = authenticate(username= Name, password=Password)
            login(request, user)
            return redirect('home')
            
        request.session['Name'] = Name
        request.session['from_one'] = True
        messages.info(request, f"{Name}")
        return redirect('logintwo')
            
    return render(request,"loginone.html")

@never_cache
def logintwo(request):
    if request.user.is_authenticated:
        return redirect('home')
    if not request.session.get('from_one'):
        return redirect('loginone')
    
    if request.method == "POST":
        Password = request.POST.get('Password')
        Name = request.session.get('Name')
        
        user = authenticate(username= Name, password=Password)
        if user is None:
            messages.error(request, "Invalid Password")
            if 'from_one' in request.session:
                del request.session['from_one']
            return redirect('loginone')
        else:
            login(request, user)
            if 'from_one' in request.session:
                del request.session['from_one']
            return redirect('home')
    
    return render(request,"logintwo.html")

def logoutp(request):
    logout(request)
    request.session.flush()
    cache.clear()
    return redirect('loginone')

@never_cache
@login_required(login_url='loginone')
def home(request):
    # user = request.user 
    # username = user.username
    # email = user.email
    # db = myclient["PROJECT"]
    # collection = db["UserData"]
    # pipeline = [{"$match": {"Name":username,"Email":email}}]
    # x = collection.aggregate(pipeline)
    
    # for i in x:
    #     Name = i.get('Name')
    #     Email = i.get('Email')
    #     Number = i.get('Number')
    #     City = i.get('City')
    #     State = i.get('State')
    #     Superuser = i.get('Superuser')

 
    return render(request, "home.html") #,{"Name": Name, "Email": Email, "Number":Number, "City":City, "State":State, "Superuser":Superuser }

@never_cache
@login_required(login_url='loginone')
def adminacess(request):
    user = request.user 
    username = user.username
    email = user.email
    db = myclient["PROJECT"]
    collection = db["UserData"]
    pipeline = [{"$match": {"Name":username,"Email":email}}]
    x = collection.aggregate(pipeline)
    for i in x:
        Superuser = i.get('Superuser')
        Doctor = i.get('Doctor')
        
    if Superuser or Doctor:
        if request.method == 'POST':
            Name = request.POST.get('Name')
            Number = request.POST.get('Number')
            Email = request.POST.get('Email')
            Password = request.POST.get('Password')
            City = request.POST.get('City')
            State = request.POST.get('State')
            Zip = request.POST.get('Zip')
            Patient = True
            
            if User.objects.filter(username=Name).exists():
                messages.info(request, "Username already taken!")
                return redirect('adminacess')
        
            if User.objects.filter(email=Email).exists():
                messages.info(request, "In this Email account already exists")
                return redirect('adminacess')
        
            if len(Number) == 10:
                pass
            else:
                messages.error(request, "check your number")
                return redirect('adminacess')
        
            if len(Name) >= 3:
                pass
            else:
                messages.error(request, "lenght of name shoud be grater than 3")
                return redirect('adminacess')
        
            if len(Password) >= 5:
                pass
            else:
                messages.error(request, "lenght of Password shoud be grater than 3")
                return redirect('adminacess')
        
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
            if Email and re.match(email_regex, Email):
                pass
            else:
                messages.error(request, "this Email account is invalid")
                return redirect('adminacess')
            
            user = User.objects.create_user(
            username=Name , email=Email )
            user.set_password(Password)
            user.save()
            
            dict = {'Name':Name,'Number':Number,'Email':Email,'Password':Password,'City':City,'State':State,'Zip':Zip,'Patient':Patient , 'Doctor': False , 'Superuser': False}
            collection.insert_one(dict)
            
            db = myclient["PROJECT"]
            collection = db["Profile"]
            dict = {'Name':Name,'Number':Number,'Email':Email,'City':City,'Doctor' :False , 'Patient' :True ,'FilePath': "profilepic/PPP.jpg" , 'BloodGroup': 'Not Mentioned' , 'Age' : 'Not Mentioned' ,'Gender' : 'Not Mentioned' , 'Emergency Contact' : 'None' , 'Specilazitation' :"None"  }
            collection.insert_one(dict)
            
            send_mail([Email],"Account Created", f"your Patient account created Sucessfully")
            
            messages.info(request, "User created")
            
            return redirect("adminacess")
        
        return render(request,"admin.html")
    else:
        return redirect("home")
        

import asyncio
import random
from playwright.async_api import async_playwright
import datetime
import ffmpeg
import subprocess  # To run FFmpeg commands
import time        # For waiting during recording
import signal      # To handle keyboard interrupts (Ctrl+C)
import os          # To handle file paths and create directories
from datetime import datetime
import threading
from .bot import Meetbotprocess 
   
loop = asyncio.new_event_loop()    # run async function process     pass this with func to run in async

def start_loop():
    """
    Starts an asyncio event loop in a separate thread.
    """
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Start the loop in a separate thread
threading.Thread(target=start_loop, daemon=True).start()

@never_cache
@login_required(login_url='loginone')
def Meetbot(request):
    user = request.user 
    username = user.username
    email = user.email
    db = myclient["PROJECT"]
    collection = db["UserData"]
    pipeline = [{"$match": {"Name":username,"Email":email}}]
    x = collection.aggregate(pipeline)
    for i in x:
        Name = i.get('Name')
        
    current_datetime = datetime.now()
    # Format the date and time for the filename
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M")
    output_filename = f"{Name}{formatted_datetime}"
    
    if request.method == 'POST':
        # BotEmail = request.POST.get('Email')
        # BotPassword = request.POST.get('Password')
        MeetLink = request.POST.get('meetlink')
        nativelanguage = request.POST.get('nativelanguage')
        
        BotEmail = "akshaaykg1@gmail.com"
        BotPassword = "PASSWORD 10"
              
        messages.info(request, "got input Processing ")
        
        asyncio.run_coroutine_threadsafe(Meetbotprocess(user,username,email,BotEmail,BotPassword,MeetLink,output_filename,nativelanguage),loop) 
        return redirect('MessageDisplay')
    
    return render(request,"meet.html")



@never_cache
@login_required(login_url='loginone')
def MessageDisplay(request):
    user = request.user 
    username = user.username
    email = user.email
    
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    collection = db['meetingdatacollection']
    
    pipeline = [
    {"$match": {"username": f"{username}", "email": f"{email}"}},
    { "$sort": { "formatted_date": -1 } },  # Sort by "amount" in descending order
    {"$project" : { "_id": 0,"message_list": 0,"participant_list": 0,"video_path": 0}},
    ]
    
    data = collection.aggregate(pipeline)
    
    
    return render (request , 'messagedisplay.html', {'username' : username , 'email': email , 'meeting_data' :data})


@never_cache
def updatepassword(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        Name = request.POST.get('Name')
        Email = request.POST.get('email')
        if not User.objects.filter(username=Name,email=Email).exists():
            print()
            messages.error(request, 'Invalid Name or Email')
            return redirect('updatepassword')
        
        random_number = random.randint(10000, 99999)
        print('=====================> your otp is ' f'{random_number}')
        
        request.session['from_updatepassword'] = True
        request.session['Name'] = Name
        request.session['Email'] = Email
        request.session['Optupdate'] = random_number
        
        send_mail([Email]," Update password ", f"your otp is {random_number} dont share with others")

        messages.info(request, f"Otp sent to {Email}")
        return redirect('updatepasswordconfirm')
        
    return render (request,'updatepassword.html')



def updatepasswordconfirm(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if not request.session.get('from_updatepassword'):
        messages.error(request, "to update password fill this form")
        return redirect('updatepassword')
    
    if request.method == 'POST':
        new_password = request.POST.get('Newpassword')
        entered_otp = int(request.POST.get('Number'))
        session_otp = int(request.session.get('Optupdate'))
        
        if entered_otp == session_otp :
            Name = request.session.get('Name')
            Email = request.session.get('Email')
            
            user = User.objects.get(username=f'{Name}',email = f'{Email}')
            user.set_password(new_password)
            user.save()
            
            client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
            db = client["PROJECT"]
            collection = db["UserData"]
            qurey = {"Name": Name,"Email":Email}
            updatequrey = {"$set":{"Password":new_password}}
            x = collection.update_one(qurey,updatequrey)

            del request.session['Name']
            del request.session['Email']
            del request.session['Optupdate']
            del request.session['from_updatepassword']
            
            messages.info(request, "Password Updated Successfully!")
            return redirect('loginone')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            del request.session['Name']
            del request.session['Email']
            del request.session['Optupdate']
            del request.session['from_updatepassword']
            return redirect('updatepassword')
    
    return render(request,"updatepasswordconfirm.html")

def mainhome(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request,"mainhome.html")


@login_required(login_url='loginone')
def Profile(request):
    user = request.user 
    username = user.username
    email = user.email
    
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    collection = db['Profile']
    
    pipeline = [
    {"$match": {"Name": f"{username}", "Email": f"{email}"}}
    ]
    
    Profiledata = list(collection.aggregate(pipeline))
    
    return render (request , 'profile.html', {'username' : username , 'email': email , 'Profiledata' :Profiledata})


from django.conf import settings
import os

@login_required(login_url='loginone')
def Editprofile(request):
    user = request.user
    username = user.username
    email = user.email

    # Connect to MongoDB
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    collection = db['Profile']

    if request.method == 'POST':
        # Initialize an empty dictionary for updates
        update_data = {}

        # Get data from the form and check if it's provided
        blood_group = request.POST.get('BloodGroup')
        if blood_group:
            update_data["BloodGroup"] = blood_group

        age = request.POST.get('Age')
        if age:
            update_data["Age"] = age

        gender = request.POST.get('Gender')
        if gender:
            update_data["Gender"] = gender

        emergency_contact = request.POST.get('EmergencyContact')
        if emergency_contact:
            update_data["EmergencyContact"] = emergency_contact  # Correctly set key

        # Debugging for Specialization
        specialization = request.POST.get('specialization') 
        if specialization:
            update_data["Specilazitation"] = specialization  # Correctly set key

        # Handle file upload
        static_folder = "D:\DOCLINK\MEETBOT FOLDER\MeetBotProject\MeetApp\static\profilepic"
        file = request.FILES.get('profile_image')
        if file:
            file_name = f"{username}_profilepic{os.path.splitext(file.name)[1]}"  # Get file extension
            file_path = os.path.join(static_folder, file_name)
            
            # Remove the old file if it exists
            if os.path.exists(file_path):
                os.remove(file_path)

            # Save the new file
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Update the file path in the database
            update_data["FilePath"] = f"profilepic/{file_name}"

        # Update the MongoDB document only if there are fields to update
        if update_data:
            collection.update_one(
                {"Name": username, "Email": email},
                {"$set": update_data}
            )

        return redirect('Profile')  # Redirect to the profile page after saving

    # Fetch user data for display in the form
    pipeline = [{"$match": {"Name": username, "Email": email}}]
    Profiledata = list(collection.aggregate(pipeline))

    # If no profile data is found, ensure the template renders without errors
    if not Profiledata:
        Profiledata = [{}]  # Use an empty dictionary as a placeholder

    return render(request, 'Editprofile.html', {
        'username': username,
        'email': email,
        'Profiledata': Profiledata
    })

@login_required(login_url='loginone')
def SendMessage(request):
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    Patient_collection = db['Profile']
    messages_collection = db['messages']
    
    if request.method == 'POST':
        Name = request.user.username.replace(" ", "_").replace("/", "_")
        from_email = request.user.email
        to_email = request.POST.get('to')
        message_text = request.POST.get('message')
        image_file = request.FILES.get('image')
        DateTime = datetime.now().strftime('%Y%m%d%H%M%S').replace(":", "-")
        
        static_folder = "D:\DOCLINK\MEETBOT FOLDER\MeetBotProject\MeetApp\static"
        
        image_path = None
        if image_file:
            image_filename = f"{Name}_img_{DateTime}.jpg"
            image_path = os.path.join('Uploads', image_filename)  # Save to a subfolder in static/
            absolute_path = os.path.join(static_folder, image_path)
            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
            with open(absolute_path, 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
            
                    
        messages_collection.insert_one({
            "from": from_email,
            "to": to_email,
            "message": message_text,
            "image_path": image_path,
            "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })
        
        return redirect('SeeMessage')
    #start
    Name = request.user.username
    from_email = request.user.email
    user_profile = Patient_collection.find_one({"Name": Name, "Email": from_email})
    
    if user_profile:
        # is_doctor = user_profile.get('Doctor', False)
        is_patient = user_profile.get('Patient', False)
        
        if is_patient:
            # If the user is only a patient, show all doctors
            doc_emails = Patient_collection.find({"Doctor": True}, {"Email": 1, "_id": 0})
            doctors = [doctor['Email'] for doctor in doc_emails]
            all_users = doctors
            return render(request, 'SendMessage.html', {'all_users':  all_users})
        
        else:
            #If the user has neither a doctor nor a patient role, show both doctors and patients
            patient_emails = Patient_collection.find({"Patient": True}, {"Email": 1, "_id": 0})
            doc_emails = Patient_collection.find({"Doctor": True}, {"Email": 1, "_id": 0})
            patients = [patient['Email'] for patient in patient_emails]
            doctors = [doctor['Email'] for doctor in doc_emails]
            all_users = patients + doctors
            return render(request, 'SendMessage.html', {'all_users':  all_users})



@login_required(login_url='loginone')
def SeeMessage(request):
    emailsearch = request.user.email
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    messages_collection = db['messages']
    
    messages = messages_collection.find({"to": emailsearch}).sort("datetime", -1)
    messages_list = list(messages)
    
    return render(request ,"SeeMessage.html", {'messages': messages_list})



@login_required(login_url='loginone')
def AddProduct(request):
    user = request.user 
    username = user.username
    email = user.email
    db = myclient["PROJECT"]
    collection = db["UserData"]
    pipeline = [{"$match": {"Name":username,"Email":email}}]
    x = collection.aggregate(pipeline)
    for i in x:
        Superuser = i.get('Superuser')
        
    if Superuser == True:
        client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
        db = client["PROJECT"]
        Product_collection = db['Product']
        if request.method == 'POST':
            Product_Name = request.POST.get('productName')
            Price = request.POST.get('price')
            description = request.POST.get('description')
            Product_Type = request.POST.get('productType')
            Image_File = request.FILES.get('image')
            
            static_folder = "D:\DOCLINK\MEETBOT FOLDER\MeetBotProject\MeetApp\static"
            Image_Path = None
            if Image_File:
                Image_File_Name = f"{Product_Name}.jpg"
                Image_Path = os.path.join('products', Image_File_Name)  # Save to a subfolder in static/
                absolute_path = os.path.join(static_folder, Image_Path)
                os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
                with open(absolute_path, 'wb') as f:
                    for chunk in Image_File.chunks():
                        f.write(chunk)
            
            Product_collection.insert_one({
                "Product Name": Product_Name,
                "Price": Price,
                "Description": description,
                "Product Type": Product_Type,
                "Image Path": Image_Path,
                })
            
            messages.info(request, "Product Added Successfully")
            return redirect('AddProduct')
        
        return render(request,'addproduct.html')
    
    else:
        return redirect('home')
    

@login_required(login_url='loginone')
def DeleteProduct(request):
    user = request.user 
    username = user.username
    email = user.email
    db = myclient["PROJECT"]
    collection = db["UserData"]
    pipeline = [{"$match": {"Name":username,"Email":email}}]
    x = collection.aggregate(pipeline)
    for i in x:
        Superuser = i.get('Superuser')
        
    if Superuser == True:
        client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
        db = client["PROJECT"]
        Product_collection = db['Product']
        if request.method == 'POST':
            Product_Name = request.POST.get('productName')
            Price = request.POST.get('price')
            
            delete_result = Product_collection.delete_one({
                "Product Name": Product_Name,
                "Price": Price  
            })
            
            if delete_result.deleted_count > 0:
                messages.info(request, "Product Deleted Successfully")
            else:
                messages.error(request, "No matching product found")
                
            return redirect('DeleteProduct')
        
        return render(request,'deleteproduct.html')
    
    else:
        return redirect('home')



@login_required(login_url='loginone')
def Products(request):
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    Product_collection = db['Product']
    product_type = request.GET.get('product_type')
    if product_type:
        products = Product_collection.find({"Product Type": product_type})
    else:
        products = Product_collection.find()
        
    Product_list = []
    for product in products:
        Product_list.append({
            "ProductName": product.get("Product Name"),
            "Price": product.get("Price"),
            "Description": product.get("Description"),
            "ProductType": product.get("Product Type"),
            "ImagePath": product.get("Image Path"),
        })     
    return render(request ,"products.html", {'Product': Product_list})


@login_required(login_url='loginone')
def AddToCart(request):
    if request.method == 'POST':
        user = request.user
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')

        client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
        db = client["PROJECT"]
        cart_collection = db['Cart']

        # Add to cart
        cart_collection.insert_one({
            "Name": user.username,
            "Email": user.email,
            "Product Name": product_name,
            "Price": price,
            "Quantity": quantity
        })

        messages.success(request, "Product added to cart successfully!")
        return redirect('Products')



@login_required(login_url='loginone')
def Cart(request):
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    Cart_collection = db['Cart']
    user = request.user
    Name = user.username
    Email = user.email
    items = []
    for item in Cart_collection.find({"Name": Name, "Email": Email}):
        item["id"] = str(item.pop("_id"))  # Rename '_id' to 'id'
        item["Product_Name"] = item.pop("Product Name", "Unknown Product")  # Handle field
        items.append(item)

    total_amount = sum(int(item['Price']) * int(item['Quantity']) for item in items)
    
    request.session['total_amount'] = total_amount
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            Cart_collection.delete_one({"_id": ObjectId(item_id)})
            return redirect('Cart')

    return render(request, "Cart.html", {'items': items, 'total_amount': total_amount})


import smtplib
from email.message import EmailMessage
@login_required(login_url='loginone')
def checkout(request):
    # Get total amount from session (if available)
    total_amount = request.session.get('total_amount')
    if int(total_amount) == 0:
        messages.error(request, "No item in Cart")
        return redirect('Products')
    
    if request.method == 'POST':
        # Handle the form submission logic
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        Image_File = request.FILES.get('file')
        payid = request.POST.get('payid')
        user = request.user
        Name = user.username
        Email = user.email
        
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
        db = client["PROJECT"]
        Cart_collection = db['Cart']
        order_collection = db['order']
        
        # Get all items in the cart
        cart_items = Cart_collection.find({"Name": Name, "Email": Email})
        
        # Folder for saving image files
        static_folder = "D:\DOCLINK\MEETBOT FOLDER\MeetBotProject\MeetApp\static"
        Image_Path = None
        
        # Save the uploaded image if exists
        if Image_File:
            try:
                Image_File_Name = f"{Name}_{payid}.jpg"  # Unique name to avoid overwriting
                Image_Path = os.path.join('orderhistory', Image_File_Name)  # Save to 'order' subfolder
                absolute_path = os.path.join(static_folder, Image_Path)
                print(f"Saving image to: {absolute_path}")
                os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
                with open(absolute_path, 'wb') as f:
                    for chunk in Image_File.chunks():
                        f.write(chunk)
                print(f"Image saved successfully to {absolute_path}")
            
            except Exception as e:
                print(f"Error saving image: {e}")
        
        # Initialize variables to store products and total price
        products = []
        total_order_price = 0

        # Loop over cart items and calculate total price
        for item in cart_items:
            product_name = item.get('Product Name')
            price = int(item.get('Price', 0))  # Default to 0 if Price is not found or is invalid
            quantity = int(item.get('Quantity', 0))
            total_price = price * quantity
            
            # Add product details to the products list
            products.append({
                "Product Name": product_name,
                "Price": price,
                "Quantity": quantity,
                "Total Price": total_price
            })
            
            # Accumulate total price
            total_order_price += total_price
            
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M")
        
        otp = random.randint(10000, 99999)
        
        
        # Prepare order data
        order_data = {
            "Name": Name,
            "Email": Email,
            "Address": address,
            "Phone": phone,
            "PayID": payid,
            "Total_Price": total_order_price,  # Total price of the order
            "Products": products,  # List of products
            "Image_Path": Image_Path,  # Image path for the order (if available)
            "Product status": "yet to be delivered",
            "Date": formatted_datetime,
            "Otp": otp
        }

        # Insert the order into the 'order' collection
        order_collection.insert_one(order_data)

        # Clear the user's cart after the order is placed
        Cart_collection.delete_many({"Name": Name, "Email": Email})
        
        msg = EmailMessage()
        msg['Subject'] = f"order Summary {formatted_datetime}"
        msg['From'] = 'akshaay.kg2021@vitbhopal.ac.in'
        msg['To'] = ', '.join([Email])
        message = f"""
        Hello {Name} ! 
        Heare is your Order summary  
        Date : {formatted_datetime}
        Total Amount : {total_order_price}
        Addreess : {address}
        Otp : {otp}
        Products: {products}
        """
        msg.set_content(message)
        server='smtp.gmail.com'
        from_email='akshaay.kg2021@vitbhopal.ac.in'
        server = smtplib.SMTP(server, 587)
        server.ehlo()
        server.starttls()
        server.set_debuglevel(1)
        server.login('akshaay.kg2021@vitbhopal.ac.in', 'jvuu kwss mneg aklz')
        server.send_message(msg)
        server.quit()
        return redirect('orderview')  
    
    return render(request, 'checkout.html', {'total_amount': total_amount})


@login_required(login_url='loginone')
def orderview(request):
    user = request.user
    username = user.username
    email = user.email

    # MongoDB connection
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    order_collection = db['order']
    user_collection = db["UserData"]

    # Fetch the Superuser status from the UserData collection
    pipeline = [{"$match": {"Name": username, "Email": email}}]
    x = user_collection.aggregate(pipeline)
    superuser = False
    for i in x:
        superuser = i.get('Superuser', False)

    # Fetch orders based on Superuser status
    if superuser:
        # If superuser, fetch all orders without filtering by Name and Email
        order_items = order_collection.find().sort("Date", -1)
    else:
        # Otherwise, filter orders by Name and Email
        order_items = order_collection.find({"Name": username, "Email": email}).sort("Date", -1)

    # Process orders to fix keys with spaces
    orders = []
    for order in order_items:
        processed_products = [
            {
                "ProductName": product.get("Product Name"),
                "Price": product.get("Price"),
                "Quantity": product.get("Quantity"),
                "TotalPrice": product.get("Total Price"),
                "ProductStatus": product.get("Product status"),
            }
            for product in order.get("Products", [])
        ]
    
        # Convert MongoDB _id to string
        order_id = str(order.get("_id"))

        orders.append({
            "OrderID": order_id,  # Include the _id as OrderID
            "Name": order.get("Name"),
            "Email": order.get("Email"),
            "Address": order.get("Address"),
            "Phone": order.get("Phone"),
            "PayID": order.get("PayID"),
            "Total_Price": order.get("Total_Price"),
            "Products": processed_products,
            "Image_Path": order.get("Image_Path"),
            "Product_status": order.get("Product status"),
            "Date": order.get("Date"),
            "Otp": order.get("Otp"),
            "Superuser": superuser,  # Pass the Superuser flag to the template
        })

    # Render the data into the template
    return render(request, 'orderview.html', {'orders': orders, 'superuser': superuser})



from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
import pymongo
from bson import ObjectId  # Add this import at the top of your file

@login_required(login_url='loginone')
def edit_order_status(request, order_id):
    # MongoDB connection
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    order_collection = db['order']

    # Fetch the order by order_id
    order = order_collection.find_one({"_id": ObjectId(order_id)})  # Use ObjectId here

    if not order:
        raise Http404("Order not found")

    # Convert `_id` to `OrderID` for template compatibility
    order['OrderID'] = str(order.pop('_id'))  # Replace `_id` with `OrderID`

    # Check if the user is a superuser
    user = request.user
    pipeline = [{"$match": {"Name": user.username, "Email": user.email}}]
    x = db["UserData"].aggregate(pipeline)
    superuser = False
    for i in x:
        superuser = i.get('Superuser', False)

    if not superuser:
        return redirect('orderview')  # Redirect non-superusers if they try to access this page

    # Handle form submission
    if request.method == 'POST':
        new_status = request.POST.get('product_status')
        if new_status:
            # Update the status in the database
            order_collection.update_one(
                {"_id": ObjectId(order_id)},  # Use ObjectId here
                {"$set": {"Product status": new_status}}
            )
            # Redirect to the order view page after update
            return redirect('orderview')

    return render(request, 'editorderstatus.html', {'order': order})


import requests
@login_required(login_url='loginone')
def emergency(request):
    print("Emergency ========================================================================>")
    user = request.user
    Name = user.username
    Email = user.email
    Usernumber = ""
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    userdata_collection = db['UserData']
    pipeline = [{"$match": {"Name": Name, "Email": Email}},{"$project": {"_id": 0, "Number": 1}}]
    result = userdata_collection.aggregate(pipeline)
    for doc in result:
        Usernumber = doc.get("Number")
    Doctor = []
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M")
    response = requests.get("http://ipinfo.io/json")
    data = response.json()
    ip = data.get("ip")
    location = data.get("loc")
    latitude, longitude = location.split(',')
    print(f"IP Address: {ip}")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="my_geopy_app")
    location = geolocator.reverse(latitude+","+longitude)
    print(location)
    address = location.raw['address']
    state = address.get('state', '')
    client = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
    db = client["PROJECT"]
    userdata_collection = db['UserData']
    pipeline = [{"$match": {"State": state, "Doctor": True}},{"$project": {"_id": 0, "Email": 1}}]
    result = userdata_collection.aggregate(pipeline)
    for doc in result:
        Doctor.append(doc.get("Email"))
        
    msg = EmailMessage()
    msg['Subject'] = f"Emergency Alert"
    msg['From'] = 'akshaay.kg2021@vitbhopal.ac.in'
    msg['To'] = ', '.join(Doctor)
    message = f"""
        Hello Doctors ! 
        there is a person in emergency , if you are available please help him , Date : {formatted_datetime}
        Name : {Name} 
        Email : {Email}
        Number : {Usernumber}
        Location : {address}
        """
    msg.set_content(message)
    server='smtp.gmail.com'
    from_email='akshaay.kg2021@vitbhopal.ac.in'
    server = smtplib.SMTP(server, 587)
    server.ehlo()
    server.starttls()
    server.set_debuglevel(1)
    server.login('akshaay.kg2021@vitbhopal.ac.in', 'jvuu kwss mneg aklz')
    server.send_message(msg)
    server.quit()
    return HttpResponse("Emergency Alert Sent to Doctors. Doctors will contact you soon.") 