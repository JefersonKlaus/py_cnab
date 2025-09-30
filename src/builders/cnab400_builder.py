"""
Construtor para arquivos CNAB 400 (Cobrança).
"""

from datetime import date
from decimal import Decimal
from typing import List

from ..interfaces import ICnabBuilder
from ..models import Cnab400Request, CnabRequest
from ..utils import CnabConstants, CnabFieldFormatter, CnabValidator


class Cnab400Builder(ICnabBuilder):
    """Construtor para arquivos CNAB 400 (Cobrança)."""

    def __init__(self):
        self.formatter = CnabFieldFormatter()
        self.validator = CnabValidator()
        self._valor_total_arquivo = Decimal("0")

    def get_record_length(self) -> int:
        """Retorna o tamanho do registro CNAB 400."""
        return 400

    def build_header(self, request: CnabRequest) -> str:
        """Constrói o registro Header."""
        if not isinstance(request, Cnab400Request):
            raise TypeError("Request deve ser do tipo Cnab400Request")

        self._valor_total_arquivo = Decimal("0")
        empresa = request.empresa

        header = ""
        # Posição 001-001: Identificação do Registro
        header += self.formatter.format_field(CnabConstants.HEADER_RECORD_400, 1)

        # Posição 002-002: Identificação do Arquivo-Remessa
        header += self.formatter.format_field("1", 1)

        # Posição 003-009: Literal Remessa
        header += self.formatter.format_field("REMESSA", 7)

        # Posição 010-011: Código de Serviço
        header += self.formatter.format_field("01", 2)

        # Posição 012-026: Literal Serviço (15 chars)
        header += self.formatter.format_field("COBRANCA", 15)

        # Posição 027-046: Código da Empresa (20 chars)
        header += self.formatter.format_field(empresa.codigo_empresa, 20)

        # Posição 047-076: Nome da Empresa (30 chars)
        header += self.formatter.format_field(empresa.nome_empresa, 30)

        # Posição 077-079: Número do banco na Câmara de Compensação
        header += self.formatter.format_field(CnabConstants.BANK_CODE, 3)

        # Posição 080-094: Nome do Banco por Extenso (15 chars)
        header += self.formatter.format_field("BANCO", 15)

        # Posição 095-100: Data da Gravação do Arquivo (DDMMYY)
        header += self.formatter.format_field(
            self.formatter.format_date_ddmmyy(date.today()), 6
        )

        # Posição 101-108: Branco (8 chars)
        header += self.formatter.format_field("", 8)

        # Posição 109-110: Identificação do Sistema (2 chars)
        header += self.formatter.format_field("MX", 2)

        # Posição 111-117: Nº Sequencial de Remessa (7 chars)
        header += self.formatter.format_field(request.nsa, 7, "0", True)

        # Posição 118-394: Branco (277 chars)
        header += self.formatter.format_field("", 277)

        # Posição 395-400: Nº Sequencial do Registro (6 chars)
        header += self.formatter.format_field("1", 6, "0", True)

        self.validator.validate_record_length(
            header, self.get_record_length(), "Header CNAB 400"
        )
        return header

    def build_detail_records(self, request: CnabRequest) -> List[str]:
        """Constrói os registros de detalhe."""
        if not isinstance(request, Cnab400Request):
            raise TypeError("Request deve ser do tipo Cnab400Request")

        registros = []
        sequencial = 2  # Começa em 2 (header = 1)

        for cobranca in request.cobrancas:
            # Acumula valor total
            self._valor_total_arquivo += cobranca.valor

            # Separa CEP em dois campos (5 + 3)
            cep_limpo = "".join(filter(str.isdigit, cobranca.pagador.cep))
            cep_base = cep_limpo[:5] if len(cep_limpo) >= 5 else cep_limpo
            cep_sufixo = cep_limpo[5:8] if len(cep_limpo) > 5 else ""

            detalhe = ""
            # Posição 001-001: Identificação do Registro
            detalhe += self.formatter.format_field(CnabConstants.DETAIL_RECORD_400, 1)

            # Posição 002-006: Agência de Débito (opcional)
            detalhe += self.formatter.format_field("", 5, "0", True)

            # Posição 007-007: Dígito da Agência de Débito (opcional)
            detalhe += self.formatter.format_field("", 1)

            # Posição 008-012: Razão da Conta-Corrente (opcional)
            detalhe += self.formatter.format_field("", 5)

            # Posição 013-019: Conta-Corrente (opcional)
            detalhe += self.formatter.format_field("", 7)

            # Posição 020-020: Dígito da Conta-Corrente (opcional)
            detalhe += self.formatter.format_field("", 1)

            # Posição 021-037: Identificação da Empresa Beneficiária no Banco (17 chars)
            id_empresa = "0"  # Primeiro caractere sempre "0"
            id_empresa += self.formatter.format_field(cobranca.carteira, 3)
            id_empresa += self.formatter.format_field(cobranca.agencia, 5, "0", True)
            id_empresa += self.formatter.format_field(cobranca.conta, 7, "0", True)
            id_empresa += self.formatter.format_field(cobranca.conta_dv, 1)
            detalhe += id_empresa

            # Posição 038-062: Nº Controle do Participante (25 chars)
            detalhe += self.formatter.format_field(cobranca.nosso_numero, 25)

            # Posição 063-065: Código do Banco a ser debitado
            detalhe += self.formatter.format_field(CnabConstants.BANK_CODE, 3)

            # Posição 066-066: Campo de Multa
            detalhe += self.formatter.format_field("0", 1)

            # Posição 067-070: Percentual de Multa
            detalhe += self.formatter.format_field("", 4)

            # Posição 071-081: Identificação do Título no Banco (Nosso Número) - 11 chars
            detalhe += self.formatter.format_field(cobranca.nosso_numero_banco, 11)

            # Posição 082-082: Dígito de Autoconferência do Número Bancário
            detalhe += self.formatter.format_field(cobranca.nosso_numero_banco_dv, 1)

            # Posição 083-092: Desconto Bonificação por dia (10 chars)
            detalhe += self.formatter.format_field("", 10, "0", True)

            # Posição 093-093: Condição para Emissão da Papeleta de Cobrança
            detalhe += self.formatter.format_field("2", 1)  # 2=Cliente emite

            # Posição 094-094: Ident. se emite Boleto para Débito Automático
            detalhe += self.formatter.format_field("N", 1)

            # Posição 095-104: Identificação da Operação do Banco (10 chars)
            detalhe += self.formatter.format_field("", 10)

            # Posição 105-105: Indicador Rateio Crédito (opcional)
            detalhe += self.formatter.format_field("", 1)

            # Posição 106-106: Endereçamento para Aviso do Débito Automático
            detalhe += self.formatter.format_field("2", 1)  # 2=não emite

            # Posição 107-108: Quantidade de Pagamentos (2 chars)
            detalhe += self.formatter.format_field("", 2)

            # Posição 109-110: Identificação da Ocorrência
            detalhe += self.formatter.format_field(cobranca.ocorrencia, 2)

            # Posição 111-120: Nº do Documento (10 chars)
            detalhe += self.formatter.format_field(cobranca.numero_documento, 10)

            # Posição 121-126: Data do Vencimento do Título (DDMMYY)
            detalhe += self.formatter.format_field(
                self.formatter.format_date_ddmmyy(cobranca.vencimento), 6
            )

            # Posição 127-139: Valor do Título (13 chars)
            detalhe += self.formatter.format_field(
                self.formatter.format_currency_cents(cobranca.valor), 13, "0", True
            )

            # Posição 140-142: Banco Encarregado da Cobrança
            detalhe += self.formatter.format_field("0", 3, "0", True)

            # Posição 143-147: Agência Depositária
            detalhe += self.formatter.format_field("0", 5, "0", True)

            # Posição 148-149: Espécie de Título
            detalhe += self.formatter.format_field("99", 2)  # 99=Outros

            # Posição 150-150: Identificação
            detalhe += self.formatter.format_field("N", 1)

            # Posição 151-156: Data da Emissão do Título (DDMMYY)
            detalhe += self.formatter.format_field(
                self.formatter.format_date_ddmmyy(cobranca.data_emissao), 6
            )

            # Posição 157-158: 1ª Instrução
            detalhe += self.formatter.format_field("0", 2, "0", True)

            # Posição 159-160: 2ª Instrução
            detalhe += self.formatter.format_field("0", 2, "0", True)

            # Posição 161-173: Valor a ser Cobrado por Dia de Atraso (13 chars)
            detalhe += self.formatter.format_field("", 13, "0", True)

            # Posição 174-179: Data Limite P/ Concessão de Desconto
            detalhe += self.formatter.format_field("", 6)

            # Posição 180-192: Valor do Desconto (13 chars)
            detalhe += self.formatter.format_field("", 13, "0", True)

            # Posição 193-205: Valor do IOF (13 chars)
            detalhe += self.formatter.format_field("", 13, "0", True)

            # Posição 206-218: Valor do Abatimento (13 chars)
            detalhe += self.formatter.format_field("", 13, "0", True)

            # Posição 219-220: Identificação do Tipo de Inscrição do Pagador
            detalhe += self.formatter.format_field(cobranca.pagador.tipo_inscricao, 2)

            # Posição 221-234: Nº Inscrição do Pagador (CPF/CNPJ) - 14 chars
            detalhe += self.formatter.format_field(
                cobranca.pagador.inscricao, 14, "0", True
            )

            # Posição 235-274: Nome do Pagador (40 chars)
            detalhe += self.formatter.format_field(cobranca.pagador.nome, 40)

            # Posição 275-314: Endereço Completo do Pagador (40 chars)
            detalhe += self.formatter.format_field(cobranca.pagador.endereco, 40)

            # Posição 315-326: 1ª Mensagem (12 chars)
            detalhe += self.formatter.format_field("", 12)

            # Posição 327-331: CEP do Pagador (5 chars)
            detalhe += self.formatter.format_field(cep_base, 5, "0", True)

            # Posição 332-334: Sufixo do CEP do Pagador (3 chars)
            detalhe += self.formatter.format_field(cep_sufixo, 3, "0", True)

            # Posição 335-394: Beneficiário Final ou 2ª Mensagem (60 chars)
            detalhe += self.formatter.format_field("", 60)

            # Posição 395-400: Nº Sequencial do Registro (6 chars)
            detalhe += self.formatter.format_field(sequencial, 6, "0", True)

            self.validator.validate_record_length(
                detalhe, self.get_record_length(), "Detalhe CNAB 400"
            )
            registros.append(detalhe)
            sequencial += 1

        return registros

    def build_trailer(self, request: CnabRequest, total_records: int) -> str:
        """Constrói o registro Trailer."""
        trailer = ""
        # Posição 001-001: Identificação do Registro
        trailer += self.formatter.format_field(CnabConstants.TRAILER_RECORD_400, 1)

        # Posição 002-394: Branco (393 chars)
        trailer += self.formatter.format_field("", 393)

        # Posição 395-400: Número Sequencial de Registro (6 chars)
        trailer += self.formatter.format_field(total_records, 6, "0", True)

        self.validator.validate_record_length(
            trailer, self.get_record_length(), "Trailer CNAB 400"
        )
        return trailer
