from utils import record_audio, transcribe_audio, synthesize_audio, play_audio, calculate_similarity
from value_extractor import get_value
from db_connection import db_connection, close_db_connection
from datetime import datetime
from user_data import UserData

class Authmanager:
    _instance = None
    
    def __new__ (cls, connection=None):
        if cls._instance is None:
            cls._instance = super(Authmanager, cls).__new__(cls)
            cls._instance.connection = connection
            cls._instance.user_data = UserData()
        return cls._instance     
    
    def are_strings_similar(self, string1, string2, threshold=0.8):
        return calculate_similarity(string1, string2) >= threshold
    
    
    def prompt_and_listen(self, prompt_text, variable, semantic_description):
        synthesize_audio(prompt_text)
        play_audio('output.mp3')
        record_audio('response.wav')
        response_text = transcribe_audio('response.wav')
        value = get_value(response_text, variable, semantic_description)
        print(f"Extracted value: {value.value}")
        return value.value
    
    def authenticate_user(self):
        auth_steps = [
            {
                "prompt": "Please can you tell me your account number.",
                "variable": "account_number",
                "semantic_description": "Extract only account number as integer no spaces or special characters.",
                "auth_function": self.authenticate_account_number
            },
            {
                "prompt": "Please state your first and last name.",
                "variable": "name",
                "semantic_description": "Extract the name from the user query in english just the name no special formatting needed.",
                "auth_function": self.authenticate_name
            },
            {
                "prompt": "Please say your date of birth",
                "variable": "dob",
                "semantic_description": "Extract the date of birth from the user response in YYYY-MM-DD.",
                "auth_function": self.authenticate_dob
            },
            {
                "prompt": "",  # This will be dynamically set based on the security question
                "variable": "security_answer",
                "semantic_description": "Extract just the security answer from the user response, so for example the response is I want to be an artist, just take artist as the answer ",
                "auth_function": self.authenticate_security_answer
            }
        ]

        for step in auth_steps:
            attempts = 3
            while attempts > 0:
                # Dynamically set the prompt for the security question
                if step["variable"] == "security_answer" and self.user_data.get_data("security_question"):
                    step["prompt"] = f"What is the answer to your security question: {self.user_data.get_data('security_question')}?"
                    
                response_value = self.prompt_and_listen(step["prompt"], step["variable"], step["semantic_description"])
                if step["auth_function"](response_value):
                    break
                else:
                    attempts -= 1
                    synthesize_audio(f"Authentication failed for {step['variable'].replace('_', ' ')}. You have {attempts} attempts left.")
                    play_audio('output.mp3')
                    if attempts == 0:
                        synthesize_audio("Authentication failed. Please try again later. GoodBye.")
                        play_audio('output.mp3')
                        return False

        return self.is_authenticated()
    
    def authenticate_account_number(self, account_number):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM pba_account WHERE acct_no = %s"
        cursor.execute(query, (account_number,))
        account = cursor.fetchone()
        # Replace with actual DB lookup
        if account:
            self.user_data.set_data("account_number", account_number)
            self.user_data.set_data("customer_id", account["customerid"])
            self.fetch_security_question()
            return True
        return False

    def fetch_security_question(self):
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT security_question, security_answer FROM pba_customer WHERE customerid = %s"
        cursor.execute(query, (self.user_data.get_data("customer_id"),))
        customer = cursor.fetchone()
        if customer:
            self.user_data.set_data("security_question", customer["security_question"])
            self.user_data.set_data("expected_security_answer", customer["security_answer"])
            
    def authenticate_name(self, name):
        if not self.user_data.get_data("customer_id"):
            return False
        
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT cfname, clname FROM pba_customer WHERE customerid = %s"
        cursor.execute(query, (self.user_data.get_data("customer_id"),))
        customer = cursor.fetchone()
        if not customer:
            return False
        
        mapped_name = f"{customer['cfname']} {customer['clname']}"
        if self.are_strings_similar(name, mapped_name):
            self.user_data.set_data("name", mapped_name)
            return True
        
        return False


    def authenticate_dob(self, dob):
        if not self.user_data.get_data("customer_id"):
            return False
        
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT date_of_birth FROM pba_customer WHERE customerid = %s"
        cursor.execute(query, (self.user_data.get_data("customer_id"),))
        customer = cursor.fetchone()
        
        if customer:
            dob_database = customer["date_of_birth"]
            print(f'DOB from database: {dob_database}')
            
            try:
                dob_input = datetime.strptime(dob, '%Y-%m-%d').date()
                if dob_input == dob_database:
                    self.user_data.set_data("dob", dob)
                    return True
            except ValueError:
                print("Invalid date format provided.")
        
        return False
    
    def authenticate_security_answer(self, security_answer):
        
        if not self.user_data.get_data("customer_id"):
            return False
        
        if self.are_strings_similar(security_answer, self.user_data.get_data("expected_security_answer"), 0.5):
            self.user_data.set_data("security_answer", security_answer)
            return True
        
        return False
        
       

    def is_authenticated(self):
        required_keys = ["account_number", "name", "dob", "security_answer"]
        return all(key in self.user_data.all_data() for key in required_keys)

    def clear_session(self):
        self.user_data.clear_data()
        
    def get_user_data(self):
        return self.user_data.all_data()
