import asyncio
import random
from playwright.async_api import async_playwright
import datetime
import ffmpeg
import subprocess  # To run FFmpeg commands
import time        # For waiting during recording
import signal      # To handle keyboard interrupts (Ctrl+C)
import os          # To handle file paths and create directories



async def meeting(email,password ,meetlink, output_filename, User_email):
    output_folder = "D:\DOCLINK\MEETBOT FOLDER\MeetBotStorage"
    # Ensure the folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_file = os.path.join(output_folder, f"{output_filename}.flv")
    audio_device = 'Stereo Mix (Realtek(R) Audio)'
    
    ffmpeg_command = [
        "C:/Users/AKSHAAY KG/Downloads/ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe",
        "-y",
        "-video_size", "1920x1080",
        "-framerate", "30",
        "-f", "gdigrab",
        "-i", "desktop",
        "-f", "dshow",
        "-i", f"audio={audio_device}",
        "-probesize", "10000000",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-strict", "experimental",
        output_file
    ]

    delay = random.randint(100, 300)
    participant_list = set()
    message_list = []
    start_time = datetime.datetime.now()
    
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel='chrome', args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context()  # record_video_dir="C:/Users/AKSHAAY KG/Videos/Captures"
        page = await context.new_page()
        
        await context.grant_permissions(['camera', 'microphone'])
        await page.mouse.move(100, 100)
        
        process = subprocess.Popen(ffmpeg_command) # start recording 
        
        await page.goto('https://workspace.google.com/products/meet/')
        await page.mouse.move(200, 200)
        await page.wait_for_timeout(5000)
        
        signin = await page.wait_for_selector("//span[contains(text(),'Sign in')]")
        await signin.click()  # sign in button
        await page.wait_for_timeout(2000)
        await page.mouse.move(300, 300)
        email_in = await page.wait_for_selector('//input[@type="email"]')
        await email_in.type(email, delay=delay)  # email box
        await page.wait_for_timeout(2000)
        click_to_pass = await page.wait_for_selector("//span[contains(text(),'Next')]")
        await click_to_pass.click(delay=delay)  # click next to pass
        await page.wait_for_timeout(2000)
        await page.mouse.move(400, 400)
        password_in = await page.wait_for_selector('//input[@type="password"]')
        await password_in.type(password, delay=delay)  # pass box
        await page.wait_for_timeout(2000)
        enter_pass = await page.wait_for_selector("//span[contains(text(),'Next')]")
        await enter_pass.click(delay=delay)  # pass enter
        await page.wait_for_timeout(2000)
        await page.mouse.move(500, 500)
        
        meet = await page.wait_for_selector('//input[@id="i8"]')
        await meet.type(meetlink, delay=1000)  # meetid enter
        await page.wait_for_timeout(2000)
        await page.mouse.move(600, 600)
        join = await page.wait_for_selector("//span[contains(text(),'Join')]", timeout=10000)
        await join.click(delay=1000)  # meet join button
        await page.wait_for_timeout(2000)
        await page.mouse.move(500, 500)
        
        div_selector_wrongmeetlink = '[jscontroller="m2Zozf"]'
        div_present = await page.locator(div_selector_wrongmeetlink).count() > 0
        
        if div_present:
            print("You can't join this call. Wrong meet link. check link ")
            process.terminate()  # Stop recording
            process.wait()
            print(f"Recording saved to {output_file}")
            await page.close()
            
            msg = EmailMessage()
            msg['Subject'] = f"Error during Meeting"
            msg['From'] = 'akshaay.kg2021@vitbhopal.ac.in'
            msg['To'] = ', '.join([User_email])
            message = "Wrong Gmeet link . if you could not even copy paste link properly dont use bot leave"
            msg.set_content(message)
            try:
                server='smtp.gmail.com'
                from_email='akshaay.kg2021@vitbhopal.ac.in'
                server = smtplib.SMTP(server, 587)
                print("selected server")
                print("connected server")
                server.ehlo()
                server.starttls()
                server.set_debuglevel(1)
                server.login('akshaay.kg2021@vitbhopal.ac.in', 'jvuu kwss mneg aklz')  # Use actual password or app password
                print("loginnn")
                server.send_message(msg)
                print("msg send")
                server.quit()
                print("quittt")
                print('Successfully sent the mail.')
                
            except aiosmtplib.SMTPException as e:
                print(f"Error sending mail: {e}")
            except Exception as e:
                print(f" Error occured while processing mail {e}")
            
            return participant_list, message_list
        else:
            pass
        
        await page.wait_for_timeout(5000)
        cam_element = await page.wait_for_selector('//div[@jsname="psRWwc"]')
        cam_value = await cam_element.get_attribute("data-is-muted")
        if cam_value == 'true':
            print('muted')
        else:
            cam_button = await page.wait_for_selector('//div[@jsname="R3GXJb"]')
            await cam_button.click(delay=delay)  # on camera
         
            
        mic_element = await page.wait_for_selector('//div[@jsname="hw0c9"]')
        mic_value = await mic_element.get_attribute("data-is-muted")
        if mic_value == 'true':
            print('muted')
        else:
            mic_button = await page.wait_for_selector('//div[@jsname="Dg9Wp"]')
            await mic_button.click(delay=delay)  # on mike
            
        req_join = await page.wait_for_selector('[jsname="Qx7uuf"]', timeout=10000)
        await req_join.click(delay=delay)  # req to join button
        
        wait_time = random.randint(5, 10)
        
        try:
            caption_element = await page.wait_for_selector('//button[@jsname="r8qRAd"]', timeout=wait_time * 1000)
            print("Element found, continuing...")
            
        except Exception as e:
            print("Element not found")# Proceed with the next block of code if the element is not found
            try:        # Wait for the "Asking to be let in..." message to appear
                print("Waiting for 'Asking to be let in...' message...")
                await page.locator('div.dHFSie:text("Asking to be let in...")').wait_for(timeout=15000)  # 15 seconds timeout
                print("'Asking to be let in...' message is visible. Monitoring...")
                
                while True:
                    asking_to_be_let_in = await page.locator('div.dHFSie:text("Asking to be let in...")').is_visible()  # Check for the "Asking to be let in..." message
                    if asking_to_be_let_in:
                        print("Asking to be let in... Waiting for 5 seconds.")
                        await page.wait_for_timeout(500)  # Wait for 5 seconds and check again
                        continue  # Recheck the state
                    # If "Asking to be let in..." is no longer visible, check the next condition
                    cannot_join = await page.locator('div.dHFSie:text("You can\'t join this call")').is_visible()
                    if cannot_join:
                        print("You can't join this call. Ending the process.")
                        process.terminate()  # Stop recording
                        process.wait()
                        print(f"Recording saved to {output_file}")
                        await page.close()
                        msg = EmailMessage()
                        msg['Subject'] = f"Error during Meeting"
                        msg['From'] = 'akshaay.kg2021@vitbhopal.ac.in'
                        msg['To'] = ', '.join([User_email])
                        message = "You can't join this call. Someone denied your request or no one accepted your request"
                        msg.set_content(message)
                        try:
                            server='smtp.gmail.com'
                            from_email='akshaay.kg2021@vitbhopal.ac.in'
                            server = smtplib.SMTP(server, 587)
                            server.ehlo()
                            server.starttls()
                            server.set_debuglevel(1)
                            server.login('akshaay.kg2021@vitbhopal.ac.in', 'jvuu kwss mneg aklz')  # Use actual password or app password
                            server.send_message(msg)
                            server.quit()
                            print('Successfully sent the mail.')
                
                        except aiosmtplib.SMTPException as e:
                            print(f"Error sending mail: {e}")
                            
                        except Exception as e:
                           print(f" Error occured while processing mail {e}")
                           
                        return participant_list, message_list  # Exit the loop and function
                    # If neither "Asking to be let in..." nor "You can't join this call" is visible, continue
                    print("Neither 'Asking to be let in...' nor 'You can't join this call' is visible. Proceeding...")
                    break
            except Exception as e:
                print(f"Error while waiting for locators: {e}")  

        
        await oncaptions(page)
        await page.wait_for_timeout(10)    #waiting time
        
        await asyncio.sleep(2)
        message_button = await page.wait_for_selector('//button[@aria-label="Chat with everyone"]')
        message_val = await message_button.get_attribute("aria-pressed")
        if message_val == 'true':
            print('on messages')
        else:
            await message_button.click()
        
        await asyncio.sleep(1)
        messenger = await page.wait_for_selector('//textarea[@jsname="YPqjbf"]')
        await messenger.type("hello i am bot , bot joined")
        await page.wait_for_timeout(2000)
        await asyncio.sleep(1)
        msg_send = await page.wait_for_selector('//button[@jsname="SoqoBf"]')
        await msg_send.click(delay=delay)
        await page.wait_for_timeout(2000)
        
        fetch_task_participant = asyncio.create_task(fetch_participants(page, participant_list))
        await asyncio.sleep(2)
        fetch_task_messages = asyncio.create_task(fetch_messages(page, message_list))
        await asyncio.sleep(1)
        monitor_time_task = asyncio.create_task(monitor_meeting_time(page, start_time))
        
        monitor_task = asyncio.create_task(monitor_page(page,fetch_task_participant, fetch_task_messages, monitor_time_task))

        try:
            while True:
                await asyncio.sleep(10)
                message_end = await page.query_selector('[jsname="r4nke"]')
                
                if message_end:
                    message_text_end = await message_end.text_content()
                    if message_text_end != "Ready to join?":
                        print("Meeting disconnected or ended.")
                        break  # Exit the loop to reach `finally`
                    else:
                        print("Ready to join message detected, continuing.")
        except Exception as e:
            print(f"Error in meeting simulation: {e}")
            
        finally:
            process.terminate() # stop
            process.wait()
            print(f"Recording saved to {output_file}")
            for task in [fetch_task_participant, fetch_task_messages, monitor_task, monitor_time_task]:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            print("Tasks cancelled. Meeting ended.")
            
            print(f"Final participant list: {participant_list}")
            print(f"Final message list: {message_list}")
            await page.close()
            return participant_list, message_list , output_file

        
        
        
    
