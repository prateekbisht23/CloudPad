# CloudPad

**CloudPad** is a lightweight, real-time text and file-sharing platform inspired by Dontpad. It allows users to create unique URLs where they can instantly share text and files with others. Unlike traditional storage platforms, CloudPad is designed for quick, temporary sharing, with automatic deletion of inactive notes.

🚨 **Note:** CloudPad is currently under development. At this stage, only real-time text sharing is functional, while file-sharing features are yet to be implemented.

## 🚀 Features

- **Instant Text Sharing** – Start typing, and your text is saved in real time.
- **Dynamic URL-Based Notes** – Create and access shared notes using custom URLs.
- **Auto-Deletion of Inactive Notes** – Notes and files are deleted after 10 hours of inactivity.
- **Lightweight and Fast** – Built with Django, optimized for speed.
- **No Account Required** – Share content instantly without signing up.

## 🛠️ Tech Stack

- **Backend:** Django, Python
- **Database:** SQLite (Initial), PostgreSQL (Future Implementation)
- **Real-Time Storage:** Supabase (Planned for File Handling)
- **Frontend:** Django Templates (No Separate Frontend Framework)

## 📌 How It Works

1. **Enter a URL** – Simply visit `cloudpad.example.com/your-note`.
2. **Start Typing** – Your text is saved in real time.
3. **Share the URL** – Others can instantly see and edit the text.
4. **Auto-Deletion** – If a note remains inactive for 10 hours, it is automatically deleted.

## 📥 Installation & Setup

### Prerequisites

- Python 3.x
- Django

### Clone the Repository

```bash
git clone https://github.com/prateekbisht23/CloudPad.git
cd CloudPad
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to start using CloudPad locally.

## 🎯 Future Enhancements

- **File Upload Support** – Share PDFs, Word documents, images, and more.
- **Improved UI/UX** – A modern, dark-themed interface.
- **Custom Expiry Times** – Users can set their own expiration periods.
- **Real-Time Collaboration** – Enable multiple users to edit a document simultaneously.
- **Mobile-Friendly Design** – Optimize for seamless usage on mobile devices.

## 📜 License

CloudPad is an open-source project under the **MIT License**.

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repository, open issues, or submit pull requests.

### Steps to Contribute

1. Fork the repository.
2. Create a new branch (`feature-new-feature`).
3. Commit your changes.
4. Push to the branch.
5. Open a pull request.

## 📧 Contact

For any queries or suggestions, feel free to reach out:

- **GitHub:** [@prateekbisht23](https://github.com/prateekbisht23)
- **Email:** [your.email@example.com](mailto:your.email@example.com)

---

🌟 **Star the repo if you find CloudPad useful!** 🚀
