# CRM Banking Assistant (TikTokCodeJam 2024)

## Overview
CRM Banking Assistant is a Customer Relationship Management (CRM) tool designed specifically for the banking sector. This AI-powered assistant helps customers manage their bank accounts, report issues, request new cards, update information, and perform other banking tasks through voice interactions. Built using Flask, Flask-SocketIO, and various AI tools, the assistant ensures seamless and efficient customer support.

## Features
- **Authentication**: Secure customer authentication using account number, name, date of birth, and security questions.
- **Check Balance**: Retrieve and report the current balance in the user's account.
- **Update Information**: Allow users to update their personal information such as address and email.
- **Block Card**: Enable users to block lost or stolen cards.
- **Request New Card**: Facilitate issuing new debit or credit cards.
- **Flag Transactions**: Report and flag fraudulent or suspicious transactions.
- **General Bank Info**: Provide information about bank services and products.
- **AI Conversations**: Engage in general chit-chat and provide human-like responses using AI.

## Technologies Used
- **Backend**: Flask, Flask-SocketIO
- **AI/ML**: OpenAI GPT-4, Whisper for speech-to-text and text-to-speech
- **Database**: MySQL
- **Audio Processing**: Pydub
- **Routing**: Custom semantic routing layers

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/crm-banking-assistant.git
   cd crm-banking-assistant
   ```
2. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements2.txt
   cd client
   npm install --legacy-peer-deps
   ```
3. **Set up environment variables**
```
    DB_HOST=your_db_host
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_DATABASE=your_db_name
    OPENAI_API_KEY=your_openai_api_key
    PINECONE_KEY=your_pinecone_key
```

4. **Run the application**
   ```bash
   python app.py
   npm start
   ```

5. **Project Structure**
    ```
    crm-banking-assistant/
    ├── client/
    │   ├── public/
    │   ├── src/
    │   │   ├── components/
    │   │   │   ├── AudioRecorder.js
    │   │   ├── App.js
    │   │   ├── index.js
    │   ├── package.json
    ├── static/
    ├── templates/
    ├── app.py
    ├── audio_data.py
    ├── auth_manager.py
    ├── ai_service.py
    ├── db_connection.py
    ├── requirements.txt
    |── routing/
    |   ├── __init__.py
    |   ├── card_routing_layer.py
    |   ├── change_info_routing_layer.py
    |   ├── map_to_task.py
    |   ├── taskrouting_layer.py
        |── transaction_dispute_layer.py
        |── yes_routing_layer.py
        |── routing_layer.py
    ├── tasks/
    |   ├── __init__.py
    |   ├── block_card.py
    |   ├── check_balance.py
    |   ├── flag_transaction.py
    |   ├── handle_bank_info.py
    |   ├── request_new_card.py
    |   ├── change_information.py
    ├── requirements2.txt
    ├── .gitignore
    ├── utils.py
    |── user_data.py
    |── value_extractor.py
    ├── README.md
    ```

## Contributors
<table>
	<tbody>
		<tr>
         <td align="center">
             <a href="https://github.com/PranavN1234">
                 <img src="https://avatars.githubusercontent.com/u/44135759?v=4" width="100;" alt="Pranav"/>
                 <br />
                 <sub >Pranav Iyer</sub>
             </a>
         </td>
         <td align="center">
             <a href="https://github.com/Purvav0511">
                 <img src="https://avatars.githubusercontent.com/u/50676996?v=4" width="100;" alt="Purvav"/>
                 <br />
                 <sub>Purvav Punyani</sub>
             </a>
         </td>
		</tr>
	<tbody>
</table>