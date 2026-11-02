# Setting up the Mac Studio

The Mac Studio gets the Book Machine in the same place as the MacBook Air: `~/Writing/book-machine`. The old trial copy goes to the Trash first.

Open Terminal (Applications → Utilities → Terminal). Paste **one line at a time** and press Enter after each. Read what it prints before the next line. If anything says `error` or `fatal`, or does not match what this page says, stop and show the partner.

**If an agent runs this page:** run one step at a time and compare the output with what the step says. At any mismatch, stop and report the exact output. Do not use `rm`. Do not skip a check. The moves outside the workspace (the Trash, `~/Writing`) need the agent's full permissions, so the author will be asked to approve them.

## What is safe

- Only one folder moves: `~/Book Machine Mac Studio`. It holds the trial copy and the empty test novel, *The Day the Music Died*.
- It goes to the Trash, not straight to deletion. You can drag it back until you empty the Trash.
- GitHub and the MacBook Air are not touched. Qitat al-Medina and its whole history live there.
- Nothing in Part 2 deletes anything. A clone only adds a folder, and it refuses if the folder already exists.

## Part 1: clean up the trial copy

**1. Find every copy on this Mac.**

```bash
find ~ -maxdepth 5 -type d -name blank-book 2>/dev/null
```

Should print exactly one line, ending in `Book Machine Mac Studio/book-machine/blank-book`. More than one line: stop.

**2. Step into the trial copy.**

```bash
cd ~/"Book Machine Mac Studio/book-machine"
```

Prints nothing.

**3. See what the trial copy has that GitHub does not.**

```bash
git status --short
```

Should print nothing, or lines starting with `??` for any of these: `novels/the-day-the-music-died/`, `writing-tools/.gitignore`, `writing-tools/openmemory.md` (the last two are OpenMemory leftovers). Anything else (other names, or lines starting with `M`): stop.

**4. Check for saves that never reached GitHub.**

```bash
git log origin/main..HEAD --oneline
```

Should print nothing. Anything printed: stop.

**5. Step back out to your home folder.**

```bash
cd ~
```

Prints nothing. You cannot move a folder you are standing in.

**6. Unlock everything inside it, so the Trash can empty it later.**

```bash
chmod -R u+w ~/"Book Machine Mac Studio"
```

Prints nothing.

**7. Move it to the Trash.**

```bash
mv ~/"Book Machine Mac Studio" ~/.Trash/
```

Prints nothing.

**8. Confirm it is gone.**

```bash
find ~ -maxdepth 5 -type d -name blank-book 2>/dev/null
```

Should print nothing.

**9. Confirm the new spot is empty.**

```bash
ls ~/Writing
```

Should say `No such file or directory`, or list folders that are not `book-machine`. If you see `book-machine`: stop.

Part 1 is done. Empty the Trash in Finder whenever you like.

## Part 2: a fresh copy from GitHub

**1. Make the Writing folder.**

```bash
mkdir -p ~/Writing
```

**2. Step into it.**

```bash
cd ~/Writing
```

**3. Download the Book Machine.**

```bash
git clone https://github.com/timothy-j-smith/book-machine.git
```

Prints a few lines ending in `done`. If it asks for a username or password: stop.

**4. Step into it.**

```bash
cd book-machine
```

**5. Check it is the newest save.**

```bash
git log -1 --oneline
```

Prints the newest save on GitHub. A fresh clone always has it. Show this line to the partner.

**6. Lock the blank book, the same as on the Air.**

```bash
chmod -R a-w blank-book
```

**7. Look at the shelf.**

```bash
ls novels
```

Should show `README.md` and `qitat-al-medina`.

**8. Remove two extensions before opening the novel.** In Cursor, open Extensions (the four-squares icon on the left). Search for each name below. If it is installed, click Uninstall.

- **OpenMemory** (by mem0). It writes its own memory rule into `writing-tools/` every time Cursor opens. The machine's rule: the files are the memory, no memory plugin.
- **Unique Window Colors.** It paints the title bar, side bar, and status bar and writes those colors into the novel's `OPEN-ME.code-workspace` every time Cursor opens.

**9. Open the novel.** In Cursor: File → Open Workspace from File → `~/Writing/book-machine/novels/qitat-al-medina/OPEN-ME.code-workspace`.

**10. Check that nothing wrote itself in.**

```bash
cd ~/Writing/book-machine && git status --short
```

Should print nothing. If it lists files, show the partner.

## Every day after this

Both Macs share one copy on GitHub. They do not sync on their own.

- **Sit down:** the partner pulls the newest save before work starts.
- **Stand up:** the partner shows what changed and asks *Save this to GitHub?*

If you update by hand, the blank book needs unlocking first, or the pull fails with `Permission denied`:

```bash
cd ~/Writing/book-machine
chmod -R u+w blank-book
git pull --ff-only
chmod -R a-w blank-book
```

One line at a time.
