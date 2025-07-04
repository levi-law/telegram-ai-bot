# 🤖 Telegram AI Bot

A professional, production-ready AI-powered Telegram bot with OpenAI Assistant API integration and multiple character personalities.

## ✨ Features

- **🎭 Multiple AI Characters**: 11 unique personalities with distinct conversation styles
- **🧠 OpenAI Assistant API**: Real AI conversations with memory and context
- **📱 Professional Telegram Integration**: Full bot functionality with commands and callbacks
- **🏗️ Clean Architecture**: Layered design with proper separation of concerns
- **🧪 Comprehensive Testing**: Unit and integration tests with pytest
- **📊 Type Safety**: Full type hints and mypy support
- **🔧 Production Ready**: Proper logging, error handling, and configuration management
- **📸 Character Images**: Visual character representation with photo commands
- **💾 Session Management**: Persistent conversations with automatic cleanup

## 🏛️ Architecture

```
src/telegram_ai_bot/
├── core/           # Application core and bot management
├── models/         # Data models and business entities
├── services/       # Business logic and external API integration
├── handlers/       # Telegram message and command handlers
├── config/         # Configuration and settings management
└── utils/          # Utility functions and helpers
```

### 🔄 Design Patterns

- **Service Layer Pattern**: Business logic separated from presentation
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: Loose coupling between components
- **Factory Pattern**: Object creation and initialization
- **Observer Pattern**: Event-driven architecture

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- OpenAI API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/levi-law/telegram-ai-bot.git
   cd telegram-ai-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your tokens and API keys
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | ✅ | - |
| `OPENAI_API_KEY` | OpenAI API key | ✅ | - |
| `BOT_NAME` | Display name for the bot | ❌ | Telegram AI Bot |
| `BOT_USERNAME` | Bot username (with @) | ❌ | @telegram_ai_bot |
| `OPENAI_MODEL` | OpenAI model to use | ❌ | gpt-3.5-turbo |
| `DEBUG` | Enable debug mode | ❌ | false |
| `LOG_LEVEL` | Logging level | ❌ | INFO |
| `SESSION_TIMEOUT` | Session timeout in seconds | ❌ | 3600 |

### Character Configuration

Characters are defined in `assets/data/characters.json`. Each character includes:

- **Basic Info**: ID, name, emoji, description
- **AI Personality**: Detailed personality prompt for OpenAI
- **Conversation Style**: How the character communicates
- **Images**: Character photos for visual representation
- **Traits**: Personality traits for categorization

## 🎭 Available Characters

| Character | Emoji | Description |
|-----------|-------|-------------|
| Riley | 🧡 | Energetic, playful, and irresistibly supportive |
| Nika | 👩‍🎓 | Shy and romantic college girl |
| Imane | 🏃‍♀️ | Confident, commanding, and fiery athlete |
| Coco | 👩‍💼 | Influencer and fashion model |
| Asha | 🌺 | Playful, curious, and free-spirited |
| Jane | 👩‍🦰 | Flirtatious traditional girl |
| Mrs. Grace | 👩‍🏫 | Caring and charming mature woman |
| Bianca | ✨ | Confident, sharp-tongued, seductively witty |
| Kate | 💜 | Caring, confident, direct mature woman |
| Nya | 🐱 | Playful, mischievous, and affectionate cat girl |
| Sakura | 🌸 | Mysterious Japanese secret agent |

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and select a character |
| `/characters` | Show character selection menu |
| `/photo` | Get a photo of your current character |
| `/startover` | Reset conversation and start fresh |
| `/status` | Show your current session status |
| `/help` | Show help message with all commands |

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interaction
└── conftest.py     # Pytest configuration and fixtures
```

## 🔧 Development

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Type checking
mypy src

# Linting
flake8 src tests
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## 📦 Package Structure

```
telegram-ai-bot/
├── src/telegram_ai_bot/    # Main package source
├── tests/                  # Test suite
├── assets/                 # Static assets (images, data)
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── deployment/             # Deployment configurations
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── pyproject.toml         # Package configuration
└── README.md              # This file
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t telegram-ai-bot .

# Run container
docker run -d --env-file .env telegram-ai-bot
```

### Production Considerations

- **Environment Variables**: Use secure secret management
- **Logging**: Configure structured logging for monitoring
- **Health Checks**: Implement health check endpoints
- **Scaling**: Consider horizontal scaling for high load
- **Monitoring**: Add metrics and alerting
- **Database**: Consider persistent storage for production

## 🔒 Security

- **API Keys**: Never commit API keys to version control
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: Built-in protection against spam and abuse
- **Error Handling**: Graceful error handling without exposing internals
- **Logging**: Sensitive data is not logged

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write tests for new features
- Update documentation for changes
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [OpenAI](https://openai.com/) - AI API and models
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/levi-law/telegram-ai-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/levi-law/telegram-ai-bot/discussions)
- **Documentation**: [Project Wiki](https://github.com/levi-law/telegram-ai-bot/wiki)

---

**Made with ❤️ for the AI community**

