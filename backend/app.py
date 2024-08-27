import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
from langchain_openai import AzureChatOpenAI
from langchain_openai import ChatOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import requests
import numpy as np
from datetime import datetime
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
import io
from openai import AzureOpenAI
from flask_mail import Mail, Message
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

load_dotenv()

key = os.getenv("KEY")
endpoint = os.getenv("ENDPOINT")
index_name = os.getenv("INDEX_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

credential = AzureKeyCredential(key)
client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

# llm = AzureChatOpenAI(
#     azure_deployment="bob-services-bot",
#     api_version="2024-05-01-preview",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
# )

llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=2000,
    timeout=None,
    max_retries=2,
)


class Config:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_ID')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(account_sid, auth_token)

app = Flask(__name__)
cors = CORS(app)
app.config.from_object(Config())

mail = Mail(app)


cred = credentials.Certificate("./firebase-credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()



@app.route("/")
def hello_world():
    return "Hello World"

def send_personalized_email(mail,content,subject):
    try:
        msg = Message(
            subject,
            sender=(os.getenv('MAIL_SENDER'), os.getenv('SENDER_MAIL_ID')),
            recipients=[os.getenv("RECEIVER_EMAIL")]
        )
        msg.html = content
        mail.send(msg)
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')



def get_region_type(pincode):
    prompt = f"""
    You are an area type classifier. Basically your task is to tell whether an area is rural or urban given the pincode of Indian cities. Note that the response should be returned in a json format where the key is the type and value is either 'rural' or 'urban' The pincode is - {pincode}
    """

    # Call LLM model to generate response
    response = llm.invoke(
        [
            (
                "system",
                "You are a helpful assistant that provides information based on the given context.",
            ),
            ("user", prompt),
        ]
    )
    response = response.content
    response = response.replace("```json", "").replace("```", "")

    # print(json.loads(response))

    return json.loads(response)["type"]


def calculate_age(dob_str):
    # Parse the date of birth string
    dob = datetime.strptime(dob_str, "%Y/%m/%d")

    # Get the current date
    today = datetime.today()

    # Calculate age
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    return age


def get_income_category(income):
    # Placeholder function to categorize income. Replace with actual logic.
    income_dict = {
        "QU3cJbpnsBk0JpGsb5YI": "high_income",
        "5KzGOBTlXjziM61yWVRL": "high_income",
        "G71gi1gH09En0CBgkvrT": "mid_income",
        "pp4urj0EbgEgiuN1yN2T": "mid_income",
        "0pK2AMV2lOuRBSpd9EhX": "low_income",
        "PlsbOfRdSB2aZgABnl6x": "low_income",
    }
    return income_dict.get(income, "unknown_income")


def determine_segment(user):
    age = calculate_age(user['dob'])
    income_category = get_income_category(user['income'])
    profession = user['profession']
    pincode = user['pincode']
    region_type = get_region_type(pincode)

    print(region_type)
    
    # Define segment rules
    if age < 30:
        if income_category == 'high_income':
            return 'young_high_income_professional'
        elif income_category == 'mid_income':
            return 'young_mid_income_professional'
        else:
            return 'young_professional'
    elif 30 <= age < 50:
        if income_category == 'high_income':
            return 'mid_career_high_income_professional'
        elif income_category == 'mid_income':
            return 'mid_career_mid_income_professional'
        else:
            return 'mid_career_professional'
    else:
        if income_category == 'high_income':
            return 'senior_high_income_professional'
        elif income_category == 'mid_income':
            return 'senior_mid_income_professional'
        else:
            return 'senior_professional'
    

    return 'other_segment'


def customer_segmentation():
    users = db.collection("user").stream()
    for i in users:
        user = i.to_dict()


def calculate_retirement_savings(
    credit_spend_apr,
    debit_spend_apr,
    credit_spend_may,
    debit_spend_may,
    credit_spend_jun,
    debit_spend_jun,
    emi_active,
    credit_amount_apr,
    credit_amount_may,
    credit_amount_jun,
    retirement_age,
    current_age,
    life_expectancy,
    desired_expenses_percentage=0.80,
    inflation_rate=0.03,
    return_rate=0.04,
):

    # Calculate monthly expenses
    monthly_expenses_apr = credit_spend_apr + debit_spend_apr + emi_active
    monthly_expenses_may = credit_spend_may + debit_spend_may + emi_active
    monthly_expenses_jun = credit_spend_jun + debit_spend_jun + emi_active

    average_monthly_expenses = np.mean(
        [monthly_expenses_apr, monthly_expenses_may, monthly_expenses_jun]
    )

    # Calculate average monthly income
    average_monthly_income = np.mean(
        [credit_amount_apr, credit_amount_may, credit_amount_jun]
    )

    # Retirement parameters
    years_to_retirement = retirement_age - current_age
    years_of_retirement = life_expectancy - retirement_age

    # Desired retirement lifestyle (e.g., 80% of current expenses)
    desired_retirement_expenses = average_monthly_expenses * desired_expenses_percentage

    # Annual expenses
    annual_retirement_expenses = desired_retirement_expenses * 12

    # Adjust annual expenses for inflation
    adjusted_annual_expenses = annual_retirement_expenses * (
        (1 + inflation_rate) ** years_to_retirement
    )

    # Calculate total retirement savings needed using Present Value formula
    def calculate_present_value(future_value, rate, periods):
        return future_value / ((1 + rate) ** periods)

    total_retirement_savings_needed = 0
    for i in range(years_of_retirement):
        annual_expense = adjusted_annual_expenses * ((1 + inflation_rate) ** i)
        total_retirement_savings_needed += calculate_present_value(
            annual_expense, return_rate, i + 1
        )

    return total_retirement_savings_needed


def get_push_notification_content(user_id, title, message):
    message = message.replace('"', "")
    response = requests.post(
        "https://app.nativenotify.com/api/indie/notification",
        json={
            "subID": user_id,
            "appId": 22691,
            "appToken": "GNcqpcDMoJaUg3CZA7HF9Q",
            "title": title,
            "message": message,
        },
    )
    return response.status_code


def generate_personalized_push_notification(user_schema, transaction_details):
    # Create the context for the prompt
    context = f"""
    You are a marketing assistant for a bank. Generate a personalized 1 line push notification related to transaction (make it catchy, quirky) content and a corresponding title (also should be eye catching and funny but smaller than the message content) for the user based on the given user schema and transaction details. The content should market the best bank cards service that the user can use to benefit from the transaction they have done. Make sure you only market the bank card service related to the transaction. Add some cool icons also to make it look attractive.

    User Schema:
    - Date of Birth: {user_schema['dob']}
    - First Name: {user_schema['first_name']}
    - Last Name: {user_schema['last_name']} 
    - Gender: {user_schema['gender']}
    - Income Bracket: {user_schema['income']}
    - Marital Status: {user_schema['marital_status']}
    - Pincode (India): {user_schema['pincode']}
    - Profession: {user_schema['profession']}
    - Dependents: Children - {user_schema['dependents']['children']}, Others - {user_schema['dependents']['others']}, Parents - {user_schema['dependents']['parents']}, Spouse - {user_schema['dependents']['spouse']}

    Transaction Details:
    - Category: {transaction_details['product_category']}
    - Remark: {transaction_details['remarks']} 
    - Price: {transaction_details['price']}
    """

    # Perform a search query to get relevant bank services
    search_results = client.search(search_text=transaction_details["remarks"], top=1)

    # Collect relevant bank services information
    services_info = ""
    for result in search_results:
        services_info += f"- Service Name: {result['source']}\n"
        services_info += f"  Description: {result['data']}\n\n"

    # print("these services - ", services_info)

    # Append the chunk and the question into prompt
    qna_prompt_template = f"""
    {context}

    Based on the user's profile and transaction, here are the relevant bank services that might be beneficial:
    {services_info}

    Note - Return the output in a json format consisting of key as 'title' and 'message' and the value being the string content in them.

    Content - 
    """

    # Call LLM model to generate response
    response = llm.invoke(
        [
            (
                "system",
                "You are a helpful assistant that provides information based on the given context.",
            ),
            ("user", qna_prompt_template),
        ]
    )
    response = response.content
    response = response.replace("```json", "").replace("```", "")

    # print(json.loads(response))

    return json.loads(response)


@app.route("/api/risk-appetite-and-suggestions", methods=["POST"])
def risk_appetite_and_suggestions():
    try:
        data = request.json
        user_id = data.get("user_id")
        user_ref = db.collection("user")

        curr_user = user_ref.document(user_id).get().to_dict()
        curr_age = calculate_age(curr_user["dob"])

        activity_ref = db.collection("customer_activity")
        activity_doc = activity_ref.where("ID", "==", user_id).get()
        final_activity = activity_doc[0].to_dict()

        user_data = {
            "credit_spend_apr": final_activity.get("cc_cons_apr", 0),
            "debit_spend_apr": final_activity.get("dc_cons_apr", 0),
            "credit_spend_may": final_activity.get("cc_cons_may", 0),
            "debit_spend_may": final_activity.get("dc_cons_may", 0),
            "credit_spend_jun": final_activity.get("cc_cons_jun", 0),
            "debit_spend_jun": final_activity.get("dc_cons_jun", 0),
            "emi_active": final_activity.get("emi_active", 0),
            "credit_amount_apr": final_activity.get("credit_amount_apr", 0),
            "credit_amount_may": final_activity.get("credit_amount_may", 0),
            "credit_amount_jun": final_activity.get("credit_amount_jun", 0),
            "retirement_age": 60,
            "current_age": curr_age,
            "life_expectancy": 80,
            "imgUrl": data.get("imgUrl", ""),
        }

        # Calculate retirement savings needed
        total_retirement_savings_needed = calculate_retirement_savings(
            user_data["credit_spend_apr"],
            user_data["debit_spend_apr"],
            user_data["credit_spend_may"],
            user_data["debit_spend_may"],
            user_data["credit_spend_jun"],
            user_data["debit_spend_jun"],
            user_data["emi_active"],
            user_data["credit_amount_apr"],
            user_data["credit_amount_may"],
            user_data["credit_amount_jun"],
            user_data["retirement_age"],
            user_data["current_age"],
            user_data["life_expectancy"],
        )

        # Prepare context for the prompt
        context = f"""
        You are a marketing assistant for a bank. Generate a personalized email marketing content for the user based on the given user data. The content should suggest bank-specific investment opportunities, services to optimize credit card usage, rewards, and benefits, and provide a customized retirement plan. Demographics of the user is -
        {curr_user}
        Be sure to include the user's name in the mail content to make it sound more personalised.

        User Data:
        - Credit card spend in April: {user_data['credit_spend_apr']}
        - Debit card spend in April: {user_data['debit_spend_apr']}
        - Credit card spend in May: {user_data['credit_spend_may']}
        - Debit card spend in May: {user_data['debit_spend_may']}
        - Credit card spend in June: {user_data['credit_spend_jun']}
        - Debit card spend in June: {user_data['debit_spend_jun']}
        - EMI active: {user_data['emi_active']}
        - Credit amount in April: {user_data['credit_amount_apr']}
        - Credit amount in May: {user_data['credit_amount_may']}
        - Credit amount in June: {user_data['credit_amount_jun']}
        - Retirement age: {user_data['retirement_age']}
        - Current age: {user_data['current_age']}
        - Life expectancy: {user_data['life_expectancy']}
        - Image URL: {user_data['imgUrl']}
        - Total retirement savings needed: {total_retirement_savings_needed}
        """
        # print(context)

        # Perform a search query to get relevant bank services
        search_results = client.search(search_text="investment opportunities", top=5)

        # Collect relevant bank services information
        services_info = ""
        for result in search_results:
            services_info += f"- Service Name: {result['source']}\n"
            services_info += f"  Description: {result['data']}\n\n"

        # Append the chunk and the question into prompt
        qna_prompt_template = f"""
        {context}

        Based on the user's data, here are the relevant bank services that might be beneficial:
        {services_info}

        Email Content:
        Please provide the content in the following JSON format:
        {{
            "subject": "subject of the mail",
            "html_content": "html template of the mail content, use orange colour background as header with 'Bank of Baroda retirement plans', include the image URL provided by the user below the header and content after that, add required headers and footers, and after best regards, add 'Bank Of Baroda, Website: https://www.bankofbaroda.in/'."
        }}
        """
        print("worked")

        # Call LLM model to generate response
        response = llm.invoke(
            [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides personalized email marketing content based on the given context.",
                },
                {"role": "user", "content": qna_prompt_template},
            ]
        )

        response = response.content.replace("```json", "").replace("```", "")

        email_content = json.loads(response)

        with app.app_context():
            send_personalized_email(mail,email_content["html_content"],email_content["subject"])

        return jsonify({"message":"Email sent successfully!"}), 200

    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


