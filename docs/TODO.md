Let's update our docs with this vital info:

FIRST: 
    - Look over all the files we already have in this project, especially the docs/ dir and drafts/ dir.
    - Start processing the/this TODO.md file, PRD.md, MVP.md.
    - Use techniques and follow steps and coding guidances from drafts/Code_Steps.md

*) Update all docs and code and helper files with this info where appropriate:
GitHub URL: https://github.com/david-slimp/GameName.git  (PAUSE on GH url for now - skip for now and do not ask, just keep this note for future)
Relative path to where game will be installed on remote prod server: [see .env for path]
    Verify and report back where our GitHub url for this project is documented  (skip for now)
    Verify and report back what we have set for our final production URL for live gameplay

DONE: We need to remember to update CHANGELOG.md after every single change!  DO NOT FORGET THIS!  Add this note to take this action in 2 different important places so that you will remember to do this.... and tell me where/how you've updated things so that you WILL remember, every time.

*) We need to install Vite (using port 26472 and the initial app version should be 0.0.1), Prettier, Husky, ESLint, etc

*) Locate the .env file at the root level of this/the project and report back what variables are being set
    Most likely the PATH will need to be changed for every project
    The .env and src/scripts/deploy.sh should be set up to use npm and 'deploy:prod" to rsync files to proper place

*) The public/meta.txt needs to end up in the game's top level dir (along side the index.html)
    When all is said and done, "npm build" should copy the file to the proper place in the dist/ dir to make that happen

*) Running the npm command to deploy should also (first) run the "npm build" command so any new code gets built properly

*) Prettier should be configured to ignore the changelog file

*) ALL paths in our code, docs, and helper files should use relative paths (not absolute paths) since the game will be installed in a deep subdir on the remote production server, as well as Vite and other local tools work better with relative paths

*) For large or complex sets of commands or tasks that take multiple steps, use this TODO.md file to keep track of progress, and help you remember what to to, create step-by-step action plans, etc...   Once tasks are done, mark them as "DONE:" in the TODO.md as well as updating the CHANGELOG.md

DONE: We will want to decide on which license to use for this project and be sure the proper LICENSE file is renamed to LICENSE.txt (which is what GitHub will want) -- we can remove the other sample license files ... for THIS project we will use AGPL3.. make sure this is the one in place and properly named.

*) Never remove or reduce our initial .gitignore file, only add to it.

DONE: Make sure the changelog file for version 0.0.1 has the proper (current) date if we are just starting out a new project and are currently on version 0.0.1

*) Any created index.html or webpage front end should have the app title and verion number (like "v0.0.1") displayed somewhere on the main/front page... preferably in the upper left of any menu/tool bar.



FINALLY: After all the above is done, and after you have gotten specific confirmation everything is done, then you can ask if we should commit the initial release as exactly "v0.0.1" with an appropriate git tag that does not repeat the version number in the tag message.  If we need to "git init" first, then do it, but ask and confirm before doing it.
    - Always be sure the version number in CHANGELOG.md is in sync with package.json and public/meta.txt
