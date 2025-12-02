import click
from .s3_operations import S3BucketManager
from .env_data import EnvConfig
import yaml

class EnvsManager():
    def __init__(self):
        self._bucket = S3BucketManager("aryon-envs-bucket")
    
    def list_envs(self):
        for env in self._bucket.list():
            yield env

    def push_env_data(self,config:EnvConfig):
        config_yaml = yaml.safe_dump(config.model_dump())
        self._bucket.put_object_data(config.name,config_yaml)

    def get_env(self, name):
        yaml_content = self._bucket.get_object_data(name)
        return EnvConfig(**yaml.safe_load(yaml_content))
    

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


if __name__ == '__main__':
    cli()