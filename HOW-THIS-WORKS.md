# The Book Machine — How This Works

**Date:** September 7, 2026  
**Purpose:** One writing system. Stop inventing a new one every few months.  
**Updated:** October 18, 2026. Dump, study passages, and where the guides live.

Read this when you feel lost. There is a matching page you can open in a browser: `BOOK-MACHINE-GUIDE.html`.

**Where you operate (the skin):** do not start in the file tree. In Terminal:

`~/Writing/book-machine/scripts/open-the-desk.sh`

A page opens: Continue, start a novel, your books. That is the desk. Cursor is the chair. This file is the map.

---

## 1. The one-sentence rule

You have **one writing system**. You sit with **one novel folder** at a time. Everything else is an **attic**. You may visit an attic. You do not write new pages there.

---

## 2. The three pieces (this is the whole machine)

“Template” was the old word. It made it sound like you should customize a new system for every book. You should not.

There are only three pieces:

1. **The method** — `~/Writing/book-machine/writing-tools/`  
   How we interview, sit down, and file. Already exists. Opened *beside* a novel. Never copied into a novel. Improve it once; every book inherits the change.

2. **The blank book** — `~/Writing/book-machine/blank-book/`  
   A master blank with the tabs already there (Today, chapters, vault, back office) and no story. Already exists. **Locked. Do not write in it. Do not open it.** When you start a book, the script or the partner copies it and *names* the copy. That copy is the novel.

3. **The novel** — `~/Writing/book-machine/novels/the-title/`  
   The whole book: Today, chapters, vault, and a back office the partner keeps. **This is the only folder you live in** for that story.

You do not manage a fourth piece. You do not make a new “workspace template” for Father of Mine and another for Walk This Way.

**When we change the machine later (not yet):**

1. A change to **writing-tools** is live for every novel the next time you open that book’s OPEN-ME. The method is one folder. You do not copy it.
2. A change to the **blank book** only matters for novels created *after* the change. Old books keep the shape they were born with unless we update them on purpose.
3. If the shape of a new novel should match a method change (a new tab, a new default file), update **both**. Unlock the blank book, edit, lock it again.
4. Write and test first. Do not redesign the blank book or the method in the same week you are trying to draft.

---

## 2A. Folders vs a workspace (read this when the words blur)

A **folder** is a box on the disk. The three pieces above are folders.

A **workspace** is a small file named `OPEN-ME.code-workspace`. That file is not a third system. It is a **seat assignment**. It tells Cursor: “show me these folders in one window.”

Those three folders are **not** three workspaces. You do **not** glue three workspaces together.

**When you write, you open one workspace file.** It is multi-root. It holds **two folders**:

1. The method (`writing-tools/`) — same folder every time. It does not get copied. It does not become a new workspace.
2. **This** novel (`novels/the-title/`) — a different folder depending on which book you opened.

The blank book (`blank-book/`) is never a workspace. You never open it to write. It is locked.

```
ONE window  =  ONE .code-workspace file
                    |
                    +-- folder: writing-tools     (always the same)
                    +-- folder: novels/the-title  (this book only)
```

If you have twenty ideas, you do **not** put all twenty in one writing window. You have twenty novel *folders* on the shelf. Each book that is far enough along gets its own `OPEN-ME`. Opening Father of Mine’s OPEN-ME does not open Qitat. The method is still sitting there on the left, unchanged.

**Who makes the workspace file?** The script or the partner, when the novel folder is created. You double-click `OPEN-ME`. You do not build a multi-root setup by hand.

**Factory vs a book’s desk**

1. `~/Writing/book-machine/OPEN-ME.code-workspace` — method + the whole `novels/` shelf. Use this to start a book or see what exists.
2. `~/Writing/book-machine/novels/the-title/OPEN-ME.code-workspace` — method + **one** book. This is the Tuesday desk.

---

## 3. What you manage vs what already exists vs what the partner creates

### 3.1 Already exists (do not recreate)

