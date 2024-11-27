from llm_service import LLMService
from db_service import DatabaseService

llm_serv=LLMService()
db_serv=DatabaseService()

#Save docs metadata
folder=r'E:\knowledge_base\iso_regulations'

metadata_list = llm_serv.get_metadata(folder_path=folder, db_service=db_serv)
db_serv.save_metadata(metadata_list)
