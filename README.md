# Pokémon Smile - Brushing App with Pokédex

![Pokémon Smile Logo](static/favicon.png)

A web application inspired by the Pokémon Smile mobile app, designed to make brushing teeth fun by allowing users to catch Pokémon while they brush. This project includes a brushing timer, Pokédex to track caught Pokémon, and user profiles.

## Features

- **Interactive Brushing Timer**: A 2-minute timer with animations to guide brushing
- **Pokémon Catching**: Catch random Pokémon when you complete brushing sessions
- **Comprehensive Pokédex**: View all your caught Pokémon with details and cries
- **User Profiles**: Create and manage profiles to track your Pokémon collection
- **Buddy Pokémon**: Select a favorite Pokémon to be your brushing buddy
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Background Music**: Toggle-able music for a more immersive experience

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Flask
- **Database**: MongoDB
- **APIs**: PokeAPI for Pokémon data
- **Audio**: Pokémon cries from Pokémon Showdown

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pokemon-smile.git
   cd pokemon-smile
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up MongoDB:
   - Install MongoDB locally or use a cloud service like MongoDB Atlas
   - Create a `.env` file with your MongoDB connection string:
     ```
     MONGO_URI=mongodb://localhost:27017/
     SECRET_KEY=your_secret_key_here
     ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Usage

### Main Menu
- Click "Get Brushing" to start a brushing session
- Access your Pokédex to view caught Pokémon
- Log in or create a profile to save your progress

### Brushing Screen
- Follow the on-screen timer and animations
- Brush for the full 2 minutes to catch a Pokémon
- Your buddy Pokémon will cheer you on

### Pokédex
- View all your caught Pokémon
- Search by name or type
- Click on a Pokémon to see details and hear its cry
- Toggle background music with the music button

## Project Structure