1. `~/Writing/book-machine/` — the factory
2. `writing-tools/` — the method
3. `blank-book/` — the blank book (locked master)
4. `novels/` — the shelf (empty until a book is created)
5. `scripts/new-novel.sh` — the photocopier

### 3.2 You manage (small list)

1. **Open the right desk** — that novel’s `OPEN-ME.code-workspace` (method + *this* book)
2. **Talk and write** — interview, scenes, edits
3. **Say the plain sentences** — *Vault this.* *I’m done for today.* *Continuing [title].*
4. **Leave attics alone** once they are snapshotted

You do not patrol `back-office/`. You do not rebuild a bible, acts file, outline, and hub before you are allowed to write.

### 3.3 The partner or the script creates

1. A new novel folder (copy of the blank book, named)
2. That novel’s `OPEN-ME.code-workspace`
3. The interview file, thin canon, thin map, and `TODAY.md` after you talk
4. Chapter files when you write
5. Vault entries, story state, session notes, and a rewritten `TODAY.md` when you stand up

If you do not want the Terminal, say: *New novel. Interview me. Title: _____*  
The partner runs the same sequence.

---

## 4. Attics (old workspaces — archive, do not start over inside them)

1. **This folder** — `CURSOR-TEMPLATE-WRITING` on the Desktop. Father of Mine, Qitat, HyperAgent dumps, the old ten-file hub. Snapshot on GitHub. Mine from here. Do not start a new novel in `writing-data/`.
2. **Walk This Way’s workspace** — a different, older, messier pile. It has Walk This Way *and* an earlier writing system (Compass and more). Same treatment later: snapshot, leave as attic, bring the *book* into the machine. Do not build a second machine inside it.
3. **Compass, HyperAgent, iCloud Cursor copies** — more attics. Visit. Do not live there.

When you are ready to let go of a large folder, you do not delete it first. You copy the book out. You keep the attic until the copy feels like the book.

---

## 5. Diagram — if you start something new

```
You have an idea
        |
        v
Say: "New novel. Interview me."
   (or run: ~/Writing/book-machine/scripts/new-novel.sh "The Title")
        |
        v
Partner / script copies the blank book
        |
        v
A folder appears:  novels/the-title/
        |
        v
Open THAT folder’s OPEN-ME.code-workspace
   (you will see: The method  |  This novel)
        |
        v
Partner interviews you  (one question at a time)
        |
        v
Partner files the talk  (interview, thin canon, Today)
        |
        v
You write a scene when you can see one
        |
        v
You stand up. Partner rewrites Today.
        |
        v
Next sitting: open the SAME workspace. Read Today. Continue.
```

You never: invent a new hub system, copy `writing-tools` into the novel, or open this Desktop archive to “set up” the book.

---

## 6. The three sittings (same machine, different first hour)

The folders do **not** change. The first thing you say changes.

### 6.1 Starting new — nothing written

1. Create the novel folder (script or partner).
2. Open that book’s `OPEN-ME`.
3. Say *Interview me.*
4. Talk. Messy is fine.
5. Write when you can see a scene. You do **not** wait for ten documents to be “done.”
6. Partner keeps the back office.

### 6.2 In motion — you are on chapter 2, 3, or 4

You already have a novel folder. You do **not** create a new one.

1. Open **that same** `OPEN-ME`.
2. Read `TODAY.md`.
3. Say *Continuing [title].*
4. Talk, write, or look (one of those, or switch).
5. Partner updates only what the story actually moved.
6. If you left for a week, you are not starting over. Today is the memory.

If the book still lives in an attic (Father of Mine in this repo, Walk This Way next door), first **bring it in**: copy into `novels/the-title/`, write Today, leave the attic untouched. Then this sitting applies.

### 6.3 The draft exists — now you are editing

Still the same novel folder. Still the same `OPEN-ME`.

1. Open that book.
2. Say *This draft needs work. Intake it.*
3. The pages are the book. Partner reads them. Partner does **not** make you fill a hub so the draft is allowed to exist.
4. You get a short list of what matters, with places in the book.
5. `TODAY.md` becomes one fight (voice, or structure, or one character).
6. You edit. Partner files the ripples.

