"""
Factory para criação de builders CNAB.
"""

from enum import Enum
from typing import Dict, Type

from ..interfaces import ICnabBuilder
from ..builders import Cnab150Builder, Cnab400Builder


class CnabFormat(Enum):
    """Enumeration dos formatos CNAB suportados."""

    CNAB_150_DEBITO = "150_debito"
    CNAB_400_COBRANCA = "400_cobranca"


class CnabBuilderFactory:
    """Factory para criação de builders CNAB."""

    # Builders disponíveis
    _builders: Dict[CnabFormat, Type[ICnabBuilder]] = {
        CnabFormat.CNAB_150_DEBITO: Cnab150Builder,
        CnabFormat.CNAB_400_COBRANCA: Cnab400Builder,
    }

    @classmethod
    def create_builder(cls, formato: str) -> ICnabBuilder:
        """
        Cria um builder CNAB baseado no formato especificado.

        Args:
            formato: String identificando o formato CNAB

        Returns:
            Instância do builder apropriado

        Raises:
            NotImplementedError: Se o formato não for suportado
        """
        try:
            cnab_format = CnabFormat(formato)
            builder_class = cls._builders[cnab_format]
            return builder_class()
        except ValueError:
            available_formats = [fmt.value for fmt in CnabFormat]
            raise NotImplementedError(
                f"Formato CNAB '{formato}' não é suportado. "
                f"Formatos disponíveis: {available_formats}"
            )

    @classmethod
    def register_builder(
        cls, formato: CnabFormat, builder_class: Type[ICnabBuilder]
    ) -> None:
        """
        Registra um novo builder na factory.

        Permite extensibilidade seguindo o princípio Open/Closed.

        Args:
            formato: Formato CNAB a ser registrado
            builder_class: Classe do builder que implementa ICnabBuilder

        Raises:
            TypeError: Se builder_class não implementar ICnabBuilder
        """
        if not issubclass(builder_class, ICnabBuilder):
            raise TypeError("Builder deve implementar a interface ICnabBuilder")

        cls._builders[formato] = builder_class

    @classmethod
    def get_available_formats(cls) -> list[str]:
        """
        Retorna lista dos formatos CNAB disponíveis.

        Returns:
            Lista com os formatos suportados
        """
        return [fmt.value for fmt in cls._builders.keys()]

    @classmethod
    def is_format_supported(cls, formato: str) -> bool:
        """
        Verifica se um formato é suportado.

        Args:
            formato: Formato a ser verificado

        Returns:
            True se o formato for suportado, False caso contrário
        """
        try:
            CnabFormat(formato)
            return True
        except ValueError:
            return False
