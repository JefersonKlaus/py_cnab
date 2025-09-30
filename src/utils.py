"""
Utilitários comuns para manipulação de dados CNAB.
"""

from datetime import date
from decimal import Decimal
from typing import Union


class CnabFieldFormatter:
    """Formatador de campos para arquivos CNAB."""

    @staticmethod
    def format_field(
        valor: Union[str, int, date, Decimal],
        tamanho: int,
        preenchimento: str = " ",
        alinhar_a_direita: bool = False,
    ) -> str:
        """
        Formata um valor para um tamanho fixo, preenchendo e truncando se necessário.

        Args:
            valor: Valor a ser formatado
            tamanho: Tamanho final do campo
            preenchimento: Caractere para preenchimento
            alinhar_a_direita: Se True, alinha à direita

        Returns:
            String formatada com o tamanho especificado
        """
        if isinstance(valor, date):
            valor_str = valor.strftime("%Y%m%d")
        elif isinstance(valor, Decimal):
            valor_str = str(int(valor * 100))  # Converte para centavos
        else:
            valor_str = str(valor)

        # Trunca se necessário
        valor_str = valor_str[:tamanho]

        # Alinha e preenche
        if alinhar_a_direita:
            return valor_str.rjust(tamanho, preenchimento)
        return valor_str.ljust(tamanho, preenchimento)

    @staticmethod
    def format_date_ddmmyy(data: date) -> str:
        """Formata data no padrão DDMMYY."""
        return data.strftime("%d%m%y")

    @staticmethod
    def format_date_yyyymmdd(data: date) -> str:
        """Formata data no padrão YYYYMMDD."""
        return data.strftime("%Y%m%d")

    @staticmethod
    def format_currency_cents(valor: Decimal) -> int:
        """Converte valor monetário para centavos."""
        return int(valor * 100)

    @staticmethod
    def format_inscricao(inscricao: str, tipo_inscricao: str) -> str:
        """
        Formata inscrição (CPF/CNPJ) removendo caracteres não numéricos
        e preenchendo com zeros à esquerda para completar 15 posições.

        Args:
            inscricao: CPF ou CNPJ
            tipo_inscricao: '1' para CNPJ, '2' para CPF

        Returns:
            Inscrição formatada com 15 posições (preenchida com zeros à esquerda)
            conforme especificação do manual CNAB 150, página 22, campo E10
        """
        # Remove caracteres não numéricos
        inscricao_limpa = "".join(filter(str.isdigit, inscricao))

        # Preenche com zeros à esquerda para completar as 15 posições
        # conforme manual CNAB 150
        return inscricao_limpa.zfill(15)


class SequentialCounter:
    """Contador sequencial para registros CNAB."""

    def __init__(self):
        self._counter = 0

    def next(self) -> int:
        """Incrementa e retorna o próximo número sequencial."""
        self._counter += 1
        return self._counter

    def current(self) -> int:
        """Retorna o número atual sem incrementar."""
        return self._counter

    def reset(self) -> None:
        """Reseta o contador."""
        self._counter = 0


class CnabValidator:
    """Validador para campos e registros CNAB."""

    @staticmethod
    def validate_record_length(
        record: str, expected_length: int, record_type: str
    ) -> None:
        """
        Valida se o registro tem o tamanho esperado.

        Args:
            record: Registro a ser validado
            expected_length: Tamanho esperado
            record_type: Tipo do registro para mensagem de erro

        Raises:
            ValueError: Se o tamanho não confere
        """
        actual_length = len(record)
        if actual_length != expected_length:
            raise ValueError(
                f"Erro no {record_type}: Tamanho gerado foi de {actual_length} "
                f"caracteres, esperado {expected_length}."
            )

    @staticmethod
    def validate_bank_code(codigo: str) -> None:
        """Valida código do banco."""
        if not codigo.isdigit() or len(codigo) != 3:
            raise ValueError("Código do banco deve ter 3 dígitos numéricos")

    @staticmethod
    def validate_cpf_cnpj(inscricao: str, tipo: str) -> None:
        """Valida CPF ou CNPJ básico (apenas formato)."""
        inscricao_limpa = "".join(filter(str.isdigit, inscricao))

        if tipo == "01":  # CPF
            if len(inscricao_limpa) != 11:
                raise ValueError("CPF deve ter 11 dígitos")
        elif tipo == "02":  # CNPJ
            if len(inscricao_limpa) != 14:
                raise ValueError("CNPJ deve ter 14 dígitos")
        else:
            raise ValueError("Tipo de inscrição deve ser '01' (CPF) ou '02' (CNPJ)")


class CnabConstants:
    """Constantes utilizadas nos arquivos CNAB."""

    # Códigos de registro
    HEADER_RECORD = "A"
    DETAIL_RECORD_150 = "E"
    TRAILER_RECORD = "Z"

    HEADER_RECORD_400 = "0"
    DETAIL_RECORD_400 = "1"
    TRAILER_RECORD_400 = "9"

    # Códigos de movimento
    DEBITO_NORMAL = "0"
    REMESSA = "01"

    # Códigos de moeda
    REAL = "03"

    # Código do banco
    BANK_CODE = "237"

    # Quebra de linha CNAB
    LINE_BREAK = "\r\n"
