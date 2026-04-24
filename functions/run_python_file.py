import os
import subprocess
from google.genai import types


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a String Python file relative to the working directory and returns its output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Arguments to pass to the Python file",
            ),
        },
        required=["file_path"],
    ),
)


def run_python_file(working_directory, file_path, args=None):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        command = ["python", target_file_path]
        if os.path.commonpath([abs_working_dir, target_file_path]) != abs_working_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not target_file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        if args:
            command.extend(args)

        process = subprocess.run(
            command, cwd=abs_working_dir, capture_output=True, text=True, timeout=30
        )

        if process.returncode != 0:
            return f"Error: Process exited with code {process.returncode}."

        if not process.stdout and not process.stderr:
            return "No output produced"
        else:
            output = ""
            if process.stdout:
                output += f"STDOUT:\n{process.stdout}"
            if process.stderr:
                output += f"\nSTDERR:\n{process.stderr}"
            return output.strip()

    except Exception as e:
        return f"Error: executing Python file: {e}"
