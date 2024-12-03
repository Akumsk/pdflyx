# db_service.py
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict
import logging

from helpers import current_timestamp, get_language_name

load_dotenv()
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DatabaseService:
    def __init__(self):
        self.dbname = db_name
        self.user = db_user
        self.password = db_password
        self.host = db_host
        self.port = db_port

    def connect(self):
        conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )
        conn.autocommit = True
        return conn

    def save_metadata(self, metadata_list):
        try:
            connection = self.connect()
            cursor = connection.cursor()

            insert_query = """
                INSERT INTO documents_server (filename, path_file, document_type, date_modified, date_of_analysis, description, language, deleted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
                ON CONFLICT (path_file) DO UPDATE
                SET
                    filename = EXCLUDED.filename,
                    document_type = EXCLUDED.document_type,
                    date_modified = EXCLUDED.date_modified,
                    date_of_analysis = EXCLUDED.date_of_analysis,
                    description = EXCLUDED.description,
                    language = EXCLUDED.language,
                    deleted = FALSE
            """

            for item in metadata_list:
                # Convert date_modified from string to datetime object
                date_modified = datetime.strptime(
                    item["date_modified"], "%Y-%m-%d %H:%M:%S"
                )
                date_of_analysis = datetime.utcnow()  # Current timestamp for analysis time

                cursor.execute(
                    insert_query,
                    (
                        item["filename"],
                        item["path_file"],
                        item["document_type"],
                        date_modified,
                        date_of_analysis,
                        item["description"],
                        item["language"],  # New language parameter
                    ),
                )

            connection.commit()
            print("Metadata saved successfully.")

        except Exception as e:
            print(f"Error saving metadata: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def mark_files_as_deleted(self, existing_file_paths):
        try:
            connection = self.connect()
            cursor = connection.cursor()

            if existing_file_paths:
                # When there are existing files, mark files not in the list as deleted
                # Convert list to tuple
                existing_file_paths_tuple = tuple(existing_file_paths)
                # If there's only one element, make sure it's a tuple
                if len(existing_file_paths_tuple) == 1:
                    existing_file_paths_tuple = (existing_file_paths_tuple[0],)

                query = """
                    UPDATE documents_server
                    SET deleted = TRUE
                    WHERE path_file NOT IN %s AND deleted = FALSE
                """
                cursor.execute(query, (existing_file_paths_tuple,))
            else:
                # When there are no existing files, mark all files as deleted
                query = """
                    UPDATE documents_server
                    SET deleted = TRUE
                    WHERE deleted = FALSE
                """
                cursor.execute(query)

            connection.commit()
            print("Marked missing files as deleted.")

        except Exception as e:
            print(f"Error marking files as deleted: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def get_file_dates(self, path_file):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                SELECT date_modified, date_of_analysis FROM documents_server
                WHERE path_file = %s
            """
            cursor.execute(query, (path_file,))
            result = cursor.fetchone()
            if result:
                db_date_modified = result[0]  # date_modified from database
                date_of_analysis = result[1]  # date_of_analysis from database
                return db_date_modified, date_of_analysis
            else:
                return None, None
        except Exception as e:
            print(f"Error getting dates for file {path_file}: {e}")
            return None, None
        finally:
            cursor.close()
            connection.close()

    def get_all_file_paths(self):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                SELECT path_file FROM documents_server
                WHERE deleted = FALSE
            """
            cursor.execute(query)
            results = cursor.fetchall()
            file_paths = [row[0] for row in results]
            return file_paths
        except Exception as e:
            print(f"Error retrieving file paths: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def get_download_access(self, path_file):
        """
        Retrieves the download_access status for a given file.

        Args:
            path_file (str): The path of the file to check access for.

        Returns:
            bool: True if download is allowed, False otherwise.
        """
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                SELECT download_access FROM documents_server
                WHERE path_file = %s AND deleted = FALSE
            """
            cursor.execute(query, (path_file,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Assuming download_access is a boolean
            else:
                # If the file doesn't exist or is marked as deleted
                return False
        except Exception as e:
            print(f"Error checking download access for file {path_file}: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    def save_folder(self, user_id, user_name, folder):
        connection = None
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                INSERT INTO folders (user_id, user_name, folder)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (user_id, user_name, folder))

            connection.commit()
            print("Contex Folder Data SAVED!!!")

        except Exception as e:
            print(f"Error saving folder data: {e}")
            connection.rollback()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_last_folder(self, user_id):
        folder = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                SELECT folder FROM folders
                WHERE user_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                folder = result[0]

        except Exception as e:
            print(f"An error occurred while fetching folder: {e}")

        return folder

    def clear_user_folder(self, user_id):
        """Clears the last folder path for the user in the database."""
        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    query = "DELETE FROM folders WHERE user_id = %s;"
                    cursor.execute(query, (user_id,))
                connection.commit()
                print(f"Cleared folder entries for user {user_id}.")
        except Exception as e:
            print(f"Error clearing user folder in database: {e}")

    def save_event_log(
        self, user_id, event_type, user_message, system_response, conversation_id
    ):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                INSERT INTO event_log (user_id, event_type, user_message, system_response, conversation_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (user_id, event_type, user_message, system_response, conversation_id),
            )
            connection.commit()
            print("Event log saved successfully.")
        except Exception as e:
            print(f"Error saving event log: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def log_exception(
        self,
        exception_type,
        exception_message,
        stack_trace,
        occurred_at,
        user_id,
        data_context,
        resolved,
        resolved_at=None,
        resolver_notes=None,
    ):
        connection = None
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                    INSERT INTO exceptions (
                        exception_type,
                        exception_message,
                        stack_trace,
                        occurred_at,
                        user_id,
                        data_context,
                        resolved,
                        resolved_at,
                        resolver_notes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING exception_id;
                """
            cursor.execute(
                query,
                (
                    exception_type,
                    exception_message,
                    stack_trace,
                    occurred_at,
                    user_id,
                    data_context,
                    resolved,
                    resolved_at,
                    resolver_notes,
                ),
            )
            exception_id = cursor.fetchone()[0]
            connection.commit()
            print(f"Exception logged with exception_id: {exception_id}")
            return exception_id  # Return the generated exception_id if needed
        except Exception as e:
            print(f"Failed to log exception: {e}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def save_message(self, conversation_id, sender_type, user_id, message_text):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                INSERT INTO messages (conversation_id, sender_type, user_id, message_text)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (conversation_id, sender_type, user_id, message_text))
            connection.commit()
            print("Message saved successfully")

        except Exception as e:
            print(f"Error saving message: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def get_chat_history(self, dialog_numbers, user_id):
        connection = None
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor()

            # Step 1: Get the last 'dialog_numbers' conversation_ids for the user
            query_conversation_ids = """
                SELECT conversation_id, MAX(timestamp) as last_datetime
                FROM messages
                WHERE user_id = %s AND sender_type = 'user'
                GROUP BY conversation_id
                ORDER BY last_datetime DESC
                LIMIT %s
            """

            cursor.execute(query_conversation_ids, (user_id, dialog_numbers))
            conversation_data = cursor.fetchall()
            conversation_ids = [str(row[0]) for row in conversation_data]

            if not conversation_ids:
                return []

            # Step 2: Fetch messages for these conversation_ids, ordered by datetime
            query_messages = """
                SELECT conversation_id, sender_type, message_text, timestamp as datetime
                FROM messages
                WHERE conversation_id = ANY(%s::uuid[])
                ORDER BY conversation_id, datetime ASC
            """
            cursor.execute(query_messages, (conversation_ids,))
            messages = cursor.fetchall()

            conversations = defaultdict(list)
            for conversation_id, sender_type, message_text, datetime in messages:
                conversations[str(conversation_id)].append((sender_type, message_text))

            # Step 3: Construct the chat history
            chat_history = []
            # Maintain the order of conversation_ids as per their datetime descending
            for conversation_id in conversation_ids:
                conversation = conversations.get(conversation_id, [])
                for sender_type, message_text in conversation:
                    if sender_type == "user":
                        chat_history.append(f"HumanMessage: {message_text}")
                    elif sender_type == "bot":
                        chat_history.append(f"AIMessage: {message_text}")

            return chat_history

        except Exception as e:
            # Handle exceptions
            print(f"An error occurred: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    ##User Functions
    def check_user_access(self, user_id):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT access FROM users WHERE user_id = %s AND is_active = True",
                (user_id,),
            )
            result = cursor.fetchone()
            if result:
                return result[0]  # True or False
            else:
                return False
        except Exception as e:
            print(f"Error checking user access: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    def save_user_info(self, user_id, user_name, language_code):
        """
        Saves or updates user information in the users table.
        On first insertion, sets language_name based on the provided language_code.
        If language_code is unsupported, defaults language_name to 'English'.
        """
        try:
            language_name = get_language_name(language_code)
        except Exception as e:
            language_name = "English"
            logger.exception(
                f"Unsupported language code '{language_code}'. "
                f"Defaulting language name to '{language_name}'."
            )

        now = current_timestamp()
        is_active = True
        access = True
        role = 'user'

        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (
                    user_id, 
                    user_name, 
                    language_code, 
                    current_language, 
                    date_joined, 
                    last_active, 
                    is_active, 
                    access, 
                    role
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET 
                    user_name = EXCLUDED.user_name,
                    language_code = EXCLUDED.language_code,
                    last_active = EXCLUDED.last_active
                """,
                (
                    user_id,
                    user_name,
                    language_code,
                    language_name,  # Correctly maps to language_name
                    now,
                    now,
                    is_active,
                    access,
                    role
                ),
            )
            connection.commit()
            logger.info(
                "User info saved/updated successfully.",
                extra={
                    "user_id": user_id,
                    "user_name": user_name,
                    "language_code": language_code,
                    "current_language": language_name,
                    "date_joined": now,
                    "last_active": now,
                    "is_active": is_active,
                    "access": access,
                    "role": role
                }
            )
        except Exception as e:
            logger.error(f"Error saving user info for user_id {user_id}: {e}")
            connection.rollback()
            raise e  # Re-raise exception if necessary
        finally:
            cursor.close()
            connection.close()

    def get_user_info(self, user_id):
        """
        Retrieves user information from the users table.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            dict or None: A dictionary containing user information or None if user does not exist.
        """
        connection = None
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                SELECT user_id, user_name, language_code, current_language, date_joined, last_active, is_active, access, role
                FROM users
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                return {
                    "user_id": result[0],
                    "user_name": result[1],
                    "language_code": result[2],
                    "current_language": result[3],
                    "date_joined": result[4],
                    "last_active": result[5],
                    "is_active": result[6],
                    "access": result[7],
                    "role": result[8],
                }
            else:
                return None
        except Exception as e:
            print(f"Error retrieving user info for user {user_id}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def update_last_active(self, user_id):
        now = datetime.utcnow()
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET last_active = %s WHERE user_id = %s", (now, user_id)
            )
            print("User last_active updated.")
        except Exception as e:
            print(f"Error updating last_active: {e}")
            self.conn.rollback()
        finally:
            cursor.close()
            connection.close()

    def update_current_language(self, user_id, current_language):
        """
        Updates the current_language for a given user in the users table.

        Args:
            user_id (str): The unique identifier of the user.
            current_language (str): The language code to set as the current language.
        """
        connection = None
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                UPDATE users
                SET current_language = %s
                WHERE user_id = %s
            """
            cursor.execute(query, (current_language, user_id))
            connection.commit()
            print(f"Updated current_language for user {user_id} to {current_language}.")
        except Exception as e:
            print(f"Error updating current_language for user {user_id}: {e}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_current_language(self, user_id):
        """
        Retrieves the current_language for a given user from the users table.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            str or None: The current language of the user or None if not set.
        """
        connection = None
        cursor = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = """
                SELECT current_language FROM users
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            print(f"Error retrieving current_language for user {user_id}: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def grant_access(self, user_id):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET access = True WHERE user_id = %s", (user_id,)
            )
            print(f"Access granted to user {user_id}.")
        except Exception as e:
            print(f"Error granting access: {e}")
            self.conn.rollback()
        finally:
            cursor.close()
            connection.close()

    def close(self):
        self.conn.close()
