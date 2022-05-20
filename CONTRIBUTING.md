## Development (developers working on feature branches)
1. work from an issue for feature/bug (is assigned to you by admin or you make an issue).  

    Issues should be about a day or two worth of work, so the branches don't stay out too long.  

    On the gitlab website, look on the left menu for "Issues".

2. make a merge request and branch from an issue.  

    On the gitlab issue detail page, right under the issue description, there is a green button that says create merge request. (The default options should be correct: make branch and merge request, source branch is master).

    Click it, and give it a few seconds, and it will make you a new branch called `<issue number>-<issue name>` and take you to merge request page with the title “WIP: `<issue>`.  
    
    On the gitlab website, look on the left menu for "Merge Requests".

3. do your work on the new branch.  

    To see the new branch locally, you need to run "fetch". checkout the new branch to switch to it.
add any comments/questions/discussions about the feature/bug to the issue page.

4. commit/push all your code.  

    on the merge request page, check that the pipeline passes.
    if all your completed code is pushed and the pipeline passes, click "resolve WIP status" on the merge request, notify an admin/approver.

5. the approver will review your code.  

    if the code is ready, the admin will merge the code to master, and delete the branch.  
if the code is not ready, the admin will add comments about what needs to be addressed and mark it WIP. address the issues and repeat 4 and 5.


## Workflow and Release (approver/admin merging to production)
using the gitlab flow process.

Branches:
* feature: branches from and to master for developer's work
* master: is protected, integration of feature branches
* production: is tagged with versions for releases

Process:
1. use issues and merge requests to make feature branches from master, CI runs on feature branch on push.
2. code reviews on merge requests.
3. once WIP is resolved on merge requests, branch is merged to master and CI runs on master.
4. when code is ready to be released, merge to production branch and tag.
5. when tagged on production, run CD to deploy new release to target.

https://docs.gitlab.com/ee/topics/gitlab_flow.html
https://about.gitlab.com/blog/2016/07/27/the-11-rules-of-gitlab-flow/ 
