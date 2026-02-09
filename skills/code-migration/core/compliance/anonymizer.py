"""
Data anonymization and masking utilities.

Provides secure data handling:
- PII masking
- Data anonymization
- Tokenization
- Secure data replacement
"""

import hashlib
import re
import secrets
from typing import Dict, List, Optional, Tuple


class DataAnonymizer:
    """
    Secure data anonymization and masking.
    
    Features:
    - PII masking
    - Data anonymization
    - Tokenization
    - Format-preserving encryption
    - Reversible anonymization
    """
    
    def __init__(self, salt: Optional[str] = None):
        """
        Initialize data anonymizer.
        
        Args:
            salt: Salt for hash-based anonymization
        """
        self.salt = salt or secrets.token_hex(16)
        self.token_map: Dict[str, str] = {}
        self.reverse_map: Dict[str, str] = {}
    
    def mask_email(self, email: str, mask_char: str = '*', preserve_domain: bool = True) -> str:
        """
        Mask email address.
        
        Args:
            email: Email to mask
            mask_char: Character to use for masking
            preserve_domain: Whether to preserve domain
            
        Returns:
            Masked email
        """
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        
        # Mask local part
        if len(local) <= 2:
            masked_local = mask_char * len(local)
        else:
            masked_local = local[0] + mask_char * (len(local) - 2) + local[-1]
        
        if preserve_domain:
            return f"{masked_local}@{domain}"
        else:
            # Mask domain as well
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                masked_domain = mask_char * len(domain_parts[0]) + '.' + '.'.join(domain_parts[1:])
            else:
                masked_domain = mask_char * len(domain)
            
            return f"{masked_local}@{masked_domain}"
    
    def mask_phone(self, phone: str, mask_char: str = '*', preserve_format: bool = True) -> str:
        """
        Mask phone number.
        
        Args:
            phone: Phone number to mask
            mask_char: Character to use for masking
            preserve_format: Whether to preserve phone format
            
        Returns:
            Masked phone number
        """
        # Extract digits
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) < 4:
            return mask_char * len(phone)
        
        # Keep last 4 digits
        visible = digits[-4:]
        masked = mask_char * (len(digits) - 4) + visible
        
        if preserve_format:
            # Try to preserve original format
            result = ''
            digit_index = 0
            
            for char in phone:
                if char.isdigit():
                    result += masked[digit_index]
                    digit_index += 1
                else:
                    result += char
            
            return result
        else:
            return masked
    
    def mask_ssn(self, ssn: str, mask_char: str = '*') -> str:
        """
        Mask Social Security Number.
        
        Args:
            ssn: SSN to mask
            mask_char: Character to use for masking
            
        Returns:
            Masked SSN
        """
        # Extract digits
        digits = re.sub(r'\D', '', ssn)
        
        if len(digits) != 9:
            return mask_char * len(ssn)
        
        # Format: ***-**-1234
        return f"{mask_char * 3}-{mask_char * 2}-{digits[-4:]}"
    
    def mask_credit_card(self, card: str, mask_char: str = '*') -> str:
        """
        Mask credit card number.
        
        Args:
            card: Credit card number to mask
            mask_char: Character to use for masking
            
        Returns:
            Masked credit card number
        """
        # Extract digits
        digits = re.sub(r'\D', '', card)
        
        if len(digits) < 4:
            return mask_char * len(card)
        
        # Show last 4 digits only
        visible = digits[-4:]
        masked = mask_char * (len(digits) - 4) + visible
        
        # Format in groups of 4
        formatted = []
        for i in range(0, len(masked), 4):
            formatted.append(masked[i:i+4])
        
        return ' '.join(formatted)
    
    def anonymize_text(self, text: str, pii_types: List[str] = None) -> str:
        """
        Anonymize PII in text.
        
        Args:
            text: Text to anonymize
            pii_types: Types of PII to anonymize
            
        Returns:
            Anonymized text
        """
        if pii_types is None:
            pii_types = ['email', 'phone', 'ssn', 'credit_card']
        
        anonymized = text
        
        if 'email' in pii_types:
            # Email pattern
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            anonymized = re.sub(email_pattern, lambda m: self.mask_email(m.group()), anonymized)
        
        if 'phone' in pii_types:
            # Phone pattern
            phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
            anonymized = re.sub(phone_pattern, lambda m: self.mask_phone(m.group()), anonymized)
        
        if 'ssn' in pii_types:
            # SSN pattern
            ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
            anonymized = re.sub(ssn_pattern, lambda m: self.mask_ssn(m.group()), anonymized)
        
        if 'credit_card' in pii_types:
            # Credit card pattern
            cc_pattern = r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
            anonymized = re.sub(cc_pattern, lambda m: self.mask_credit_card(m.group()), anonymized)
        
        return anonymized
    
    def tokenize(self, value: str, reversible: bool = True) -> str:
        """
        Tokenize a value.
        
        Args:
            value: Value to tokenize
            reversible: Whether tokenization should be reversible
            
        Returns:
            Tokenized value
        """
        if reversible:
            # Use deterministic tokenization
            token = hashlib.sha256(f"{value}{self.salt}".encode()).hexdigest()[:16]
            
            # Store mapping for reversal
            self.token_map[value] = token
            self.reverse_map[token] = value
            
            return token
        else:
            # Use random tokenization
            return secrets.token_hex(8)
    
    def detokenize(self, token: str) -> Optional[str]:
        """
        Reverse tokenization.
        
        Args:
            token: Token to detokenize
            
        Returns:
            Original value or None if not found
        """
        return self.reverse_map.get(token)
    
    def anonymize_name(self, name: str, preserve_initial: bool = True) -> str:
        """
        Anonymize a name.
        
        Args:
            name: Name to anonymize
            preserve_initial: Whether to preserve first initial
            
        Returns:
            Anonymized name
        """
        parts = name.strip().split()
        
        if not parts:
            return name
        
        if preserve_initial and parts:
            # Keep first initial
            initial = parts[0][0] + '.'
            return f"{initial} [ANONYMIZED]"
        else:
            return "[ANONYMIZED]"
    
    def anonymize_address(self, address: str, preserve_zip: bool = False) -> str:
        """
        Anonymize an address.
        
        Args:
            address: Address to anonymize
            preserve_zip: Whether to preserve ZIP code
            
        Returns:
            Anonymized address
        """
        # Extract ZIP code if preservation is requested
        zip_code = None
        if preserve_zip:
            zip_match = re.search(r'\b\d{5}(?:-\d{4})?\b', address)
            if zip_match:
                zip_code = zip_match.group()
        
        # Replace street address
        anonymized = re.sub(r'\d+\s+.*?(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)', 
                          '[ADDRESS REDACTED]', address, flags=re.IGNORECASE)
        
        # Add back ZIP code if preserved
        if zip_code:
            anonymized += f", {zip_code}"
        
        return anonymized.strip()
    
    def hash_anonymize(self, value: str, length: int = 16) -> str:
        """
        Hash-based anonymization.
        
        Args:
            value: Value to anonymize
            length: Length of hash to return
            
        Returns:
            Hashed value
        """
        hash_value = hashlib.sha256(f"{value}{self.salt}".encode()).hexdigest()
        return hash_value[:length]
    
    def format_preserving_anonymize(self, value: str, format_type: str) -> str:
        """
        Format-preserving anonymization.
        
        Args:
            value: Value to anonymize
            format_type: Type of format (email, phone, ssn, etc.)
            
        Returns:
            Format-preserved anonymized value
        """
        if format_type == 'email':
            return self.mask_email(value)
        elif format_type == 'phone':
            return self.mask_phone(value)
        elif format_type == 'ssn':
            return self.mask_ssn(value)
        elif format_type == 'credit_card':
            return self.mask_credit_card(value)
        elif format_type == 'name':
            return self.anonymize_name(value)
        elif format_type == 'address':
            return self.anonymize_address(value)
        else:
            # Default to hash-based anonymization
            return self.hash_anonymize(value)
    
    def batch_anonymize(self, data: Dict[str, str], field_types: Dict[str, str]) -> Dict[str, str]:
        """
        Batch anonymize multiple fields.
        
        Args:
            data: Dictionary of data to anonymize
            field_types: Dictionary mapping field names to anonymization types
            
        Returns:
            Anonymized data
        """
        anonymized = {}
        
        for field, value in data.items():
            field_type = field_types.get(field, 'text')
            
            if field_type == 'skip':
                anonymized[field] = value
            elif field_type == 'token':
                anonymized[field] = self.tokenize(value)
            elif field_type == 'hash':
                anonymized[field] = self.hash_anonymize(value)
            else:
                anonymized[field] = self.format_preserving_anonymize(value, field_type)
        
        return anonymized
    
    def generate_anonymization_report(self, original_data: Dict, anonymized_data: Dict) -> Dict:
        """
        Generate report of anonymization changes.
        
        Args:
            original_data: Original data
            anonymized_data: Anonymized data
            
        Returns:
            Anonymization report
        """
        report = {
            'fields_processed': len(original_data),
            'fields_changed': 0,
            'field_details': {},
            'tokens_generated': len(self.token_map)
        }
        
        for field in original_data:
            if field in anonymized_data:
                original = original_data[field]
                anonymized = anonymized_data[field]
                
                changed = original != anonymized
                if changed:
                    report['fields_changed'] += 1
                
                report['field_details'][field] = {
                    'original_length': len(str(original)),
                    'anonymized_length': len(str(anonymized)),
                    'changed': changed,
                    'anonymization_type': self._detect_anonymization_type(original, anonymized)
                }
        
        return report
    
    def _detect_anonymization_type(self, original: str, anonymized: str) -> str:
        """Detect the type of anonymization applied."""
        if anonymized == original:
            return 'none'
        elif anonymized.startswith('[ANONYMIZED]') or anonymized == '[ADDRESS REDACTED]':
            return 'masking'
        elif re.match(r'^[a-f0-9]+$', anonymized):
            return 'hash'
        elif len(anonymized) == 16 and anonymized in self.token_map.values():
            return 'token'
        elif '*' in anonymized:
            return 'partial_mask'
        else:
            return 'unknown'
    
    def get_anonymization_statistics(self) -> Dict:
        """
        Get statistics about anonymization operations.
        
        Returns:
            Anonymization statistics
        """
        return {
            'total_tokens': len(self.token_map),
            'reversible_tokens': len(self.reverse_map),
            'salt_length': len(self.salt),
            'supported_types': ['email', 'phone', 'ssn', 'credit_card', 'name', 'address', 'text']
        }
