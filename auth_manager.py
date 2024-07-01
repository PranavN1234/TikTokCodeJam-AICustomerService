from utils import calculate_similarity, transcribe_audio, synthesize_audio, play_audio, record_audio
from value_extractor import get_value
from datetime import datetime
from user_data import UserData

class Authmanager:
    _instance = None
    
    def __new__(cls, connection=None, auth_steps=None):
        if cls._instance is None:
            cls._instance = super(Authmanager, cls).__new__(cls)
            cls._instance.connection = connection
            cls._instance.user_data = UserData()
            cls._instance.auth_steps = auth_steps  # Set auth_steps here
        return cls._instance
    
    def are_strings_similar(self, string1, string2, threshold=0.8):
        return calculate_similarity(string1, string2) >= threshold

    def get_auth_steps(self):
        return self.auth_steps  # Return the auth_steps

    def handle_auth_step_response(self, response_text, step):
        value = get_value(response_text, step["variable"], step["semantic_description"])
        print(f"Extracted value: {value.value}")
        return value.value

    def set_security_question_prompt(self):
        security_question = self.user_data.get_data("security_question")
        if security_question:
            for step in self.auth_steps:
                if step["variable"] == "security_answer":
                    step["prompt"] = f"What is the answer to your security question: {security_question}?"

    def authenticate_account_number(self, account_number):
        print(f"Authenticating account number: {account_number}")
        cursor = self.connection.cursor(dictionary=True)
        query = "SELECT * FROM pba_account WHERE acct_no = %s"
        cursor.execute(query, (account_number,))
        account = cursor.fetchone()
        if account:
            self.user_data.set_data("account_number", account_number)
            self.user_data.set_data("customer_id", account["customerid"])
            self.fetch_security_question()
            self.set_security_question_prompt()  # Ensure the prompt is set here
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
        print(f"Authenticating name: {name}")
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
        print(f"Authenticating date of birth: {dob}")
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
        print(f"Authenticating security answer: {security_answer}")
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
