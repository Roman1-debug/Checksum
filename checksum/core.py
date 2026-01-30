"""
Core checksum verification functionality.
Compare file hashes against known values.
"""

import hashlib
import os
from typing import Dict, Any


class ChecksumEngine:
    """File integrity verification engine."""
    
    def __init__(self):
        self.supported_algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512,
        }
    
    def calculate_hash(self, file_path: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """
        Calculate hash of a file.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm
        
        Returns:
            Dictionary with hash result
        """
        alg = algorithm.lower()
        if alg not in self.supported_algorithms:
            return {
                'success': False,
                'error': f"Unsupported algorithm: {algorithm}"
            }
        
        if not os.path.exists(file_path):
            return {'success': False, 'error': f"File not found: {file_path}"}
        
        try:
            h = self.supported_algorithms[alg]()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(chunk)
            
            return {
                'success': True,
                'algorithm': alg,
                'hash_value': h.hexdigest(),
                'file_path': file_path,
                'file_size': os.path.getsize(file_path)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_checksum(self, file_path: str, expected_hash: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """
        Verify file checksum against expected value.
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm
        
        Returns:
            Dictionary with verification result
        """
        result = self.calculate_hash(file_path, algorithm)
        
        if not result['success']:
            return result
        
        calculated = result['hash_value'].lower()
        expected = expected_hash.lower()
        match = calculated == expected
        
        return {
            'success': True,
            'match': match,
            'file_path': file_path,
            'file_size': result['file_size'],
            'algorithm': algorithm.lower(),
            'expected_hash': expected,
            'calculated_hash': calculated
        }
    
    def verify_checksum_file(self, checksum_file: str) -> Dict[str, Any]:
        """
        Verify multiple files from a checksum file.
        
        Supports formats:
        - MD5SUM: <hash>  <filename>
        - SHA256SUM: <hash>  <filename>
        
        Args:
            checksum_file: Path to checksum file
        
        Returns:
            Dictionary with verification results
        """
        if not os.path.exists(checksum_file):
            return {'success': False, 'error': f"Checksum file not found: {checksum_file}"}
        
        try:
            results = []
            base_dir = os.path.dirname(checksum_file)
            
            # Detect algorithm from filename
            filename = os.path.basename(checksum_file).lower()
            if 'md5' in filename:
                algorithm = 'md5'
            elif 'sha1' in filename:
                algorithm = 'sha1'
            elif 'sha512' in filename:
                algorithm = 'sha512'
            else:
                algorithm = 'sha256'  # default
            
            with open(checksum_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse line: <hash>  <filename>
                    parts = line.split(None, 1)
                    if len(parts) != 2:
                        results.append({
                            'line': line_num,
                            'error': 'Invalid format',
                            'success': False
                        })
                        continue
                    
                    expected_hash, filename = parts
                    file_path = os.path.join(base_dir, filename)
                    
                    # Verify
                    result = self.verify_checksum(file_path, expected_hash, algorithm)
                    result['line'] = line_num
                    result['filename'] = filename
                    results.append(result)
            
            # Summary
            total = len(results)
            passed = sum(1 for r in results if r.get('match', False))
            failed = sum(1 for r in results if r.get('success', True) and not r.get('match', False))
            errors = sum(1 for r in results if not r.get('success', True))
            
            return {
                'success': True,
                'checksum_file': checksum_file,
                'algorithm': algorithm,
                'total': total,
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'results': results
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
