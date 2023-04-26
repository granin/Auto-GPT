
import os
from bot import run_bot
from input_processing import process_input

def on_output_file_updated(content):
    print(f"File updated: {content}")
    return True

def get_user_input():
    return input("Please enter some text: ")

def on_exit():
    print("Stopped monitoring file.")

def main():
    output_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')
    input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

    run_bot(output_filename, input_filename, on_output_file_updated, get_user_input, process_input, on_exit)

if __name__ == "__main__":
    main()