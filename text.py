# text.py


class Greetings:

    @staticmethod
    def welcome_back(user_name):
        return (
            f"Welcome back, {user_name}! 👋\n\n"
            "I'm here to help you with your construction and design questions. Here's what we can do together:\n\n"
            "📚 Browse our /knowledge_base of construction regulations\n"
            "📎 Upload any PDF document and ask me questions about it\n\n"
            "Quick commands at your service:\n"
            "🔄 /start - See this welcome message again\n"
            "⚙️ /status - Check your current settings\n"
            "🗑️ /clear_context - Start fresh by clearing your document history\n\n"
            "What would you like to explore today?"
        )

    @staticmethod
    def first_time():
        return (
            "👋 **Hello! I'm your design assistant**\n\n"
            "I'm here to help architects, designers, and engineers navigate construction regulations "
            "and technical documentation.\n\n"
            "Here's how I can assist you:\n\n"
            "📚 Access construction regulations through our /knowledge_base\n"
            "📎 Share any PDF document, and I'll help you understand its contents\n"
            "❓ Ask questions in plain language - I'll handle the technical details\n\n"
            "Helpful commands to get started:\n"
            "🔄 /start - See this introduction again\n"
            "⚙️ /status - View your current settings\n"
            "🗑️ /clear_context - Reset your document history\n\n"
            "What would you like to know about?"
        )


class Status:
    @staticmethod
    def knowledge_base_set(user_name, knowledge_base_name, file_list, empty_list=None):
        response = (
            f"📊 <b>Current Status</b>\n\n"
            f"Hi {user_name}! Here's your workspace setup:\n\n"
            f"📚 <b>Active Knowledge Base:</b> {knowledge_base_name}\n\n"
            f"📋 <b>Available Documents:</b>\n{file_list}\n\n"
        )
        if empty_list:
            empty_files = "\n".join(empty_list)
            response += (
                f"⚠️ <b>Attention Needed</b>\n"
                f"The following documents need your attention:\n{empty_files}\n\n"
                f"💡 Tip: Make sure these files are in PDF format and properly readable. "
                f"Feel free to upload them again!"
            )
        return response

    @staticmethod
    def knowledge_base_no_files(user_name, knowledge_base_name):
        return (
            f"📊 <b>Knowledge Base Status</b>\n\n"
            f"Hi {user_name}!\n\n"
            f"You're currently working with the '<i>{knowledge_base_name}</i>' knowledge base, "
            f"but I don't see any valid documents yet.\n\n"
            f"💡 Need help? Try:\n"
            f"• Selecting a different knowledge base\n"
            f"• Uploading your own documents\n"
            f"• Checking file formats (PDF recommended)"
        )

    @staticmethod
    def no_knowledge_base_selected(user_name):
        return (
            f"📊 <b>Workspace Status</b>\n\n"
            f"Hi {user_name}!\n\n"
            f"Looks like we haven't selected a knowledge base yet.\n\n"
            f"💡 Quick Start:\n"
            f"1. Use /knowledge_base to explore available topics\n"
            f"2. Select the area that matches your needs\n"
            f"3. Start asking questions!\n\n"
            f"Need something specific? Just let me know! 👋"
        )

    @staticmethod
    def upload_set(user_name, file_list, empty_list=None):
        response = (
            f"📊 <b>Document Status</b>\n\n"
            f"Hi {user_name}!\n\n"
            f"I'm working with your uploaded documents:\n\n"
            f"📋 <b>Active Documents:</b>\n{file_list}\n\n"
        )
        if empty_list:
            empty_files = "\n".join(empty_list)
            response += (
                f"⚠️ <b>Document Issues Detected</b>\n"
                f"These files need attention:\n{empty_files}\n\n"
                f"💡 Quick Fix Tips:\n"
                f"• Check if files are in PDF format\n"
                f"• Ensure files aren't password-protected\n"
                f"• Try re-uploading the document\n\n"
                f"Need help? Just ask! 🤝"
            )
        return response

    @staticmethod
    def upload_no_files(user_name):
        return (
            f"📊 <b>Document Status</b>\n\n"
            f"Hi {user_name}!\n\n"
            f"I'm ready to work with your documents, but I don't see any valid files yet.\n\n"
            f"💡 You can:\n"
            f"• Upload PDF documents directly to our chat\n"
            f"• Use /knowledge_base to access standard regulations\n"
            f"• Ask me questions about any construction topic\n\n"
            f"Need guidance? I'm here to help! 🤝"
        )

    @staticmethod
    def no_context(user_name):
        return (
            f"📊 <b>Workspace Status</b>\n\n"
            f"Hi {user_name}!\n\n"
            f"Your workspace is ready, but we haven't loaded any documents yet.\n\n"
            f"💡 Let's get started:\n"
            f"1. Upload PDF documents directly to our chat, or\n"
            f"2. Use /knowledge_base to access construction regulations\n\n"
            f"Which would you prefer to explore first? 🤔"
        )


