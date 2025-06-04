# EvasionHub CLI

A command-line client for the EvasionHub Python obfuscation service. This tool provides a simple interface to obfuscate Python files using the EvasionHub.com API directly from your terminal.

![image](https://github.com/user-attachments/assets/ae53a45f-a001-41e9-86ba-c154809b5d6c)

## Overview

EvasionHub CLI is a Python-based command-line tool that communicates with the EvasionHub API to obfuscate Python source code.

## Features

- Simple command-line interface for the Polymorphic Python code obfuscation project I have hosted at [evasionhub.com](https://evasionhub.com)
- Detailed obfuscation statistics and performance metrics


## Requirements

- `requests` library for HTTP communication

## Installation

1. Download the `evasionhub-cli.py` script
2. Install the required dependency:
   
   `pip install requests`
   

## Usage

### Basic Usage


`python3 evasionhub-cli.py <input_file> <output_file>`


### Examples

Obfuscate a Python file:

`python3 evasionhub-cli.py script.py obfuscated_script.py`


Enable verbose output for detailed information:

`python3 evasionhub-cli.py input.py output.py --verbose`


Set a custom timeout (useful for large files):

`python3 evasionhub-cli.py script.py obfuscated.py --timeout 20`


Disable coloured output (useful for CI/CD environments):

`python3 evasionhub-cli.py script.py obfuscated.py --no-colour`


### Command-Line Options

| Option | Description |
|--------|-------------|
| `input_file` | Path to the input Python file to obfuscate |
| `output_file` | Path where the obfuscated file will be saved |
| `-v, --verbose` | Enable verbose output with detailed statistics |
| `--timeout SECONDS` | Set request timeout in seconds (default: 120) |
| `--no-colour, --no-color` | Disable coloured terminal output |
| `-h, --help` | Show help message and exit |

## Output

Upon completion, you'll see a summary including:
- Processing time
- File size comparison (before/after)
- Obfuscation statistics (compression ratio, mutation ID, etc.)


## API Information

This tool communicates with the EvasionHub API at `https://evasionhub.com/obfuscate`. 

The service:

- Accepts Python source code for obfuscation
- Has a file size limit of 2MB
- Implements rate limiting for fair usage
- Returns obfuscated code with detailed statistics generated relating to the obfuscation operations.

## Troubleshooting

### Common Issues

**"File too large" error**: The API has a 2MB limit. Consider splitting large files.

**"Rate limited" error**: Wait a moment before making another request. The API implements rate limiting of 20 req p/m to ensure fair usage.

**Network connection errors**: Check your internet connection and ensure you can access `evasionhub.com`.

**Permission denied**: Ensure you have read permissions for the input file and write permissions for the output directory.

### Verbose Mode

Use the `--verbose` flag to get detailed information about:
- API endpoint and payload size
- HTTP response codes and timing
- Detailed obfuscation statistics
- Network request details

## Examples

### Basic Obfuscation
```bash
# Obfuscate a simple script
python3 evasionhub-cli.py hello_world.py obfuscated_hello.py
```

### Batch Processing
```bash
# Obfuscate multiple files
for file in *.py; do
    python3 evasionhub-cli.py "$file" "obfuscated_$file"
done
```

### CI/CD Integration
```bash
# Use in automated environments
python3 evasionhub-cli.py src/main.py dist/main.py --no-colour --timeout 300
```

## Support

For support with the [Evasionhub service](https://evasionhub.com) or API, feel free to leave a message to @stuub on discord
