import sendgrid
from sendgrid.helpers.mail import Mail
from django.conf import settings


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
