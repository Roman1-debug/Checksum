#!/usr/bin/env python3
"""
checksum CLI - Professional file integrity verification tool
"""

import sys
import os
import argparse
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import box

from checksum.core import ChecksumEngine
from checksum import __version__


console = Console()


BANNER = """
[cyan]
             
        
                 
                 
       
              
[/cyan]
[dim]File Integrity Verification Tool | v{version}[/dim]
"""


def print_banner(quiet: bool = False):
    """Print the tool banner."""
    if not quiet:
        console.print(BANNER.format(version=__version__))


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def verify_single_file(args):
    """Verify a single file against expected hash."""
    engine = ChecksumEngine()
    
    # Validate file
    if not os.path.exists(args.file):
        console.print(f"[red]✗[/red] File not found: {args.file}")
        return 1
    
    # Verify
    if not args.quiet:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Verifying {args.algorithm.upper()} checksum...", total=100)
            result = engine.verify_checksum(args.file, args.hash, args.algorithm)
            progress.update(task, completed=100)
    else:
        result = engine.verify_checksum(args.file, args.hash, args.algorithm)
    
    # Display result
    if not result['success']:
        console.print(f"[red]✗[/red] Error: {result['error']}")
        return 1
    
    if args.output == "json":
        console.print(json.dumps(result, indent=2))
        return 0 if result['match'] else 1
    
    # Text output
    if result['match']:
        console.print(f"\n[green]✓ CHECKSUM VERIFIED[/green]")
        console.print(f"[dim]File:[/dim] [cyan]{result['file_path']}[/cyan]")
        console.print(f"[dim]Size:[/dim] [yellow]{format_size(result['file_size'])}[/yellow]")
        console.print(f"[dim]Algorithm:[/dim] [yellow]{result['algorithm'].upper()}[/yellow]")
        
        if args.verbose:
            console.print(f"\n[dim]Expected:[/dim]  [green]{result['expected_hash']}[/green]")
            console.print(f"[dim]Calculated:[/dim] [green]{result['calculated_hash']}[/green]")
        
        return 0
    else:
        console.print(f"\n[red]✗ CHECKSUM MISMATCH[/red]")
        console.print(f"[dim]File:[/dim] [cyan]{result['file_path']}[/cyan]")
        console.print(f"[dim]Size:[/dim] [yellow]{format_size(result['file_size'])}[/yellow]")
        console.print(f"[dim]Algorithm:[/dim] [yellow]{result['algorithm'].upper()}[/yellow]")
        console.print(f"\n[dim]Expected:[/dim]  [green]{result['expected_hash']}[/green]")
        console.print(f"[dim]Calculated:[/dim] [red]{result['calculated_hash']}[/red]")
        
        console.print(f"\n[yellow]⚠[/yellow] [bold]File may be corrupted or tampered![/bold]")
        return 1


def verify_checksum_file(args):
    """Verify multiple files from a checksum file."""
    engine = ChecksumEngine()
    
    # Validate checksum file
    if not os.path.exists(args.checksum_file):
        console.print(f"[red]✗[/red] Checksum file not found: {args.checksum_file}")
        return 1
    
    # Verify
    if not args.quiet:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Verifying checksums...", total=None)
            result = engine.verify_checksum_file(args.checksum_file)
    else:
        result = engine.verify_checksum_file(args.checksum_file)
    
    # Display results
    if not result['success']:
        console.print(f"[red]✗[/red] Error: {result['error']}")
        return 1
    
    if args.output == "json":
        console.print(json.dumps(result, indent=2))
        return 0 if result['failed'] == 0 and result['errors'] == 0 else 1
    
    # Text output - Summary
    console.print(f"\n[cyan]Checksum Verification Results[/cyan]")
    console.print(f"[dim]File:[/dim] [cyan]{result['checksum_file']}[/cyan]")
    console.print(f"[dim]Algorithm:[/dim] [yellow]{result['algorithm'].upper()}[/yellow]\n")
    
    # Summary table
    summary_table = Table(box=box.ROUNDED, show_header=False)
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Count", justify="right")
    
    summary_table.add_row("[green]✓ Passed[/green]", f"[green]{result['passed']}[/green]")
    summary_table.add_row("[red]✗ Failed[/red]", f"[red]{result['failed']}[/red]")
    summary_table.add_row("[yellow]⚠ Errors[/yellow]", f"[yellow]{result['errors']}[/yellow]")
    summary_table.add_row("[cyan]Total[/cyan]", f"[cyan]{result['total']}[/cyan]")
    
    console.print(summary_table)
    
    # Detailed results if verbose or if there are failures
    if args.verbose or result['failed'] > 0 or result['errors'] > 0:
        console.print(f"\n[cyan]Detailed Results:[/cyan]\n")
        
        details_table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        details_table.add_column("File", style="cyan")
        details_table.add_column("Status", justify="center")
        details_table.add_column("Details")
        
        for r in result['results']:
            filename = r.get('filename', 'Unknown')
            
            if not r.get('success', True):
                # Error
                error = r.get('error', 'Unknown error')
                details_table.add_row(filename, "[yellow]⚠[/yellow]", f"[yellow]{error}[/yellow]")
            elif r.get('match', False):
                # Passed
                if args.verbose:
                    details_table.add_row(filename, "[green]✓[/green]", "[dim]OK[/dim]")
            else:
                # Failed
                details_table.add_row(
                    filename,
                    "[red]✗[/red]",
                    f"[red]Mismatch[/red]"
                )
        
        console.print(details_table)
    
    # Exit code
    if result['failed'] > 0 or result['errors'] > 0:
        console.print(f"\n[yellow]⚠[/yellow] [bold]Some files failed verification![/bold]")
        return 1
    else:
        console.print(f"\n[green]✓[/green] [bold]All files verified successfully![/bold]")
        return 0


