import click
import yaml
import os
from .s3_operations import S3BucketManager
from .env_data import EnvConfig



from .github_wrapper import trigger_github_workflow
    

class EnvsManager():
    def __init__(self):
        self._bucket = S3BucketManager("aryon-envs-bucket")
        self._envs_prefix = "envs/"
    def _get_token(self):
        github_token = os.environ.get("ENV_CLI_GITHUB_SECRET")
        if not github_token:
            raise ValueError("GITHUB_PAT environment variable not set.")
        return github_token
    
    def list_envs(self):
        for env in self._bucket.list(self._envs_prefix):
            yield env.replace(self._envs_prefix,"")

    def push_env_data(self,config:EnvConfig):
        config_yaml = yaml.safe_dump(config.model_dump())
        self._bucket.put_object_data(f"{self._envs_prefix}{config.name}",config_yaml)

    def get_env(self, name):
        yaml_content = self._bucket.get_object_data(f"{self._envs_prefix}{name}")
        return EnvConfig(**yaml.safe_load(yaml_content))

    def apply(self,name):
        env = self.get_env(name)
        self._get_token()
        owner,repo =  env.git_repo.split('/')[-2].replace('git@github.com:',''), env.git_repo.split('/')[-1].replace('.git', ''),
        trigger_github_workflow(
            token=self._get_token(),
            owner=owner,
            repo=repo,
            workflow_file_name=".github/workflows/apply.yml",
            workflow_inputs=dict(env=name),
            target_branch=env.follow_branch,
            )

    

_env = EnvsManager()
@click.group()
def cli():
    pass

@cli.command()
def list_envs():
    for x in _env.list_envs():
        print(x)

@cli.command()
@click.option("--git-repo",required=True)
@click.argument("name")
def new_env(git_repo,name):
    if name in _env.list_envs():
        click.echo(f"Environment '{name}' already exists.")
        return -1
    _env.push_env_data(EnvConfig(name=name, git_repo=git_repo))

@cli.command()
@click.argument("name")
def get(name):
    print(yaml.dump(_env.get_env(name).model_dump()))
    

@cli.command()
@click.argument("name")
def checkout_ref(name):
    print(_env.get_env(name).follow_branch)


@cli.command()
@click.argument("name")
def manual_apply(name):
    _env.apply(name)

@cli.command()
@click.argument("repo_url")
@click.argument("branch")
def repo_new_version(repo_url,branch):
    for name in _env.list_envs():
        env = _env.get_env(name)
        if branch == env.follow_branch and env.git_repo == repo_url:
            print(f'apply env {name}')
            _env.apply(name)


if __name__ == '__main__':
    cli()