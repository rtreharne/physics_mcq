# ⚛️ PhysicsMCQs.org

A modern, mobile-first Django web application for A-Level Physics multiple-choice questions — tailored for students, teachers, and tutors. Create quizzes, track performance, download PDFs, and log in with Google.

---

## 🚀 Features

- ✅ 100% Google-only authentication (via OAuth2)
- 🧠 Quiz engine with:
  - Randomised, topic-filtered questions
  - Per-question timers & difficulty labels
  - Instant feedback with correct answers + explanations
- 📊 Personalised **results dashboard** with:
  - Past quiz history
  - Topic-level performance tracking
- 📄 One-click PDF downloads for offline/classroom use
- 🛠️ Admin CSV upload tools (bulk questions, topics, keywords)
- 📱 Fully responsive & thumb-friendly design (built with Bootstrap 5)

---

## 🖥️ Tech Stack

- **Backend**: Django 4+ (pure Django, no DRF)
- **Frontend**: HTML, Bootstrap 5, vanilla JS
- **Authentication**: [django-allauth](https://django-allauth.readthedocs.io/) (Google only)
- **PDF Generation**: ReportLab (via custom view)
- **Hosting**: Render (GitHub-based CI/CD ready)

---

## 🔐 Google OAuth Setup

To enable Google login:

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and configure:
   - OAuth 2.0 Client ID
   - **Authorized redirect URIs**:
     ```
     http://localhost:8000/accounts/google/login/callback/
     ```
   - **Authorized JavaScript origins**:
     ```
     http://localhost:8000
     ```
3. Add your credentials to Django admin under:  
   **Social Applications → Google**
4. Add the app to **Site 1** and save.

---

## ⚙️ Local Development

### 1. Clone the repo

```bash
git clone https://github.com/your-username/physics-mcqs.git
cd physics-mcqs
```

### 2. Set up virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Migrate database & create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the dev server

```bash
python manage.py runserver
```

Visit: [http://localhost:8000](http://localhost:8000)

---

## 🧪 Testing

- Test Google login: [http://localhost:8000/accounts/login/](http://localhost:8000/accounts/login/)
- Test uploading questions: `/admin/mcq/question/upload-csv/`
- View quiz history at: `/my-quizzes/`
- Try PDF export after selecting keywords on homepage

---

## 📁 Admin Features

- Upload topics and questions via CSV
- Add exam boards, keywords, explanations, difficulty levels
- Assign multiple exam boards or keywords per question
- Manage quiz attempts and analytics

---

## 📌 Roadmap

- [ ] Add student leaderboard mode
- [ ] Export quiz attempts to CSV
- [ ] Add fuzzy search and keyword/tag filters
- [ ] Add spaced repetition / smart revision logic
- [ ] Launch public version at [physicsmcqs.org](http://physicsmcqs.org)

---

## 👨‍🏫 About

Built by **Dr. Robert Treharne**  
University of Liverpool — Senior Lecturer in Technology Enhanced Learning

Created to help students master A-Level Physics through targeted retrieval practice, instant feedback, and data-informed revision.

> Want to contribute or collaborate? Open an issue or email: R.Treharne@liverpool.ac.uk

---

## 📜 License

MIT License — free to use, fork, modify, and build on.

---

## 💻 Screenshots (Coming Soon)

- Homepage with topic filtering and keyword selectors
- Mobile-first quiz interface with per-question timing
- Results dashboard with accuracy bars by topic

---