# text.py

from telegram import BotCommand
import logging

class CommandDescriptions:
    """
    Contains translations for command descriptions.
    """

    @staticmethod
    def get_commands(language="English"):
        """
        Returns a list of BotCommand instances with descriptions in the specified language.
        """
        descriptions = {
            "English": {
                "start": "Display introduction message",
                "knowledge_base": "Select a knowledge base",
                "status": "Display current status and information",
                "clear_context": "Clear the current context",
                "language": "Select your preferred language",
            },
            "Russian": {
                "start": "Показать вводное сообщение",
                "knowledge_base": "Выбрать базу знаний",
                "status": "Показать текущий статус и информацию",
                "clear_context": "Очистить текущий контекст",
                "language": "Выбрать предпочитаемый язык",
            },
            "Indonesian": {
                "start": "Tampilkan pesan pengantar",
                "knowledge_base": "Pilih basis pengetahuan",
                "status": "Tampilkan status dan informasi saat ini",
                "clear_context": "Hapus konteks saat ini",
                "language": "Pilih bahasa yang Anda inginkan",
            },
            # Add more languages as needed
        }

        lang_commands = descriptions.get(language, descriptions["English"])

        commands = [
            BotCommand("start", lang_commands["start"]),
            BotCommand("knowledge_base", lang_commands["knowledge_base"]),
            BotCommand("status", lang_commands["status"]),
            BotCommand("clear_context", lang_commands["clear_context"]),
            BotCommand("language", lang_commands["language"]),
        ]

        return commands

class Translations:
    @staticmethod
    def uploaded_documents(language):
        translations = {
            "English": "your uploaded documents",
            "Russian": "ваши загруженные документы",
            "Indonesian": "dokumen yang Anda unggah",
        }
        return translations.get(language, "your uploaded documents")

class LanguageResponses:
    @staticmethod
    def language_set_success(selected_language):
        messages = {
            "English": "✅ Language has been set to English.",
            "Russian": "✅ Язык установлен на Русский.",
            "Indonesian": "✅ Bahasa telah diatur ke Bahasa Indonesia.",
        }
        return messages.get(selected_language, "✅ Language has been updated.")

    @staticmethod
    def select_language_prompt(language):
        prompts = {
            "English": "Please select your preferred language:",
            "Russian": "Пожалуйста, выберите предпочитаемый язык:",
            "Indonesian": "Silakan pilih bahasa yang Anda inginkan:",
        }
        return prompts.get(language, "Please select your preferred language:")

class Greetings:

    @staticmethod
    def first_time(language="English", user_name=""):
        messages = {
            "English": (
                "\U0001F44B <b>Hello! I'm your design assistant</b>\n\n"
                "🏗️ Get instant construction recommendations and expert answers to your building questions through this smart Telegram bot 🤖\n\n"
                "Here's how I can assist you:\n\n"
                "\U0001F4DA Access construction regulations through our /knowledge_base\n"
                "❓ Ask questions in plain language - I'll handle the technical details\n\n"
                "Helpful commands to get started:\n"
                "\U0001F504 /start - See this introduction again\n"
                "🌐 /language - Select your preferred language\n"
                "⚙️ /status - View your current settings\n"
                "🗑️ /clear_context - Reset your document history\n\n"
                "What would you like to know about?"
            ),
            "Russian": (
                "\U0001F44B <b>Здравствуйте! Я ваш помощник по дизайну</b>\n\n"
                "🏗️ Получите мгновенные рекомендации по строительству и экспертные ответы на ваши вопросы через этого умного Telegram бота 🤖\n\n"
                "Вот как я могу вам помочь:\n\n"
                "\U0001F4DA Доступ к строительным нормам через нашу /knowledge_base\n"
                "❓ Задавайте вопросы простым языком - я разберусь с техническими деталями\n\n"
                "Полезные команды для начала:\n"
                "\U0001F504 /start - Посмотреть это введение снова\n"
                "🌐 /language - Выбрать язык\n"
                "⚙️ /status - Просмотреть текущие настройки\n"
                "🗑️ /clear_context - Сбросить историю документов\n\n"
                "О чем бы вы хотели узнать?"
            ),
            "Indonesian": (
                "\U0001F44B <b>Halo! Saya asisten desain Anda</b>\n\n"
                "🏗️ Dapatkan rekomendasi konstruksi dan jawaban ahli untuk pertanyaan pembangunan Anda secara instan melalui bot Telegram pintar ini 🤖\n\n"
                "Berikut cara saya dapat membantu Anda:\n\n"
                "\U0001F4DA Akses peraturan konstruksi melalui /knowledge_base kami\n"
                "❓ Ajukan pertanyaan dalam bahasa sederhana - saya akan menangani detail teknisnya\n\n"
                "Perintah yang berguna untuk memulai:\n"
                "🌐 /language - Pilih bahasa\n"
                "\U0001F504 /start - Lihat pengantar ini lagi\n"
                "⚙️ /status - Lihat pengaturan Anda saat ini\n"
                "🗑️ /clear_context - Atur ulang riwayat dokumen Anda\n\n"
                "Apa yang ingin Anda ketahui?"
            ),
        }
        return messages.get(language, messages["English"])


