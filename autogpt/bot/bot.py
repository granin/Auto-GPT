

# bot.py

import os
import time
import datetime

def get_file_mtime(filename):
    return os.stat(filename).st_mtime

def rename_old_session_files(file_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    new_file_name = f"{file_path}_session_{timestamp}.txt"
    os.rename(file_path, new_file_name)

def run_bot(output_filename, input_filename, on_output_file_updated, get_user_input, process_input, on_exit):
    last_mtime = None
    last_content = None
    user_input_expected = False

    while True:
        try:
            if os.path.exists(output_filename):
                current_mtime = get_file_mtime(output_filename)

                if last_mtime is None or current_mtime != last_mtime:
                    with open(output_filename, "r") as f:
                        content = f.read()
                        if content != last_content and content.strip() != "":
                            user_input_expected = on_output_file_updated(content)
                            last_content = content
                            last_mtime = current_mtime
                        else:
                            user_input_expected = False

                if user_input_expected:
                    try:
                        user_input = get_user_input()
                        if user_input.strip() == "":
                            break
                        processed_input = process_input(user_input)

                        with open(input_filename, "w") as input_file:
                            input_file.write(processed_input)

                        user_input_expected = False

                    except KeyboardInterrupt:
                        on_exit()
                        break

            else:
                last_mtime = None

            time.sleep(0.5)
        except KeyboardInterrupt:
            on_exit()
            break