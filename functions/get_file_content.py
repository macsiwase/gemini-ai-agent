import os
from config import MAX_CHARS
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of a specified file relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to read, relative to the working directory",
            ),
        },
        required=["file_path"],
    ),
)


def get_file_content(working_directory, file_path):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        if os.path.commonpath([abs_working_dir, target_file_path]) != abs_working_dir:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_file_path, "r") as f:
            file_content_string = f.read(MAX_CHARS)

            if f.read(1):
                file_content_string += (
                    f' [...File "{file_path}" truncated at {MAX_CHARS} characters]'
                )

        return file_content_string
    except Exception as e:
        return f"Error reading file: {str(e)}"