def calculate_checksum(args):
    """Calculate checksum for a file."""
    engine = ChecksumEngine()
    
    # Validate file
    if not os.path.exists(args.file):
        console.print(f"[red]✗[/red] File not found: {args.file}")
        return 1
    
    # Calculate
    if not args.quiet:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Calculating {args.algorithm.upper()} hash...", total=100)
            result = engine.calculate_hash(args.file, args.algorithm)
            progress.update(task, completed=100)
    else:
        result = engine.calculate_hash(args.file, args.algorithm)
    
    # Display result
    if not result['success']:
        console.print(f"[red]✗[/red] Error: {result['error']}")
        return 1
    
    if args.output == "json":
        console.print(json.dumps(result, indent=2))
    else:
        console.print(f"\n[green]✓[/green] Checksum calculated successfully!")
        console.print(f"[dim]File:[/dim] [cyan]{result['file_path']}[/cyan]")
        console.print(f"[dim]Size:[/dim] [yellow]{format_size(result['file_size'])}[/yellow]")
        console.print(f"[dim]Algorithm:[/dim] [yellow]{result['algorithm'].upper()}[/yellow]\n")
        
        panel = Panel(
            result['hash_value'],
            title=f"[cyan]{result['algorithm'].upper()} Checksum[/cyan]",
            border_style="green",
            box=box.ROUNDED
        )
        console.print(panel)
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="checksum - Professional file integrity verification tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Calculate checksum
  checksum calc -f file.zip
  checksum calc -f file.zip -a sha512
  
  # Verify single file
  checksum verify -f file.zip -H abc123...
  checksum verify -f file.zip -H abc123... -a sha256
  
  # Verify from checksum file
  checksum verify -c SHA256SUMS
  checksum verify -c MD5SUMS -v

Checksum File Format:
  <hash>  <filename>
  
  Example (SHA256SUMS):
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  file1.txt
  d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f  file2.txt
        """
    )
    
    parser.add_argument("--version", action="version", version=f"checksum v{__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Calculate command
    calc_parser = subparsers.add_parser("calc", help="Calculate file checksum")
    calc_parser.add_argument("-f", "--file", required=True, help="File to hash")
    calc_parser.add_argument(
        "-a", "--algorithm",
        choices=["md5", "sha1", "sha256", "sha512"],
        default="sha256",
        help="Hash algorithm [default: sha256]"
    )
    calc_parser.add_argument("-o", "--output", choices=["text", "json"], default="text", help="Output format")
    calc_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    calc_parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify file checksum")
    verify_group = verify_parser.add_mutually_exclusive_group(required=True)
    verify_group.add_argument("-f", "--file", help="File to verify")
    verify_group.add_argument("-c", "--checksum-file", help="Checksum file (MD5SUMS, SHA256SUMS, etc.)")
    
    verify_parser.add_argument("-H", "--hash", help="Expected hash value (for single file)")
    verify_parser.add_argument(
        "-a", "--algorithm",
        choices=["md5", "sha1", "sha256", "sha512"],
        default="sha256",
        help="Hash algorithm [default: sha256]"
    )
    verify_parser.add_argument("-o", "--output", choices=["text", "json"], default="text", help="Output format")
    verify_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    verify_parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        return 0
    
    # Print banner
    print_banner(args.quiet or args.output == "json")
    
    # Route to appropriate handler
    try:
        if args.command == "calc":
            return calculate_checksum(args)
        elif args.command == "verify":
            if args.checksum_file:
                return verify_checksum_file(args)
            elif args.file and args.hash:
                return verify_single_file(args)
            else:
                console.print("[red]✗[/red] Error: --hash is required when verifying a single file")
                return 1
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠[/yellow] Operation cancelled by user")
        return 1
    
    except Exception as e:
        console.print(f"[red]✗[/red] Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())

