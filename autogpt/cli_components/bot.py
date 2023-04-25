import os
import time
from input_processing import process_input

def get_file_mtime(filename):
    return os.stat(filename).st_mtime

def main():
    # Get the absolute path of the Assistant_Reply.txt file
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Assistant_Reply.txt')

    # Get the absolute path of the file you want to write the processed input to
    input_filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'Processed_Input.txt')

    last_mtime = None
    last_line_number = 0

    while True:
        try:
            if os.path.exists(filename):
                current_mtime = get_file_mtime(filename)

                if last_mtime is None or current_mtime != last_mtime:
                    with open(filename, "r") as f:
                        content = f.readlines()

                        if len(content) > last_line_number:
                            new_content = content[last_line_number:]
                            print(f"New content: {''.join(new_content)}")
                            last_line_number = len(content)
                            last_mtime = current_mtime

                            try:
                                user_input = input("Please enter some text: ")
                                processed_input = process_input(user_input)

                                # Write processed_input to the input_filename
                                with open(input_filename, "w") as input_file:
                                    input_file.write(processed_input)

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
