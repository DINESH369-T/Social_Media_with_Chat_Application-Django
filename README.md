# Django Social Media with Chat Application 💬

Django Social Media with Chat Application is a full-stack social media and real-time communication platform developed using Django. The application combines essential social networking features with instant private messaging, allowing users to share content, interact with posts, and communicate with other users through a single web application.

Built with Django, Django Channels, WebSockets, and JavaScript, the platform provides an interactive social experience with features such as user authentication, image sharing, likes, comments, and real-time chat with message delivery and read receipts.

---

## 1. Core Architecture & Technical Deep-Dive

### 🔐 Custom User Management & Authentication

- **What it is:** A custom user management system implemented using Django models and session-based authentication.
- **What it does:**
  - Allows users to register and log in using their credentials.
  - Stores user information in a custom `Users` model.
  - Uses Django password hashing to securely store passwords.
  - Maintains user sessions to manage authenticated access.
  - Supports profile picture uploads and updates.
- **Why we use it:** A custom user model provides control over user-related data and makes it easier to integrate authentication with the application's social networking features.

### 📝 Social Media Post Management

The post management system allows users to create and interact with content shared across the platform.

**1. Post Creation**
- Users can publish posts containing text content and images.
- Post information is stored in the database using Django models.
- Uploaded images are handled through Django's media file management.

**2. Like Management**
- Users can like and unlike posts.
- A separate `Like` model maintains the relationship between users and posts.
- A unique constraint prevents the same user from liking the same post multiple times.
- The application dynamically tracks the total number of likes.

**3. Comment Management**
- Users can add comments to individual posts.
- Each comment is associated with its author and the corresponding post.
- Comments are stored with timestamps to maintain their creation history.

**Why it matters:** These features provide the basic interaction mechanisms required for a social networking platform.

### 💬 Real-Time Private Chat Architecture

The real-time messaging system is one of the core components of the application. It uses Django Channels and WebSockets to establish persistent communication between two users.

**1. WebSocket Connection (`consumers.py`)**
- Establishes a persistent WebSocket connection between the client and server.
- Uses Django Channels consumers to handle incoming and outgoing messages.
- Authenticates the sender using the user's session.
- Associates the conversation with the correct participants.

**2. Conversation Management (`chat/views.py`)**
- Identifies the two users participating in a conversation.
- Generates a consistent room name based on their usernames.
- Retrieves previous messages from the database.
- Displays conversation history in chronological order.

**3. Message Storage (`Message` Model)**
- Stores the sender, receiver, message content, and timestamp.
- Maintains an `is_read` Boolean field to track whether a message has been seen.
- Preserves conversation history for future access.

**4. Message Delivery & Read Receipts**
- Sends messages instantly through WebSocket communication.
- Displays a `Sent` status for outgoing messages.
- Updates the status to `Seen` when the recipient opens the conversation and the messages are marked as read.
- Uses WebSocket events to communicate read-receipt updates to the chat interface.

**Why we use WebSockets:** Unlike traditional HTTP requests, WebSockets maintain a persistent, two-way connection between the client and server. This allows messages and read-receipt updates to be exchanged without repeatedly refreshing the page.

---

### 🌐 Frontend & API Integration

The frontend combines Django templates with JavaScript and Bootstrap to provide an interactive user experience.

- **Django Templates:** Dynamically render user profiles, posts, comments, and chat history.
- **JavaScript:** Handles frontend interactions, asynchronous requests, and WebSocket communication.
- **Bootstrap 5:** Provides responsive layouts and reusable UI components.
- **Django REST Framework:** Supports API-based operations for selected post-related functionalities.

---

## 2. User Features & Capabilities (What You Can Do)

- **👤 User Registration & Login:** Create an account and securely log in to the platform.
- **🖼️ Profile Management:** Upload and update profile pictures.
- **📝 Create Posts:** Share text-based content and images.
- **❤️ Like & Unlike Posts:** Interact with posts shared by other users.
- **💬 Comments:** Add and view comments on posts.
- **⚡ Real-Time Private Messaging:** Communicate instantly with other registered users.
- **✓ Message Status:** Track whether outgoing messages have been sent or seen.
- **🕒 Chat History:** Access previous conversations with message timestamps.
- **📱 Responsive Interface:** Use the application through a responsive web interface built with Bootstrap.

---

## 3. Tech Stack Summary

| Layer | Technologies & Tools |
|---|---|
| Backend Framework | Python, Django |
| Real-Time Communication | Django Channels, WebSockets |
| ASGI Server | Daphne |
| API Development | Django REST Framework |
| Database | SQLite |
| Frontend | HTML5, CSS3, JavaScript |
| UI Framework | Bootstrap 5 |
| Authentication | Django Sessions, Password Hashing |
| File Management | Django Media File Handling |
| Environment Configuration | python-dotenv, `.env` |

---

## 4. Database Architecture

The application uses Django ORM to manage relationships between users, posts, likes, comments, and messages.

### Main Models

| Model | Responsibility |
|---|---|
| `Users` | Stores user information and profile pictures. |
| `Post` | Stores posts created by users. |
| `Like` | Maintains user-to-post like relationships. |
| `Comment` | Stores comments associated with posts and users. |
| `Message` | Stores private messages, sender, receiver, timestamps, and read status. |

These relationships help maintain structured application data and support the platform's social networking and messaging functionality.

---

## 5. Project Directory Structure

```text
django-social-chat/
│
├── media/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── proj_3/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── chat/
│   ├── models.py
│   ├── views.py
│   ├── consumers.py
│   ├── routing.py
│   └── ...
│
├── templates/
├── static/
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 6. Quick Start & Installation Guide

### Prerequisites

- Python 3.10+ installed on your system.
- Git installed on your system.
- pip package manager.

### Step 1: Clone the Repository

```bash
git clone https://github.com/DINESH369-T/Social_Media_with_Chat_Application-Django.git
```

Navigate into the project directory:

```bash
cd django-social-chat
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root directory.

Add your Django secret key:

```env
DJANGO_SECRET_KEY=your_django_secret_key_here
```

Do not upload your actual `.env` file or secret key to GitHub.

### Step 5: Apply Database Migrations

```bash
python manage.py migrate
```

### Step 6: Start the Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to:

```text
http://127.0.0.1:8000/
```

---

## 7. Project Objective

The objective of Django Social Connect is to develop a social networking platform that integrates content sharing and real-time private communication.

Through this project, the implementation explores Django web development, relational database management, session-based authentication, REST APIs, and real-time communication using WebSockets and Django Channels.