@app.route("/api/triggertransaction", methods=["POST"])
def trigger_transaction():
    print("In trigger api")
    try:
        transaction_ref = db.collection("transaction")
        user_ref = db.collection("user")
        income_ref = db.collection("income_brackets")
        profession_ref = db.collection("profession")
        transactions = request.json
        # for transaction in transactions:
        #     transaction = transaction_ref.add(transaction)
        #     transaction = transaction[1].get().to_dict()
        final_transaction = transactions[0]
        user = user_ref.document(
            final_transaction["user_id"],
        )
        user_doc = user.get()

        if not user_doc.exists:
            return {"res": "not found"}, 404
        else:
            user_dict = user_doc.to_dict()
            income_doc = income_ref.document(user_dict["income"]).get()
            # print(income_doc.to_dict())
            profession = user_dict["profession"].get()
            # print(profession.to_dict())
            del user_dict["income"]
            del user_dict["profession"]
            user_dict["income"] = income_doc.to_dict()
            user_dict["profession"] = profession.to_dict()

            message = generate_personalized_push_notification(
                user_dict, final_transaction
            )

            # response = get_push_notification_content(
            #     final_transaction["user_id"], "", message
            # )
            response = get_push_notification_content(
                "fS7xbvDjrsbVfiUmNjU5o9UOTrm1", message["title"], message["message"]
            )

            return {"data": response}, 200
    except Exception as e:
        print(str(e))
        return {"error\n\n\n\n": str(e)}, 500


