"""
Construtor para arquivos CNAB 150 (Débito Automático).
"""

from datetime import date
from typing import List

from ..interfaces import ICnabBuilder
from ..models import Cnab150Request, CnabRequest
from ..utils import CnabFieldFormatter, CnabValidator, CnabConstants


class Cnab150Builder(ICnabBuilder):
    """Construtor para arquivos CNAB 150 (Débito Automático)."""
    
    def __init__(self):
        self.formatter = CnabFieldFormatter()
        self.validator = CnabValidator()
    
    def get_record_length(self) -> int:
        """Retorna o tamanho do registro CNAB 150."""
        return 150
    
    def build_header(self, request: CnabRequest) -> str:
        """Constrói o registro Header."""
        if not isinstance(request, Cnab150Request):
            raise TypeError("Request deve ser do tipo Cnab150Request")
        
        empresa = request.empresa
        
        header = ""
        # Posição 001-001: Código do Registro
        header += self.formatter.format_field(CnabConstants.HEADER_RECORD, 1)
        
        # Posição 002-002: Código de Remessa
        header += self.formatter.format_field('1', 1)  # 1=Remessa
        
        # Posição 003-022: Código do Convênio (20 chars)
        header += self.formatter.format_field(empresa.codigo_convenio, 20)
        
        # Posição 023-042: Nome da Empresa (Destinatária) (20 chars)
        header += self.formatter.format_field(empresa.nome_empresa, 20)
        
        # Posição 043-045: Código do Banco (Depositária) (3 chars)
        header += self.formatter.format_field(empresa.codigo_banco, 3, '0', True)
        
        # Posição 046-065: Nome do Banco (Depositária) (20 chars)
        header += self.formatter.format_field(empresa.nome_banco, 20)
        
        # Posição 066-073: Data de Geração do Arquivo (YYYYMMDD) (8 chars)
        header += self.formatter.format_field(
            self.formatter.format_date_yyyymmdd(date.today()), 8
        )
        
        # Posição 074-079: Número Sequencial do Arquivo (NSA) (6 chars)
        header += self.formatter.format_field(request.nsa, 6, '0', True)
        
        # Posição 080-081: Versão do Layout (2 chars)
        header += self.formatter.format_field('08', 2)
        
        # Posição 082-098: Identificação do Serviço (17 chars)
        header += self.formatter.format_field('DEBITO AUTOMATICO', 17)
        
        # Posição 099-150: Reservado para o futuro (52 chars)
        header += self.formatter.format_field('', 52)
        
        self.validator.validate_record_length(header, self.get_record_length(), "Header CNAB 150")
        return header
    
    def build_detail_records(self, request: CnabRequest) -> List[str]:
        """Constrói os registros de detalhe."""
        if not isinstance(request, Cnab150Request):
            raise TypeError("Request deve ser do tipo Cnab150Request")
        
        registros = []
        
        for debito in request.debitos:
            detalhe = ""
            # Posição 001-001: Código do Registro
            detalhe += self.formatter.format_field(CnabConstants.DETAIL_RECORD_150, 1)
            
            # Posição 002-026: Identificação do Cliente na Empresa (Destinatária) (25 chars)
            detalhe += self.formatter.format_field(debito.id_cliente_empresa, 25)
            
            # Posição 027-030: Agência para Débito (4 chars)
            detalhe += self.formatter.format_field(debito.agencia_debito, 4)
            
            # Posição 031-050: Identificação do Cliente no Banco (Depositária) (20 chars)
            detalhe += self.formatter.format_field(debito.conta_cliente, 20)
            
            # Posição 051-058: Data do Vencimento (YYYYMMDD) (8 chars)
            detalhe += self.formatter.format_field(
                self.formatter.format_date_yyyymmdd(debito.vencimento), 8
            )
            
            # Posição 059-073: Valor do Débito (15 chars) - em centavos
            detalhe += self.formatter.format_field(
                self.formatter.format_currency_cents(debito.valor), 15, '0', True
            )
            
            # Posição 074-075: Código da Moeda (2 chars)
            detalhe += self.formatter.format_field(CnabConstants.REAL, 2)
            
            # Posição 076-128: Uso da Empresa (Destinatária) (53 chars)
            detalhe += self.formatter.format_field('', 53)
            
            # Posição 129-129: Uso da Empresa (Destinatária) (1 char)
            detalhe += self.formatter.format_field('', 1)
            
            # Posição 130-130: Tipo de Identificação (CPF/CNPJ) (1 char)
            detalhe += self.formatter.format_field('', 1)
            
            # Posição 131-145: Identificação (Número do CPF/CNPJ) (15 chars)
            detalhe += self.formatter.format_field('', 15, '0', True)
            
            # Posição 146-146: Tipo de Operação (1 char)
            detalhe += self.formatter.format_field('', 1)
            
            # Posição 147-147: Utilização do Cheque Especial (1 char)
            detalhe += self.formatter.format_field('', 1)
            
            # Posição 148-148: Opção de Débito Parcial ou integral após o vencimento (1 char)
            detalhe += self.formatter.format_field('', 1)
            
            # Posição 149-149: Reservado para o futuro (1 char)
            detalhe += self.formatter.format_field('', 1)
            
            # Posição 150-150: Código do Movimento (1 char)
            detalhe += self.formatter.format_field(debito.codigo_movimento, 1)
            
            self.validator.validate_record_length(detalhe, self.get_record_length(), "Detalhe CNAB 150")
            registros.append(detalhe)
        
        return registros
    
    def build_trailer(self, request: CnabRequest, total_records: int) -> str:
        """Constrói o registro Trailer."""
        # Calcula valor total dos registros (apenas detalhes)
        valor_total = sum(
            self.formatter.format_currency_cents(debito.valor) 
            for debito in request.debitos
        ) if isinstance(request, Cnab150Request) else 0
        
        trailer = ""
        # Posição 001-001: Código do Registro
        trailer += self.formatter.format_field(CnabConstants.TRAILER_RECORD, 1)
        
        # Posição 002-007: Total de registros do arquivo (6 chars)
        trailer += self.formatter.format_field(total_records, 6, '0', True)
        
        # Posição 008-024: Valor total dos registros do arquivo (17 chars) - em centavos
        trailer += self.formatter.format_field(valor_total, 17, '0', True)
        
        # Posição 025-150: Reservado para o futuro (126 chars)
        trailer += self.formatter.format_field('', 126)
        
        self.validator.validate_record_length(trailer, self.get_record_length(), "Trailer CNAB 150")
        return trailer