


# 🥦 Smart Pantry OS

> **A "Living" Kitchen Assistant that tracks inventory, scans receipts, and suggests recipes based on what you actually have.**


https://github.com/user-attachments/assets/e1d51c55-b64c-4e47-9847-575a19e7dd2a

---

## 🧐 The Problem
Managing a modern kitchen is surprisingly complex. We often face these daily struggles:
* **"What do I have?"** Forgetting ingredients buried in the back of the fridge.
* **"What can I cook?"** Staring at a pile of random ingredients with no inspiration.
* **"I just bought this!"** Manually typing every item from a grocery receipt into an app is tedious and prone to error.
* **"Food Waste"** Throwing away produce because we forgot it existed or didn't know how to use it.

## 💡 The Solution
**Smart Pantry OS** is an AI-powered kitchen operating system designed to automate the boring parts of cooking. It uses **Computer Vision (GPT-4o)** to read receipts, **Databases** to track stock down to the gram, and **Generative AI** to act as a Michelin-star chef that plans meals based *only* on what is currently in stock.

---

## 🚀 Key Features

### 📸 1. AI Receipt Scanner
* **Upload & Forget:** Snap a photo of any grocery receipt (Costco, Walmart, etc.).
* **Smart Parsing:** Uses **GPT-4o-mini (Vision)** to extract item names, quantities, and units.
* **Auto-Categorization:** Automatically sorts items into *Dairy, Produce, Pantry, Snacks, etc.*
* **Intelligent Logic:** Knows that "Cape Cod" is a chip brand (Pantry) and not a Fish (Fridge).

### 📦 2. "Living" Inventory System
* **Visual Dashboard:** See your stock sorted by category in a clean UI.
* **Fractional Usage:** Used half an onion? Click `½` or `¼` to update the stock to `0.5` instead of deleting it.
* **Multi-User Support:** Supports multiple family members with separate, private databases.
* **Restock Alerts:** When an item hits `0`, it automatically moves to the **Shopping List** tab.

### 👨‍🍳 3. Context-Aware Chef
* **Time Awareness:** Recognizes if it's Morning, Afternoon, or Evening and suggests *Breakfast, Lunch, or Dinner* accordingly.
* **Inventory-Based Recipes:** Suggests recipes using *only* your available ingredients (plus common staples like Salt/Oil).
* **Smart Deduction:** Clicking "I Cooked This" automatically subtracts the correct amount of ingredients from your database.
* **Dynamic Scaling:** Adjusts recipe portions and ingredient deductions dynamically for 1 to 10 people.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python-based UI)
* **AI Logic:** [OpenAI GPT-4o-mini](https://openai.com/) (Vision & Text reasoning)
* **Database:** [SQLite](https://www.sqlite.org/) (Lightweight, local storage per user)
* **Image Handling:** Pillow (PIL)
* **Authentication:** SHA-256 Hashed Passwords

---

## ⚙️ How to Run Locally

### 1. Clone the Repository
```bash
git clone [https://github.com/ShubhamRSY/smart_pantry_agent.git](https://github.com/ShubhamRSY/smart_pantry_agent.git)
cd smart_pantry_agent
```
2. Install Dependencies
Bash

pip install -r requirements.txt
3. Set up API Keys
Create a .env file in the root directory and add your OpenAI Key:

Plaintext

OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxx"
4. Run the App
Bash

streamlit run main.py
🧠 Project Architecture
Code snippet

graph TD
    User([User]) -->|Uploads Receipt| Scanner[AI Scanner]
    User -->|Asks: What to cook?| Chef[AI Chef]

    subgraph "Core Logic"
        Scanner -->|Extracts Data| GPT[GPT-4o-mini Vision]
        GPT -->|Categorizes| DB[(SQLite Database)]
        Chef -->|Reads Stock| DB
        Chef -->|Generates Recipe| GPT_Text[GPT-4o-mini Text]
    end

    subgraph "User Interface"
        DB -->|Show Inventory| UI[Streamlit Dashboard]
        GPT_Text -->|Recipe Cards| UI
        UI -->|'I Cooked This'| Deduct[Smart Deduction Engine]
        Deduct -->|Update Qty| DB
    end
🔮 Future Roadmap
[ ] Expiration Tracking: AI estimation of shelf life for produce.

[ ] Voice Mode: "Hey Pantry, remove 2 eggs."

[ ] Barcode Scanning: For items without receipts.

[ ] Nutrition Analysis: Calculate macros for suggested meals.

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page