Adding chapters to a finished draft is sitting 6.2. Hating the prose is sitting 6.3 with one fight: the sentences.

### 6.4 The dump — every sitting, one pile

The dump is not a fourth way to write. It is how raw material arrives while you are starting, continuing, or rewriting.

1. One dump per novel: `novels/the-title/dump/`.
2. Throw in prose, notes, character scraps, half-outlines, and worries. You do not sort them.
3. The partner files what became a decision: chapters only when you say it is the book, canon, story map, or the vault.
4. Say *Dump this* with no interview and no new chapter when you only need the pile caught.

`dump/study/` is for short passages from novels you own, print and electronic. Private education. The GitHub repo is private, so those snippets may live there and in an author folder. Label them with the author and the book. They are teachers. They are not your chapters. The partner does not scold, and does not paste those sentences into the manuscript.

---

## 7. What you open, every Tuesday

1. **To write a book you already started in the machine** — that book’s `OPEN-ME.code-workspace`
2. **To start a new book** — factory `~/Writing/book-machine/OPEN-ME.code-workspace`, then create the novel, then switch to *that* book’s `OPEN-ME`
3. **To mine an attic** — this workspace, or later Walk This Way’s workspace, in a *separate* window. Copy out. Do not move in.

If the status bar or the folder list looks like the old ten-file house, you are in an attic.

---

## 8. What you say (plain sentences)

1. *New novel. Interview me. Title: _____*
2. *Continuing [title].*
3. *This draft needs work. Intake it.*
4. *Vault this.*
5. *Park that for book two.*
6. *I’m done for today.*
7. *Dump this.*
8. *This is study.* Name the author and the book.

---

## 9. What you never do again

1. Build a new writing system because the last one felt messy.
2. Write inside `blank-book/`.
3. Copy the method into the novel.
4. Keep ten documents in sync by hand.
5. Start a new novel inside this Desktop archive or inside Walk This Way’s old workspace.
6. Open five old workspaces “just to be safe” and then not know which one is the book.

---

## 10. Walk This Way (later, same recipe)

1. That workspace is an attic, like this one, only larger.
2. Snapshot it (git / GitHub) when you are ready, the way we are snapshotting this pile.
3. Leave it.
4. Bring **the manuscript** into `~/Writing/book-machine/novels/walk-this-way/`.
5. Tools that belong to *all* books go into `writing-tools/` once — not a second Compass living beside a second machine.

Until that sitting, do not start rewriting Walk This Way in a brand-new invented folder.

---

## 11. Paths (this Mac, local disk, not iCloud)

| What | Path |
|------|------|
| The machine | `~/Writing/book-machine/` |
| The method | `~/Writing/book-machine/writing-tools/` |
| The blank book | `~/Writing/book-machine/blank-book/` |
| Your books | `~/Writing/book-machine/novels/` |
| New-book script | `~/Writing/book-machine/scripts/new-novel.sh "The Title"` |
| This attic | `~/Desktop/CURSOR-TEMPLATE-WRITING/` |
| Walk This Way attic (Air copy) | `~/Writing/Walk_This_Way-draft-3.1-complete/` |
| The machine on GitHub (private) | `https://github.com/timothy-j-smith/book-machine` |
| This attic on GitHub (private) | `https://github.com/timothy-j-smith/cursor-writing-template` |
| Friend’s interface photos | `~/Desktop/CURSOR-TEMPLATE-WRITING/friend-ui/` |
| Open the first desk | `~/Writing/book-machine/scripts/open-the-desk.sh` |

The browser desk is a first door: continue, start a book, list books. The website-like front end is not built yet. Her screenshots in `friend-ui/` are the reference for that face. The folders above stay the back end.

---

## 12. If you get that lost feeling

1. You are not starting over.
2. Open `~/Writing/book-machine/` and this guide.
3. If the book already has a folder under `novels/`, open **that** `OPEN-ME` and read `TODAY.md`.
4. If it does not, you are either starting new (section 6.1) or bringing a book in from an attic (section 6.2, last paragraph).
5. Do not create a new system.
