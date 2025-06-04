#!/usr/bin/env python3
"""
EvasionHub API Wrapper
https://evasionhub.com

Usage: python3 evasionhub-cli.py <input_file> <output_file> [options]
"""

import sys
import argparse
import json
import requests
import time
from pathlib import Path
import os
from typing import Dict, Any, Optional, Tuple

API_URL = "https://evasionhub.com/obfuscate"
USER_AGENT = "OSI API"
DEFAULT_TIMEOUT = 120
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


class Colours:
    # Regulars
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GREY = '\033[90m'

    # Bold col
    BRED = '\033[1;91m'
    BGREEN = '\033[1;92m'
    BYELLOW = '\033[1;93m'
    BBLUE = '\033[1;94m'
    BPURPLE = '\033[1;95m'
    BCYAN = '\033[1;96m'
    BWHITE = '\033[1;97m'

    # Formatting
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    # Semantic
    SUCCESS = '\033[1;92m'    # Bold green
    ERROR = '\033[1;91m'      # Bold red
    WARNING = '\033[1;93m'    # Bold yellow
    INFO = '\033[1;91m'
    # INFO = '\033[1;94m'       # Bold blue
    ACCENT = '\033[1;96m'     # Bold cyan


class TerminalOutput:

    def __init__(self, use_colours: bool = True, indent_size: int = 2):
        self.use_colours = use_colours
        self.indent_size = indent_size

    def _colour(self, colour_code: str) -> str:
        """Return colour code if colours are enabled, empty string otherwise"""
        return colour_code if self.use_colours else ""

    def _indent(self, level: int) -> str:
        """Generate indentation string for given level"""
        return "  " * level


    def format_size(self, size_bytes: int) -> str:
        """file size with their respective units. p.s fuck you im not supporting GB"""
        bold_start = self._colour(Colours.BOLD)
        bold_end = self._colour(Colours.END)

        if size_bytes < 1024:
            return f"{bold_start}{size_bytes}{bold_end} bytes"
        elif size_bytes < 1024 * 1024:
            size_kb = size_bytes / 1024
            return f"{bold_start}{size_kb:.1f}{bold_end} KB"
        else:
            size_mb = size_bytes / (1024 * 1024)
            return f"{bold_start}{size_mb:.2f}{bold_end} MB"

    def format_time(self, seconds: float) -> str:
        """request duration"""
        bold_start = self._colour(Colours.BOLD)
        bold_end = self._colour(Colours.END)

        if seconds < 1:
            return f"{bold_start}{seconds*1000:.0f}{bold_end}ms"
        else:
            return f"{bold_start}{seconds:.2f}{bold_end}s"

    def format_path(self, path: str) -> str:
        """file paths"""
        accent_start = self._colour(Colours.ERROR)
        accent_end = self._colour(Colours.END)
        return f"{accent_start}{path}{accent_end}"

    def format_value(self, value: Any) -> str:
        """Format the good shit so you kow its the good shit"""
        bold_start = self._colour(Colours.BOLD)
        bold_end = self._colour(Colours.END)
        return f"{bold_start}{value}{bold_end}"


    def banner(self) -> None:
        """the best bit"""
        cyan_start = self._colour(Colours.BCYAN)
        red_start = self._colour(Colours.BRED)
        white_start = self._colour(Colours.BWHITE)
        yellow_start = self._colour(Colours.BYELLOW)
        purple_start = self._colour(Colours.BPURPLE)
        colour_end = self._colour(Colours.END)

        banner = f'''


                                    {red_start}d8b                         888               888{colour_end}
                                    {red_start}Y8P                         888               888{colour_end}
                                                                {red_start}888               888{colour_end}
{white_start} .d88b.  888  888  8888b.  .d8888b  888  .d88b.  88888b.{colour_end}        {red_start}88888b.  888  888 88888b.{colour_end}
{white_start}d8P  Y8b 888  888     "88b 88K      888 d88""88b 888 "88b{colour_end}       {red_start}888 "88b 888  888 888 "88b{colour_end}
{white_start}88888888 Y88  88P .d888888 "Y8888b. 888 888  888 888  888{colour_end}       {red_start}888  888 888  888 888  888{colour_end}
{white_start}Y8b.      Y8bd8P  888  888      X88 888 Y88..88P 888  888{colour_end}       {red_start}888  888 Y88b 888 888 d88P{colour_end}
 {white_start}"Y8888    Y88P   "Y888888  88888P' 888  "Y88P"  888  888{colour_end}       {red_start}888  888  "Y88888 88888P"{colour_end}


{colour_end}
{white_start}                    Python Obfuscation API Client{colour_end}
{yellow_start}                         evasionhub.com{colour_end}
{purple_start}                             @stuub{colour_end}
'''
        print(banner)

    def step(self, step_num: int, total_steps: int, description: str) -> None:
        """Step header & progress indicator"""
        info_colour = self._colour(Colours.INFO)
        white_colour = self._colour(Colours.BWHITE)
        colour_end = self._colour(Colours.END)

        progress = f"[{step_num}/{total_steps}]"
        print(f"\n{info_colour}▶ {progress}{colour_end} {white_colour}{description}{colour_end}")

    def success(self, message: str, indent: int = 0) -> None:
        """success message"""
        success_colour = self._colour(Colours.SUCCESS)
        colour_end = self._colour(Colours.END)
        spaces = self._indent(indent)
        print(f"{spaces}{success_colour}✓{colour_end} {message}")

    def error(self, message: str, indent: int = 0) -> None:
        """error message"""
        error_colour = self._colour(Colours.ERROR)
        colour_end = self._colour(Colours.END)
        spaces = self._indent(indent)
        print(f"{spaces}{error_colour}✗{colour_end} {message}")

    def warning(self, message: str, indent: int = 0) -> None:
        """warning message"""
        warning_colour = self._colour(Colours.WARNING)
        colour_end = self._colour(Colours.END)
        spaces = self._indent(indent)
        print(f"{spaces}{warning_colour}⚠{colour_end} {message}")

    def info(self, message: str, indent: int = 0) -> None:
        """info"""
        info_colour = self._colour(Colours.INFO)
        colour_end = self._colour(Colours.END)
        spaces = self._indent(indent)
        print(f"{spaces}{info_colour}ℹ{colour_end} {message}")

    def detail(self, label: str, value: str, indent: int = 1) -> None:
        """Print detail (label & value)"""
        grey_colour = self._colour(Colours.GREY)
        dim_colour = self._colour(Colours.DIM)
        colour_end = self._colour(Colours.END)
        spaces = self._indent(indent)
        print(f"{spaces}{grey_colour}•{colour_end} {dim_colour}{label}:{colour_end} {value}")

    def metric(self, label: str, value: Any, unit: str = "", indent: int = 1) -> None:
        """Print metrics"""
        cyan_colour = self._colour(Colours.CYAN)
        colour_end = self._colour(Colours.END)
        spaces = self._indent(indent)
        formatted_value = self.format_value(value) + unit
        print(f"{spaces}{cyan_colour}▸{colour_end} {label}: {formatted_value}")

    def summary(self, input_file: str, output_file: str, processing_time: float,
                stats: Dict[str, Any], input_size: Optional[int], output_size: Optional[int]) -> None:
        """jank for output result"""
        green_colour = self._colour(Colours.BGREEN)
        green_border = self._colour(Colours.GREEN)
        white_colour = self._colour(Colours.BWHITE)
        cyan_colour = self._colour(Colours.BCYAN)
        cyan_bullet = self._colour(Colours.CYAN)
        yellow_colour = self._colour(Colours.BYELLOW)
        yellow_border = self._colour(Colours.BYELLOW)
        yellow_bullet = self._colour(Colours.YELLOW)
        red_border = self._colour(Colours.BRED)
        purple_colour = self._colour(Colours.BPURPLE)
        colour_end = self._colour(Colours.END)

        print(f"\n{red_border}╭─ {colour_end}{white_colour}Obfuscation Complete{colour_end}{red_border} ─╮{colour_end}")
        print(f"{red_border}│{colour_end}")
        print(f"{red_border}│{colour_end} {white_colour}Input:{colour_end}  {self.format_path(input_file)}")
        print(f"{red_border}│{colour_end} {white_colour}Output:{colour_end} {self.format_path(output_file)}")
        print(f"{red_border}│{colour_end}")

        # perf metrics
        print(f"{red_border}│{colour_end} {yellow_colour}Performance:{colour_end}")
        print(f"{red_border}│{colour_end}   {yellow_bullet}•{colour_end} Processing time: {self.format_time(processing_time)}")

        # size comparison
        if input_size and output_size:
            ratio = output_size / input_size
            size_change = f"{ratio:.1f}x" if ratio >= 1 else f"0.{int(ratio*10)}x"
            print(f"{red_border}│{colour_end}   {yellow_bullet}•{colour_end} Size change: {self.format_size(input_size)} → {self.format_size(output_size)} ({self.format_value(size_change)})")

        # obfuscation stats
        if stats:
            print(f"{red_border}│{colour_end}")
            print(f"{red_border}│{colour_end} {purple_colour}Obfuscation Details:{colour_end}")

            if 'compression_ratio' in stats:
                print(f"{red_border}│{colour_end}   {purple_colour}•{colour_end} Compression ratio: {self.format_value(stats['compression_ratio'])}")

            if 'mutation_id' in stats:
                print(f"{red_border}│{colour_end}   {purple_colour}•{colour_end} Mutation ID: {self.format_value(stats['mutation_id'])}")

            if 'compression_layers' in stats:
                print(f"{red_border}│{colour_end}   {purple_colour}•{colour_end} Compression layers: {self.format_value(stats['compression_layers'])}")

        print(f"{red_border}│{colour_end}")
        print(f"{red_border}╰─────────────────────────╯{colour_end}")


