# SET UP PROJECT
1. In terminal: Go to the folder you want to put the project in (Hint: use `cd` command)
2. In terminal: `git clone https://github.com/jessicadpo/capstone.git`
3. Navigate to the capstone folder in your file explorer.
4. Open the capstone folder in PyCharm.
5. In PyCharm's terminal:
   1. Windows: `pip install -r requirements.txt` 
   2. macOS: `pip3 install -r requirements.txt`
6. In PyCharm's terminal (Initialize the database):
   1. Windows: `python manage.py migrate` 
   2. macOS: `python3 manage.py migrate`

# CREATE A NEW BRANCH
1. Create a new branch per task, NOT per person.
2. `git pull origin main` Make sure you have the most recent version of the main branch.
3. `git checkout -b task-branch-name` Create and switch to your task branch at the same time.
4. `git status`. Double-check you're in the correct branch.
5. To run the server/website:
   1. Windows: `python manage.py runserver`
   2. macOS: `python3 manage.py runserver`
6. Access application at http://127.0.0.1:8000
7. Open a 2nd terminal for entering git commands.

# UPLOADING CHANGES TO GITHUB
### IF NOT DONE YET = Commit
1. `git add .`. Adds all the files to be committed.
2. `git status`. Double-check that all relevant files are in green.
3. `git commit -m "Descriptive commit message here"`
4. Press ENTER.
5. `git checkout main` Switch to local main branch.
6. `git pull origin main` Update local main branch to match GitHub's most recent main branch.
7. `git checkout task-branch-name` Switch back to your task branch.
8. `git merge main` Merge local main branch into your task branch.
9. If there are merge conflicts, resolve (if you can) or ask for clarifications on Discord.
10. `git push origin task-branch-name` DO NOT WRITE "git push origin main". DO NOT WRITE "git merge task-branch-name".

### IF DONE = Commit & Pull Request
1. `git add .` Adds all the files to be committed.
2. `git status` Double-check that all relevant files are in green.
3. `git commit -m "Descriptive commit message here"`
4. Press ENTER.
5. `git checkout main` Switch to local main branch (VERY IMPORTANT)
6. `git pull origin main` Update local main branch to match GitHub's most recent main branch.
7. `git checkout task-branch-name` Switch back to your task branch (VERY IMPORTANT)
8. `git merge main` Merge local main branch into your task branch.
9. If there are merge conflicts, resolve (if you can) or ask for clarifications on Discord.
10. `git push origin task-branch-name` DO NOT WRITE "git push origin main". DO NOT WRITE "git merge task-branch-name". 
11. In GitHub: Make sure your code passes all linters & automated tests 
12. In GitHub: If the code is complete and tested, create a pull request. 
14. Ping the Discord server to ask someone to review your code.

# PEER-REVIEW CODE
1. Retrieve branch from GitHub:
   1. If this is the first time reviewing this branch: `git fetch origin branch-to-review`
   2. If you have already fetched this branch before: `git pull origin task-branch-name`
2. `git checkout branch-to-review`
3. `pip install -r requirements.txt` In case a new package requirement was added.
4. `python manage.py migrate` In case models.py was modified .
5. To run the server/website:
   1. Windows: `python manage.py runserver`
   2. macOS: `python3 manage.py runserver`
6. Access application at http://127.0.0.1:8000
7. Test that all buttons, links, and form inputs work correctly (pretend you're a user)
8. **If FAIL:**
   1. On GitHub: Describe the issues found & (if you know what went wrong) propose solutions.
   2. Select "Request changes" before submitting you review
   3. Ping the code author on Discord & let them know to check your review
9. **If PASS:** Accept pull request & let the code author know that they can merge the branch.
