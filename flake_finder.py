#!/usr/bin/env python3

import sys
import subprocess
import re

from argparse import ArgumentParser

MAX_RUNS = 1000  # Maximum number of runs to prevent infinite loops

RED = "\033[0;31m"
GREEN = "\033[0;32m"
LIGHT_BLUE = "\033[1;34m"
RESET = "\033[0m"


def colorize_failed(line: str) -> str:
    return line.replace("Failed ", f"{RED}Failed {RESET}").replace(
        "Passed", f"{GREEN}Passed{RESET}"
    )


def run_test(run_num: int, additional_dotnet_args: list[str]):
    print(f"{LIGHT_BLUE}Starting Run #{run_num}{RESET}")

    dotnet_test_args = []
    standard_dotnet_test_args = [
        "dotnet",
        "test",
        "-v",
        "n",
        "-l:console;verbosity=detailed",
    ]
    no_restore_and_build_args = ["--no-restore", "--no-build"]

    if run_num == 1:
        dotnet_test_args = standard_dotnet_test_args + additional_dotnet_args
    else:
        dotnet_test_args = (
            standard_dotnet_test_args
            + no_restore_and_build_args
            + additional_dotnet_args
        )

    process = subprocess.Popen(
        dotnet_test_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    keep = False
    passed = failed = 0

    for line in process.stdout:
        line = line.rstrip()

        # Always show logs coming from ITestOutputHelper:
        if re.search(r"Standard Output Messages:", line):
            print(line)
            keep = True
            continue

        # Stop printing lines after a log if run is done
        if re.search(r"Test Run Successful.", line) or re.search(
            r"Test Run Failed.", line
        ):
            keep = False
            continue

        # Per-test result lines (Passed/Failed)
        if re.match(r"^\s+(Passed\s|Failed\s)", line):
            if re.match(r"^\s+(Failed\s)", line):
                print(colorize_failed(line))
                keep = True
            else:
                print(colorize_failed(line))
                keep = False
            continue

        # Summary counts
        if re.match(r"^\s*Passed:\s+\d+", line):
            passed = int(re.search(r"\d+", line).group())
            continue

        if re.match(r"^\s*Failed:\s+\d+", line):
            failed = int(re.search(r"\d+", line).group())
            continue

        # Keep printing lines after a failed test block
        if keep and len(line.strip()) > 0:
            print(line)

    process.wait()
    print(f"{'':80}", end="\r", file=sys.stderr)  # clear progress
    print(
        f"Run {run_num} Complete ({GREEN}Passed: {passed}{RESET} {RED}Failed: {failed}{RESET})"
    )
    if failed > 0:
        input("Press any key to continue to next run...")


def main():
    parser = ArgumentParser(
        description="Run dotnet tests multiple times and capture ITestOutputHelper output."
    )
    parser.add_argument(
        "dotnet_args", nargs="*", help="Additional arguments to pass to dotnet test"
    )
    args = parser.parse_args()

    for i in range(1, MAX_RUNS):
        run_test(i, args.dotnet_args)


if __name__ == "__main__":
    main()
