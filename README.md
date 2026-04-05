# Bakso Simulator: Kindness For A Better World

Bakso Simulator: Kindness For A Better World is a Python-based simulation game that highlights social awareness and compassion. In this game, players take on the role of a bakso (Indonesian meatball soup) seller who must manage their business while facing meaningful choices: focus on profit or help those in need.


## 📁 Game Structure

```
Bakso Simulator
│
├── 📁 assets
│   └── images
│       ├── backgrounds
│       ├── characters
│       └── items
│
├── 📁 src (Core Game Logic)
│   │
│   ├── 📁 models
│   │   └── (Data structures: player, customer, items, etc.)
│   │
│   ├── 📁 scenes
│   │   └── (Game flow: menu, gameplay, end screen)
│   │
│   ├── 📁 ui
│   │   └── (User interface system)
│   │
│   ├── 📁 utils
│   │   └── (Helper / utility functions)
│   │
│   ├── ⚙️ config.py
│   │   └── (Game configuration: prices, settings, etc.)
│   │
│   ├── 🧠 customer_manager.py
│   │   └── (Handles customers: types, conditions, interactions)
│   │
│   ├── 🎮 game.py
│   │   └── (Main game logic)
│   │
│   ├── 🖥 ui_components.py
│   │   └── (UI elements like buttons, text, etc.)
│   │
│   └── ▶️ main.py
│       └── (Entry point to run the game)
│
├── 📄 requirements.txt
│   └── (List of required libraries)
│
└── 📄 README.md
    └── (Project documentation)


## 🎮 Gameplay

* Players sell bakso to customers each day
* Different types of customers will appear with unique conditions
* Players can choose to:

  * Sell bakso to earn money 💰
  * Give free meals to customers in need 🤝
* Every decision will affect:

  * The player’s finances
  * Kindness reputation ✨


## ⚙️ Key Features

* 🛒 Simple buying and selling system
* 💵 Basic money management
* ❤️ Charity feature (giving free food)
* 🧠 Decision-making system (profit vs kindness)
* 📈 Reputation system (optional / future development)


## 🎯 Project Goals

This project was created to:

* Participate in a competition with the theme **“Kindness for a Better World”**
* Demonstrate that games can be used as an educational medium
* Encourage empathy, kindness, and social awareness


## 🚀 How to Run

1. Make sure Python is installed
2. Clone this repository:

   ```bash
   git clone https://github.com/username/bakso-simulator.git
   ```
3. Navigate to the project folder:

   ```bash
   cd bakso-simulator
   ```
4. Run the program:

   ```bash
   python main.py
   ```


## 🛠 Technologies

- Python (Console-based)
- Arcade Library


## 💡 Future Improvements

* GUI (more interactive interface)
* Level system & cart upgrades
* More customer variations (kids, workers, elderly, etc.)
* Random events (discounts, donation waves, etc.)
* Leaderboard (based on kindness & profit)


## ✨ Moral Message

> “Profit helps you survive, but kindness makes you meaningful.”


## 📝 License

MIT License
