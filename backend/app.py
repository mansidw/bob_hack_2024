import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import firebase
import uuid
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


app = Flask(__name__)
cors = CORS(app)

cred = credentials.Certificate("./firebase-credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route("/")
def hello_world():
    return "Hello World"

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

    return json.loads(response)


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
    
    if pincode == 530068:
        return 'local_resident'

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
    You are a marketing assistant for a bank. Generate a personalized 1 line push notification (make it catchy, quirky) content and a corresponding title (also should be eye catching and funny but smaller than the message content) for the user based on the given user schema and transaction details. The content should market the best bank cards service that the user can use to benefit from the transaction they have done. Add some cool icons also to make it look attractive.

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
        You are a marketing assistant for a bank. Generate a personalized email marketing content for the user based on the given user data. The content should suggest bank-specific investment opportunities, services to optimize credit card usage, rewards, and benefits, and provide a customized retirement plan.

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
        print("worked")

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
            "html_content": "html template of the mail content, use orange colour background as header with 'Bank of Baroda retirement plans', include the image URL provided by the user, add required headers and footers, and after best regards, add 'Bank Of Baroda, Website: https://www.bankofbaroda.in/'"
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

        return jsonify(email_content), 200

    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


@app.route("/api/trigger-transaction", methods=["POST"])
def trigger_transaction():
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
        return {"error": str(e)}, 500


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


if __name__ == "__main__":
    app.run(debug=True)
