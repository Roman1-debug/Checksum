# checksum

```
  ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██╗   ██╗███╗   ███╗
 ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██║   ██║████╗ ████║
 ██║     ███████║█████╗  ██║     █████╔╝ ███████╗██║   ██║██╔████╔██║
 ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ╚════██║██║   ██║██║╚██╔╝██║
 ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████║╚██████╔╝██║ ╚═╝ ██║
  ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝
```

**File Integrity Verification Tool**

A professional file integrity verification tool designed for cybersecurity professionals. Verify file checksums against known values to detect tampering, corruption, or unauthorized modifications.

## Features

- **Single File Verification**: Verify individual files against expected checksums
- **Batch Verification**: Verify multiple files from checksum files (MD5SUMS, SHA256SUMS, etc.)
- **Multiple Algorithms**: MD5, SHA1, SHA256, SHA512
- **Beautiful Output**: Rich, colored terminal output with detailed results
- **Fast Processing**: Efficient chunked file reading for large files
- **Multiple Formats**: Output as human-readable text or JSON
- **Professional**: Designed to look and feel like real security tools
- **Verbose Mode**: Detailed output with hash comparisons
- **Quiet Mode**: Minimal output for scripting

## Installation

### Method 1: Using pipx (Recommended)

**pipx** installs Python CLI tools in isolated environments, preventing conflicts.

```bash
# Install pipx (if not already installed)
sudo apt install pipx        # Debian/Ubuntu/Kali
brew install pipx            # macOS

# Ensure pipx is in PATH
pipx ensurepath

# Install checksum
git clone https://github.com/Roman1-debug/checksum.git
cd checksum
pipx install .
```

### Method 2: From Source (Virtual Environment)

```bash
# Clone the repository
git clone https://github.com/Roman1-debug/checksum.git
cd checksum

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install .

# Use (while venv is active)
checksum --version
```

### Requirements

- Python 3.8 or higher
- rich >= 13.0.0

## Usage

### Calculate Checksum

```bash
# Calculate SHA256 checksum (default)
checksum calc -f file.zip

# Calculate with specific algorithm
checksum calc -f document.pdf -a md5
checksum calc -f image.jpg -a sha512

# JSON output
checksum calc -f file.tar.gz -o json
```

### Verify Single File

```bash
# Verify file against expected SHA256 hash
checksum verify -f file.zip -H abc123def456...

# Verify with specific algorithm
checksum verify -f file.zip -H abc123... -a sha256

# Verbose mode (shows both hashes)
checksum verify -f file.zip -H abc123... -v
```

### Verify from Checksum File

```bash
# Verify files from SHA256SUMS file
checksum verify -c SHA256SUMS

# Verify from MD5SUMS file
checksum verify -c MD5SUMS

# Verbose mode (show all files, not just failures)
checksum verify -c SHA256SUMS -v

# JSON output
checksum verify -c SHA256SUMS -o json
```

## Command-Line Options

### Calculate Command

```
checksum calc [options]

Required:
  -f, --file FILE       File to hash

Options:
  -a, --algorithm {md5,sha1,sha256,sha512}
                        Hash algorithm [default: sha256]
  -o, --output {text,json}
                        Output format [default: text]
  -v, --verbose         Verbose output
  -q, --quiet          Quiet mode (no banner)
```

### Verify Command

```
checksum verify [options]

Required (one of):
  -f, --file FILE       File to verify (requires --hash)
  -c, --checksum-file FILE
                        Checksum file (MD5SUMS, SHA256SUMS, etc.)

Options:
  -H, --hash HASH       Expected hash value (for single file)
  -a, --algorithm {md5,sha1,sha256,sha512}
                        Hash algorithm [default: sha256]
  -o, --output {text,json}
                        Output format [default: text]
  -v, --verbose         Verbose output
  -q, --quiet          Quiet mode (no banner)
```

## Checksum File Format

