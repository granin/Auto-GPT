

# /Users/m/git/1ai/Auto-GPT/autogpt/cli_components/capture_utils.py
import json
from typing import List
from telegram import Update

_capture_buffer: List[str] = []

def pretty_print_nested_dict(nested_dict):
    output = []
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            value_str = pretty_print_nested_dict(value)
        else:
            value_str = str(value)
        output.append(f"{key}: {value_str}")
    return "\n".join(output)

def capture_content(title, content, update: Update = None):
    if content:
        if isinstance(content, list):
            content = " ".join(content)
        elif isinstance(content, dict):
            content = pretty_print_nested_dict(content)
    else:
        content = ""
    _capture_buffer.append(content)

    # Add this block to send the content immediately
    if update:
        send_captured_content(update)

def write_captured_content_to_file(file_path):
    content_list = []

    for item in _capture_buffer:
        try:
            data = json.loads(item)
            if "embeddings" in data:
                del data["embeddings"]
            content_list.append(pretty_print_nested_dict(data))
        except json.JSONDecodeError:
            content_list.append(item)

    content = "\n".join(content_list)

    with open(file_path, "w") as f:
        f.write(content)
#
# from typing import List
# from telegram import Update
#
# _capture_buffer: List[str] = []
#
# def pretty_print_nested_dict(nested_dict):
#     output = []
#     for key, value in nested_dict.items():
#         if isinstance(value, dict):
#             value_str = pretty_print_nested_dict(value)
#         else:
#             value_str = str(value)
#         output.append(f"{key}: {value_str}")
#     return "\n".join(output)
#
# def capture_content(title, content, update: Update = None):
#     if content:
#         if isinstance(content, list):
#             content = " ".join(content)
#         elif isinstance(content, dict):
#             content = pretty_print_nested_dict(content)
#     else:
#         content = ""
#     _capture_buffer.append(content)
#
#     # Add this block to send the content immediately
#     if update:
#         send_captured_content(update)
#
# def write_captured_content_to_file(file_path):
#     content = "\n".join(_capture_buffer)
#     with open(file_path, "w") as f:
#         f.write(content)
