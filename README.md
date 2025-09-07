# Mira Food Store Chatbot 🍴🤖

A **mini food ordering website** integrated with a **Dialogflow chatbot** and **FastAPI backend**.  
Users can **place, track, add, or remove orders** in real-time through the chatbot.  

---

## 🌟 Features

- **Dialogflow Chatbot** for interactive ordering  
- **Place Orders**: Select food items and quantity  
- **Track Orders**: Check the status of your order  
- **Add or Remove Orders**: Modify your order dynamically  
- **Simple Frontend**: Responsive HTML & CSS interface  

---

## ⚡ How it Works

1. User visits the landing page.  
2. Chatbot pops up immediately for interaction.  
3. User can:  
   - Place a new order  
   - Track an existing order  
   - Add more items to an order  
   - Remove items from an order  
4. FastAPI backend handles **order management** and stores data in **MySQL**.  

---

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS  
- **Chatbot:** Dialogflow Messenger  
- **Backend:** Python, FastAPI  
- **Database:** MySQL  

---

## 🚀 How to Run

### Frontend
- Open `index.html` in browser OR  
- Use **VS Code Live Server**  

### Backend
1. Run the FastAPI server locally:
   ```bash
   uvicorn main:app --reload
2. Expose your local server using ngrok (required for Dialogflow HTTPS):

          ngrok http 8000


3.Copy the HTTPS URL from ngrok (e.g., https://abcd1234.ngrok.io)

4.In Dialogflow Console → Fulfillment → Webhook, replace the webhook URL with the ngrok HTTPS URL

5.Save and enable the webhook

⚠️ Note: Localhost (http://127.0.0.1:8000) cannot be used in Dialogflow; it requires a public HTTPS URL, which ngrok provides.
