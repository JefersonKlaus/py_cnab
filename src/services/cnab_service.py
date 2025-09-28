"""
Serviços para geração e manipulação de arquivos CNAB.
"""

from typing import List
from ..interfaces import ICnabBuilder
from ..models import CnabRequest
from ..utils import CnabConstants


class CnabGeneratorService:
    """Serviço para geração de arquivos CNAB."""
    
    def __init__(self, builder: ICnabBuilder):
        """Inicializa o serviço com um builder específico."""
        self.builder = builder
    
    def generate_file(self, request: CnabRequest) -> str:
        """Gera o conteúdo do arquivo CNAB."""
        try:
            # Valida a requisição
            self._validate_request(request)
            
            lines = []
            
            # Header
            header = self.builder.build_header(request)
            lines.append(header)
            
            # Detalhes
            detail_records = self.builder.build_detail_records(request)
            lines.extend(detail_records)
            
            # Trailer
            total_records = len(lines) + 1
            trailer = self.builder.build_trailer(request, total_records)
            lines.append(trailer)
            
            # Retorna o arquivo com quebras de linha CNAB
            return CnabConstants.LINE_BREAK.join(lines) + CnabConstants.LINE_BREAK
            
        except Exception as e:
            raise ValueError(f"Erro ao gerar arquivo CNAB: {str(e)}") from e
    
    def _validate_request(self, request: CnabRequest) -> None:
        """
        Valida os dados da requisição.
        
        Args:
            request: Requisição a ser validada
            
        Raises:
            ValueError: Se a requisição for inválida
        """
        if not isinstance(request, CnabRequest):
            raise TypeError("Request deve herdar de CnabRequest")
        
        # A validação específica é feita nos models através de __post_init__
        # Aqui fazemos apenas validações gerais
        if request.nsa <= 0:
            raise ValueError("NSA deve ser um número positivo")


class CnabFileService:
    """
    Serviço de alto nível para operações com arquivos CNAB.
    
    Oferece uma interface simplificada para salvar arquivos gerados.
    """
    
    @staticmethod
    def save_to_file(content: str, filepath: str) -> None:
        """
        Salva o conteúdo CNAB em um arquivo.
        
        Args:
            content: Conteúdo do arquivo CNAB
            filepath: Caminho onde salvar o arquivo
            
        Raises:
            IOError: Se não for possível escrever no arquivo
        """
        try:
            with open(filepath, 'w', encoding='latin-1') as file:
                file.write(content)
        except Exception as e:
            raise IOError(f"Erro ao salvar arquivo {filepath}: {str(e)}") from e
    
    @staticmethod
    def validate_file_content(content: str, expected_record_length: int) -> List[str]:
        """
        Valida o conteúdo de um arquivo CNAB.
        
        Args:
            content: Conteúdo do arquivo
            expected_record_length: Tamanho esperado de cada registro
            
        Returns:
            Lista de erros encontrados (vazia se não houver erros)
        """
        errors = []
        lines = content.split(CnabConstants.LINE_BREAK)
        
        # Remove linha vazia no final se existir
        if lines and not lines[-1]:
            lines.pop()
        
        for i, line in enumerate(lines, 1):
            if len(line) != expected_record_length:
                errors.append(
                    f"Linha {i}: Tamanho {len(line)}, esperado {expected_record_length}"
                )
        
        return errors