class Status:
    @staticmethod
    def knowledge_base_set(user_name, knowledge_base_name, file_list, empty_list=None, language="English"):
        messages = {
            "English": (
                f"\U0001F4CA <b>Current Status</b>\n\n"
                f"Hi {user_name}! Here's your workspace setup:\n\n"
                f"\U0001F4DA <b>Active Knowledge Base:</b> {knowledge_base_name}\n\n"
                f"\U0001F4CB <b>Available Documents:</b>\n{file_list}\n\n"
            ),
            "Russian": (
                f"\U0001F4CA <b>Текущий статус</b>\n\n"
                f"Привет, {user_name}! Вот настройка вашего рабочего пространства:\n\n"
                f"\U0001F4DA <b>Активная база знаний:</b> {knowledge_base_name}\n\n"
                f"\U0001F4CB <b>Доступные документы:</b>\n{file_list}\n\n"
            ),
            "Indonesian": (
                f"\U0001F4CA <b>Status Saat Ini</b>\n\n"
                f"Hai {user_name}! Berikut adalah pengaturan ruang kerja Anda:\n\n"
                f"\U0001F4DA <b>Basis Pengetahuan Aktif:</b> {knowledge_base_name}\n\n"
                f"\U0001F4CB <b>Dokumen Tersedia:</b>\n{file_list}\n\n"
            ),
        }
        response = messages[language]
        if empty_list:
            empty_files = "\n".join(empty_list)
            attention_messages = {
                "English": (
                    f"\u26A0 <b>Attention Needed</b>\n"
                    f"The following documents need your attention:\n{empty_files}\n\n"
                    f"\U0001F4A1 Tip: Make sure these files are in PDF format and properly readable. "
                    f"Feel free to upload them again!"
                ),
                "Russian": (
                    f"\u26A0 <b>Необходимо внимание</b>\n"
                    f"Следующие документы требуют вашего внимания:\n{empty_files}\n\n"
                    f"\U0001F4A1 Совет: Убедитесь, что эти файлы в формате PDF и открываются корректно. "
                    f"Можете заново загрузить эти файлы!"
                ),
                "Indonesian": (
                    f"\u26A0 <b>Perhatian Diperlukan</b>\n"
                    f"Dokumen berikut memerlukan perhatian Anda:\n{empty_files}\n\n"
                    f"\U0001F4A1 Tip: Pastikan dokumen-dokumen ini dalam format PDF dan dapat dibaca dengan baik. "
                    f"Jangan ragu untuk mengunggahnya kembali!"
                ),
            }
            response += attention_messages[language]
        return response

    @staticmethod
    def knowledge_base_no_files(user_name, knowledge_base_name, language="English"):
        messages = {
            "English": (
                f"\U0001F4CA <b>Knowledge Base Status</b>\n\n"
                f"Hi {user_name}!\n\n"
                f"You're currently working with the '<i>{knowledge_base_name}</i>' knowledge base, "
                f"but I don't see any valid documents yet.\n\n"
                f"\U0001F4A1 Need help? Try:\n"
                f"• Selecting a different knowledge base\n"
                f"• Uploading your own documents\n"
                f"• Checking file formats (PDF recommended)"
            ),
            "Russian": (
                f"\U0001F4CA <b>Статус базы знаний</b>\n\n"
                f"Привет, {user_name}!\n\n"
                f"Сейчас вы работаете с базой знаний '<i>{knowledge_base_name}</i>', "
                f"но я не вижу ни одного документа.\n\n"
                f"\U0001F4A1 Нужна помощь? Попробуйте:\n"
                f"• Выбрать другую базу знаний\n"
                f"• Загрузить свои собственные документы\n"
                f"• Проверить формат файлов (PDF рекомендуется)"
            ),
            "Indonesian": (
                f"\U0001F4CA <b>Status Basis Pengetahuan</b>\n\n"
                f"Hai {user_name}!\n\n"
                f"Anda saat ini bekerja dengan basis pengetahuan '<i>{knowledge_base_name}</i>', "
                f"tetapi saya belum melihat dokumen yang valid.\n\n"
                f"\U0001F4A1 Butuh bantuan? Coba:\n"
                f"• Pilih basis pengetahuan yang berbeda\n"
                f"• Unggah dokumen Anda sendiri\n"
                f"• Periksa format file (PDF direkomendasikan)"
            ),
        }
        return messages[language]

    @staticmethod
    def no_knowledge_base_selected(user_name, language="English"):
        messages = {
            "English": (
                f"\U0001F4CA <b>Workspace Status</b>\n\n"
                f"Hi {user_name}!\n\n"
                f"Looks like we haven't selected a knowledge base yet.\n\n"
                f"\U0001F4A1 Quick Start:\n"
                f"1. Use /knowledge_base to explore available topics\n"
                f"2. Select the area that matches your needs\n"
                f"3. Start asking questions!\n\n"
                f"Need something specific? Just let me know! \U0001F44B"
            ),
            "Russian": (
                f"\U0001F4CA <b>Статус рабочего пространства</b>\n\n"
                f"Привет, {user_name}!\n\n"
                f"Похоже, что мы еще не выбрали базу знаний.\n\n"
                f"\U0001F4A1 Быстрый старт:\n"
                f"1. Воспользуйтесь /knowledge_base для поиска доступных тем\n"
                f"2. Выберите область, которая соответствует вашим нуждам\n"
                f"3. Начните задавать вопросы!\n\n"
                f"Нужно что-то конкретное? Просто сообщите мне! \U0001F44B"
            ),
            "Indonesian": (
                f"\U0001F4CA <b>Status Ruang Kerja</b>\n\n"
                f"Hai {user_name}!\n\n"
                f"Sepertinya kita belum memilih basis pengetahuan.\n\n"
                f"\U0001F4A1 Mulai Cepat:\n"
                f"1. Gunakan /knowledge_base untuk menjelajahi topik yang tersedia\n"
                f"2. Pilih area yang sesuai dengan kebutuhan Anda\n"
                f"3. Mulailah mengajukan pertanyaan!\n\n"
                f"Butuh sesuatu yang spesifik? Beri tahu saya! \U0001F44B"
            ),
        }
        return messages[language]

    @staticmethod
    def upload_set(user_name, file_list, empty_list=None, language="English"):
        messages = {
            "English": (
                f"\U0001F4CA <b>Document Status</b>\n\n"
                f"Hi {user_name}!\n\n"
                f"I'm working with your uploaded documents:\n\n"
                f"\U0001F4CB <b>Active Documents:</b>\n{file_list}\n\n"
            ),
            "Russian": (
                f"\U0001F4CA <b>Статус документов</b>\n\n"
                f"Привет, {user_name}!\n\n"
                f"Я работаю с вашими загруженными документами:\n\n"
                f"\U0001F4CB <b>Активные документы:</b>\n{file_list}\n\n"
            ),
            "Indonesian": (
                f"\U0001F4CA <b>Status Dokumen</b>\n\n"
                f"Hai {user_name}!\n\n"
                f"Saya sedang bekerja dengan dokumen yang Anda unggah:\n\n"
                f"\U0001F4CB <b>Dokumen Aktif:</b>\n{file_list}\n\n"
            ),
        }
        response = messages[language]
        if empty_list:
            empty_files = "\n".join(empty_list)
            attention_messages = {
                "English": (
                    f"⚠ <b>Document Issues Detected</b>\n"
                    f"These files need attention:\n{empty_files}\n\n"
                    f"\U0001F4A1 Quick Fix Tips:\n"
                    f"• Check if files are in PDF format\n"
                    f"• Ensure files aren't password-protected\n"
                    f"• Try re-uploading the document\n\n"
                    f"Need help? Just ask! \U0001F91D"
                ),
                "Russian": (
                    f"⚠ <b>Обнаружены проблемы с документами</b>\n"
                    f"Эти файлы требуют внимания:\n{empty_files}\n\n"
                    f"\U0001F4A1 Быстрые советы по исправлению:\n"
                    f"• Проверьте, что файлы в формате PDF\n"
                    f"• Убедитесь, что файлы не защищены паролем\n"
                    f"• Попробуйте заново загрузить файл\n\n"
                    f"Нужна помощь? Просто спросите! \U0001F91D"
                ),
                "Indonesian": (
                    f"⚠ <b>Masalah Dokumen Terdeteksi</b>\n"
                    f"Dokumen-dokumen ini memerlukan perhatian:\n{empty_files}\n\n"
                    f"\U0001F4A1 Tips Perbaikan Cepat:\n"
                    f"• Periksa apakah file dalam format PDF\n"
                    f"• Pastikan file tidak dilindungi kata sandi\n"
                    f"• Coba unggah ulang dokumen\n\n"
                    f"Butuh bantuan? Tanya saja! \U0001F91D"
                ),
            }
            response += attention_messages[language]
        return response

    @staticmethod
    def upload_no_files(user_name, language="English"):
        messages = {
            "English": (
                f"\U0001F4CA <b>Document Status</b>\n\n"
                f"Hi {user_name}!\n\n"
                f"I'm ready to work with your documents, but I don't see any valid files yet.\n\n"
                f"\U0001F4A1 You can:\n"
                f"• Upload PDF documents directly to our chat\n"
                f"• Use /knowledge_base to access standard regulations\n"
                f"• Ask me questions about any construction topic\n\n"
                f"Need guidance? I'm here to help! \U0001F91D"
            ),
            "Russian": (
                f"\U0001F4CA <b>Статус документов</b>\n\n"
                f"Привет, {user_name}!\n\n"
                f"Я готов работать с вашими документами, но пока не вижу ни одного валидного файла.\n\n"
                f"\U0001F4A1 Вы можете:\n"
                f"• Загрузить PDF-документы напрямую в наш чат\n"
                f"• Воспользоваться /knowledge_base для доступа к стандартным правилам\n"
                f"• Задавать мне вопросы по любой теме по строительству\n\n"
                f"Нужно какое-то руководство? Я здесь, чтобы помочь! \U0001F91D"
            ),
            "Indonesian": (
                f"\U0001F4CA <b>Status Dokumen</b>\n\n"
                f"Hai {user_name}!\n\n"
                f"Saya siap untuk bekerja dengan dokumen Anda, tetapi saya belum melihat file yang valid.\n\n"
                f"\U0001F4A1 Anda dapat:\n"
                f"• Unggah dokumen PDF langsung ke obrolan kita\n"
                f"• Gunakan /knowledge_base untuk mengakses peraturan standar\n"
                f"• Ajukan pertanyaan kepada saya tentang topik konstruksi apa pun\n\n"
                f"Butuh panduan? Saya di sini untuk membantu! \U0001F91D"
            ),
        }
        return messages[language]

    @staticmethod
    def no_context(user_name, language="English"):
        messages = {
            "English": (
                f"\U0001F4CA <b>Workspace Status</b>\n\n"
                f"Hi {user_name}!\n\n"
                f"Your workspace is ready, but we haven't loaded any documents yet.\n\n"
                f"\U0001F4A1 Let's get started:\n"
                f"1. Upload PDF documents directly to our chat, or\n"
                f"2. Use /knowledge_base to access construction regulations\n\n"
                f"Which would you prefer to explore first? \U0001F914"
            ),
            "Russian": (
                f"\U0001F4CA <b>Статус рабочего пространства</b>\n\n"
                f"Привет, {user_name}!\n\n"
                f"Ваше рабочее пространство готово, но мы еще не загрузили ни одного документа.\n\n"
                f"\U0001F4A1 Давайте начнем:\n"
                f"1. Загрузить PDF-документы напрямую в этот чат, или\n"
                f"2. Воспользоваться /knowledge_base для доступа к строительным нормам\n\n"
                f"С чего вы хотите начать? \U0001F914"
            ),
            "Indonesian": (
                f"\U0001F4CA <b>Status Ruang Kerja</b>\n\n"
                f"Hai {user_name}!\n\n"
                f"Ruang kerja Anda sudah siap, tetapi kami belum memuat dokumen apa pun.\n\n"
                f"\U0001F4A1 Mari kita mulai:\n"
                f"1. Unggah dokumen PDF langsung ke obrolan kita, atau\n"
                f"2. Gunakan /knowledge_base untuk mengakses peraturan konstruksi\n\n"
                f"Mana yang ingin Anda jelajahi terlebih dahulu? \U0001F914"
            ),
        }
        return messages[language]