class Responses:
    @staticmethod
    def request_access():
        return "📂 To get started, please share the folder path where your documents are stored:"

    @staticmethod
    def grant_access_success(user_id):
        return (
            f"✅ Access granted to user {user_id}! They can now use all bot features."
        )

    @staticmethod
    def grant_access_usage():
        return "ℹ️ To grant access, use: /grant_access <user_id>"

    @staticmethod
    def access_denied():
        return (
            "🔒 Access needed!\n\n"
            "To start using the bot, please use /request_access to get permission.\n"
            "An admin will review your request shortly."
        )

    @staticmethod
    def access_requested():
        return (
            "📫 Access Request Sent!\n\n"
            "Your request has been forwarded to our admin team.\n"
            "You'll receive a notification once access is granted."
        )

    @staticmethod
    def unauthorized_action():
        return (
            "🔒 Authorization Required\n\n"
            "You'll need additional permissions for this action.\n"
            "Please contact your administrator for assistance."
        )

    @staticmethod
    def invalid_folder_path():
        return (
            "⚠️ Folder Path Issue\n\n"
            "I couldn't find the folder you specified.\n"
            "Please check the path and try again.\n\n"
            "💡 Tip: Make sure the path is complete and correctly formatted."
        )

    @staticmethod
    def no_valid_files():
        return (
            "📂 No Valid Documents Found\n\n"
            "I couldn't find any documents to work with in that folder.\n"
            "Please ensure the folder contains PDF, DOCX, or XLSX files."
        )

    @staticmethod
    def documents_indexed():
        return (
            "✅ Success!\n\n"
            "All documents have been indexed and are ready for your questions.\n"
            "What would you like to know about them?"
        )

    @staticmethod
    def folder_is_set(folder_path, empty_list=None):
        response = (
            f"📁 **Folder Successfully Connected!**\n\n"
            f"📍 Location: {folder_path}\n\n"
            f"✅ Your documents are ready for queries!\n"
        )
        if empty_list:
            empty_files = "\n".join(empty_list)
            response += (
                f"\n⚠️ Some files need attention:\n{empty_files}\n\n"
                f"💡 Tips:\n"
                f"• Ensure files are in PDF format\n"
                f"• Check for password protection\n"
                f"• Try re-uploading if necessary\n"
            )
        else:
            response += "\n🎉 Perfect! All files are properly indexed and ready to use."
        return response

    @staticmethod
    def indexing_error():
        return (
            "⚠️ Oops! Something went wrong while preparing your documents.\n"
            "Please try again in a few moments."
        )

    @staticmethod
    def upload_success():
        return (
            "✅ Upload Complete!\n\n"
            "Your documents are successfully indexed and ready to use.\n"
            "What would you like to know about them? 🤔"
        )

    @staticmethod
    def upload_partial_success():
        return (
            "📄 Partial Upload Complete\n\n"
            "I've indexed all PDF files you've sent.\n\n"
            "💡 Note: Only PDF files are supported. Other file types were skipped.\n\n"
            "Ready for your questions about the PDF documents! 🤓"
        )

    @staticmethod
    def unsupported_files():
        return (
            "⚠️ Unsupported File Type\n\n"
            "I can only work with PDF files at the moment.\n\n"
            "💡 Please convert your documents to PDF format and try again."
        )

    @staticmethod
    def processing_error():
        return (
            "⚠️ Processing Issue\n\n"
            "I couldn't read your files properly.\n\n"
            "💡 Please check:\n"
            "• Files are in PDF format\n"
            "• PDFs aren't password-protected\n"
            "• Files aren't corrupted"
        )

    @staticmethod
    def generic_error():
        return (
            "⚠️ Unexpected Issue\n\n"
            "Something went wrong while processing your request.\n\n"
            "💡 Please try:\n"
            "• Waiting a moment\n"
            "• Trying again\n"
            "• Contacting support if the issue persists"
        )

    @staticmethod
    def no_files_received():
        return (
            "📎 No Files Found\n\n"
            "I haven't received any files with your message.\n\n"
            "💡 To share documents:\n"
            "• Click the attachment icon\n"
            "• Select your PDF files\n"
            "• Send them in the chat"
        )

    @staticmethod
    def file_too_large():
        return (
            "⚠️ File Size Limit Exceeded\n\n"
            "Files must be under 20MB to process.\n\n"
            "💡 Try:\n"
            "• Compressing the PDF\n"
            "• Splitting into smaller files\n"
            "• Removing unnecessary pages"
        )

    @staticmethod
    def context_cleared():
        return (
            "🗑️ Your workspace has been reset.\n\n"
            "You can now select a new knowledge base using /knowledge_base or upload new documents.\n\n"
            "What would you like to do next?"
        )

    @staticmethod
    def unknown_command():
        return (
            "❓ I'm not sure what you mean.\n\n"
            "💡 You can try:\n"
            "• Using /help to see available commands\n"
            "• Asking me a question about construction or design\n"
            "• Uploading a document for me to analyze"
        )


