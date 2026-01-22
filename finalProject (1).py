import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QMessageBox, QStackedWidget, QListWidget, QListWidgetItem, QFormLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDateEdit
import smtplib
import imaplib
import email
from email.message import EmailMessage
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from email.header import decode_header
from PyQt5.QtGui import QFont, QIcon

# Configure API with environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.home_screen = None
        self.setWindowTitle("Smart Email Assistant - Login")
        self.resize(420, 320)
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f9fc;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 16px;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 16px;
            }
            QLineEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
                min-width: 120px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QMessageBox {
                background-color: #f7f9fc;
            }
        """)

        # Title Label
        self.title_label = QLabel("🔐 Smart Email Assistant")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))

        # Email Input
        self.emailid_label = QLabel("📧 Email ID:")
        self.emailid_input = QLineEdit()
        self.emailid_input.setPlaceholderText("Enter your email...")

        # Password Input
        self.password_label = QLabel("🔑 PassKey:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your passkey...")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Toggle Password Button
        self.toggle_password_btn = QPushButton("👁")
        self.toggle_password_btn.setFixedSize(40, 30)
        self.toggle_password_btn.setStyleSheet("background: #bdc3c7; border-radius: 5px;")
        self.toggle_password_btn.clicked.connect(self.toggle_password)

        # Horizontal layout for password and toggle button
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_btn)

        # Login Button
        self.loginButton = QPushButton("Log In")
        self.loginButton.clicked.connect(self.check_login)

        # Form Layout
        form_layout = QFormLayout()
        form_layout.addRow(self.emailid_label, self.emailid_input)
        form_layout.addRow(self.password_label, password_layout)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addSpacing(10)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.loginButton, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def toggle_password(self):
        """Toggle password visibility."""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    @staticmethod
    def authenticate_gmail(emailid, passkey):
        """Authenticate with Gmail using SMTP."""
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(emailid, passkey)
            print("Log In Successful.")
            return True
        except smtplib.SMTPAuthenticationError:
            print("Authentication failed.")
            return False
        except Exception as e:
            print("Error:", e)
            return False

    def check_login(self):
        """Check credentials and open home screen."""
        emailid = self.emailid_input.text()
        passkey = self.password_input.text()

        if self.authenticate_gmail(emailid, passkey):
            self.open_home_screen()
        else:
            QMessageBox.warning(self, "Error", "Incorrect username or password")

    def open_home_screen(self):
        """Open home screen."""
        QMessageBox.information(self, "Success", "Login Successful!")
        self.home_screen = HomeScreen(self.emailid_input.text(), self.password_input.text())
        self.hide()
        self.home_screen.show()

class SendEmail(QWidget):
    def __init__(self, emailid, password, smtp_server='smtp.gmail.com', smtp_port=587):
        super().__init__()
        self.emailid = emailid
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, recipient_email, subject, body):
        msg = EmailMessage()
        msg['From'] = self.emailid
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.set_content(body)

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.emailid, self.password)
                smtp.send_message(msg)

            print("✅ Email sent successfully!")
            return True, "Email sent successfully!"

        except smtplib.SMTPAuthenticationError:
            print("❌ Authentication failed! Invalid email or password.")
            return False, "Authentication failed! Check your email or password."

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False, f"Failed to send email: {e}"

class SideBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(200)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                margin-bottom: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        self.frame = QVBoxLayout()

        self.inbox_button = QPushButton("Mails")
        self.compose_button = QPushButton("Compose")
        self.ai_button = QPushButton("Email Generation")
        self.schedule_button = QPushButton("Schedule Email")
        self.logout_button = QPushButton("Logout")

        self.frame.addWidget(self.inbox_button)
        self.frame.addWidget(self.compose_button)
        self.frame.addWidget(self.ai_button)
        self.frame.addWidget(self.schedule_button)
        self.frame.addWidget(self.logout_button)
        self.frame.addStretch()

        self.setLayout(self.frame)

    def connect_buttons(self, inbox_function, compose_func, ai_func, schedule_func, logout_func):
        self.inbox_button.clicked.connect(inbox_function)
        self.compose_button.clicked.connect(compose_func)
        self.ai_button.clicked.connect(ai_func)
        self.schedule_button.clicked.connect(schedule_func)
        self.logout_button.clicked.connect(logout_func)

class InboxPage(QWidget):
    def __init__(self, emailid, passkey):
        super().__init__()
        self.emailid, self.passkey = emailid, passkey
        main_layout = QVBoxLayout()
        self.stack = QStackedWidget()

        self.create_inbox_page()
        self.create_email_view_page()

        self.stack.addWidget(self.inbox_page)
        self.stack.addWidget(self.email_view_page)

        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.latest_emails()

    def create_inbox_page(self):
        self.inbox_page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Inbox")
        title.setAlignment(Qt.AlignCenter)

        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self.show_email_details)

        # Refresh Button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.latest_emails)

        layout.addWidget(title)
        layout.addWidget(self.refresh_button)  # Add the refresh button to the layout
        layout.addWidget(self.email_list)
        self.inbox_page.setLayout(layout)

    def create_email_view_page(self):
        self.email_view_page = QWidget()
        layout = QVBoxLayout()

        self.sender_label = QLabel("From: ")
        self.subject_label = QLabel("Subject: ")
        self.body_text = QTextEdit()
        self.body_text.setReadOnly(True)

        self.back_button = QPushButton("Back to Inbox")
        self.back_button.clicked.connect(self.go_back_to_inbox)

        layout.addWidget(self.sender_label)
        layout.addWidget(self.subject_label)
        layout.addWidget(self.body_text)
        layout.addWidget(self.back_button)

        self.email_view_page.setLayout(layout)

    def latest_emails(self):
        self.email_list.clear()  # Clear the current list before refreshing
        try:
            print("Connecting to Gmail IMAP...")
            imap_server = imaplib.IMAP4_SSL("imap.gmail.com")

            # IMAP Login
            try:
                imap_server.login(self.emailid, self.passkey)
                print("✅ IMAP Login Successful")
            except imaplib.IMAP4.error as e:
                QMessageBox.critical(self, "IMAP Error", f"Login failed: {e}")
                print(f"❌ IMAP Login failed: {e}")
                return

            imap_server.select("INBOX")
            status, email_numbers = imap_server.search(None, "ALL")

            if status != "OK":
                QMessageBox.warning(self, "Search Error", "Failed to search inbox.")
                print("❌ Search Error")
                return

            mail_ids = email_numbers[0].split()
            if not mail_ids:
                QMessageBox.information(self, "No Emails", "Inbox is empty.")
                print("📭 No emails found.")
                return

            # Fetch only the latest 15 emails
            latest_mails = mail_ids[-15:]
            self.emails_data = []

            for num in reversed(latest_mails):
                res, msg_data = imap_server.fetch(num, "(RFC822)")

                if res != "OK":
                    print(f"❌ Error fetching mail ID {num}")
                    continue

                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                # Decode the subject
                subject, encoding = decode_header(email_message.get("Subject", "No Subject"))[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")

                sender = email_message.get("From", "Unknown Sender")

                body = ""
                try:
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain" and part.get("Content-Disposition") is None:
                                charset = part.get_content_charset() or "utf-8"
                                body = part.get_payload(decode=True).decode(charset, errors="ignore")
                                break
                    else:
                        charset = email_message.get_content_charset() or "utf-8"
                        body = email_message.get_payload(decode=True).decode(charset, errors="ignore")
                except Exception as decode_err:
                    print(f"⚠️ Decode Error: {decode_err}")
                    body = "(Unable to decode email body.)"

                # Create a QListWidgetItem with only the subject
                item = QListWidgetItem(subject)
                # Set the sender as a tooltip or additional data
                item.setToolTip(f"From: {sender}")
                self.email_list.addItem(item)

                self.emails_data.append({
                    "subject": subject,
                    "sender": sender,
                    "body": body
                })

            imap_server.logout()
            print("✅ IMAP Disconnected Successfully")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            print(f"❌ Critical error: {e}")

    def show_email_details(self, item):
        index = self.email_list.currentRow()
        email_data = self.emails_data[index]

        self.sender_label.setText(f"From: {email_data['sender']}")
        self.subject_label.setText(f"Subject: {email_data['subject']}")
        self.body_text.setPlainText(email_data['body'])

        self.stack.setCurrentIndex(1)

    def go_back_to_inbox(self):
        self.stack.setCurrentIndex(0)

class ComposeEmail(QWidget):
    def __init__(self, user_email, user_password, parent=None):
        super().__init__(parent)
        self.user_email = user_email
        self.user_password = user_password

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Compose Email")
        layout = QFormLayout()
        label_style = "font-weight: bold; font-size: 16px;"

        recipient_label = QLabel("To:")
        recipient_label.setStyleSheet(label_style)
        self.recipient_input = QLineEdit()

        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet(label_style)
        self.subject_input = QLineEdit()

        body_label = QLabel("Body:")
        body_label.setStyleSheet(label_style)
        self.body_input = QTextEdit()

        send_button = QPushButton("Send Email")
        send_button.clicked.connect(self.send_email)

        layout.addRow(recipient_label, self.recipient_input)
        layout.addRow(subject_label, self.subject_input)
        layout.addRow(body_label, self.body_input)
        layout.addRow(send_button)

        self.setLayout(layout)

    def send_email(self):
        recipient = self.recipient_input.text()
        subject = self.subject_input.text()
        body = self.body_input.toPlainText()

        if not recipient or not subject or not body:
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        sender = SendEmail(self.user_email, self.user_password)
        success, message = sender.send_email(recipient, subject, body)

        if success:
            QMessageBox.information(self, "Success", message)
            self.clear_fields()
        else:
            QMessageBox.warning(self, "Error", message)

    def clear_fields(self):
        self.recipient_input.clear()
        self.subject_input.clear()
        self.body_input.clear()


class AIGeneratePage(QWidget):
    def __init__(self, user_email=None, user_password=None):
        super().__init__()
        self.user_email = user_email
        self.user_password = user_password

        layout = QVBoxLayout()

        # Heading
        title = QLabel("AI Email Generator & Sender")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Apply bold style to labels
        label_style = "font-weight: bold; font-size: 16px;"

        # --- Input Section ---
        self.receiver_name_input = QLineEdit()
        self.receiver_name_input.setPlaceholderText("Receiver's Name (Required)")

        self.sender_name_input = QLineEdit()
        self.sender_name_input.setPlaceholderText("Sender's Name (Required)")

        # Smaller Description Box (Max 3 Lines)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Email Description (Required, Max 3 Lines)")
        self.description_input.setFixedHeight(60)
        self.description_input.textChanged.connect(self.limit_description_lines)

        receiver_label = QLabel("Receiver's Name:")
        receiver_label.setStyleSheet(label_style)
        layout.addWidget(receiver_label)
        layout.addWidget(self.receiver_name_input)

        sender_label = QLabel("Sender's Name:")
        sender_label.setStyleSheet(label_style)
        layout.addWidget(sender_label)
        layout.addWidget(self.sender_name_input)

        description_label = QLabel("Email Description:")
        description_label.setStyleSheet(label_style)
        layout.addWidget(description_label)
        layout.addWidget(self.description_input)

        # Generate Button
        self.generate_button = QPushButton("Generate Email Content")
        self.generate_button.clicked.connect(self.generate_email)
        layout.addWidget(self.generate_button)

        # --- Editable Compose Section ---
        self.to_email_input = QLineEdit()
        self.to_email_input.setPlaceholderText("Recipient Email Address (Required)")

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Email Subject (Editable)")

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Email Body (Editable)")

        to_label = QLabel("To:")
        to_label.setStyleSheet(label_style)
        layout.addWidget(to_label)
        layout.addWidget(self.to_email_input)

        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet(label_style)
        layout.addWidget(subject_label)
        layout.addWidget(self.subject_input)

        body_label = QLabel("Body:")
        body_label.setStyleSheet(label_style)
        layout.addWidget(body_label)
        layout.addWidget(self.body_input)

        # Send Button
        self.send_button = QPushButton("Send Email")
        self.send_button.clicked.connect(self.send_email)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def limit_description_lines(self):
        max_lines = 3
        text = self.description_input.toPlainText()

        lines = text.split('\n')
        if len(lines) > max_lines:
            self.description_input.blockSignals(True)
            self.description_input.setPlainText('\n'.join(lines[:max_lines]))
            cursor = self.description_input.textCursor()
            cursor.movePosition(cursor.End)
            self.description_input.setTextCursor(cursor)
            self.description_input.blockSignals(False)

    def generate_email(self):
        receiver_name = self.receiver_name_input.text().strip()
        sender_name = self.sender_name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        # Validation
        if not receiver_name or not sender_name or not description:
            QMessageBox.warning(self, "Missing Fields", "Please fill in Receiver Name, Sender Name, and Description.")
            return

        # Compose the prompt (we ask Gemini to start with a subject on first line)
        prompt = (
            f"Write a professional email from {sender_name} to {receiver_name}. "
            f"The email should be about: {description}. "
            "Start the email with a subject line on the first line, then a blank line, followed by the body."
        )

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)

            if response and hasattr(response, 'text'):
                full_content = response.text.strip()
                print("✅ AI Email Content Generated\n", full_content)

                # Extract subject (first non-empty line)
                subject, body = self.extract_subject_and_body(full_content)

                # Populate compose fields
                self.subject_input.setText(subject)
                self.body_input.setPlainText(body)

            else:
                self.body_input.setPlainText("Failed to generate email body.")
                print("❌ No response from AI model")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate: {e}")
            print(f"❌ Error: {e}")

    def extract_subject_and_body(self, content):
        lines = content.split("\n")
        subject = ""
        body_lines = []

        for i, line in enumerate(lines):
            if line.strip() and not subject:  # First non-empty line is subject
                subject = line.strip()
                continue
            if subject and line.strip():  # Everything else is body
                body_lines = lines[i:]
                break

        body = "\n".join(body_lines).strip()
        if not subject:
            subject = "Generated Email"

        return subject[9:], body

    def send_email(self):
        to_email = self.to_email_input.text().strip()
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()

        if not to_email or not subject or not body:
            QMessageBox.warning(self, "Missing Fields", "Please fill in recipient email, subject, and body before sending.")
            return

        # Send email using SendEmail class
        sender = SendEmail(self.user_email, self.user_password)
        success, message = sender.send_email(to_email, subject, body)

        if success:
            QMessageBox.information(self, "Success", message)
            self.clear_fields()
        else:
            QMessageBox.warning(self, "Error", message)

    def clear_fields(self):
        self.receiver_name_input.clear()
        self.sender_name_input.clear()
        self.description_input.clear()
        self.to_email_input.clear()
        self.subject_input.clear()
        self.body_input.clear()

class SchedulePage(QWidget):
    def __init__(self, user_email, user_password):
        super().__init__()

        self.user_email = user_email
        self.user_password = user_password
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        self.setWindowTitle("Schedule Email")
        self.resize(400, 400)

        layout = QFormLayout()

        # Recipient Input
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Recipient Email")

        # Subject Input
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Email Subject")

        # Body Input
        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Email Body")

        # Date Picker
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())

        # Time Selection (Hour, Minute, AM/PM)
        self.hour_dropdown = QComboBox()
        self.hour_dropdown.addItems([str(i) for i in range(1, 13)])

        self.minute_dropdown = QComboBox()
        self.minute_dropdown.addItems([f"{i:02}" for i in range(0, 60)])

        self.ampm_dropdown = QComboBox()
        self.ampm_dropdown.addItems(["AM", "PM"])

        # Time Layout
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.hour_dropdown)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.minute_dropdown)
        time_layout.addWidget(self.ampm_dropdown)

        # Schedule Button
        self.schedule_button = QPushButton("Schedule Email")
        self.schedule_button.clicked.connect(self.schedule_email)

        # Add Widgets to Layout
        layout.addRow(QLabel("Recipient:"), self.recipient_input)
        layout.addRow(QLabel("Subject:"), self.subject_input)
        layout.addRow(QLabel("Body:"), self.body_input)
        layout.addRow(QLabel("Select Date:"), self.date_picker)
        layout.addRow(QLabel("Select Time:"), time_layout)
        layout.addRow(self.schedule_button)

        self.setLayout(layout)

    def schedule_email(self):
        recipient = self.recipient_input.text().strip()
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()

        if not all([recipient, subject, body]):
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        # Get selected date & time
        selected_date = self.date_picker.date().toString("yyyy-MM-dd")
        hour = int(self.hour_dropdown.currentText())
        minute = int(self.minute_dropdown.currentText())
        ampm = self.ampm_dropdown.currentText()

        # Convert to 24-hour format
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0

        # Construct datetime object
        send_time = datetime.datetime.strptime(
            f"{selected_date} {hour}:{minute}", "%Y-%m-%d %H:%M"
        )

        # Check if the selected time is in the past
        if send_time < datetime.datetime.now():
            QMessageBox.warning(self, "Error", "Selected time is in the past!")
            return

        # Schedule Email
        self.scheduler.add_job(
            self.send_email, "date", run_date=send_time,
            args=[recipient, subject, body]
        )

        QMessageBox.information(self, "Success", f"Email scheduled for {send_time}")

    def send_email(self, recipient, subject, body):
        """Use SendEmail class to send the email."""
        email_sender = SendEmail(self.user_email, self.user_password)
        success, message = email_sender.send_email(recipient, subject, body)
        print(f"📨 Scheduled Email Status: {message}")

class HomeScreen(QWidget):
    def __init__(self, emailid, passkey):
        super().__init__()

        self.setWindowTitle("Home Screen")
        self.resize(800, 600)

        self.sidebar = SideBar()
        self.sidebar.connect_buttons(
            self.show_inbox_page,
            self.compose_mail,
            self.show_ai_generation,
            self.show_scheduling,
            self.logout
        )

        self.stack = QStackedWidget()
        self.inbox_page = InboxPage(emailid, passkey)
        self.compose_page = ComposeEmail(emailid, passkey)
        self.ai_page = AIGeneratePage(emailid, passkey)
        self.schedule_page = SchedulePage(emailid, passkey)

        self.stack.addWidget(self.inbox_page)
        self.stack.addWidget(self.compose_page)
        self.stack.addWidget(self.ai_page)
        self.stack.addWidget(self.schedule_page)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        self.setLayout(main_layout)

    def show_inbox_page(self):
        print("Switching to Inbox Page")
        self.stack.setCurrentWidget(self.inbox_page)

    def compose_mail(self):
        print("Switching to Compose Mail")
        self.stack.setCurrentWidget(self.compose_page)

    def show_ai_generation(self):
        print("Switching to AI Generation Page")
        self.stack.setCurrentWidget(self.ai_page)

    def show_scheduling(self):
        print("Switching to Scheduling Page")
        self.stack.setCurrentWidget(self.schedule_page)

    def logout(self):
        print("Logging out")
        confirm = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.close()
            self.login_screen = LoginWindow()
            self.login_screen.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())