async def oncaptions(page):
    caption_element = await page.wait_for_selector('//button[@jsname="r8qRAd"]',timeout=120000)
    caption_value = await caption_element.get_attribute("aria-pressed")
    if caption_value == 'true':
        print('cap on')
    else:
        await caption_element.click()
 
   
async def fetch_participants(page, participant_list):
    async def update_participants():
        participant_button = await page.wait_for_selector('//button[@aria-label="People"]')
        participant_val = await participant_button.get_attribute("aria-pressed")
        if participant_val == 'true':
            print('on people')
        else:
            await participant_button.click()        
        
        
        try:
            # Get all elements matching the participant selector
            participants = await page.query_selector_all('//div[@jscontroller="ZHOeze"]')
            if not participants:
                print("No participants found. Check selectorsss.")
                return

            # Iterate over each element and extract `aria-label`
            for participant in participants:
                try:
                    aria_label = await participant.get_attribute("aria-label")
                    if aria_label:
                        participant_list.add(aria_label)
                    else:
                        print('no label')
                except Exception as inner_e:
                    print(f"Error accessing aria-label for a participant: {inner_e}")
            
            print(f"Updated participant list: {participant_list}")
        except Exception as e:
            print(f"Error fetching participants: {e}")
            raise

    while True:
        await update_participants()
        await asyncio.sleep(10)


