# Pokémon Smile - Brushing App with Pokédex

![Pokémon Smile Logo](static/favicon.png)

A web application inspired by the Pokémon Smile mobile app, designed to make brushing teeth fun by allowing users to catch Pokémon while they brush. This project includes a brushing timer, Pokédex to track caught Pokémon, and user profiles.

## Features

- **Interactive Brushing Timer**: A 2-minute timer with animations to guide brushing
- **Brushing Motion Tracking**: Real-time tracking of hand brushing movements with visual feedback
- **Brushing Progress Bars**: Visual indicators showing progress for side-to-side and up-and-down brushing
- **Motion Visualization**: Optional visualization overlay showing brush motion patterns and intensity
- **Pokémon Catching**: Catch random Pokémon when you complete brushing sessions
- **Shadow Pokémon Reveal**: Mysterious shadow Pokémon appear at the horizon and gradually reveal themselves
- **Comprehensive Pokédex**: View all your caught Pokémon with details and cries
- **User Profiles**: Create and manage profiles to track your Pokémon collection
- **Buddy Pokémon**: Select a favorite Pokémon to be your brushing buddy
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Background Music**: Toggle-able music for a more immersive experience
- **Cross-Origin Support**: CORS implementation for handling external requests

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Flask
- **Database**: MongoDB
- **Computer Vision**: JavaScript-based motion detection and analysis
- **APIs**: PokeAPI for Pokémon data
- **Audio**: Pokémon cries and background music from various sources
- **Security**: CORS support for secure cross-origin requests

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
   - Create a `.env` file with your MongoDB connection string and other settings:
     ```
     MONGO_URI=mongodb://localhost:27017/
     FLASK_ENV=development
     SECRET_KEY=your_secret_key_here
     FLASK_DEBUG=1
     BASE_URL=http://localhost:5000
     ```

5. Run the application:
   ```
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Docker Support

For containerized deployment:

1. Build and run using Docker Compose:
   ```
   docker-compose up --build
   ```

2. The app will be available at `http://localhost:5000`

## Usage

### Main Menu
- Click "Get Brushing" to start a brushing session
- Access your Pokédex to view caught Pokémon
- Try on different hats in the Hats section
- Log in or create a profile to save your progress
- Your buddy Pokémon appears at the bottom of the screen

### Brushing Screen
- Follow the on-screen timer and animations
- Use the "Show Tracking" button to visualize your brushing motion
- Monitor your brushing technique with the side-to-side and up-and-down progress bars
- Aim to fill both progress bars by using proper brushing techniques
- Brush for the full 2 minutes to catch a Pokémon
- Watch as the shadow Pokémon gradually reveals itself
- Your buddy Pokémon will cheer you on from the bottom of the screen
- Click the Pokéball to catch the Pokémon once revealed

### Pokédex
- View all your caught Pokémon
- Search by name or type
- Click on a Pokémon to see details and hear its cry
- Toggle background music with the music button

## Recent Improvements

- **Brushing Motion Detection**: Added real-time tracking of hand brushing movements
- **Visual Feedback**: Color-coded motion vectors show brushing direction and intensity
- **Progress Tracking**: Progress bars for side-to-side and up-and-down brushing techniques
- **Brushing Statistics**: Capture results include brushing scores for different techniques
- **Enhanced Buddy Pokémon**: Improved positioning and sizing for better visibility
- **Shadow Pokémon Animation**: Shadow Pokémon now appear at the horizon with a gradual reveal
- **Improved Database Connections**: Better error handling for MongoDB connections
- **Music Path Fixes**: Updated music file references for consistent playback
- **CORS Support**: Added cross-origin support for improved security
- **Mobile Responsiveness**: Better scaling for different screen sizes

## Project Structure

The application follows a simple Flask structure:
- `app.py`: Main application file with routes and business logic
- `templates/`: HTML templates for rendering pages
- `static/`: CSS, JavaScript, images, and audio files
- `requirements.txt`: Python dependencies
- `Dockerfile` & `docker-compose.yml`: Container configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is for educational purposes only. Pokémon and related properties are trademarks of Nintendo, Game Freak, and The Pokémon Company.
