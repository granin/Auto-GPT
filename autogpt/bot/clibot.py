


# Auto-GPT/autogpt/cli_components/bot.py
import os
import time
import datetime
from input_processing import process_input

def get_file_mtime(filename):
    return os.stat(filename).st_mtime

def rename_old_session_files(file_path):
    # Add timestamp to the old session filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    new_file_name = f"{file_path}_session_{timestamp}.txt"
    os.rename(file_path, new_file_name)

def main():
    # Get the absolute path of the Assistant_Reply.txt file
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')

    # Get the absolute path of the file you want to write the processed input to
    input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

    # Rename old session files
    if os.path.exists(filename):
        rename_old_session_files(filename)
    if os.path.exists(input_filename):
        rename_old_session_files(input_filename)

    # Create new empty files for the new session
    open(filename, "w").close()
    open(input_filename, "w").close()

    last_mtime = None
    last_content = None
    user_input_expected = False

    while True:
        try:
            if os.path.exists(filename):
                current_mtime = get_file_mtime(filename)

                if last_mtime is None or current_mtime != last_mtime:
                    with open(filename, "r") as f:
                        content = f.read()
                        if content != last_content and content.strip() != "":
                            print(f"File updated: {content}")
                            last_content = content
                            last_mtime = current_mtime
                            user_input_expected = True
                        else:
                            user_input_expected = False

                if user_input_expected:
                    try:
                        user_input = input("Please enter some text: ")
                        if user_input.strip() == "":
                            break
                        processed_input = process_input(user_input)

                        # Write processed_input to the input_filename
                        with open(input_filename, "w") as input_file:
                            input_file.write(processed_input)

                        user_input_expected = False

                    except KeyboardInterrupt:
                        print("Stopping input capture.")
                        break

            else:
                last_mtime = None

            time.sleep(0.5)
        except KeyboardInterrupt:
            print("Stopped monitoring file.")
            break

if __name__ == "__main__":
    main()
