import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import pickle

# Load OAuth credentials from secrets
CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"]
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [st.secrets["redirect_uri"]],
            }
        },
        scopes=SCOPES,
        redirect_uri=st.secrets["redirect_uri"]
    )

def main():
    st.title("Upload file to Google Drive")

    if "credentials" not in st.session_state:
        st.session_state.credentials = None

    if not st.session_state.credentials:
        flow = get_flow()
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"[Authenticate with Google]({auth_url})")
        code = st.text_input("Enter the code from Google")

        if code:
            flow.fetch_token(code=code)
            st.session_state.credentials = flow.credentials

    if st.session_state.credentials:
        drive_service = build('drive', 'v3', credentials=st.session_state.credentials)
        uploaded_file = st.file_uploader("Choose a file to upload")
        if uploaded_file is not None:
            with open(uploaded_file.name, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            file_metadata = {'name': uploaded_file.name, 'parents': [st.secrets["drive_folder_id"]]}
            media = MediaFileUpload(uploaded_file.name, resumable=True)
            drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            st.success(f"File {uploaded_file.name} uploaded successfully!")

if __name__ == "__main__":
    main()
