# Yazik

Yazik is a tool that aims to help improve vocabulary. It tracks words, their definitions, and where they were encountered.

Yazik is the English phonetic spelling of the Czech word Jazyk, which means 'tongue'.

## Dependencies

python3

## Installation

Checkout yazik.

Add the path to bin/yazik to your shell. eg, for sh-like shells with the repository at ~/apps/yazik:
```
export PATH=${PATH}:~/apps/yazik/bin
```

And add the yazik module to pythons modules list.
```
export PYTHONPATH=${PYTHONPATH}:~/apps/yazik
```
## Usage

Use *--help* for full command information. The below lists the main set of steps to use.

### Add an author (optional)

```
$ yazik author add William Shakespeare
```

### Add a book (optional)

Add a book without author:
```
$ yazik book add Romeo And Juliet
```
The book can be linked to an author. First create the author (See Add an author) and run instead:
```
$ yazik book add Romeo And Juliet --author William Shakespeare
```

### Add a word

Add a word, not linked to a book.
```
$ yazik word add Hath
```
Add a word, but linked to a book. The book must be created first (See Add a book).
```
$ yazik word add Hath --book Romeo And Juliet
```
Yazik will print the definition of the word if it hasn't been seen before, otherwise it will let you know that it's a new word.

You can then add a definition for a new word.
```
$ yazik word def --word Hath archaic version of HAVE
```

## Notes

Yazik will assume the last word or book so these options are generally not needed. eg, the below command will add a definition for *hath* provided that *hath* was the most recently added word.
```
$ yazik word def archaic version of HAVE
```

The --book and --author options will search for the most appropriate match so full names and titles are often not needed, only enough to distinguish them from other entries. Yazik will emit a message if the provided values are ambiguous or result in no matches.

## Credits

Yazik is copyright (c) 2018 by Acke and released under the GPLv3.
See the accompanying LICENSE file for more information.



