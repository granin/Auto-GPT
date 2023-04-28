


# capture_utils.py
from typing import List
from telegram import Update
import os

_capture_buffer: List[str] = []
def check_file_for_y(file_path):
    try:
        with open(file_path, "r") as f:
            content = f.read().strip().lower()
            if content in ["y", "n"]:
                return content
    except FileNotFoundError:
        pass
    return None


def delete_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass

def save_and_print_user_input(user_input):
    input_filename = "/Users/m/git/1ai/Auto-GPT/Processed_Input.txt"
    with open(input_filename, "w") as f:
        f.write(user_input)
    print(f"User input saved: {user_input}")

async def get_human_feedback(update: Update, context) -> None:
    """Get human feedback."""
    user_input = update.message.text
    save_and_print_user_input(user_input)
def pretty_print_nested_dict(nested_dict):
    output = []
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            value_str = pretty_print_nested_dict(value)
        else:
            value_str = str(value)
        output.append(f"{key}: {value_str}")
    return "\n".join(output)

def capture_content(title, content, update: Update = None, file_path: str = None):
    if content:
        if isinstance(content, list):
            content = " ".join(content)
        elif isinstance(content, dict):
            content = pretty_print_nested_dict(content)
    else:
        content = ""
    _capture_buffer.append(content)

    # send the content immediately
    # if update:
    #     send_captured_content(update)

    # save the content to a file
    if file_path:
        write_captured_content_to_file(file_path)

def write_captured_content_to_file(file_path):
    content = "\n".join(_capture_buffer)
    with open(file_path, "w") as f:
        f.write(content)
