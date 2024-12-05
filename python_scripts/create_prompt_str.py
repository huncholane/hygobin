import os
import subprocess
import click


@click.command("Generate a PS1 prompt")
@click.option(
    "--branch-style",
    "-b",
    default="\\e[32m",
    help="The style used for the branch string.",
)
@click.option(
    "--user-style", "-u", default="\\e[33m", help="The style used for the user string."
)
@click.option(
    "--hostname-style",
    "-h",
    default="\\e[34m",
    help="The style used for the hostname string.",
)
@click.option(
    "--path-style", "-p", default="\\e[35m", help="The style used for the path string."
)
@click.option(
    "--additional-info",
    "-a",
    default="\\d \\t\\n$(random_quote)",
    help="Additional information to display in the prompt on the second line.",
)
@click.option(
    "--prompt-symbol",
    "-s",
    default="🚀",
    help="The symbol used to indicate the prompt.",
)
@click.option(
    "--line-start",
    "-l",
    default=">>> ",
    help="The symbol used at the beginning of each new line in the prompt.",
)
def main(
    branch_style,
    user_style,
    hostname_style,
    path_style,
    additional_info,
    prompt_symbol,
    line_start,
):
    branch = subprocess.getoutput("git branch --show-current")
    branch_str = f" ({branch_style}{branch}\\e[0m)" if branch else ""
    additional_info = f"{additional_info}\\n" if additional_info else ""
    # Create the PS1 prompt using escape sequences
    ps1_prompt = (
        f"{line_start}{user_style}\\u"  # User
        f"{hostname_style}@\\h"  # Hostname
        f"{path_style}:\\w"  # Current working directory
        f"{branch_str}\\n"  # Git branch (if available)
        f"{additional_info}"  # Additional information
        f"\\e[0m{prompt_symbol} "  # Reset formatting and show the prompt symbol
    ).replace("\\n", f"\\n{line_start}")

    # Print the generated PS1 prompt
    print(ps1_prompt)


if __name__ == "__main__":
    main()
