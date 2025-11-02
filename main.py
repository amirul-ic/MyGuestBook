import os
from datetime import datetime

import pytz
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fasthtml.common import *

MAX_NAME_CHAR = 200
MAX_MESSAGE_CHAR = 200
TIMESTAMP_FMT = "%Y-%m-%d %I:%M:%S %p CET"

app,rt = fast_app()

# Initialize Supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def get_cet_time():
    cet_tz = pytz.timezone("Asia/Kuala_Lumpur")
    return datetime.now(cet_tz)


def add_message(name, message):
    timestamp = get_cet_time().strftime(TIMESTAMP_FMT)
    supabase.table("MyGuestBook").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()


def get_messages():
    # Sort by 'id' in descending order to get the latest entries first
    response = (supabase.table("MyGuestBook").select("*").order("id", desc=True).execute())
    return response.data


def render_message(entry):
    return (
        Article(
            Header(f"Name: {entry['name']}"),
            P(entry["message"]),
            Footer(Small(Em(f"Posted: {entry['timestamp']}"))),
        ),
    )

def render_message_list():
    messages = get_messages()
    return Div(
        *[render_message(entry) for entry in messages],
    id="message-list",
    )



def render_content():
    form = Form(
        Fieldset(
            Input(
                type="text",
                name="name",
                placeholder="Name",
                required=True,
                maxlength=MAX_NAME_CHAR,
            ),
            Input(
                type="text",
                name="message",
                placeholder="Message",
                required=True,
                maxlength=MAX_MESSAGE_CHAR,
            ),
            Button("Submit", type="submit"),
            role="group",
        ),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request="this.reset()",
    )

    return Div(
    P(Em("Write someting nice!")),
    form,
    Div(
        "Made with .. by ",
        A("Amirul", href = "https://youtube.com/", target="_blank"),
    ),
    Hr(),
    render_message_list(),
    )


@rt('/')
def get(): 
    return Titled("My Guestbook 📖", render_content())


@rt("/submit-message", methods=["POST"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()


serve()