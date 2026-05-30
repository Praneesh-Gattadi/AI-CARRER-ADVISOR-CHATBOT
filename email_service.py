import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger

def send_verification_email(to_email: str, username: str, otp: str) -> tuple[bool, str]:
    """
    Sends a beautifully formatted HTML email containing the verification OTP.
    Falls back to logging the OTP if SMTP settings are missing or connection fails.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = os.getenv("SMTP_PORT", "587")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_sender = os.getenv("SMTP_SENDER") or smtp_username
    
    # Validation of configurations
    if not smtp_username or not smtp_password:
        fallback_msg = (
            f"\n\n"
            f"==========================================================\n"
            f"[SMTP FALLBACK] OTP Verification Code Generated!\n"
            f"User: {username}\n"
            f"Email: {to_email}\n"
            f"Verification Code: {otp}\n"
            f"Note: Add SMTP_USERNAME/SMTP_PASSWORD in .env for real delivery.\n"
            f"==========================================================\n"
        )
        logger.warning(fallback_msg)
        print(fallback_msg, flush=True)
        return True, "SMTP configurations not found. Code generated in terminal logs for sandbox testing."

    try:
        # SMTP Port conversion
        try:
            port = int(smtp_port)
        except ValueError:
            port = 587

        msg = MIMEMultipart()
        msg['From'] = smtp_sender
        msg['To'] = to_email
        msg['Subject'] = "Verify Your Carrer Coach Account"
        
        # Professional HTML body template
        body = f"""
        <html>
        <body style="font-family: 'Outfit', Arial, sans-serif; background-color: #0b0f19; padding: 30px; color: #f3f4f6; margin: 0;">
            <div style="max-width: 550px; margin: 0 auto; background-color: #111827; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: 1px solid #1f2937; text-align: center;">
                <div style="margin-bottom: 25px;">
                    <img src="https://img.icons8.com/fluency/96/000000/rocket.png" width="60" height="60" alt="Logo" style="margin-bottom: 15px;" />
                    <h2 style="color: #a855f7; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">Carrer Coach Verification</h2>
                    <p style="color: #9ca3af; font-size: 13px; margin: 5px 0 0 0;">Enterprise GenAI Guidance Hub</p>
                </div>
                
                <hr style="border: 0; border-top: 1px solid #1f2937; margin: 25px 0;" />
                
                <div style="text-align: left; line-height: 1.6; font-size: 15px; color: #d1d5db;">
                    <p>Hello <strong style="color: #f3f4f6;">{username}</strong>,</p>
                    <p>Thank you for choosing <strong>Carrer Coach</strong>! To complete your registration and secure your profile, please verify your email address by entering the 6-digit code below in the signup screen:</p>
                </div>
                
                <div style="margin: 35px 0;">
                    <div style="display: inline-block; font-size: 36px; font-weight: 800; color: #ffffff; letter-spacing: 6px; background: linear-gradient(135deg, #a855f7, #6366f1); padding: 14px 28px; border-radius: 12px; box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4); text-align: center;">
                        {otp}
                    </div>
                </div>
                
                <p style="color: #9ca3af; font-size: 13px; margin-top: 25px;">This verification code is valid for <strong>10 minutes</strong>. If you did not register for an account, please disregard this email.</p>
                
                <hr style="border: 0; border-top: 1px solid #1f2937; margin: 25px 0;" />
                
                <p style="color: #6b7280; font-size: 11px; margin: 0;">This is an automated system notification. Please do not reply directly to this email.</p>
                <p style="color: #4b5563; font-size: 10px; margin: 5px 0 0 0;">Powered by Gemini & Career Advisor Security Layer</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # SMTP Handshake
        server = smtplib.SMTP(smtp_server, port, timeout=10)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_sender, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Verification email successfully sent to: {to_email}")
        return True, "Email sent successfully."
    except Exception as e:
        # Fallback in case of SMTP errors
        err_msg = str(e)
        fallback_msg = (
            f"\n\n"
            f"==========================================================\n"
            f"[SMTP ERROR: {err_msg}]\n"
            f"[FALLBACK OUT] OTP Verification Code Generated!\n"
            f"User: {username}\n"
            f"Email: {to_email}\n"
            f"Verification Code: {otp}\n"
            f"Note: SMTP failed, code is printed here for sandbox testing.\n"
            f"==========================================================\n"
        )
        logger.error(f"Failed to send verification email to {to_email}: {err_msg}")
        logger.warning(fallback_msg)
        print(fallback_msg, flush=True)
        return True, f"Failed to deliver email: {err_msg}. Code printed in terminal logs for demo usage."
