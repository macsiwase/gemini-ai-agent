import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
        required=["directory"],
    ),
)


def get_files_info(working_directory, directory="."):
    try:
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_working_dir, directory))
        valid_target_dir = (
            os.path.commonpath([abs_working_dir, target_dir]) == abs_working_dir
        )

        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        dir_contents = []

        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            filesize = os.path.getsize(item_path)
            is_dir = os.path.isdir(item_path)
            dir_contents.append(
                f"- {item}: file_size={filesize} bytes, is_dir={is_dir}"
            )

        return "\n".join(dir_contents)

    except Exception as e:
        return f"Error listing files: {e}"
