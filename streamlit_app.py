import streamlit as st
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# Show title and description
st.title("✨ Poetic Email Composer")
st.write(
    "This app helps you compose beautiful, poetic emails and sends them to recipients with @bhavyabgada.dev domain. "
    "The emails are crafted using OpenAI's GPT-3.5 model to ensure they're both professional and poetic."
)

# Load credentials from secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]
email_sender = st.secrets["EMAIL_SENDER"]
email_password = st.secrets["EMAIL_PASSWORD"]
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")


def is_valid_email(email):
    """Validate email format and domain"""
    pattern = r'^[a-zA-Z0-9._%+-]+@bhavyabgada\.dev$'
    return bool(re.match(pattern, email))

def generate_poetic_email(subject, content):
    """Generate a poetic version of the email using OpenAI"""
    client = OpenAI(api_key=openai_api_key)
    prompt = f"""
    Transform this email into a poetic yet professional message.
    Keep the core message but make it more elegant and artistic.
    
    Subject: {subject}
    Content: {content}
    
    Make sure to:
    1. Keep it professional
    2. Maintain the original message
    3. Add poetic elements
    4. Structure it beautifully
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    
    return response.choices[0].message.content

def send_email(to_email, subject, body):
    """Send email using SMTP"""
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False

# Create the email form
with st.form("email_form"):
    recipient_email = st.text_input("Recipient Email (@bhavyabgada.dev only)")
    email_subject = st.text_input("Subject")
    email_content = st.text_area("Your Message")
    
    # Add a preview button and a send button
    col1, col2 = st.columns(2)
    preview_button = col1.form_submit_button("Preview Poetic Version")
    send_button = col2.form_submit_button("Send Email")

# Handle form submission
if preview_button and email_content:
    if not is_valid_email(recipient_email):
        st.error("Please enter a valid @bhavyabgada.dev email address.")
    else:
        with st.spinner("Generating poetic version..."):
            poetic_content = generate_poetic_email(email_subject, email_content)
            st.subheader("Preview of Your Poetic Email:")
            st.write("**Subject:**", email_subject)
            st.write("**Content:**")
            st.write(poetic_content)
            
            # Store the poetic version in session state
            st.session_state.poetic_content = poetic_content

if send_button:
    if not is_valid_email(recipient_email):
        st.error("Please enter a valid @bhavyabgada.dev email address.")
    elif not email_subject or not email_content:
        st.error("Please fill in all fields.")
    else:
        # Use the poetic version if it exists, otherwise generate it
        if 'poetic_content' not in st.session_state:
            with st.spinner("Generating poetic version..."):
                poetic_content = generate_poetic_email(email_subject, email_content)
        else:
            poetic_content = st.session_state.poetic_content
            
        with st.spinner("Sending email..."):
            if send_email(recipient_email, email_subject, poetic_content):
                st.success("Email sent successfully! ✨")
                # Clear the session state
                if 'poetic_content' in st.session_state:
                    del st.session_state.poetic_content
