"""
Interface base para construtores de arquivos CNAB.
Define o contrato comum que todos os builders devem seguir.
"""

from abc import ABC, abstractmethod
from typing import List
from ..models import CnabRequest


class ICnabBuilder(ABC):
    """
    Interface para construtores de arquivos CNAB.
    
    Seguindo o princípio da Inversão de Dependência (DIP) do SOLID,
    esta interface define o contrato que todas as implementações devem seguir.
    """
    
    @abstractmethod
    def build_header(self, request: CnabRequest) -> str:
        """
        Constrói o registro Header do arquivo.
        
        Args:
            request: Dados da requisição contendo informações da empresa
            
        Returns:
            String contendo o registro header formatado
        """
        pass
    
    @abstractmethod
    def build_detail_records(self, request: CnabRequest) -> List[str]:
        """
        Constrói todos os registros de detalhe do arquivo.
        
        Args:
            request: Dados da requisição contendo lista de transações
            
        Returns:
            Lista de strings, cada uma representando um registro de detalhe
        """
        pass
    
    @abstractmethod
    def build_trailer(self, request: CnabRequest, total_records: int) -> str:
        """
        Constrói o registro Trailer do arquivo.
        
        Args:
            request: Dados da requisição
            total_records: Total de registros no arquivo
            
        Returns:
            String contendo o registro trailer formatado
        """
        pass
    
    @abstractmethod
    def get_record_length(self) -> int:
        """
        Retorna o tamanho esperado de cada registro para este formato CNAB.
        
        Returns:
            Tamanho do registro em caracteres
        """
        pass