async def fetch_messages(page, message_list):
    async def update_messages():
        message_button = await page.wait_for_selector('//button[@aria-label="Chat with everyone"]')
        message_val = await message_button.get_attribute("aria-pressed")
        if message_val == 'true':
            print('on messages')
        else:
            await message_button.click()        
        
        
        try:
            messages = await page.query_selector_all('//div[@jsname="Ypafjf"]')
            if not messages:
                print("No messages found. Check selectorsss.")
                return

            # Iterate over each element and extract `aria-label`
            for message in messages:
                try:
                    sender_name_element = await message.query_selector('.poVWob')
                    sender_name = await sender_name_element.text_content() if sender_name_element else "Unknown Sender"
                    
                    message_text_element = await message.query_selector('//div[@jsname="dTKtvb"]')
                    message_text = await message_text_element.text_content() if message_text_element else "No Message"
                    
                    if {"sender": sender_name, "message": message_text} not in message_list:
                        message_list.append({"sender": sender_name, "message": message_text})
                
                except Exception as e:
                    print(f"Error processing a message: {e}")   
                    continue
            
            print("Fetched messages:", message_list)
        except Exception as e:
            print(f"Error fetching participants: {e}")
            raise

    while True:
        await update_messages()
        await asyncio.sleep(10)


async def monitor_meeting_time(page, start_time):
    while True:
        elapsed_time = (datetime.datetime.now() - start_time).total_seconds() / 60  # Calculate elapsed time in minutes
        
        if elapsed_time > 3:
            print("Meeting has been running for over 30 minutes.")
            
            try:
                # Fetch the participant count
                participant_element = await page.query_selector('//div[@class="uGOf1d"]')
                if participant_element:
                    participant_count = int(await participant_element.text_content())
                    print(f"Current participant count: {participant_count}")
                    
                    if participant_count == 1:
                        print("Only one participant left. Leaving the meeting.")
                        end_button = await page.query_selector('//button[@jsname="CQylAd"]')
                        await end_button.click() # Call a function to leave the meeting
                        return
                    else:
                        print(f"{participant_count} participants present. Waiting for 5 more minutes.")
                        await asyncio.sleep(60)  # Wait for 5 minutes
                else:
                    print("Unable to fetch participant count. Retrying.")
            except Exception as e:
                print(f"Error fetching participant count: {e}")
        else:
            print(f"Elapsed time: {elapsed_time:.2f} minutes. Continuing to monitor.")
            await asyncio.sleep(60)  # Check every minute



