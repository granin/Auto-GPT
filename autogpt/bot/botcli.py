import os
from bot import run_bot
from input_capture import process_input
import datetime
def on_output_file_updated(content):
    print(f"File updated: {content}")
    return True

def get_user_input():
    return input("Please enter some text: ")

def on_exit():
    print("Stopped monitoring file.")

def get_file_mtime(filename):
    return os.stat(filename).st_mtime

def rename_old_session_files(file_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    new_file_name = f"{file_path}_session_{timestamp}.txt"
    os.rename(file_path, new_file_name)

def main():
    output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')
    input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

    # Rename old session files
    if os.path.exists(output_filename):
        rename_old_session_files(output_filename)
    if os.path.exists(input_filename):
        rename_old_session_files(input_filename)

    # Create new empty files for the new session
    open(output_filename, "w").close()
    open(input_filename, "w").close()

    run_bot(output_filename, input_filename, on_output_file_updated, get_user_input, process_input, on_exit)

if __name__ == "__main__":
    main()