class Responses:
    @staticmethod
    def request_access(language="English"):
        messages = {
            "English": "📂 <b>To get started</b>, please share the folder path where your documents are stored:",
            "Russian": "📂 <b>Чтобы начать</b>, пожалуйста, поделитесь путем к папке, где хранятся ваши документы:",
            "Indonesian": "📂 <b>Untuk memulai</b>, silakan bagikan jalur folder tempat dokumen Anda disimpan:",
        }
        return messages[language]

    @staticmethod
    def grant_access_success(user_id, language="English"):
        messages = {
            "English": f"✅ <b>Access granted</b> to user {user_id}! They can now use all bot features.",
            "Russian": f"✅ <b>Доступ предоставлен</b> пользователю {user_id}! Теперь они могут использовать все функции бота.",
            "Indonesian": f"✅ <b>Akses diberikan</b> kepada pengguna {user_id}! Mereka sekarang dapat menggunakan semua fitur bot.",
        }
        return messages[language]

    @staticmethod
    def grant_access_usage(language="English"):
        messages = {
            "English": "ℹ️ To grant access, use: /grant_access <user_id>",
            "Russian": "ℹ️ Чтобы предоставить доступ, используйте: /grant_access <user_id>",
            "Indonesian": "ℹ️ Untuk memberikan akses, gunakan: /grant_access <user_id>",
        }
        return messages[language]

    @staticmethod
    def access_denied(language="English"):
        messages = {
            "English": (
                "🔒 <b>Access needed!</b>\n\n"
                "To start using the bot, please use /request_access to get permission.\n"
                "An admin will review your request shortly."
            ),
            "Russian": (
                "🔒 <b>Требуется доступ!</b>\n\n"
                "Чтобы начать использовать бота, пожалуйста, используйте /request_access для запроса разрешения.\n"
                "Администратор рассмотрит ваш запрос в ближайшее время."
            ),
            "Indonesian": (
                "🔒 <b>Akses diperlukan!</b>\n\n"
                "Untuk mulai menggunakan bot, silakan gunakan /request_access untuk mendapatkan izin.\n"
                "Admin akan meninjau permintaan Anda segera."
            ),
        }
        return messages[language]

    @staticmethod
    def access_requested(language="English"):
        messages = {
            "English": (
                "📫 <b>Access Request Sent!</b>\n\n"
                "Your request has been forwarded to our admin team.\n"
                "You'll receive a notification once access is granted."
            ),
            "Russian": (
                "📫 <b>Запрос доступа отправлен!</b>\n\n"
                "Ваш запрос был отправлен нашей команде администраторов.\n"
                "Вы получите уведомление, как только доступ будет предоставлен."
            ),
            "Indonesian": (
                "📫 <b>Permintaan Akses Dikirim!</b>\n\n"
                "Permintaan Anda telah diteruskan ke tim admin kami.\n"
                "Anda akan menerima notifikasi setelah akses diberikan."
            ),
        }
        return messages[language]

    @staticmethod
    def unauthorized_action(language="English"):
        messages = {
            "English": (
                "🔒 <b>Authorization Required</b>\n\n"
                "You'll need additional permissions for this action.\n"
                "Please contact your administrator for assistance."
            ),
            "Russian": (
                "🔒 <b>Требуется авторизация</b>\n\n"
                "Вам нужны дополнительные разрешения для этого действия.\n"
                "Пожалуйста, свяжитесь с вашим администратором для помощи."
            ),
            "Indonesian": (
                "🔒 <b>Otorisasi Diperlukan</b>\n\n"
                "Anda memerlukan izin tambahan untuk tindakan ini.\n"
                "Silakan hubungi administrator Anda untuk bantuan."
            ),
        }
        return messages[language]

    @staticmethod
    def invalid_folder_path(language="English"):
        messages = {
            "English": (
                "⚠️ <b>Folder Path Issue</b>\n\n"
                "I couldn't find the folder you specified.\n"
                "Please check the path and try again.\n\n"
                "💡 <b>Tip:</b> Make sure the path is complete and correctly formatted."
            ),
            "Russian": (
                "⚠️ <b>Проблема с путем к папке</b>\n\n"
                "Я не смог найти указанную вами папку.\n"
                "Пожалуйста, проверьте путь и попробуйте снова.\n\n"
                "💡 <b>Совет:</b> Убедитесь, что путь полный и правильно отформатирован."
            ),
            "Indonesian": (
                "⚠️ <b>Masalah Jalur Folder</b>\n\n"
                "Saya tidak dapat menemukan folder yang Anda tentukan.\n"
                "Silakan periksa jalurnya dan coba lagi.\n\n"
                "💡 <b>Tip:</b> Pastikan jalurnya lengkap dan diformat dengan benar."
            ),
        }
        return messages[language]

    @staticmethod
    def no_valid_files(language="English"):
        messages = {
            "English": (
                "📂 <b>No Valid Documents Found</b>\n\n"
                "I couldn't find any documents to work with in that folder.\n"
                "Please ensure the folder contains PDF, DOCX, or XLSX files."
            ),
            "Russian": (
                "📂 <b>Не найдено действительных документов</b>\n\n"
                "Я не смог найти документы для работы в этой папке.\n"
                "Пожалуйста, убедитесь, что папка содержит файлы PDF, DOCX или XLSX."
            ),
            "Indonesian": (
                "📂 <b>Tidak Ada Dokumen Valid Ditemukan</b>\n\n"
                "Saya tidak dapat menemukan dokumen untuk bekerja di folder tersebut.\n"
                "Pastikan folder berisi file PDF, DOCX, atau XLSX."
            ),
        }
        return messages[language]

    @staticmethod
    def not_allowed_download(language="English"):
        messages = {
            "English": (
                "🚫 Access Restricted 😔\n\n"
                "Oops! This file cannot be downloaded at the moment. 🔒\n"
                "Perhaps the copyright holder has restricted download rights. 🛡️\n"
                "We respect intellectual property guidelines. 💡"
            ),
            "Russian": (
                "🚫 Доступ ограничен 😔\n\n"
                "Упс! В данный момент этот файл нельзя загрузить. 🔒\n"
                "Возможно, правообладатель ограничил права на загрузку. 🛡️\n"
                "Мы уважаем правила интеллектуальной собственности. 💡"
            ),
            "Indonesian": (
                "🚫 Akses Dibatasi 😔\n\n"
                "Ups! File ini tidak dapat diunduh saat ini. 🔒\n"
                "Mungkin pemegang hak cipta telah membatasi hak unduhan. 🛡️\n"
                "Kami menghormati pedoman hak kekayaan intelektual. 💡"
            ),
        }
        return messages[language]


    @staticmethod
    def documents_indexed(language="English"):
        messages = {
            "English": (
                "✅ <b>Success!</b>\n\n"
                "All documents have been indexed and are ready for your questions.\n"
                "What would you like to know about them?"
            ),
            "Russian": (
                "✅ <b>Успех!</b>\n\n"
                "Все документы были индексированы и готовы для ваших вопросов.\n"
                "Что вы хотели бы узнать о них?"
            ),
            "Indonesian": (
                "✅ <b>Sukses!</b>\n\n"
                "Semua dokumen telah diindeks dan siap untuk pertanyaan Anda.\n"
                "Apa yang ingin Anda ketahui tentang mereka?"
            ),
        }
        return messages[language]

    @staticmethod
    def folder_is_set(folder_path, empty_list=None, language="English"):
        if empty_list:
            empty_files = "\n".join(empty_list)
            additional_info = (
                f"\n⚠️ <b>Some files need attention:</b>\n{empty_files}\n\n"
                f"💡 <b>Tips:</b>\n"
                f"• Ensure files are in PDF format\n"
                f"• Check for password protection\n"
                f"• Try re-uploading if necessary\n"
            )
        else:
            additional_info = "\n🎉 <b>Perfect!</b> All files are properly indexed and ready to use."

        messages = {
            "English": (
                f"📁 <b>Folder Successfully Connected!</b>\n\n"
                f"📍 <b>Location:</b> {folder_path}\n\n"
                f"✅ Your documents are ready for queries!\n"
                f"{additional_info}"
            ),
            "Russian": (
                f"📁 <b>Папка успешно подключена!</b>\n\n"
                f"📍 <b>Расположение:</b> {folder_path}\n\n"
                f"✅ Ваши документы готовы для запросов!\n"
                f"{additional_info}"
            ),
            "Indonesian": (
                f"📁 <b>Folder Berhasil Terhubung!</b>\n\n"
                f"📍 <b>Lokasi:</b> {folder_path}\n\n"
                f"✅ Dokumen Anda siap untuk kueri!\n"
                f"{additional_info}"
            ),
        }
        return messages[language]

    @staticmethod
    def indexing_error(language="English"):
        messages = {
            "English": (
                "⚠️ <b>Oops!</b> Something went wrong while preparing your documents.\n"
                "Please try again in a few moments."
            ),
            "Russian": (
                "⚠️ <b>Упс!</b> Что-то пошло не так при подготовке ваших документов.\n"
                "Пожалуйста, попробуйте снова через несколько минут."
            ),
            "Indonesian": (
                "⚠️ <b>Ups!</b> Terjadi kesalahan saat menyiapkan dokumen Anda.\n"
                "Silakan coba lagi dalam beberapa saat."
            ),
        }
        return messages[language]

    @staticmethod
    def upload_success(language="English"):
        messages = {
            "English": (
                "✅ <b>Upload Complete!</b>\n\n"
                "Your documents are successfully indexed and ready to use.\n"
                "What would you like to know about them? 🤔"
            ),
            "Russian": (
                "✅ <b>Загрузка завершена!</b>\n\n"
                "Ваши документы успешно индексированы и готовы к использованию.\n"
                "Что вы хотели бы узнать о них? 🤔"
            ),
            "Indonesian": (
                "✅ <b>Unggahan Selesai!</b>\n\n"
                "Dokumen Anda berhasil diindeks dan siap digunakan.\n"
                "Apa yang ingin Anda ketahui tentang mereka? 🤔"
            ),
        }
        return messages[language]

    @staticmethod
    def upload_partial_success(language="English"):
        messages = {
            "English": (
                "📄 <b>Partial Upload Complete</b>\n\n"
                "I've indexed all PDF files you've sent.\n\n"
                "💡 <b>Note:</b> Only PDF files are supported. Other file types were skipped.\n\n"
                "Ready for your questions about the PDF documents! 🤓"
            ),
            "Russian": (
                "📄 <b>Частичная загрузка завершена</b>\n\n"
                "Я индексировал все отправленные вами PDF файлы.\n\n"
                "💡 <b>Примечание:</b> Поддерживаются только PDF файлы. Другие типы файлов были пропущены.\n\n"
                "Готов ответить на ваши вопросы о PDF документах! 🤓"
            ),
            "Indonesian": (
                "📄 <b>Unggahan Sebagian Selesai</b>\n\n"
                "Saya telah mengindeks semua file PDF yang Anda kirim.\n\n"
                "💡 <b>Catatan:</b> Hanya file PDF yang didukung. Jenis file lain diabaikan.\n\n"
                "Siap untuk pertanyaan Anda tentang dokumen PDF! 🤓"
            ),
        }
        return messages[language]

    @staticmethod
    def unsupported_files(language="English"):
        messages = {
            "English": (
                "⚠️ <b>Unsupported File Type</b>\n\n"
                "I can only work with PDF files at the moment.\n\n"
                "💡 Please convert your documents to PDF format and try again."
            ),
            "Russian": (
                "⚠️ <b>Неподдерживаемый тип файла</b>\n\n"
                "На данный момент я могу работать только с PDF файлами.\n\n"
                "💡 Пожалуйста, преобразуйте ваши документы в формат PDF и попробуйте снова."
            ),
            "Indonesian": (
                "⚠️ <b>Jenis File Tidak Didukung</b>\n\n"
                "Saat ini saya hanya dapat bekerja dengan file PDF.\n\n"
                "💡 Silakan ubah dokumen Anda ke format PDF dan coba lagi."
            ),
        }
        return messages[language]

    @staticmethod
    def processing_error(language="English"):
        messages = {
            "English": (
                "⚠️ <b>Processing Issue</b>\n\n"
                "I couldn't read your files properly.\n\n"
                "💡 Please check:\n"
                "• Files are in PDF format\n"
                "• PDFs aren't password-protected\n"
                "• Files aren't corrupted"
            ),
            "Russian": (
                "⚠️ <b>Проблема обработки</b>\n\n"
                "Я не смог правильно прочитать ваши файлы.\n\n"
                "💡 Пожалуйста, проверьте:\n"
                "• Файлы в формате PDF\n"
                "• PDF не защищены паролем\n"
                "• Файлы не повреждены"
            ),
            "Indonesian": (
                "⚠️ <b>Masalah Pemrosesan</b>\n\n"
                "Saya tidak dapat membaca file Anda dengan benar.\n\n"
                "💡 Silakan periksa:\n"
                "• File dalam format PDF\n"
                "• PDF tidak dilindungi kata sandi\n"
                "• File tidak rusak"
            ),
        }
        return messages[language]

    @staticmethod
    def generic_error(language="English"):
        messages = {
            "English": (
                "⚠️ <b>Unexpected Issue</b>\n\n"
                "Something went wrong while processing your request.\n\n"
                "💡 Please try:\n"
                "• Waiting a moment\n"
                "• Trying again\n"
                "• Contacting support if the issue persists"
            ),
            "Russian": (
                "⚠️ <b>Неожиданная проблема</b>\n\n"
                "Что-то пошло не так при обработке вашего запроса.\n\n"
                "💡 Пожалуйста, попробуйте:\n"
                "• Подождать немного\n"
                "• Попробовать снова\n"
                "• Связаться с поддержкой, если проблема сохраняется"
            ),
            "Indonesian": (
                "⚠️ <b>Masalah Tak Terduga</b>\n\n"
                "Terjadi kesalahan saat memproses permintaan Anda.\n\n"
                "💡 Silakan coba:\n"
                "• Menunggu sebentar\n"
                "• Mencoba lagi\n"
                "• Menghubungi dukungan jika masalah berlanjut"
            ),
        }
        return messages[language]

    @staticmethod
    def no_files_received(language="English"):
        messages = {
            "English": (
                "📎 <b>No Files Found</b>\n\n"
                "I haven't received any files with your message.\n\n"
                "💡 <b>To share documents:</b>\n"
                "• Click the attachment icon\n"
                "• Select your PDF files\n"
                "• Send them in the chat"
            ),
            "Russian": (
                "📎 <b>Файлы не найдены</b>\n\n"
                "Я не получил никаких файлов с вашим сообщением.\n\n"
                "💡 <b>Чтобы поделиться документами:</b>\n"
                "• Нажмите на значок вложения\n"
                "• Выберите ваши PDF файлы\n"
                "• Отправьте их в чат"
            ),
            "Indonesian": (
                "📎 <b>Tidak Ada File Ditemukan</b>\n\n"
                "Saya belum menerima file apa pun dengan pesan Anda.\n\n"
                "💡 <b>Untuk membagikan dokumen:</b>\n"
                "• Klik ikon lampiran\n"
                "• Pilih file PDF Anda\n"
                "• Kirim mereka di chat"
            ),
        }
        return messages[language]

    @staticmethod
    def file_too_large(language="English"):
        messages = {
            "English": (
                "⚠️ <b>File Size Limit Exceeded</b>\n\n"
                "Files must be under 20MB to process.\n\n"
                "💡 Try:\n"
                "• Compressing the PDF\n"
                "• Splitting into smaller files\n"
                "• Removing unnecessary pages"
            ),
            "Russian": (
                "⚠️ <b>Превышен лимит размера файла</b>\n\n"
                "Файлы должны быть менее 20 МБ для обработки.\n\n"
                "💡 Попробуйте:\n"
                "• Сжать PDF\n"
                "• Разделить на меньшие файлы\n"
                "• Удалить ненужные страницы"
            ),
            "Indonesian": (
                "⚠️ <b>Batas Ukuran File Terlampaui</b>\n\n"
                "File harus di bawah 20MB untuk diproses.\n\n"
                "💡 Coba:\n"
                "• Kompres PDF\n"
                "• Membagi menjadi file lebih kecil\n"
                "• Menghapus halaman yang tidak perlu"
            ),
        }
        return messages[language]

    @staticmethod
    def context_cleared(language="English"):
        messages = {
            "English": (
                "🗑️ Your workspace has been reset.\n\n"
                "You can now select a new knowledge base using /knowledge_base or upload new documents.\n\n"
                "What would you like to do next?"
            ),
            "Russian": (
                "🗑️ Ваше рабочее пространство было сброшено.\n\n"
                "Теперь вы можете выбрать новую базу знаний, используя /knowledge_base, или загрузить новые документы.\n\n"
                "Что бы вы хотели сделать дальше?"
            ),
            "Indonesian": (
                "🗑️ Ruang kerja Anda telah direset.\n\n"
                "Anda sekarang dapat memilih basis pengetahuan baru menggunakan /knowledge_base atau mengunggah dokumen baru.\n\n"
                "Apa yang ingin Anda lakukan selanjutnya?"
            ),
        }
        return messages[language]

    @staticmethod
    def unknown_command(language="English"):
        messages = {
            "English": (
                "❓ I'm not sure what you mean.\n\n"
                "💡 You can try:\n"
                "• Using /help to see available commands\n"
                "• Asking me a question about construction or design\n"
                "• Uploading a document for me to analyze"
            ),
            "Russian": (
                "❓ Я не уверен, что вы имеете в виду.\n\n"
                "💡 Вы можете попробовать:\n"
                "• Использовать /help, чтобы увидеть доступные команды\n"
                "• Задать мне вопрос о строительстве или дизайне\n"
                "• Загрузить документ для анализа"
            ),
            "Indonesian": (
                "❓ Saya tidak yakin apa yang Anda maksud.\n\n"
                "💡 Anda dapat mencoba:\n"
                "• Menggunakan /help untuk melihat perintah yang tersedia\n"
                "• Menanyakan pertanyaan tentang konstruksi atau desain\n"
                "• Mengunggah dokumen untuk saya analisis"
            ),
        }
        return messages[language]