@app.route("/api/store-customer-activity", methods=["POST"])
def store_customer_activity():
    try:
        activity_ref = db.collection("customer_activity")
        activities = request.json
        for activity in activities:
            activity = activity_ref.add(activity)
            activity = activity[1].get().to_dict()

        return {"data": "Success"}, 200
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500

@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    try:
        user_question = request.json.get("question", "")
        if not user_question:
            return {"error": "Question is required"}, 400

        # Fetch the appropriate chunk from the database
        context = """"""
        results = client.search(search_text=user_question, top=3)

        for doc in results:
            context += "\n" + doc['data']
        print("con" + context)

        # Append the chunk and the question into prompt
        qna_prompt_template = f"""You will be provided with the question and a related context, you need to answer the question using the context.
            Context:
            {context}

            Question:
            {user_question}

            Make sure to answer the question only using the context provided, if the context doesn't contain the answer then return "I don't have enough information to answer the question".

            Answer:"""

        # Call LLM model to generate response
        response = llm.invoke([
            {"role": "system", "content": "You are a helpful assistant that provides information based on the given context."},
            {"role": "user", "content": qna_prompt_template}
        ])

        return {"answer": response.content}, 200

    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


@app.route("/api/send-call", methods=["POST"])
def send_call():
    try:
        data = request.json
        user_id = data.get("user_id")
        user_ref = db.collection("user")

        curr_user = user_ref.document(user_id).get().to_dict()
        base_prompt = "Get all the bank of baroda services and products that are made especially for the farmers of India. Make sure to includ the exact services with their proper names and schemes." if curr_user["profession"] == "farmer" else "Get all the bank of baroda services and products that are made especially for the defence personnels (both for retired or not) of India. Make sure to includ the exact services with their proper names and schemes."
        # Fetch the appropriate chunk from the database
        context = """"""
        results = client.search(search_text=base_prompt, top=3)

        for doc in results:
            context += "\n" + doc['data']
        print("con" + context)

        # Append the chunk and the question into prompt
        qna_prompt_template = f"""
            You are a marketing assistant for a bank. Generate a personalized 4 to 5 lines content for the user based on the given user data. The content should suggest bank-specific plans, products and services. Demographics of the user is -
            {curr_user}
            Be sure to include the user's name in the call content to make it sound more personalised. Generate the content in hindi language only. Make sure to include the Bank of Baroda mention in the content to let the user know that the call is from bank of baroda.

            Make sure to answer the question only using the context provided, if the context doesn't contain the answer then return "I don't have enough information to answer the question".

            Answer:"""

        # Call LLM model to generate response
        response = llm.invoke([
            {"role": "system", "content": "You are a helpful assistant that provides information based on the given context."},
            {"role": "user", "content": qna_prompt_template}
        ])

        # print(response.content)

        vresp = VoiceResponse()
        vresp.say(response.content, language="hi-IN", voice="Polly.Aditi")

        call = twilio_client.calls.create(
            from_=os.getenv("TWILIO_NUMBER"),
            to=os.getenv("RECEIVER_NUMBER"),
            twiml=str(vresp)
        )

        return {"message": call.sid}, 200

    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500
    