async def monitor_page(page, fetch_task_participant, fetch_task_messages , monitor_time_task):
    try:
        while True:
            # Check for the message element to detect meeting status
            message_element = await page.query_selector('[jsname="r4nke"]')
            if message_element:
                message_text = await message_element.text_content()

                # If the message is anything other than "Ready to join?"
                if message_text != "Ready to join?":
                    print("Meeting disconnected or status changed, stopping fetch task participents.")
                    print("Meeting disconnected or status changed, stopping fetch task message.")
                    fetch_task_participant.cancel()  # Stop the fetch task
                    fetch_task_messages.cancel()
                    monitor_time_task.cancel()
                    return  # Exit monitoring task
                else:
                    print("Ready to join message detected, continuing.")
            
            await asyncio.sleep(30)  # Check every 45 seconds
    except Exception as e:
        print(f"Error in monitoring page: {e}")
        fetch_task_participant.cancel() 
        fetch_task_messages.cancel()
        monitor_time_task.cancel()
        

    
async def main(email,password,meetlink,output_filename,User_email):
    participant_list, message_list ,output_file  = await meeting(email = f"{email}",password = f"{password}" ,meetlink= f"{meetlink}", output_filename = f'{output_filename}' , User_email = f"{User_email}")
    print('--------------00000-------------')
    print("everything overrrrr ----------------------------------------------------")
    print(message_list)
    print(participant_list)
    print("over-------------------------")
    return message_list,participant_list,output_file


# asyncio.run(main(
#     email=BotEmail,
#     password=BotPassword,
#     meetlink=MeetLink,
#     output_filename=output_filename
# ))



# from pymongo import MongoClient
# import gridfs
# #!pip install Flask pymongo
# import pymongo

# output_folder = "C:/Users/AKSHAAY KG/Videos/Meet Bot"

# def Savevideodb(output_filename,username):
#     client = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = client["imagedb"]
#     fs = gridfs.GridFS(db)
#     path = os.path.join(output_folder, f"{output_filename}.flv",metadata={"uploaded_by": f"{username}"})
#     with open(path, "rb") as f:
#         file_id = fs.put(f,filename = {output_filename} )     # in fs.put content_type="video/mp4", metadata={"uploaded_by": "user123"}      
#         print(f"File stored with ID: {file_id}")
    
#     print('item saved in db')
  


# import os
# import subprocess
# target_size_gb = 1.95

# def get_file_size(output_filename):
#     file_path = "C:/Users/AKSHAAY KG/Videos/Meet Bot"
#     videopath = os.path.join(file_path, f"{output_filename}.flv")
#     """Get the size of the file in GB."""
#     file_size_bytes = os.path.getsize(videopath)
#     return file_size_bytes / (1024 ** 3) 

  

# import pymongo
# def store_meetdata(username,meetname,date,gemini_data,email,videoid):
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["meetingdata"]   #local db name
#     collection = db['meetingdatacollection']
#     dict = {'name':f'{username}', 'meetname': f'{meetname}' , "date": f'{date}' , "gemini_data" : f'{gemini_data}', "email" : f'{email}', "videoid" : f'{videoid}' }
#     collection.insert_one(dict)    


