# app/parsers/base_parser.py
from abc import ABC, abstractmethod
from sqlmodel import Session

class BaseParser(ABC):
    """
    Abstract base class for data parsers.
    Defines a standard interface for parsers that read data from a source
    and load it into the database.
    """
    
    @abstractmethod
    def parse_and_load(self, file_path: str, session: Session) -> None:
        """
        Abstract method to parse a file and load its data into the database.
        
        Args:
            file_path: The path to the source file.
            session: The database session to use for insertion.
        """
        pass