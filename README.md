````md
# NestMate 🏠

NestMate is a full-stack smart rental and roommate matching platform built using React, Django, MongoDB, Redis, and WebSockets.  
The platform helps users find rental properties, compatible roommates, real-time chat connections, and digital rental agreements.

---

# 🚀 Features

## 🏡 Property Listings
- Create rental listings
- Upload images
- Property details and pricing
- Search and filtering
- Nearby listings
- Scam detection system

---

## 🤝 Roommate Matching
- Lifestyle questionnaire
- Compatibility scoring
- Match suggestions
- Roommate requests
- Match comparison system

---

## 💬 Real-Time Chat
- WebSocket-based messaging
- Live room updates
- Read/unread messages
- Chat room management
- Deal negotiation support

---

## 📄 Rental Agreements
- Digital agreement generation
- Agreement signing
- PDF download/view
- Agreement status tracking

---

## 📊 Analytics
- Market price insights
- City statistics
- Heatmaps
- Scam analytics
- Trust leaderboard

---

# 🛠 Tech Stack

## Frontend
- React
- Vite
- Tailwind CSS
- Zustand
- Axios

---

## Backend
- Django
- Django REST Framework
- Django Channels
- Daphne

---

## Database
- MongoDB Atlas
- SQLite (Django internal apps)

---

## Realtime & Cache
- Redis
- WebSockets

---

# 📁 Project Structure

```bash
home_rental/
│
├── frontend/                # React frontend
│
├── apps/
│   ├── accounts/
│   ├── listings/
│   ├── roommate/
│   ├── chat/
│   ├── agreements/
│   └── analytics/
│
├── media/
├── static/
├── templates/
│
├── home_rental/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── manage.py
````


# 🐍 Backend Setup

## Create Virtual Environment

```bash
python -m venv venv
```

---

## Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🌐 Frontend Setup

```bash
cd frontend
npm install
```

---

# 🍃 MongoDB Atlas Setup

Create a MongoDB Atlas cluster from:

[MongoDB Atlas](https://www.mongodb.com/cloud/atlas?utm_source=chatgpt.com)

Add your connection string inside `.env`

Example:

```env
MONGO_URI=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/nestmate?retryWrites=true&w=majority
```

---

# 🔴 Redis Setup

Install Redis locally and run:

```bash
redis-server
```

Default:

```env
REDIS_URL=redis://127.0.0.1:6379/0
```

---

# 🔐 Environment Variables

Create `.env` file in root directory:

```env
DEBUG=True

SECRET_KEY=your_secret_key

MONGO_URI=your_mongodb_atlas_uri

REDIS_URL=redis://127.0.0.1:6379/0

EMAIL_USER=your_email
EMAIL_PASSWORD=your_password

GOOGLE_MAPS_API_KEY=your_google_maps_key
```

---

# ▶️ Running Backend

## Apply Migrations

```bash
python manage.py migrate
```

---

## Start Daphne Server

```bash
daphne -b 127.0.0.1 -p 8000 home_rental.asgi:application
```

Backend runs at:

```text
http://127.0.0.1:8000
```

---

# ▶️ Running Frontend

Inside frontend folder:

```bash
npm run dev
```

Frontend runs at:

```text
http://127.0.0.1:3000
```

---

# 🧪 Testing

## Django Tests

```bash
python manage.py test
```

---

## Frontend Linting

```bash
npx eslint src
```

---

# 📦 Production Build

```bash
npm run build
```

---

# 🌍 Deployment

## Frontend

Deploy on:

[Vercel](https://vercel.com?utm_source=chatgpt.com)

---

## Backend

Deploy on:

[Render](https://render.com?utm_source=chatgpt.com)

---

## Database

Use:

[MongoDB Atlas](https://www.mongodb.com/cloud/atlas?utm_source=chatgpt.com)

---

# 📌 Future Improvements

* AI roommate recommendations
* Voice/video calling
* Payment gateway integration
* Push notifications
* Mobile application
* Advanced fraud detection
* Smart property recommendations

---

# 👨‍💻 Author

Developed by Mahek.

Built with React, Django, MongoDB.

---

# 📄 License

This project is for educational and startup prototype purposes.

```
```