class KnowledgeBaseResponses:
    @staticmethod
    def unknown_knowledge_base(language="English"):
        messages = {
            "English": (
                "\U0001F4C2 <b>Empty Knowledge Base</b>\n\n"
                "The selected knowledge base appears to be empty or contains no readable files.\n\n"
                "\U0001F4A1 You can:\n"
                "\u2022 Select a different knowledge base\n"
                "\u2022 Upload your own documents\n"
                "\u2022 Contact support if you believe this is an error\n\n"
                "Need help? Just ask! \U0001F91D"
            ),
            "Russian": (
                "\U0001F4C2 <b>Пустая база знаний</b>\n\n"
                "Выбранная база знаний пуста или не содержит читаемых файлов.\n\n"
                "\U0001F4A1 Вы можете:\n"
                "\u2022 Выбрать другую базу знаний\n"
                "\u2022 Загрузить свои документы\n"
                "\u2022 Обратиться в поддержку, если считаете, что это ошибка\n\n"
                "Нужна помощь? Просто спросите! \U0001F91D"
            ),
            "Indonesian": (
                "\U0001F4C2 <b>Basis Pengetahuan Kosong</b>\n\n"
                "Basis pengetahuan yang dipilih tampaknya kosong atau tidak berisi file yang dapat dibaca.\n\n"
                "\U0001F4A1 Anda dapat:\n"
                "\u2022 Pilih basis pengetahuan yang berbeda\n"
                "\u2022 Unggah dokumen Anda sendiri\n"
                "\u2022 Hubungi dukungan jika menurut Anda ini adalah kesalahan\n\n"
                "Butuh bantuan? Tanyakan saja! \U0001F91D"
            ),
        }
        return messages[language]

    @staticmethod
    def no_valid_files_in_knowledge_base(language="English"):
        return KnowledgeBaseResponses.unknown_knowledge_base(language)

    @staticmethod
    def indexing_error(language="English"):
        messages = {
            "English": (
                "\u26A0\uFE0F <b>Oops!</b> Something went wrong while preparing the knowledge base documents.\n"
                "Please try again in a few moments."
            ),
            "Russian": (
                "\u26A0\uFE0F <b>Ой!</b> Что-то пошло не так при подготовке документов базы знаний.\n"
                "Попробуйте снова через несколько минут."
            ),
            "Indonesian": (
                "\u26A0\uFE0F <b>Ups!</b> Terjadi kesalahan saat menyiapkan dokumen basis pengetahuan.\n"
                "Silakan coba lagi dalam beberapa saat."
            ),
        }
        return messages[language]

    @staticmethod
    def knowledge_base_set_success(knowledge_base_name, language="English"):
        messages = {
            "English": (
                f"\u2705 <b>Knowledge Base Connected!</b>\n\n"
                f"\U0001F4DA Now using: <i>{knowledge_base_name}</i>\n\n"
                f"\U0001F4A1 You can:\n"
                f"\u2022 Ask questions about regulations\n"
                f"\u2022 Request specific information\n"
                f"\u2022 Search for standards\n\n"
                f"What would you like to know about? \U0001F914"
            ),
            "Russian": (
                f"\u2705 <b>База знаний подключена!</b>\n\n"
                f"\U0001F4DA Сейчас используется: <i>{knowledge_base_name}</i>\n\n"
                f"\U0001F4A1 Вы можете:\n"
                f"\u2022 Задавать вопросы о нормативных актах\n"
                f"\u2022 Запрашивать конкретную информацию\n"
                f"\u2022 Искать стандарты\n\n"
                f"Что вы хотите узнать? \U0001F914"
            ),
            "Indonesian": (
                f"\u2705 <b>Basis Pengetahuan Terhubung!</b>\n\n"
                f"\U0001F4DA Sekarang menggunakan: <i>{knowledge_base_name}</i>\n\n"
                f"\U0001F4A1 Anda dapat:\n"
                f"\u2022 Mengajukan pertanyaan tentang regulasi\n"
                f"\u2022 Meminta informasi spesifik\n"
                f"\u2022 Mencari standar\n\n"
                f"Apa yang ingin Anda ketahui? \U0001F914"
            ),
        }
        return messages[language]

    @staticmethod
    def unknown_command(language="English"):
        messages = {
            "English": (
                "\u2753 <b>I'm not sure what you mean.</b>\n\n"
                "\U0001F4A1 You can try:\n"
                "\u2022 Using /help to see available commands\n"
                "\u2022 Asking me a question about construction or design\n"
                "\u2022 Uploading a document for me to analyze"
            ),
            "Russian": (
                "\u2753 <b>Я не уверен, что вы имеете в виду.</b>\n\n"
                "\U0001F4A1 Вы можете попробовать:\n"
                "\u2022 Использовать /help для просмотра доступных команд\n"
                "\u2022 Задать мне вопрос о строительстве или дизайне\n"
                "\u2022 Загрузить документ для анализа"
            ),
            "Indonesian": (
                "\u2753 <b>Saya tidak yakin apa yang Anda maksud.</b>\n\n"
                "\U0001F4A1 Anda dapat mencoba:\n"
                "\u2022 Menggunakan /help untuk melihat perintah yang tersedia\n"
                "\u2022 Mengajukan pertanyaan kepada saya tentang konstruksi atau desain\n"
                "\u2022 Mengunggah dokumen untuk saya analisis"
            ),
        }
        return messages[language]

    @staticmethod
    def select_knowledge_base(language="English"):
        messages = {
            "English": "Please choose a knowledge base to explore:",
            "Russian": "Пожалуйста, выберите базу знаний для исследования:",
            "Indonesian": "Silakan pilih basis pengetahuan untuk dijelajahi:",
        }
        return messages[language]



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
    def documents_not_indexed(language="English"):
        messages={
            "English": (
                "📚 Let's Get Started! 👋\n\n"
                "It seems we haven't set up any documents yet. 🤔\n"
                "Please use /knowledge_base to choose a topic! ✨"
            ),
            "Russian": (
                "📚 Давайте начнем! 👋\n\n"
                "Похоже, документы еще не настроены. 🤔\n"
                "Пожалуйста, используйте /knowledge_base, чтобы выбрать тему! ✨"
            ),
            "Indonesian": (
                "📚 Mari Mulai! 👋\n\n"
                "Sepertinya kita belum menyiapkan dokumen apapun. 🤔\n"
                "Silakan gunakan /knowledge_base untuk memilih topik! ✨"
            ),
        }
        return messages[language]

    @staticmethod
    def no_valid_documents(language="English"):
        messages = {
            "English": (
                "📂 No Documents Found\n\n"
                "I couldn't find any documents to work with.\n"
                "Please make sure you've added some files to your folder or upload them here."
            ),
            "Russian": (
                "📂 Документы не найдены\n\n"
                "Я не смог найти документы для работы.\n"
                "Пожалуйста, убедитесь, что вы добавили файлы в папку или загрузите их здесь."
            ),
            "Indonesian": (
                "📂 Tidak Ada Dokumen Ditemukan\n\n"
                "Saya tidak dapat menemukan dokumen untuk diproses.\n"
                "Pastikan Anda telah menambahkan beberapa file ke folder Anda atau unggah di sini."
            ),
        }
        return messages[language]


    def unknown_command(language="English"):
        messages = {
            "English": (
                "\u2753 <b>I'm not sure what you mean.</b>\n\n"
                "\U0001F4A1 You can try:\n"
                "\u2022 Using /help to see available commands\n"
                "\u2022 Asking me a question about construction or design\n"
                "\u2022 Uploading a document for me to analyze"
            ),
            "Russian": (
                "\u2753 <b>Я не уверен, что вы имеете в виду.</b>\n\n"
                "\U0001F4A1 Вы можете попробовать:\n"
                "\u2022 Использовать /help для просмотра доступных команд\n"
                "\u2022 Задать мне вопрос о строительстве или дизайне\n"
                "\u2022 Загрузить документ для анализа"
            ),
            "Indonesian": (
                "\u2753 <b>Saya tidak yakin apa yang Anda maksud.</b>\n\n"
                "\U0001F4A1 Anda dapat mencoba:\n"
                "\u2022 Menggunakan /help untuk melihat perintah yang tersedia\n"
                "\u2022 Mengajukan pertanyaan kepada saya tentang konstruksi atau desain\n"
                "\u2022 Mengunggah dokumen untuk saya analisis"
            ),
        }
        return messages[language]