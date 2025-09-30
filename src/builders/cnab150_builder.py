"""
Construtor para arquivos CNAB 150 (Débito Automático).
"""

from datetime import date
from typing import List

from ..interfaces import ICnabBuilder
from ..models import Cnab150Request, CnabRequest
from ..utils import CnabConstants, CnabFieldFormatter, CnabValidator


class Cnab150Builder(ICnabBuilder):
    """Construtor para arquivos CNAB 150/DBT627 - Versão 08 (Débito Automático)."""

    def __init__(self):
        self.formatter = CnabFieldFormatter()
        self.validator = CnabValidator()

    def get_record_length(self) -> int:
        """Retorna o tamanho do registro CNAB 150."""
        return 150

    def build_header(self, request: CnabRequest) -> str:
        """Constrói o registro Header (Registro "A")."""
        if not isinstance(request, Cnab150Request):
            raise TypeError("Request deve ser do tipo Cnab150Request")

        empresa = request.empresa

        header = ""
        # A01 - Posição 001-001: Código do Registro
        header += self.formatter.format_field(CnabConstants.HEADER_RECORD, 1)

        # A02 - Posição 002-002: Código de Remessa
        header += self.formatter.format_field("1", 1)  # 1=Remessa

        # A03 - Posição 003-022: Código do Convênio (20 chars)
        header += self.formatter.format_field(empresa.codigo_convenio, 20)

        # A04 - Posição 023-042: Nome da Empresa (Destinatária) (20 chars)
        header += self.formatter.format_field(empresa.nome_empresa, 20)

        # A05 - Posição 043-045: Código do Banco (Depositária) (3 chars)
        header += self.formatter.format_field(empresa.codigo_banco, 3, "0", True)

        # A06 - Posição 046-065: Nome do Banco (Depositária) (20 chars)
        header += self.formatter.format_field(empresa.nome_banco, 20)

        # A07 - Posição 066-073: Data de Geração do Arquivo (AAAAMMDD) (8 chars)
        header += self.formatter.format_field(
            self.formatter.format_date_yyyymmdd(date.today()), 8
        )

        # A08 - Posição 074-079: Número Sequencial do Arquivo (NSA) (6 chars)
        header += self.formatter.format_field(request.nsa, 6, "0", True)

        # A09 - Posição 080-081: Versão do Layout (2 chars)
        header += self.formatter.format_field("08", 2)

        # A10 - Posição 082-098: Identificação do Serviço (17 chars)
        header += self.formatter.format_field("DEBITO AUTOMATICO", 17)

        # A11 - Posição 099-150: Reservado para o futuro (52 chars)
        header += self.formatter.format_field("", 52)

        self.validator.validate_record_length(
            header, self.get_record_length(), "Header (Registro A)"
        )
        return header

    def build_detail_records(self, request: CnabRequest) -> List[str]:
        """Constrói os registros de detalhe de Débito em Conta (Registro "E")."""
        if not isinstance(request, Cnab150Request):
            raise TypeError("Request deve ser do tipo Cnab150Request")

        registros = []

        for debito in request.debitos:
            detalhe = ""
            # E01 - Posição 001-001: Código do Registro
            detalhe += self.formatter.format_field(CnabConstants.DETAIL_RECORD_150, 1)

            # E02 - Posição 002-026: Identificação do Cliente na Destinatária (25 chars)
            detalhe += self.formatter.format_field(debito.id_cliente_empresa, 25)

            # E03 - Posição 027-030: Agência para Débito (4 chars)
            detalhe += self.formatter.format_field(debito.agencia_debito, 4, "0", True)

            # E04 - Posição 031-050: Identificação do Cliente na Depositária (Conta) (20 chars)
            detalhe += self.formatter.format_field(debito.conta_cliente, 20, "0", True)

            # E05 - Posição 051-058: Data do Vencimento (AAAAMMDD) (8 chars)
            detalhe += self.formatter.format_field(
                self.formatter.format_date_yyyymmdd(debito.vencimento), 8
            )

            # E06 - Posição 059-073: Valor do Débito (15 chars) - em centavos
            detalhe += self.formatter.format_field(
                self.formatter.format_currency_cents(debito.valor), 15, "0", True
            )

            # E07 - Posição 074-075: Código da Moeda (2 chars)
            detalhe += self.formatter.format_field(CnabConstants.REAL, 2)

            # E08 - Posição 076-128: Uso da Instituição Destinatária (53 chars)
            detalhe += self.formatter.format_field("", 53)

            # Posição 129-129: Campo relacionado ao E08 para tratamento acordado (1 char)
            detalhe += self.formatter.format_field("", 1)

            # E09 - Posição 130-130: Tipo de Identificação (1=CNPJ, 2=CPF) (1 char)
            detalhe += self.formatter.format_field(debito.tipo_inscricao, 1)

            # E10 - Posição 131-145: Identificação (Número do CPF/CNPJ) (15 chars)
            # Preenchido com zeros à esquerda conforme manual CNAB 150
            inscricao_formatada = self.formatter.format_inscricao(
                debito.inscricao, debito.tipo_inscricao
            )
            detalhe += inscricao_formatada

            # E11 - Posição 146-146: Tipo de Operação (1 char)
            detalhe += self.formatter.format_field(debito.tipo_operacao, 1)

            # E12 - Posição 147-147: Utilização do Cheque Especial (1 char)
            # Usa "0" como padrão se campo estiver vazio (opcional)
            cheque_especial = (
                debito.utilizacao_cheque_especial
                if debito.utilizacao_cheque_especial
                else "0"
            )
            detalhe += self.formatter.format_field(cheque_especial, 1)

            # E13 - Posição 148-148: Opção de Débito Parcial ou integral após o vencimento (1 char)
            # Usa "0" como padrão se campo estiver vazio (opcional)
            debito_parcial = (
                debito.opcao_debito_parcial if debito.opcao_debito_parcial else "0"
            )
            detalhe += self.formatter.format_field(debito_parcial, 1)

            # E14 - Posição 149-149: Reservado para o futuro (1 char)
            detalhe += self.formatter.format_field("", 1)

            # E15 - Posição 150-150: Código do Movimento (1 char)
            detalhe += self.formatter.format_field(debito.codigo_movimento, 1)

            self.validator.validate_record_length(
                detalhe, self.get_record_length(), "Detalhe (Registro E)"
            )
            registros.append(detalhe)

        return registros

    def build_trailer(self, request: CnabRequest, total_records: int) -> str:
        """Constrói o registro Trailer."""
        # Calcula valor total dos registros (soma do campo E06)
        valor_total = (
            sum(
                self.formatter.format_currency_cents(debito.valor)
                for debito in request.debitos
            )
            if isinstance(request, Cnab150Request)
            else 0
        )

        trailer = ""
        # Z01 - Posição 001-001: Código do Registro
        trailer += self.formatter.format_field(CnabConstants.TRAILER_RECORD, 1)

        # Z02 - Posição 002-007: Total de registros do arquivo (6 chars)
        trailer += self.formatter.format_field(str(total_records), 6, "0", True)

        # Z03 - Posição 008-024: Valor total dos registros do arquivo (17 chars) - em centavos
        trailer += self.formatter.format_field(str(valor_total), 17, "0", True)

        # Z04 - Posição 025-150: Reservado para o futuro (126 chars)
        trailer += self.formatter.format_field("", 126)

        self.validator.validate_record_length(
            trailer, self.get_record_length(), "Trailer (Registro Z)"
        )
        return trailer
