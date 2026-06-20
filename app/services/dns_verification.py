# app/services/dns_verification.py
import dns.resolver
import dns.exception
from typing import Tuple, Dict, Optional

class DNSVerificationService:
    
    @staticmethod
    async def check_spf_record(domain: str) -> Tuple[bool, str]:
        """Check SPF record - returns (is_valid, message)"""
        try:
            # Configure resolver with timeout
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            answers = resolver.resolve(domain, 'TXT')
            for rdata in answers:
                txt_value = rdata.to_text().strip('"')
                if 'v=spf1' in txt_value:
                    return True, "SPF record found and valid"
                elif 'include:' in txt_value:
                    return True, "SPF record found with include mechanism"
            
            return False, "No valid SPF record found (v=spf1 not present)"
            
        except dns.resolver.NXDOMAIN:
            return False, "Domain does not exist"
        except dns.resolver.NoAnswer:
            return False, "No TXT record found for SPF"
        except dns.resolver.Timeout:
            return False, "DNS lookup timeout - please try again"
        except dns.resolver.LifetimeTimeout:
            return False, "DNS query took too long - please try again"
        except Exception as e:
            return False, f"DNS lookup failed: {str(e)}"
    
    @staticmethod
    async def check_dkim_record(domain: str, selector: str = 'default') -> Tuple[bool, str]:
        """Check DKIM record - returns (is_valid, message)"""
        dkim_domain = f"{selector}._domainkey.{domain}"
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            answers = resolver.resolve(dkim_domain, 'TXT')
            for rdata in answers:
                txt_value = rdata.to_text().strip('"')
                if 'v=DKIM1' in txt_value and 'p=' in txt_value:
                    return True, "DKIM record found and valid"
                elif 'v=DKIM1' in txt_value:
                    return False, "DKIM record found but missing public key"
            
            return False, f"No DKIM record found at {dkim_domain}"
            
        except dns.resolver.NXDOMAIN:
            return False, f"DKIM record not found at {dkim_domain}"
        except dns.resolver.NoAnswer:
            return False, f"No DKIM record at {dkim_domain}"
        except dns.resolver.Timeout:
            return False, "DKIM lookup timeout - please try again"
        except Exception as e:
            return False, f"DKIM check failed: {str(e)}"
    
    @staticmethod
    async def check_dmarc_record(domain: str) -> Tuple[bool, str]:
        """Check DMARC record - returns (is_valid, message)"""
        dmarc_domain = f"_dmarc.{domain}"
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            answers = resolver.resolve(dmarc_domain, 'TXT')
            for rdata in answers:
                txt_value = rdata.to_text().strip('"')
                if 'v=DMARC1' in txt_value:
                    # Parse DMARC policy
                    policy = "unknown"
                    if 'p=reject' in txt_value:
                        policy = "reject"
                    elif 'p=quarantine' in txt_value:
                        policy = "quarantine"
                    elif 'p=none' in txt_value:
                        policy = "none"
                    
                    return True, f"DMARC record found (policy: {policy})"
                else:
                    return False, "Found TXT record but not DMARC"
            
            return False, "No DMARC record found"
            
        except dns.resolver.NXDOMAIN:
            return False, "No DMARC record found"
        except dns.resolver.NoAnswer:
            return False, "No DMARC record at _dmarc"
        except dns.resolver.Timeout:
            return False, "DMARC lookup timeout - please try again"
        except Exception as e:
            return False, f"DMARC check failed: {str(e)}"