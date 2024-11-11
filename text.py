# text.py

class Greetings:
    @staticmethod
    def welcome_back(user_name):
        return (
            f"Welcome back, {user_name}! I have loaded your previous folder for context.\n\n"
            "You can specify any folder using /folder.\n"
            "/start - Display this introduction message.\n"
            "/status - Display your current settings.\n"
            "Send any message without a command to ask a question."
        )

    @staticmethod
    def first_time():
        return (
            "Welcome to the AI document assistant bot! This bot generates responses using documents "
            "in a specified folder or files you send directly in the chat. You can interact with the bot using the following commands:\n\n"
            "/start - Display this introduction message.\n"
            "/folder - Set the folder path where your documents are located.\n"
            "/status - Display your current settings.\n"
            "Send any message without a command to ask a question."
        )


class Status:
    @staticmethod
    def folder_set(user_name, folder_path, file_list):
        return (
            f"Status Information:\n\n"
            f"Dear {user_name},\n"
            f"The folder path is currently set to: {folder_path}\n\n"
            f"Valid Files:\n{file_list}\n\n"
        )

    @staticmethod
    def folder_no_files(user_name, folder_path):
        return (
            f"Status Information:\n\n"
            f"Dear {user_name},\n"
            f"The folder path is currently set to: {folder_path}, but no valid files were found.\n"
        )

    @staticmethod
    def upload_set(user_name, file_list):
        return (
            f"Status Information:\n\n"
            f"Dear {user_name},\n"
            f"Documents sent to the chat are used as context.\n\n"
            f"Valid Files:\n{file_list}\n\n"
        )

    @staticmethod
    def upload_no_files(user_name):
        return (
            f"Status Information:\n\n"
            f"Dear {user_name},\n"
            f"Documents sent to the chat are used as context, but no valid files were found.\n"
        )

    @staticmethod
    def no_context(user_name):
        return (
            f"Status Information:\n\n"
            f"Dear {user_name},\n"
            "No context has been set yet. You can set it using the /folder command or by sending documents directly to the chat.\n"
        )


class Responses:
    @staticmethod
    def request_access():
        return "Please provide the folder path for your documents:"

    @staticmethod
    def grant_access_success(user_id):
        return f"User {user_id} has been granted access."

    @staticmethod
    def grant_access_usage():
        return "Usage: /grant_access <user_id>"

    @staticmethod
    def access_denied():
        return "You do not have access, please use /request_access."

    @staticmethod
    def access_requested():
        return "Your access request has been sent to the admin."

    @staticmethod
    def unauthorized_action():
        return "You are not authorized to perform this action."

    @staticmethod
    def invalid_folder_path():
        return "Invalid folder path. Please provide a valid path."

    @staticmethod
    def no_valid_files():
        return "No valid files found in the folder. Please provide a folder containing valid documents."

    @staticmethod
    def documents_indexed():
        return "Documents successfully indexed."

    @staticmethod
    def indexing_error():
        return "An error occurred while loading and indexing your documents. Please try again later."

    @staticmethod
    def upload_success():
        return (
            "Your documents have been uploaded and indexed successfully. "
            "You may now ask any questions related to these documents."
        )

    @staticmethod
    def upload_partial_success():
        return (
            "You have selected different file types. Only the PDF files have been uploaded and indexed. "
            "You may now ask any questions related to these PDF documents."
        )

    @staticmethod
    def unsupported_files():
        return (
            "I'm sorry, but only PDF files are supported. Please upload your documents in PDF format."
        )

    @staticmethod
    def processing_error():
        return (
            "I'm sorry, but I couldn't process the files you sent. "
            "Please ensure they are in PDF format and try again."
        )

    @staticmethod
    def generic_error():
        return (
            "An unexpected error occurred while processing your files. Please try again later."
        )

    @staticmethod
    def no_files_received():
        return (
            "I'm sorry, but I didn't receive any files. Please attach your documents and try again."
        )

    @staticmethod
    def file_too_large():
        return "I'm sorry, but I couldn't process the file more than 20Mb. Please upload PDF files less than 20Mb."


class FileResponses:
    @staticmethod
    def file_not_found():
        return "File not found."

    @staticmethod
    def send_file_error():
        return "An error occurred while sending the file."

    @staticmethod
    def folder_not_set():
        return "Folder path not set."