class EvasionHubClient:
    """API communication with EvasionHub"""

    def __init__(self, api_url: str = API_URL, user_agent: str = USER_AGENT, timeout: int = DEFAULT_TIMEOUT):
        self.api_url = api_url
        self.user_agent = user_agent
        self.timeout = timeout

    def obfuscate(self, code: str, output: TerminalOutput, verbose: bool = False) -> Dict[str, Any]:
        """request to EvasionHub API"""
        payload = {"code": code}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
            "Accept": "application/json"
        }

        payload_size = len(json.dumps(payload))

        output.info("Sending obfuscation request...", indent=1)
        output.detail("API endpoint", output.format_value(self.api_url), indent=2)
        output.detail("Payload size", output.format_size(payload_size), indent=2)

        if verbose:
            output.detail("User-Agent", output.format_value(self.user_agent), indent=2)
            output.detail("Timeout", output.format_time(self.timeout), indent=2)

        try:
            start_time = time.time()

            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            elapsed_time = time.time() - start_time

            output.success(f"Request completed in {output.format_time(elapsed_time)}", indent=1)

            if verbose:
                output.detail("Status code", output.format_value(response.status_code), indent=2)
                output.detail("Response size", output.format_size(len(response.content)), indent=2)

            # deal with httperror
            if response.status_code == 413:
                raise requests.RequestException("File too large - exceeds 2MB limit")
            elif response.status_code == 429:
                raise requests.RequestException("Rate limited - please try again later")
            elif response.status_code != 200:
                raise requests.RequestException(f"HTTP {response.status_code}: {response.text}")

            # parse JSON resp
            try:
                result = response.json()
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON response from server")

            return result

        except requests.exceptions.Timeout:
            raise requests.RequestException(f"Request timed out after {output.format_time(self.timeout)}")
        except requests.exceptions.ConnectionError:
            raise requests.RequestException("Failed to connect to EvasionHub.com")
        except requests.exceptions.RequestException as e:
            if "File too large" in str(e) or "Rate limited" in str(e):
                raise
            raise requests.RequestException(f"Network error: {e}")


