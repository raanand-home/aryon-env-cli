import os
from github import Github, Auth, InputGitAuthor

def trigger_github_workflow(token,owner,repo,workflow_file_name,target_branch,workflow_inputs):
    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_user(owner).get_repo(repo)
    workflow = repo.get_workflow(workflow_file_name)
    success = workflow.create_dispatch(
        ref=target_branch, 
        inputs=workflow_inputs
    )
    if not success:
        raise Exception("Faild_to_launch")