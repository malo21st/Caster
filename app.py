import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
import tweepy
from io import BytesIO, BufferedReader
from PIL import Image

consumer_key    = st.secrets["API_KEY"]
consumer_secret = st.secrets["API_SECRET"]
access_token    = st.secrets["ACCESS_TOKEN"]
access_token_secret = st.secrets["ACCESS_TOKEN_SECRET"]

## create Client
# def ClientInfo():
#     client = tweepy.Client(bearer_token    = st.secrets["BEARER_TOKEN"],
#                            consumer_key    = st.secrets["API_KEY"],
#                            consumer_secret = st.secrets["API_SECRET"],
#                            access_token    = st.secrets["ACCESS_TOKEN"],
#                            access_token_secret = st.secrets["ACCESS_TOKEN_SECRET"],
#                           )
#     return client
# client = ClientInfo()

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth)

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

@st.cache()
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
df = pd.DataFrame(rows, columns=["title", "text", "tag"])
df_index = df.index

# Print results.
st.title("Caster - tweet so easy -")
picture_data = st.file_uploader("Choose a picture", type=['png', 'jpg', 'jpeg'])
if picture_data:
    st.image(picture_data)
    # Save image in-memory
#     im = Image.open(picture_data)
#     b = BytesIO()
#     im.save(b, "PNG")
#     b.seek(0)
#     fp = BufferedReader(b)
    
st.dataframe(df)

msg_idx = st.radio("Select message.", df_index, horizontal=True)
init_msg = f"{df.loc[msg_idx, 'title']}\n{df.loc[msg_idx, 'text']}\n{df.loc[msg_idx, 'tag']}"
message = st.text_area("edit message.", value=init_msg) #, height=100)

if st.button('Cast tweet'):
#      client.create_tweet(text=message)
    api.update_status_with_media(status = message, filename = picture_data)
#     # Upload media to Twitter APIv1.1
#     ret = api.media_upload(filename="dummy", file=fp)

#     # Attach media to tweet
#     api.update_status(media_ids=[ret.media_id_string], status=message)
