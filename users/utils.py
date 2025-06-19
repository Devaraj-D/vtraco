import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings
from sendgrid import SendGridAPIClient


def send_invitation_email(email, username, password):
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject='Welcome to the Platform – Your Login Credentials',
        html_content=f"""
            <h3>Welcome!</h3>
            <p>You have been added as an employee.</p>
            <p><b>Login Credentials:</b></p>
            <ul>
                <li>Username: {username}</li>
                <li>Password: {password}</li>
            </ul>
            <p>Please login and change your password using the "Forgot Password" option if needed.</p>
        """
    )

    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        sg.send(message)
        print("successfully")
    except Exception as e:
        print(f"SendGrid Error: {e}")

def send_otp_email(email, username, otp):
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject='Your OTP for Password Reset',
        html_content=f"""
            <h3>Hello {username},</h3>
            <p>You requested to reset your password.</p>
            <p><b>Your OTP is: <span style='color:blue'>{otp}</span></b></p>
            <p>This OTP is valid for a limited time. Do not share it with anyone.</p>
            <br>
            <p>Thanks,<br>Support Team</p>
        """
    )

    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"OTP Email sent to {email}. Status code: {response.status_code}")
    except Exception as e:
        print(f"SendGrid OTP email error: {e}")