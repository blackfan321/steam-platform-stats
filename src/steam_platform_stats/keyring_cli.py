from keyring.errors import KeyringError
from rich.console import Console
from rich.prompt import Confirm, Prompt

from .credentials import SteamCredentials
from .steam_api import validate_credentials

console = Console()
err_console = Console(stderr=True)


def _cancelled() -> None:
    console.print("\n[dim]Cancelled.[/dim]\n")


def _prompt(message: str, *, password: bool = False) -> str | None:
    try:
        return Prompt.ask(message, password=password).strip()
    except (KeyboardInterrupt, EOFError):
        _cancelled()
        return None


def _ask_steam_id() -> int | None:
    while True:
        steam_id_raw = _prompt("[cyan]Steam64 ID[/cyan]")
        if steam_id_raw is None:
            return None

        try:
            return int(steam_id_raw)
        except ValueError:
            console.print(
                "\n[red]Error:[/red] Steam64 ID must be a number. Try again.\n"
            )


def _ask_api_key() -> str | None:
    while True:
        steam_api_key = _prompt("[cyan]Steam API key[/cyan]", password=True)
        if steam_api_key is None:
            return None

        if steam_api_key:
            return steam_api_key

        console.print("\n[red]Error:[/red] API key cannot be empty. Try again.\n")


def _print_store_guide() -> None:
    console.print(
        "1. Copy your Steam64 ID from "
        + "[link=https://steamid.xyz/]steamid.xyz[/link]\n"
        + "2. Create an API key at "
        + "[link=https://steamcommunity.com/dev/apikey]"
        + "steamcommunity.com/dev/apikey[/link]\n"
        + "3. Enter both below to save them to the [bold]system keyring[/bold]\n"
    )


def run_keyring_help() -> None:
    console.print(
        "[bold]Available commands:[/bold]\n"
        + "\n"
        + "  [cyan]store[/cyan]   — save credentials to the system keyring\n"
        + "  [cyan]status[/cyan]  — show whether credentials are stored\n"
        + "  [cyan]clear[/cyan]   — remove credentials from the system keyring\n"
    )


def run_keyring_status() -> None:
    try:
        config = SteamCredentials.load_from_keyring()
    except KeyringError as e:
        err_console.print(
            f"[yellow]Warning:[/yellow] could not read system keyring ({e})"
        )
        return
    except ValueError as e:
        err_console.print(f"[yellow]Warning:[/yellow] {e}")
        return

    if config is None:
        console.print(
            "\n[yellow]Keyring empty[/yellow] — no Steam credentials stored.\n"
            + "\n"
            + "[dim]Run `steam-platform-stats keyring store` to save them.[/dim]\n"
        )
        return

    console.print(
        f"\nSteam64 ID: [bold]{config.steam_id}[/bold]\n[green]Keyring OK[/green]\n"
    )


def run_keyring_store() -> None:
    console.clear()
    _print_store_guide()

    steam_id = _ask_steam_id()
    if steam_id is None:
        return

    steam_api_key = _ask_api_key()
    if steam_api_key is None:
        return

    console.print("\n[dim]Checking credentials with Steam API...[/dim]")
    result = validate_credentials(steam_api_key, steam_id)
    if not result.ok:
        err_console.print(f"[red]Error:[/red] {result.message}\n")
        return

    try:
        SteamCredentials.save_to_keyring(steam_api_key, steam_id)
    except KeyringError as e:
        err_console.print(
            f"[red]Error:[/red] could not write to system keyring: {e}\n"
        )
        return

    console.print(f"[green]{result.message}[/green]. Saved to the system keyring.\n")


def run_keyring_clear() -> None:
    try:
        empty = SteamCredentials.load_from_keyring() is None
    except KeyringError as e:
        err_console.print(f"[red]Error:[/red] could not read system keyring ({e})\n")
        return
    except ValueError:
        empty = False  # incomplete credentials — still offer clear

    if empty:
        console.print("\n[dim]Keyring already empty — nothing to clear.[/dim]\n")
        return

    console.print()
    try:
        confirmed = Confirm.ask(
            "Remove Steam credentials from the system keyring?", default=False
        )
    except (KeyboardInterrupt, EOFError):
        _cancelled()
        return

    if not confirmed:
        _cancelled()
        return

    try:
        SteamCredentials.clear_keyring()
    except KeyringError as e:
        err_console.print(
            f"\n[red]Error:[/red] could not clear system keyring ({e})\n"
        )
        return

    console.print("\n[green]Credentials removed from the system keyring.[/green]\n")