@app.route('/api/add-watermark', methods=['POST'])
def add_watermark():
    # Check if the request contains an image
    if 'image' not in request.files:
        return {"error": "No image file provided"}, 400
    
    # Get the image from the request
    image_file = request.files['image']
    image = Image.open(image_file).convert("RGBA")  # Ensure the image is in RGBA mode
    
    # Create watermark text with current year
    current_year = datetime.now().year
    watermark_text = f"© Bank of Baroda {current_year}"
    draw = ImageDraw.Draw(image)
    
    # Load a larger TrueType font
    font = ImageFont.truetype("arial.ttf", 36)  # Use a larger font size (36)
    
    # Calculate the position for the watermark (top right corner)
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    width, height = image.size
    x = width - text_width - 10  # Margin from the right edge
    y = 10  # Margin from the top edge
    
    # Create a transparent layer for the watermark
    watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
    watermark_draw = ImageDraw.Draw(watermark_layer)
    
    # Add the watermark text to the transparent layer with reduced transparency
    watermark_draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255))  # Light grey color with 20% transparency
    
    # Add logo image to the bottom left corner
    if 'logo' in request.files:
        logo_file = request.files['logo']
        logo = Image.open(logo_file).convert("RGBA")
        
        # Resize logo if necessary
        logo_width, logo_height = logo.size
        max_logo_size = min(width // 10, height // 10)  # Restrict logo to 20% of image dimensions
        if logo_width > max_logo_size or logo_height > max_logo_size:
            logo.thumbnail((max_logo_size, max_logo_size), Image.LANCZOS)
        
        # Position the logo
        logo_x = 10  # Margin from the left edge
        logo_y = height - logo.height - 10  # Margin from the bottom edge
        
        # Paste the logo onto the transparent layer
        watermark_layer.paste(logo, (logo_x, logo_y), logo)
    
    # Composite the watermark and logo onto the original image
    watermarked_image = Image.alpha_composite(image, watermark_layer)
    
    # Convert the image back to RGB mode before saving
    watermarked_image = watermarked_image.convert("RGB")
    
    # Add metadata to the image
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("Title", "Bank of Baroda Watermarked Image")
    metadata.add_text("Copyright", "Bank of Baroda | Copyright Reserved")
    metadata.add_text("Creation Date", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Save the image to a BytesIO object with metadata
    img_io = io.BytesIO()
    watermarked_image.save(img_io, format='PNG', pnginfo=metadata)
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')


@app.route("/api/generate-image", methods=["POST"])
def generate_image(user_id):
    data = request.json

    user_id = data.get("user_id")
    user_ref = db.collection("user")
    curr_user = user_ref.document(user_id).get().to_dict()
    curr_age = calculate_age(curr_user["dob"])

    prompt=""
    size = data.get("size", "1024x1024")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    client = AzureOpenAI(
        api_version="2024-05-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

    result = client.images.generate(
        model="Dalle3",
        prompt="<the user's prompt>",
        n=1
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "prompt": prompt,
        "size": size,
        "n": 1
    }

    response = requests.post(f"{AZURE_OPENAI_ENDPOINT}/v1/images/generations", json=payload, headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to generate image", "details": response.json()}), response.status_code

    image_data = response.json()
    return jsonify(image_data)

    
if __name__ == "__main__":
    app.run(debug=True)
