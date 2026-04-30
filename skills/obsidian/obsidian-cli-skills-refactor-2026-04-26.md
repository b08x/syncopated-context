---
title: "Obsidian CLI Skills Refactor - 2026-04-26"
tags:
  - obsidian-cli
  - skills
  - refactor
last updated: 2026-04-26 18:59:00
---
![[/Daily/assets/Code Pattern Extraction/image-800-800.png]]



[18:34:17] Yeah.
 Alright so the objective is to refactor the um skill uh to
 uh include more specifics in terms of uh category and tag
 uh constraints um, other things like that Uh. use the uh
 obsidian uh skill that utilizes the obsidian C_L_I_

[18:34:40] Hmm.
 For like figuring out um you know what, tags to use based
 on what's already there, uh what's redundant wh um
 note that um

[18:35:05] Note that um
 Uh the obsidian C_L_I_ is also also useful for just
 extracting uh the headers from nodes to be able to kind of
 uh save on on uh processing context and what not.

[18:53:52] Yep.
 So ultimately uh from code insights uh what I'm gonna want
 to get out of that is y you know, eighty to ninety percent
 of the sessions um are sort of um test in uh what works
 what doesn't uh so there's going to be very few sessions
 that contain a workflow from end to end that uh you know uh
 i i you know,
 contains the best um you know steps or whatever um so what
 I'm gonna need you know what I'm looking for uh to get out
 of each session uh is uh is to extract the

[18:54:06] whatever. Um so what I'm gonna need you know what I'm
 looking for uh to get out of each session uh is uh is to
 extract the parts that work uh extract the parts that
 worked um compare them to uh other sessions where similar
 patterns are found uh and to optimise uh we can use Hermes
 uh s for

[18:55:12] So for example right now um I'm in the middle of a session
 that's creating a skill that's going to organise the
 folders in uh my obsidian vault.
 Um so there's uh several aspects to that session that I
 would like to keep and apply uh for future use and then you
 know the rest of it can be discarded uh and as far as
 future use uh that might be creating additional skills that
 might be um you know creating an agent that might be
 creating a script that might be creating an Ansible
 playbook a combination of those things uh or something else
 entirely.

[18:55:59] And certainly one of the goals is to move away from the uh
 mark-down skills uh into more programic uh type based uh D
SPI modules, either in Python or Ruby.

[18:56:22] And yeah again there's certainly um a good amount of this
 that can be transferred into uh the Ansible context.

[18:59:02] Yeah so for like right now uh the CLOD code is in the
 middle of a task uh, reorganizing files and uh I believe it
 calls like several extra steps just to move files uh I
 guess you know these are for security you know reasons or
 what have you um but it's a little uh uh you know that's a
 lot of overhead on a uh Linux system

[18:59:30] but it's a little uh you know that's a lot of overhead on a
 uh Linux system.
 And I distinguish Linux system here uh only because uh it's
 not necessary given other f um environmental factors uh for
 example you know S_E_ Linux and permissions and containers
 and stuff like that uh I can't speak for Windows at the
 moment.