Checksum files should follow the standard format used by `md5sum`, `sha256sum`, etc.:

```
<hash>  <filename>
```

**Example SHA256SUMS file:**
```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  file1.txt
d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f  file2.txt
5f4dcc3b5aa765d61d8327deb882cf99  file3.dat
```

**Notes:**
- Two spaces between hash and filename
- Filenames are relative to the checksum file location
- Lines starting with `#` are treated as comments
- Algorithm is auto-detected from filename (MD5SUMS, SHA256SUMS, etc.)

## Output Examples

### Calculate Checksum
```
[OK] Checksum calculated successfully!
File: document.pdf
Size: 2.45 MB
Algorithm: SHA256

╭─────────────── SHA256 Checksum ───────────────╮
│ e3b0c44298fc1c149afbf4c8996fb92427ae41e464 │
│ 9b934ca495991b7852b855                      │
╰───────────────────────────────────────────────╯
```

### Verify Single File (Success)
```
[OK] CHECKSUM VERIFIED
File: file.zip
Size: 1.23 MB
Algorithm: SHA256
```

### Verify Single File (Failure)
```
[FAIL] CHECKSUM MISMATCH
File: file.zip
Size: 1.23 MB
Algorithm: SHA256

Expected:  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
Calculated: d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f

[WARN] File may be corrupted or tampered!
```

### Verify Checksum File
```
Checksum Verification Results
File: SHA256SUMS
Algorithm: SHA256

╭──────────┬───────╮
│ [OK] Passed │    45 │
│ [FAIL] Failed │     2 │
│ [WARN] Errors │     1 │
│ Total    │    48 │
╰──────────┴───────╯

Detailed Results:

╭─────────────────┬────────┬──────────╮
│ File            │ Status │ Details  │
├─────────────────┼────────┼──────────┤
│ corrupted.zip   │   [FAIL]    │ Mismatch │
│ missing.txt     │   [WARN]    │ Not found│
╰─────────────────┴────────┴──────────╯

[WARN] Some files failed verification!
```

## Development

### Project Structure

```
checksum/
├── checksum/
│   ├── __init__.py      # Package metadata
│   ├── cli.py           # CLI interface
│   └── core.py          # Checksum verification engine
├── requirements.txt     # Dependencies
├── setup.py            # Installation script
├── README.md           # This file
├── LICENSE             # MIT License
└── .gitignore          # Git ignore rules
```

### Testing

```bash
# Calculate checksum
checksum calc -f README.md

# Create a checksum file
checksum calc -f file1.txt -q | cut -d' ' -f1 > SHA256SUMS
echo "  file1.txt" >> SHA256SUMS

# Verify from checksum file
checksum verify -c SHA256SUMS

# Test mismatch detection
echo "invalid_hash  file1.txt" > BAD_SUMS
checksum verify -c BAD_SUMS
```

## Use Cases

- **Download Verification**: Verify downloaded files match published checksums
- **File Integrity Monitoring**: Detect unauthorized file modifications
- **Forensics**: Verify evidence integrity in digital forensics
- **Software Distribution**: Verify software packages before installation
- **Backup Verification**: Ensure backups match original files
- **Malware Detection**: Compare file hashes against known malware databases
- **Compliance**: Meet regulatory requirements for data integrity

## Security Considerations

- **Algorithm Choice**: Use SHA256 or SHA512 for security-critical applications
- **MD5/SHA1**: Only use for compatibility; they're cryptographically broken
- **Checksum Files**: Protect checksum files from tampering (use signatures)
- **Exit Codes**: Script-friendly exit codes (0=success, 1=failure)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Roman**
- GitHub: [@Roman1-debug](https://github.com/Roman1-debug)

## Contributing

Contributions, issues, and feature requests are welcome!

## Show Your Support

Give a star if this project helped you!

---

**Note**: This tool is designed for legitimate security purposes and system administration. Always ensure you have permission before verifying files you don't own.
