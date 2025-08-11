# QUBE 🧠

QUBE is an interactive quiz application designed to provide an engaging and dynamic quizzing experience. It features real-time live quizzes, AI-powered quiz generation, and a vast collection of quizzes to explore.

## ✨ Features

*   **Live Quizzes:** Participate in real-time quiz sessions with instant feedback and competitive leaderboards.
*   **AI-Generated Quizzes:** Leverage AI (Google Gemini API) to create unique and diverse quiz content on various topics, offering endless possibilities.
*   **Explore Different Quizzes:** Discover and play a wide range of pre-existing quizzes across multiple categories, from general knowledge to specific subjects.
*   **Secure User Authentication:** Robust user management powered by Firebase Authentication, ensuring secure registration, login, and profile management.
*   **Image Management:** Efficiently store and deliver quiz-related images and user profile pictures using Cloudinary, optimizing performance and delivery.

## 🚀 Technologies Used

*   **Frontend:**
    *   HTML5
    *   CSS3 (with Tailwind CSS for utility-first styling, enabling rapid UI development)
    *   JavaScript (for interactive elements and dynamic content updates)
*   **Backend:**
    *   Python (Flask framework, providing a lightweight and flexible web server)
    *   Socket.IO (for real-time communication in live quizzes, enabling instant updates and interactions)
*   **Database:**
    *   PostgreSQL (for robust data storage and management of quiz data, user profiles, scores, and more)
*   **Authentication:**
    *   Firebase Authentication (for secure user registration, login, and session management, leveraging Google's robust authentication services)
*   **Cloud Services:**
    *   Cloudinary (for efficient storage, optimization, and delivery of user-uploaded images and quiz assets, reducing server load and improving media handling)
*   **API:**
    *   Google Gemini API (for AI quiz generation, allowing the application to create diverse and engaging quiz questions dynamically)

## 🛠️ Installation

Follow these steps to set up and run QUBE locally:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd QUBE
    ```

2.  **Set up Python Virtual Environment:**
    ```bash
    python -m venv env
    ```

3.  **Activate the Virtual Environment:**
    *   **Windows:**
        ```bash
        .\env\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source env/bin/activate
        ```

4.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure you have a `requirements.txt` file in your project root with all Python dependencies listed, including `psycopg2-binary` for PostgreSQL, `firebase-admin` for Firebase, `cloudinary` for Cloudinary, `Flask-SocketIO`, etc.)*

5.  **Install Node.js Dependencies (for Tailwind CSS):**
    ```bash
    npm install
    ```
    *(Note: Ensure Node.js and npm are installed on your system. You can download them from [nodejs.org](https://nodejs.org/).)*

6.  **Compile Tailwind CSS (in watch mode):**
    Open a **separate terminal** and run:
    ```bash
    npx tailwindcss -i .\static\css\tailwind.css -o .\static\css\output.css --watch
    ```
    This command will watch for changes in `tailwind.css` and recompile `output.css` automatically, ensuring your styles are always up-to-date.

7.  **Configure Environment Variables:**
    Create a `.env` file in the root directory of the project and add the following environment variables. Replace the placeholder values with your actual credentials.

    ```
    # Firebase Configuration (Client-side SDK credentials)
    FIREBASE_API_KEY="YOUR_FIREBASE_API_KEY"
    FIREBASE_AUTH_DOMAIN="YOUR_FIREBASE_AUTH_DOMAIN"
    FIREBASE_DATABASE_URL="YOUR_FIREBASE_DATABASE_URL"
    FIREBASE_PROJECT_ID="YOUR_FIREBASE_PROJECT_ID"
    FIREBASE_STORAGE_BUCKET="YOUR_FIREBASE_STORAGE_BUCKET"
    FIREBASE_MESSAGING_SENDER_ID="YOUR_FIREBASE_MESSAGING_SENDER_ID"
    FIREBASE_APP_ID="YOUR_FIREBASE_APP_ID"
    FIREBASE_MEASUREMENT_ID="YOUR_FIREBASE_MEASUREMENT_ID"

    # PostgreSQL Database Connection String
    # Example: postgresql://user:password@host:port/dbname
    SQLALCHEMY_DATABASE_URI="YOUR_POSTGRESQL_DATABASE_URI"

    # Application Specific Settings
    UPLOAD_FOLDER="static/profile_pics"
    ALLOWED_EXTENSIONS="png,jpg,jpeg"

    # Cloudinary Configuration for image storage
    CLOUDINARY_CLOUD_NAME="YOUR_CLOUDINARY_CLOUD_NAME"
    CLOUDINARY_API_KEY="YOUR_CLOUDINARY_API_KEY"
    CLOUDINARY_API_SECRET="YOUR_CLOUDINARY_API_SECRET"

    # Google Gemini API Key for AI quiz generation
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    *   **PostgreSQL Setup:** Ensure you have a PostgreSQL server running and a database created. Update `SQLALCHEMY_DATABASE_URI` accordingly. You might need to run database migrations or schema setup commands after this step (e.g., `flask db upgrade` if using Flask-Migrate).
    *   **Firebase Setup:** Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com/). You can find these credentials (API Key, Auth Domain, Project ID, etc.) in your Firebase project settings under "Project settings" -> "General" -> "Your apps" -> "Firebase SDK snippet" (choose "Config").
    *   **Cloudinary Setup:** Create a Cloudinary account at [cloudinary.com](https://cloudinary.com/) to obtain your cloud name, API key, and API secret from your dashboard.
    *   **Gemini API Key:** Obtain your API key from the Google AI Studio at [aistudio.google.com](https://aistudio.google.com/) or Google Cloud Console.

## 🏃 Usage

After completing all the installation steps and configuring your environment variables, you can run the Flask server:

```bash
flask run
```

The application should now be accessible in your web browser at `http://127.0.0.1:5000/` (or the address specified by Flask). You can then register a new user, explore quizzes, and participate in live sessions.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature` or `bugfix/YourBugfix`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'` or `Fix: Description of bug fix`).
5.  Push to the branch (`git push origin feature/YourFeature`).
6.  Open a Pull Request, describing your changes in detail.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for more details.

## 📧 Contact

For any inquiries, feedback, or support, please reach out to [Your Name/Email/Social Media Link].
