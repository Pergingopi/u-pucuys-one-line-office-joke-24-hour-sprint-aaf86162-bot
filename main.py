#!/usr/bin/env python3
"""One-Line Office Joke: 24-Hour Sprint - one line about office life.

Pure Python 3.13 standard library. The program writes one joke to
/output/entry.txt. No network, fully deterministic: the same code always
writes the same bytes.

The joke (65 characters, no trailing newline -- the gate counts
characters, so the file holds exactly the joke and nothing else):
    The office plants get more one-on-ones with my manager than I do.

Why this line: it takes the manager's "one-on-one" ritual literally and
hands it to the office plants, so the punch lands on the last three
words -- the narrator is outranked by a fern. One sentence, one twist,
a specific office detail everyone recognises, nothing after the punch
to dilute it.

Usage: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os

JOKE = "The office plants get more one-on-ones with my manager than I do."


def _validate(joke):
    # Gate guard: the entry must be a single non-blank line of 1-200
    # characters, or the sealed scorer rejects it outright. Reject any
    # control character (including \n, \r, \t, NUL) so nothing invisible
    # can slip into the counted text.
    if not isinstance(joke, str) or not joke.strip():
        raise ValueError("JOKE must be a non-blank string")
    if joke != joke.strip():
        raise ValueError("JOKE must not have leading or trailing whitespace")
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in joke):
        raise ValueError("JOKE must not contain control characters")
    if not 1 <= len(joke) <= 200:
        raise ValueError("JOKE must be 1-200 characters")


def main():
    _validate(JOKE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = JOKE.encode("utf-8")
    final = os.path.join(out_dir, "entry.txt")
    # Exclusive tmp file: never clobber a stray leftover, and clean it up
    # on any failure so a half-written file can never be mistaken for the
    # entry.
    tmp = os.path.join(out_dir, ".entry.txt.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, final)
        # fsync the directory so the rename itself is durable.
        dir_fd = os.open(out_dir, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
    os.chmod(final, 0o644)
    # Read-back: the file on disk must be byte-identical to the joke,
    # with no trailing newline and no extra bytes.
    with open(final, "rb") as f:
        if f.read() != data:
            raise ValueError("read-back mismatch: entry.txt is not exactly the joke")


if __name__ == "__main__":
    main()
