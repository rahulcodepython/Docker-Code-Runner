import docker
import os
import io
import tarfile
import subprocess


def create_code_file():
    code = """
def function_to_test(x):
    return x * 2    
val = int(input())
print(function_to_test(val))
"""

    with open("code.py", "w") as file:
        file.write(code)


def copy_file_to_container(container, src_path, dest_path):
    # Create a tar stream of the file
    tar_stream = io.BytesIO()

    # Create a tar file
    with tarfile.open(fileobj=tar_stream, mode='w') as tar:
        tar.add(src_path, arcname=os.path.basename(dest_path)) # Add the file to the tar file

    tar_stream.seek(0) # Reset the stream to the beginning

    # Copy the tar stream to the container
    container.put_archive(os.path.dirname(dest_path), tar_stream)


def run_main_script(input_value):
    # Command to execute main.py with input_value
    command = ['python', 'code.py']

    # Using subprocess to run the command and capture output
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)

    # Run the command with the input_value
    stdout, _ = process.communicate(input=input_value)

    # Return the output
    return stdout.strip()


def run_code_in_container(inputs: list):
    client = docker.from_env()
    results: dict = {}

    # Create a temporary container from the Dockerfile
    container = client.containers.run("python-test", detach=True)

    # Copy the code.py file to the container
    copy_file_to_container(container, "code.py", "/app/code.py")

    for index, value in enumerate(inputs):
        # Run the main script with the input value
        output = run_main_script(str(value))
        results[index] = output

    # Stop and remove the container
    container.stop()
    container.remove()

    return results


if __name__ == "__main__":
    create_code_file()
    test_cases = [1, 2, 3]
    result_output = run_code_in_container(test_cases)
    print(result_output)