class FileProcessor:
    """file operations and validation"""

    @staticmethod
    def validate_file_size(file_path: str) -> int:
        """Validate file size against max (2mb)"""
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_size} bytes (maximum: {MAX_FILE_SIZE} bytes)")
        return file_size

    @staticmethod
    def read_input_file(file_path: str, output: TerminalOutput) -> str:
        """yumyum give me code"""
        try:
            input_path = Path(file_path)

            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {output.format_path(file_path)}")

            if not input_path.is_file():
                raise ValueError(f"Input path is not a file: {output.format_path(file_path)}")

            file_size = FileProcessor.validate_file_size(file_path)
            size_formatted = output.format_size(file_size)

            if file_size > 100 * 1024:
                output.warning(f"Large file detected: {size_formatted}", indent=1)

            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                raise ValueError("Input file is empty")

            output.success(f"Read input file: {output.format_path(file_path)}", indent=1)
            output.detail("File size", size_formatted, indent=2)
            output.detail("Lines", output.format_value(len(content.splitlines())), indent=2)

            return content

        except UnicodeDecodeError:
            raise ValueError("Input file is not valid UTF-8 text")

    @staticmethod
    def write_output_file(output_path: str, obfuscated_code: str, output: TerminalOutput) -> int:
        """i ate too much mom, im gonna sick"""
        try:
            output_file = Path(output_path)

            # Create parent directories if they don't exist
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Write obfuscated code
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated_code)

            # Check written file size
            file_size = output_file.stat().st_size
            size_formatted = output.format_size(file_size)

            output.success(f"Obfuscated code written to: {output.format_path(output_path)}", indent=1)
            output.detail("Output size", size_formatted, indent=2)
            output.detail("Lines", output.format_value(len(obfuscated_code.splitlines())), indent=2)

            return file_size

        except PermissionError:
            raise ValueError(f"Permission denied writing to: {output.format_path(output_path)}")
        except OSError as e:
            raise ValueError(f"Failed to write output file: {e}")


