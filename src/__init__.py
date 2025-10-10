"""
API pública da biblioteca py_cnab.
Fornece uma interface simplificada para uso externo.
"""

from .factories import CnabBuilderFactory, CnabFormat
from .models import (
    Cnab150EmpresaData,
    DBT627V8Request,
    Cnab400EmpresaData,
    Cnab400Request,
    CnabRequest,
    CobrancaData,
    DebitoAutomaticoData,
    EmpresaData,
    PagadorData,
)
from .services import CnabFileService, CnabGeneratorService
from .utils import CnabValidator


class CnabGenerator:
    """Interface principal para geração de arquivos CNAB."""

    @staticmethod
    def generate_cnab_150(request: DBT627V8Request) -> str:
        """Gera arquivo CNAB 150 (Débito Automático)."""
        builder = CnabBuilderFactory.create_builder(CnabFormat.CNAB_150_DEBITO.value)
        service = CnabGeneratorService(builder)
        return service.generate_file(request)

    @staticmethod
    def generate_cnab_400(request: Cnab400Request) -> str:
        """Gera arquivo CNAB 400 (Cobrança)."""
        builder = CnabBuilderFactory.create_builder(CnabFormat.CNAB_400_COBRANCA.value)
        service = CnabGeneratorService(builder)
        return service.generate_file(request)

    @staticmethod
    def save_file(content: str, filepath: str) -> None:
        """Salva conteúdo CNAB em arquivo."""
        CnabFileService.save_to_file(content, filepath)

    @staticmethod
    def validate_file(content: str, formato: str) -> list[str]:
        """Valida conteúdo de arquivo CNAB. Retorna lista de erros."""
        builder = CnabBuilderFactory.create_builder(formato)
        expected_length = builder.get_record_length()
        return CnabFileService.validate_file_content(content, expected_length)

    @staticmethod
    def get_supported_formats() -> list[str]:
        """Retorna lista de formatos CNAB suportados."""
        return CnabBuilderFactory.get_available_formats()


__version__ = "1.0.0"
__all__ = [
    "CnabGenerator",
    # Models
    "EmpresaData",
    "Cnab150EmpresaData",
    "Cnab400EmpresaData",
    "DebitoAutomaticoData",
    "PagadorData",
    "CobrancaData",
    "CnabRequest",
    "DBT627V8Request",
    "Cnab400Request",
    # Factories
    "CnabBuilderFactory",
    "CnabFormat",
    # Services (para uso avançado)
    "CnabGeneratorService",
    "CnabFileService",
    # Utils (para uso avançado)
    "CnabValidator",
]