class KnowledgeBaseResponses:
    @staticmethod
    def unknown_knowledge_base():
        return (
            "📂 Empty Knowledge Base\n\n"
            "The selected knowledge base appears to be empty or contains no readable files.\n\n"
            "💡 You can:\n"
            "• Select a different knowledge base\n"
            "• Upload your own documents\n"
            "• Contact support if you believe this is an error\n\n"
            "Need help? Just ask! 🤝"
        )

    @staticmethod
    def no_valid_files_in_knowledge_base():
        return (
            "📂 Empty Knowledge Base\n\n"
            "The selected knowledge base appears to be empty or contains no readable files.\n\n"
            "💡 You can:\n"
            "• Select a different knowledge base\n"
            "• Upload your own documents\n"
            "• Contact support if you believe this is an error\n\n"
            "Need help? Just ask! 🤝"
        )

    @staticmethod
    def indexing_error():
        return (
            "⚠️ Oops! Something went wrong while preparing the knowledge base documents.\n"
            "Please try again in a few moments."
        )

    @staticmethod
    def knowledge_base_set_success(knowledge_base_name):
        return (
            f"✅ Knowledge Base Connected!\n\n"
            f"📚 Now using: {knowledge_base_name}\n\n"
            f"💡 You can:\n"
            f"• Ask questions about regulations\n"
            f"• Request specific information\n"
            f"• Search for standards\n\n"
            f"What would you like to know about? 🤔"
        )

    @staticmethod
    def unknown_command():
        return (
            "❓ I'm not sure what you mean.\n\n"
            "💡 You can try:\n"
            "• Using /help to see available commands\n"
            "• Asking me a question about construction or design\n"
            "• Uploading a document for me to analyze"
        )

    @staticmethod
    def select_knowledge_base():
        return (
            "Please choose a knowledge base to explore:"
        )


class FileResponses:
    @staticmethod
    def file_not_found():
        return (
            "🔍 File Not Found\n\n"
            "I couldn't locate the file you're looking for.\n\n"
            "💡 Common solutions:\n"
            "• Check if the file name is correct\n"
            "• Verify the file hasn't been moved or deleted\n"
            "• Try uploading the file again\n"
            "• Use /status to see your available files\n\n"
            "Need help finding something specific? Let me know! 🤝"
        )

    @staticmethod
    def send_file_error():
        return (
            "⚠️ File Sharing Issue\n\n"
            "I encountered a problem while trying to send the file.\n\n"
            "💡 Please try:\n"
            "• Waiting a moment and requesting again\n"
            "• Checking if the file isn't too large (max 20MB)\n"
            "• Verifying file permissions\n\n"
            "Still having trouble? I can help you find an alternative solution! 🔧"
        )

    @staticmethod
    def folder_not_set():
        return (
            "Oops! It looks like we haven't set up your documents yet.\n"
            "Please select a knowledge base using /knowledge_base or upload some files."
        )

class ContextErrors:
    @staticmethod
    def documents_not_indexed():
        return (
            "📚 Let's Get Started!\n\n"
            "It seems we haven't set up any documents yet.\n"
            "Please use /knowledge_base to choose a topic or upload some files to get started."
        )

    @staticmethod
    def no_valid_documents():
        return (
            "📂 No Documents Found\n\n"
            "I couldn't find any documents to work with.\n"
            "Please make sure you've added some files to your folder or upload them here."
        )