import smtplib
from email.message import EmailMessage
def send_mail(to_email, subject, message, server='smtp.gmail.com',
              from_email='akshaay.kg2021@vitbhopal.ac.in'):
    # import smtplib
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_email)
    msg.set_content(message)
    print(msg)
    try:
        # Connect using TLS
        server = smtplib.SMTP(server, 587)
        server.starttls()  # Secure the connection with TLS
        server.set_debuglevel(1)
        server.login(from_email, 'jvuu kwss mneg aklz')  # Use actual password or app password
        server.send_message(msg)
        server.quit()
        print('Successfully sent the mail.')
    
    except smtplib.SMTPException as e:
        print(f"Error sending mail: {e}")
        
    


from langchain_core.output_parsers import JsonOutputParser #pip install langchain 
import google.generativeai as genai
import os
import time
import aiosmtplib
import pymongo
async def geminicontentdata(message_list, participant_list, video_path , native_language, MeetLink , formatted_date ,username , email):
    os.environ['OPENAI_API_KEY'] = ("AIzaSyBZb-E0LNgp3X3nJ1mi77A_m5ib1B1AMoo")
    genai.configure(api_key=os.environ['OPENAI_API_KEY'])
    model = genai.GenerativeModel("gemini-1.5-flash")
    print(f"Uploading file... to gemini")
    video_file = genai.upload_file(path=video_path,mime_type='video/x-flv')
    print(f"Completed upload: {video_file.uri}")
    # Check whether the file is ready to be used.
    while video_file.state.name == "PROCESSING":
        print('... processing file', end='')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)
    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
    
    # Create the prompt.
    
    prompt = """
You are tasked with analyzing a doctor-patient meeting based on the provided files:

{video_link}: A video recording of the meeting.
{message_list}: A list of messages exchanged during the meeting.
{participant_list}: A list of participants in the meeting (doctor, patient, attendant if any).
{native_language}: The patient’s native language.
Instructions:
Step 1: Understand the Inputs Thoroughly
Video Content:
Watch the video attentively. Focus on what symptoms the patient describes and what instructions, treatments, or next steps the doctor advises.
Message List:
Read the messages to understand any additional clarifications or details provided by the doctor.
Participant List:
Identify the roles of the participants (doctor, patient, attendant if any). Do not mention the participants by name or identity in the output. Focus only on the content of the conversation.
Step 2: Generate Outputs
Provide the results in the following structured format:

1. Summary (English)
Write a brief and clear summary of the meeting in English.
Use language from the patient’s perspective, like: “You are having fever,” “The doctor advises you to…”
Focus only on the symptoms, the doctor's advice, and any treatments or next steps.
Do not mention the participants' identities or roles. Avoid unnecessary information.
If the conversation occurs in the native language, also write the summary in that language. Ensure both summaries are grammatically accurate.
2. Suggestions (Content Info)
Provide simple and actionable suggestions related to the discussed condition in English.
Examples:
For fever: "Drink plenty of water, rest well, and avoid heavy physical activities. Take prescribed fever-reducing medications."
For cold: "Avoid cold drinks and rest in a warm environment. Drink warm fluids to soothe your throat."
If both native language and English are used in the meeting, provide suggestions in both languages.
Keep the suggestions brief and clear (2-4 sentences). Do not use complex medical terminology.
3. Important Points
List the specific instructions given by the doctor that the patient must follow in English.

Only include what the doctor explicitly said. Do not add extra points or assumptions.
Example instructions:
"Take Paracetamol in the morning and at night."
"Rest for 2-3 days and drink plenty of fluids."
If both native language and English are spoken, provide the points in both languages.
Important Note: Avoid generic instructions like "Take care" or any information that the doctor did not specifically provide.

4. Medical Instructions and Follow-Up
Medications: List prescribed medications, including the name, dosage, and time to take. Even if mentioned in the summary, mention it here also in detail as prescribed by the doctor.
Scans/Tests and Admission Status:
If scans/tests or hospital admission are required, list them.
If none are required, say: "Not required."
Next Appointment:
If the doctor mentioned a follow-up appointment, provide the date and time.
If not mentioned, state: "Not mentioned."
If both native language and English are used, include this information in both languages.

Output Format:
Provide the final results in this JSON structure:

{
  "english": {
    "summary": "Brief summary of the meeting in English.",
    "suggestions": "Simple suggestions related to the condition in English.",
    "important_points": [
      "Instruction 1 in English",
      "Instruction 2 in English"
    ],
    "medical_instructions_and_follow_up": {
      "medicines": [
        {"name": "Medicine Name", "dosage": "Dosage and time to take"}
      ],
      "scans_tests_and_admission": "Details in English.",
      "next_appointment": "Details in English."
    }
  },
  "native_language": {
    "summary": "Brief summary of the meeting in the native language.",
    "suggestions": "Simple suggestions related to the condition in the native language.",
    "important_points": [
      "Instruction 1 in the native language",
      "Instruction 2 in the native language"
    ],
    "medical_instructions_and_follow_up": {
      "medicines": [
        {"name": "Medicine Name", "dosage": "Dosage and time to take"}
      ],
      "scans_tests_and_admission": "Details in native language.",
      "next_appointment": "Details in native language."
    }
  }
}

Critical Notes:

no content : if there is no content in meeting like patient not there or doctor not there or no talking takes place then return every json saying meeting did not happen 

Shared Content: If the doctor shows or plays any material (e.g., video, chart), note the content, provide a brief explanation in the summary, and include any links or names of the material in the Important Points if identifiable.

Dual Language Support: Ensure the output includes both English and the native language (if spoken) where applicable.

Grammatical Precision:Ensure both English and native language text are grammatically accurate and clear.

Explicit Details Only: Do not add generic advice or assumptions. Only include details explicitly communicated by the doctor.
Thoroughly analyze the meeting by matching the video, audio, captions, and messages to ensure every important detail is captured.

Short and Clear: Keep all content concise and to the point. Avoid unnecessary elaboration or repetition.

Dates and Times:Explicitly mention all dates and times. Convert vague terms such as “tomorrow,” “next week,” or “this month” into precise dates.

Speaker Details: If the doctor speaks, their name and title are noted where applicable (e.g., "Dr. John" or "Dr. Vijay").

Phone Numbers or Contact Details: If the doctor leaves a phone number, referral information, or any contact details in the messages or meeting, it will be included in the output under Important Points.

Meaningful Points:Only specific and actionable instructions from the doctor are included under Important Points. Exclude vague statements like "Take care" or "Stay safe".

No Assumptions: Only include details explicitly stated by the doctor. Do not add additional recommendations or advice.

Suggestions: Focus on meaningful, actionable instructions or recommendations. Do not include any vague or non-actionable advice.

"""
    
    
    # Choose a Gemini model.
    model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
    # Make the LLM request.
    print("Making LLM inference request...")
    import json
    response = model.generate_content(contents=[prompt,video_file,json.dumps(message_list, indent=4),str(participant_list),native_language],request_options={"timeout": 600})
    print(response.text)
    genai.delete_file(video_file.name)
    print(f'Deleted file {video_file.uri}')
    
    MeetLink = MeetLink
    formatted_date = formatted_date
    username =username
    email = email
    native_language = native_language
    
    from langchain_core.output_parsers import JsonOutputParser
    output_parser = JsonOutputParser()
    parsed_response = output_parser.parse(response.text)
    English_Summary = parsed_response['english']['summary']
    English_Suggestions = parsed_response['english']['suggestions']
    English_Important_Points = parsed_response['english']['important_points']
    English_Medicines = parsed_response['english']['medical_instructions_and_follow_up']["medicines"]
    English_Scans_Tests_And_Admission = parsed_response['english']['medical_instructions_and_follow_up']["scans_tests_and_admission"]
    English_Next_Appointment = parsed_response['english']['medical_instructions_and_follow_up']["next_appointment"]
    
    Native_Summary = parsed_response['native_language']['summary']
    Native_Suggestions = parsed_response['native_language']['suggestions']
    Native_Important_Points = parsed_response['native_language']['important_points']
    Native_Medicines = parsed_response['native_language']['medical_instructions_and_follow_up']["medicines"]
    Native_Scans_Tests_And_Admission = parsed_response['native_language']['medical_instructions_and_follow_up']["scans_tests_and_admission"]
    Native_Next_Appointment = parsed_response['native_language']['medical_instructions_and_follow_up']["next_appointment"]
    
    print("start mongo")
    
    try:
        myclient = pymongo.MongoClient("mongodb+srv://akshaaykg:PASSWORD10@meetbot.yugo9.mongodb.net/?tls=true")
        print('connected')
        db = myclient["PROJECT"]   #local db name
        collection = db['meetingdatacollection']
        dict = {'username':username, 'email' : email , 'formatted_date': formatted_date , 'MeetLink': MeetLink , 'native_language' : native_language , 'English_Summary':English_Summary, 'English_Suggestions':English_Suggestions , 'English_Important_Points':English_Important_Points , 'English_Medicines':English_Medicines, 'English_Scans_Tests_And_Admission':English_Scans_Tests_And_Admission, 'English_Next_Appointment':English_Next_Appointment, 'Native_Summary':Native_Summary, 'Native_Suggestions':Native_Suggestions , 'Native_Important_Points' :Native_Important_Points , 'Native_Medicines' :Native_Medicines, 'Native_Scans_Tests_And_Admission':Native_Scans_Tests_And_Admission , 'Native_Next_Appointment' : Native_Next_Appointment , 'message_list': message_list, 'participant_list': list(participant_list) , 'video_path' : video_path }
        res = collection.insert_one(dict) 
        inserted_id = res.inserted_id
    except Exception as e:
        print("An error occurred while inserting meeting data:", e)
    
    msg = EmailMessage()
    msg['Subject'] = f"Meeting Summary {formatted_date}"
    msg['From'] = 'akshaay.kg2021@vitbhopal.ac.in'
    msg['To'] = ', '.join([email])
    message = f"""
    Hello {username} ! 
    Heare is your meeting summary  
    
    Date : {formatted_date}
    Meet : {MeetLink}
    Language : {native_language}
    
    English_Summary : {English_Summary} 
    
    English_Suggestions : {English_Suggestions} 
    
    English_Important_Points : {English_Important_Points} 
    
    English_Medicines : {English_Medicines} 
    
    English_Scans_Tests_And_Admission : {English_Scans_Tests_And_Admission} 
    
    English_Next_Appointment : {English_Next_Appointment}
    
    Native_Summary : {Native_Summary} 
    
    Native_Suggestions : {Native_Suggestions}  
    
    Native_Important_Points : {Native_Important_Points} 
    
    Native_Medicines : {Native_Medicines}  
    
    Native_Scans_Tests_And_Admission : {Native_Scans_Tests_And_Admission}  
    
    Native_Next_Appointment : {Native_Next_Appointment}
    
    Thank You for choosing out BOT
    """
    msg.set_content(message)
    print(msg)
    try:
        print("working failed")
        server='smtp.gmail.com'
        from_email='akshaay.kg2021@vitbhopal.ac.in'
        # Connect using TLS
        server = smtplib.SMTP(server, 587)
        print("selected server")
        # server.connect()
        print("connected server")
        server.ehlo()
        server.starttls()  # Secure the connection with TLS
        # print("secured  ")
        server.set_debuglevel(1)
        server.login('akshaay.kg2021@vitbhopal.ac.in', 'jvuu kwss mneg aklz')  # Use actual password or app password
        print("loginnn")
        server.send_message(msg)
        print("msg send")
        server.quit()
        print("quittt")
        print('Successfully sent the mail.')
    
    except aiosmtplib.SMTPException as e:
        print(f"Error sending mail: {e}")
    
    except Exception as e:
        print(f" Error occured while processing mail {e}")
    return(inserted_id)



async def Meetbotprocess(user,username,email,BotEmail,BotPassword,MeetLink,output_filename,nativelanguage):
    user = user 
    username = username
    email = email
    BotEmail = BotEmail
    BotPassword = BotPassword
    MeetLink = MeetLink
    output_filename = output_filename
    nativelanguage = nativelanguage
    print("happening")
    
    result = await main(
                        email=BotEmail,
                        password=BotPassword,
                        meetlink=MeetLink,
                        output_filename=output_filename,
                        User_email = email
                    )
                
    message_list, participant_list , output_file = result
    print("Process done successfully!")
    print("in bot process")  
    print(message_list)
    print(participant_list)
    
    
    video_link = output_file  # need to cahnge this 
    
    current_datetime = datetime.datetime.now()
    # Format the date and time for the filename
    formatted_date = current_datetime.strftime("%Y-%m-%d_%H-%M")
    inserted_id = await geminicontentdata(message_list, participant_list, video_path = video_link , native_language = nativelanguage, MeetLink = MeetLink, formatted_date = formatted_date , username = username , email = email)
    

    print("finally gemini data over  ---------------- ------")
    print(inserted_id)
     
     