class ResponseParser:
    """API resp parsing"""

    @staticmethod
    def parse_response(response: Dict[str, Any], output: TerminalOutput, verbose: bool = False) -> Tuple[str, Dict[str, Any], float]:
        """Parse API response"""
        if not isinstance(response, dict):
            raise ValueError("Invalid response format")

        # was successful?
        if not response.get("success", False):
            error_msg = response.get("error", "Unknown error occurred")
            raise ValueError(f"Obfuscation failed: {error_msg}")

        # yes? ok great
        obfuscated_code = response.get("obfuscated_code")
        if not obfuscated_code:
            raise ValueError("No obfuscated code in response")

        # because stats r cool #nerdemoji
        stats = response.get("stats", {})
        processing_time = response.get("processing_time", 0)

        output.success("API response parsed successfully", indent=1)
        output.detail("Processing time", output.format_time(processing_time), indent=2)
        output.detail("Output size", output.format_size(len(obfuscated_code)), indent=2)

        if verbose and stats:
            output.info("Obfuscation statistics:", indent=1)
            for key, value in stats.items():
                label = key.replace('_', ' ').title()
                output.metric(label, value, indent=2)

        return obfuscated_code, stats, processing_time


class EvasionHubCLI:
    """application class"""

    def __init__(self):
        self.output = TerminalOutput()
        self.client = EvasionHubClient()
        self.file_processor = FileProcessor()
        self.response_parser = ResponseParser()

    def run(self) -> int:
        """Main app entry point"""
        parser = self._create_argument_parser()

        if len(sys.argv) < 3:
            parser.print_help()
            return 1

        args = parser.parse_args()

        # ticker 4 client timeout
        self.client.timeout = args.timeout

        # Disable colours if requested (boooooooring)
        if hasattr(args, 'no_colour') and args.no_colour:
            self.output.use_colours = False

        # Print banner unless disabled (boooooooring)
        if not getattr(args, 'no_banner', False):
            self.output.banner()

        return self._process_obfuscation(args)

    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """lord n savior argparse giving me the ability to add options no one cares about"""
        parser = argparse.ArgumentParser(
            description="EvasionHub API Client - Obfuscate Python files using evasionhub.com",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s script.py obfuscated.py
  %(prog)s input.py output.py --verbose
  %(prog)s ~/code/script.py ~/output/obfuscated.py
            """
        )

        parser.add_argument('input_file', help='Path to input Python file')
        parser.add_argument('output_file', help='Path to output obfuscated file')
        parser.add_argument('-v', '--verbose', action='store_true',
                          help='Enable verbose output')
        parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT,
                          help=f'Request timeout in seconds (default: {DEFAULT_TIMEOUT})')
        parser.add_argument('--no-colour', '--no-color', action='store_true',
                          help='Disable coloured output')

        return parser

    def _process_obfuscation(self, args) -> int:
        """do thing with obf request"""
        input_size = None
        output_size = None

        try:
            # 1: Read #nerdemoji
            self.output.step(1, 4, "Reading input...")
            python_code = self.file_processor.read_input_file(args.input_file, self.output)
            input_size = len(python_code.encode('utf-8'))

            # 2: Send req to api pls
            self.output.step(2, 4, "Sending obfuscation request...")
            api_response = self.client.obfuscate(python_code, self.output, args.verbose)

            # 3: look at it for a moment
            self.output.step(3, 4, "Processing response...")
            obfuscated_code, stats, processing_time = self.response_parser.parse_response(
                api_response, self.output, args.verbose
            )

            # 4: your package, mlord
            self.output.step(4, 4, "Writing output file...")
            output_size = self.file_processor.write_output_file(
                args.output_file, obfuscated_code, self.output
            )

            # talk shit real loud
            self.output.summary(
                args.input_file, args.output_file, processing_time,
                stats, input_size, output_size
            )

            return 0

        except KeyboardInterrupt:
            self.output.error("Operation cancelled by user :(")
            return 130
        except FileNotFoundError as e:
            self.output.error(str(e))
            return 2
        except ValueError as e:
            self.output.error(str(e))
            return 1
        except requests.RequestException as e:
            self.output.error(f"API request failed: {e}")
            return 3
        except Exception as e:
            self.output.error(f"Unexpected error: {e}")
            if args.verbose:
                grey_colour = self.output._colour(Colours.GREY)
                colour_end = self.output._colour(Colours.END)
                print(f"\n{grey_colour}Stack trace:{colour_end}")
                import traceback
                traceback.print_exc()
            return 1


def main() -> int:
    """Application entry point"""
    cli = EvasionHubCLI()
    return cli.run()


if __name__ == "__main__":
    exit(main())
