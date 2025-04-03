# Pokémon Smile - Web-Based Brushing Companion

![Pokémon Smile Logo](static/favicon.png)

A web application inspired by the Pokémon Smile mobile app that makes brushing teeth fun by allowing users to catch Pokémon while they brush. Built with Python/Flask and modern web technologies.

## 🌟 Key Features

- **Brushing Timer**: 2-minute interactive timer with motion tracking
- **Pokémon Collection**: Catch Pokémon by completing brushing sessions
- **Motion Detection**: Real-time tracking of brushing movements
- **User Profiles**: Track progress and manage Pokémon collection
- **PWA Support**: Works offline and installable on mobile devices
- **Cross-Platform**: Responsive design for all devices

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/pokemon-smile.git
   cd pokemon-smile
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Create a `.env` file:
   ```
   MONGO_URI=mongodb://localhost:27017/
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   FLASK_DEBUG=1
   BASE_URL=http://localhost:5000
   ```

3. **Run the App**
   ```bash
   python app.py
   ```

### Docker Deployment

#### Mac/Linux
```bash
./docker-start.sh start   # Start app
./docker-start.sh logs    # View logs
./docker-start.sh stop    # Stop app
```

#### Windows
```powershell
.\docker-start.ps1 start  # Start app
.\docker-start.ps1 logs   # View logs
.\docker-start.ps1 stop   # Stop app
```

Visit `http://localhost:5000` in your browser.

## 📚 Documentation

- [API Documentation](API.md) - Detailed API endpoints and usage
- [Development Guide](PLANNING.md) - Architecture and development guidelines
- [Task List](TASKS.md) - Current sprint and backlog items

## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3.8+, Flask
- **Database**: MongoDB
- **Container**: Docker
- **APIs**: PokeAPI integration
- **PWA**: Service Workers, Manifest

## 🔒 Security Features

- JWT-based authentication
- CORS protection
- Rate limiting
- Secure password handling
- HTTPS enforcement

## 🧪 Testing

```bash
# Run all tests
./run_tests.sh

# Run specific test suite
python -m pytest tests/test_api.py
```

## 📦 Publishing

### To Docker Hub
```bash
# Mac/Linux
./docker-push.sh

# Windows
.\docker-push.ps1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [PLANNING.md](PLANNING.md) for coding standards and guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Pokémon is a trademark of Nintendo/Creatures Inc./GAME FREAK inc.
- This is a fan project and is not affiliated with Nintendo or The Pokémon Company
- Thanks to [PokeAPI](https://pokeapi.co/) for the Pokémon data
