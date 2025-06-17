#!/usr/bin/env python3

import sys
import subprocess
import re

from argparse import ArgumentParser

RED = "\033[0;31m"
GREEN = "\033[0;32m"
LIGHT_BLUE = "\033[1;34m"
RESET = "\033[0m"


def colorize_failed(line: str) -> str:
    return line.replace("Failed ", f"{RED}Failed {RESET}").replace(
        "Passed ", f"{GREEN}Passed {RESET}"
    )


def run_test(run_num: int, additional_dotnet_args: list[str], show_passed: bool):
    run_passed = run_failed = 0

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
    failed_test_namespaces = []  # Collect namespaces for failed tests in this run

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
                run_failed += 1
                print(colorize_failed(line))
                keep = True
                # Try to extract the namespace from the test name
                test_match = re.search(r"Failed\s+(.+?)\s*\[", line)
                if test_match:
                    full_test_name = test_match.group(1)
                    failed_test_namespaces.append(full_test_name)
                else:
                    failed_test_namespaces.append("<unknown>")
            else:
                run_passed += 1
                if show_passed:
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
    return failed_test_namespaces, run_passed, run_failed


def main():
    parser = ArgumentParser(
        description="Run dotnet tests multiple times and capture ITestOutputHelper output."
    )
    parser.add_argument(
        "runs",
        type=int,
        help="Number of times to run the tests",
    )
    parser.add_argument(
        "--show-passed",
        action="store_true",
        help="Show output for passed tests as well",
    )
    parser.add_argument(
        "dotnet_args", nargs="*", help="Additional arguments to pass to dotnet test"
    )
    args = parser.parse_args()

    all_failed_namespaces = {}
    total_passed = total_failed = 0
    for i in range(1, args.runs + 1):
        failed_namespaces, run_passed, run_failed = run_test(
            i, args.dotnet_args, args.show_passed
        )
        total_passed += run_passed
        total_failed += run_failed
        for ns in failed_namespaces:
            if ns not in all_failed_namespaces:
                all_failed_namespaces[ns] = 0
            all_failed_namespaces[ns] += 1

    print(f"\n{LIGHT_BLUE}====Test Summary:===={RESET}")
    print(f"Total Runs: {args.runs}")
    print(f"{GREEN}Total Passed: {total_passed}{RESET}")
    print(f"{RED}Total Failed: {total_failed}{RESET}")

    if all_failed_namespaces:
        print(f"\n{RED}Failed Tests Summary:{RESET}")
        for ns, count in sorted(all_failed_namespaces.items(), key=lambda x: -x[1]):
            print(f"  {ns}: {count} failures")
    else:
        print(f"\n{GREEN}No test failures detected in any namespace!{RESET}")


if __name__ == "__main__":
    main()
