# Emergency Services Chatbot

This project is an Emergency Services Chatbot built using OpenAI's GPT model, Gradio for the interface, and a Pinecone vector database for emergency action retrieval. The chatbot assists users by guiding them through emergency situations, storing user messages, and fetching location-based assistance details. The chatbot also includes a feature to artificially delay the response from the database to simulate real-world response times.

## Features

- **Emergency Action Retrieval**: The chatbot can fetch immediate next steps for a given emergency based on the information stored in the vector database.
- **Message Storage**: Users can send messages to Dr. Adrin, which are stored in a MongoDB database.
- **Location Assistance**: The chatbot can fetch the user's location and provide an estimated time of arrival for assistance.
- **Asynchronous Processing**: The chatbot includes an artificial 15-second delay when fetching emergency actions to simulate real-world response times, while still keeping the user engaged with interim questions.

## Project Structure

```plaintext
project_name/
│
├── .env
├── main.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── config.py
│   └── constants.py
│
├── models/
│   ├── __init__.py
│   ├── ai_model.py
│   ├── emergency.py
│   ├── tools.py
│   └── utils.py
│
├── services/
│   ├── __init__.py
│   ├── database.py
│   ├── pinecone_service.py
│   └── message_service.py
│
└── interfaces/
    ├── __init__.py
    ├── gradio_interface.py
    └── chat_interface.py
```

## Requirements

The following Python packages are required to run this project:

- `gradio`: For building the web interface.
- `python-dotenv`: For loading environment variables from a `.env` file.
- `openai`: For interacting with OpenAI's GPT models.
- `langchain`: Provides support for managing chains of calls to language models.
- `pinecone-client`: For interacting with the Pinecone vector database.
- `pymongo`: For interacting with MongoDB databases.

## Installation

Follow these steps to set up and run the project:

1. **Clone the repository**:

   First, clone the repository to your local machine using the following command:

   ```bash
   git clone https://github.com/your-username/emergency-services-chatbot.git
   cd emergency-services-chatbot
   ```

2. **Create a virtual environment** (optional but recommended):

   It's good practice to use a virtual environment to manage your dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```
3. **Install dependencies**:

   Install the required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```
    This step guides users to install all necessary dependencies listed in the `requirements.txt` file. You can include this in your `README.md` under the installation section.
4. **Set up environment variables**:

   Create a `.env` file in the root directory of your project and add the following:

   ```env
   OPEN_AI_KEY=your_openai_api_key
   PINECONE_DB=your_pinecone_key
   MONGO_DB_URI=your_mongo_uri
    ```
    This step explains how to configure the necessary environment variables to connect to the OpenAI API, Pinecone database, and MongoDB.
5. **Set up Pinecone Database**:

   Ensure that your Pinecone index is set up and ready for use. The index should store vectorized representations of emergency actions.

   To set up Pinecone:

   - Sign up for an account at [Pinecone](https://www.pinecone.io/).
   - Create an index in your Pinecone account. You can do this through the Pinecone dashboard or via the Pinecone client in Python.
   - Ensure that the name of the index matches the one used in your code (`"emergency-db"` in this case).
   - Refer to the [Pinecone documentation](https://docs.pinecone.io/docs/quickstart) for more detailed instructions on setting up and managing your Pinecone index.
5. **Set up Pinecone Database**:

   Ensure that your Pinecone index is set up and ready for use. The index should store vectorized representations of emergency actions.

   To set up Pinecone:

   - Sign up for an account at [Pinecone](https://www.pinecone.io/).
   - Create an index in your Pinecone account. You can do this through the Pinecone dashboard or via the Pinecone client in Python.
   - Ensure that the name of the index matches the one used in your code (`"emergency-db"` in this case).
   - Refer to the [Pinecone documentation](https://docs.pinecone.io/docs/quickstart) for more detailed instructions on setting up and managing your Pinecone index.
7. **Run the application**:

   Once you have set up the environment and dependencies, you can start the chatbot application by running:

   ```bash
   python main.py
    ```
    This command will launch the Gradio interface where you can interact with the chatbot.
	- Open the URL provided by Gradio in your web browser to start using the chatbot.
	- Interact with the chatbot by typing in messages, reporting emergencies, or asking for assistance.

The application will handle user inputs, provide emergency instructions, and store messages in the MongoDB database.
This step explains how to run the application and start the Gradio interface, allowing users to interact with the chatbot.