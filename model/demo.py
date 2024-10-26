import magic
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import DirectoryLoader

# Path to magic.mgc file
magic_file_path = r"C:\Program Files (x86)\GnuWin32\share\misc\magic.mgc"

# Initialize the Magic object with the specified path
mime = magic.Magic(magic_file=magic_file_path)

# Continue with your script
load_dotenv()
embeddings = OpenAIEmbeddings()
loader = DirectoryLoader('news', glob="**/*.txt")
documents = loader.load()
print(len(documents))
